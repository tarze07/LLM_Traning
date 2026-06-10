# vLLM obsługujące elementy wewnętrzne: PagedAttention, ciągłe dozowanie, wstępne wypełnianie fragmentami

> Dominacja vLLM w 2026 r. opiera się na trzech łącznych wartościach domyślnych, a nie na jednej sztuczce. Funkcja PagedAttention jest zawsze włączona. Ciągłe przetwarzanie wsadowe wprowadza nowe żądania do aktywnej partii pomiędzy iteracjami dekodowania. Kawałki wstępnego wypełnienia są długimi monitami, dzięki czemu tokeny dekodowania nigdy nie głodują. Włącz wszystkie trzy, a Lama 3.3 70B FP8 na jednym H100 SXM5 osiąga prędkość 2200-2400 tok/s przy 128 jednocześnie — około 25% powyżej wartości domyślnej vLLM i 3-4 razy naiwna pętla PyTorch. Ta lekcja odczytuje moduł planujący i jądro uwagi na poziomie, który możesz narysować na diagramie, a kończy się zabawkowym ciągłym modułem dozującym w `code/main.py`, który planuje wstępne wypełnienie i dekodowanie w sposób, w jaki robi to vLLM.

**Typ:** Ucz się
**Języki:** Python (stdlib, harmonogram ciągłego przetwarzania wsadowego zabawek)
**Wymagania wstępne:** Faza 17 · 01 (Udostępnianie modelu), Faza 11 (Inżynieria LLM)
**Czas:** ~75 minut

## Cele nauczania

- Wyjaśnij PagedAttention jako alokator pamięci podręcznej KV: bloki, tabele bloków i dlaczego fragmentacja utrzymuje się poniżej 4% przy obciążeniu produkcyjnym.
- Diagram ciągłego dozowania na poziomie iteracji: jak gotowe sekwencje opuszczają partię, a nowe dołączają bez opróżniania.
- Opisz fragmentaryczne wstępne wypełnienie w jednym zdaniu i podaj, jaką metrykę opóźnienia chroni (wskazówka: jest to ogon TTFT, a nie średnia przepustowość).
- Wymień problem 2026 vLLM v0.18.0, który gryzie zespoły, umożliwiając jednocześnie każdą optymalizację.

## Problem

Naiwna pętla obsługi PyTorch uruchamia jedno żądanie na raz: tokenizacja, wstępne wypełnienie, dekodowanie do EOS, powrót. U jednego użytkownika to działa. Przy stu jest już kolejka cierpliwych ludzi. Oczywista poprawka — statyczne wsadowanie — umieszcza każde żądanie w najdłuższym wierszu polecenia w oknie, umieszcza każde dekodowanie w najdłuższym oczekiwanym wyjściu i wstrzymuje całą partię w najwolniejszej sekwencji. Płacisz za dopełnienie, którego nigdy nie używasz, a szybkie żądania czekają na powolne.

vLLM rozwiązuje trzy problemy na raz. PagedAttention zapobiega fragmentacji pamięci podręcznej KV przed zjedzeniem 60-80% pamięci GPU, tak jak robi to klasyczna alokacja ciągła. Ciągłe przetwarzanie wsadowe pozwala żądaniom dołączać do partii i ją opuszczać pomiędzy każdą iteracją dekodowania, dzięki czemu partia jest zawsze pełna prawdziwej pracy. Podzielone wstępne wypełnienie dzieli monit zawierający 32 tys. tokenów na ~512 tokenów wycinków, które przeplatają się z dekodowaniem, więc długi monit nie blokuje każdego tokenu dekodowania na GPU.

Domyślna produkcja na rok 2026 obejmuje wszystkie trzy włączone. Musisz zrozumieć, co robi każdy z nich, ponieważ wszystkie tryby awarii znajdują się w harmonogramie, a nie w modelu.

## Koncepcja

### PagedAttention jako system pamięci wirtualnej

Pamięć podręczna KV to `num_layers × 2 × num_heads × head_dim × seq_len × bytes_per_element` na sekwencję. Dla Lamy 3.3 70B przy 8192 tokenach, czyli około 1,25 GB na sekwencję w BF16. Jeśli wstępnie zarezerwujesz 8192 slotów na każde żądanie, ale przeciętne żądanie wykorzystuje tylko 1500 tokenów, zmarnujesz około 82% zarezerwowanego HBM. Klasyczne dozowanie pozwala na pokrycie tych strat.

PagedAttention zapożycza pomysł z pamięci wirtualnej systemu operacyjnego. Pamięć podręczna KV nie jest ciągła w sekwencji. Jest przydzielany w blokach o stałym rozmiarze (domyślnie 16 tokenów). Każda sekwencja ma tabelę bloków, która odwzorowuje pozycje tokenów logicznych na identyfikatory bloków fizycznych. Kiedy sekwencja przekracza przydzielone bloki, dodawany jest jeszcze jeden blok. Po zakończeniu jego bloki wracają do puli.

Fragmentacja spada z 60-80% (klasyczna) do poniżej 4% (PagedAttention). Nie włączasz PagedAttention z flagą — jest to jedyny statek vLLM z alokatorem. Pokrętło to `--gpu-memory-utilization` (domyślnie 0,9), które informuje vLLM, ile HBM ma zarezerwować dla bloków KV po załadowaniu odważników i aktywacjach.

### Ciągłe przetwarzanie wsadowe na poziomie iteracji

Stare „dynamiczne grupowanie wsadowe” czekało na wypełnienie partii przez okno (powiedzmy 10 ms), a następnie uruchamiało wstępne wypełnianie + dekodowanie + dekodowanie + dekodowanie, aż do zakończenia każdej sekwencji. Szybkie sekwencje zostały wcześniej zakończone i pozostały bezczynne, podczas gdy procesor graficzny dokończył wolne.

Pomiędzy każdym etapem dekodowania działa ciągłe przetwarzanie wsadowe. Nazwij zbiór działających sekwencji listą `RUNNING`. W każdej iteracji:

1. Każda sekwencja w `RUNNING`, która właśnie trafiła w EOS lub max_tokens, jest usuwana.
2. Osoba planująca sprawdza kolejkę oczekujących. Jeżeli są wolne bloki KV, dopuszcza nowe sekwencje (wstępnie wypełnione lub wznowione).
3. Przejście w przód działa na tym, co znajduje się teraz w `RUNNING`, emitując jeden nowy token na sekwencję.

Rozmiar partii nigdy nie jest dopełniany do stałej liczby. Sekwencje znajdujące się w różnych pozycjach wyjścia mają jedną połączoną do przodu. W vLLM 2026 nazywa się to `V1 scheduler`. Kluczowy niezmiennik: program planujący działa raz na iterację dekodowania, a nie raz na żądanie.

### Kawałki wstępnego wypełnienia chronią ogon TTFT

Wstępne wypełnienie jest powiązane z obliczeniami. Monit o wartości 32 tys. tokenów w Lamie 3.3 70B zajmuje ~800 ms czystego wstępnego wypełnienia na jednym H100. Podczas wstępnego wypełniania dekoduj tokeny dla każdej innej sekwencji w oczekiwaniu na partię. W pętli obsługującej opóźnienie pierwszego tokenu (TTFT) jednego długiego monitu staje się sygnałem opóźnienia między tokenami (ITL) dla dziesiątek innych użytkowników.

Wstępne wypełnienie fragmentaryczne dzieli wstępne wypełnienie na porcje o stałym rozmiarze (domyślnie 512 tokenów) i planuje każdą porcję jako jednostkę. Pomiędzy fragmentami program planujący może przyspieszyć sekwencje dekodowania o jeden token. Zamieniasz małe bezwzględne opóźnienie przed wypełnieniem (kilka ms na fragment) na znacznie mniejsze wahania czasu dekodowania. P99 ITL przy mieszanym obciążeniu spada z ~50 ms do ~15 ms w opublikowanych testach porównawczych.

### Trzy ustawienia domyślne wchodzą w interakcję

Wszystkie trzy cechy zakładają się wzajemnie. PagedAttention zapewnia planiście szczegółowe zasoby KV, z którymi można handlować. Ciągłe przetwarzanie wsadowe wymaga drobnoziarnistych zasobów, więc przyjęcie nowej sekwencji nie wymusza globalnego przetasowania. Wstępne wypełnienie fragmentaryczne to decyzja podejmowana przez planistę na tej samej liście `RUNNING` — jest to jeszcze jedna zasada planisty, a nie oddzielny system.

Nie musisz znać każdej flagi. Musisz wiedzieć, co optymalizuje harmonogram: dobry wynik w ramach budżetu bloku KV, z zastrzeżeniem fragmentarycznego krojenia wstępnego.

### Problem z wersją 2026 v0.18.0

W vLLM v0.18.0 nie można łączyć `--enable-chunked-prefill` z dekodowaniem spekulatywnym w modelu roboczym (`--speculative-model`). Udokumentowanym wyjątkiem jest dekodowanie spekulacyjne N-gramowego GPU w harmonogramie V1. Zespoły, które włączają każdą flagę bez przeczytania informacji o wersji, przy uruchomieniu dostają błąd wykonania, a nie miękką regresję. Jeśli Twoim spekulacyjnym zyskiem było włączenie wstępnego wypełniania fragmentarycznego, ponownie dokonaj wyboru — właściwą odpowiedzią w 2026 r. będzie często EAGLE-3 bez wstępnego wypełniania fragmentarycznego, a nie model roboczy z fragmentarycznym wstępnym wypełnieniem, który się nie kompiluje.

### Liczby, które powinieneś zapamiętać

- Lama 3.3 70B FP8, H100 SXM5, 128 jednocześnie, wszystkie trzy włączone: 2200-2400 tok/s.
- Ten sam model, domyślny vLLM (bez wstępnego wypełnienia fragmentami): ~1800 tok/s.
- Ten sam model, naiwna pętla do przodu PyTorch: ~600 tok/s.
- Odpady po fragmentacji KV w ramach PagedAttention przy obciążeniu produkcyjnym: <4%.
- P99 ITL przy mieszanym obciążeniu: ~15 ms z fragmentarycznym wypełnieniem wstępnym, ~50 ms bez.

### Jak wygląda harmonogram

```
while True:
    finished = [s for s in RUNNING if s.is_done()]
    for s in finished: release_blocks(s); RUNNING.remove(s)

    while WAITING and have_free_blocks_for(WAITING[0]):
        s = WAITING.pop(0)
        allocate_initial_blocks(s)
        RUNNING.append(s)

    # schedule prefill chunks + decode in one batch
    batch = []
    for s in RUNNING:
        if s.in_prefill:
            batch.append(next_prefill_chunk(s))   # e.g. 512 tokens
        else:
            batch.append(decode_one_token(s))     # 1 token

    run_forward(batch)                            # one fused GPU call
```

`code/main.py` to dokładnie ta pętla w stdlib Python z fałszywymi licznikami tokenów i fałszywym opóźnieniem przekazywania. Uruchomienie go pokazuje, jak fragmentaryczne wstępne wypełnienie utrzymuje sekwencje dekodowania przy życiu podczas długiego wstępnego wypełniania.

## Użyj tego

`code/main.py` symuluje harmonogram w stylu vLLM z przełączalnymi funkcjami. Uruchom, aby zobaczyć:

- Tryb `NAIVE`: jedno żądanie na raz, bez przetwarzania wsadowego.
- Tryb `STATIC`: wypełnienie i oczekiwanie, klasyczne przetwarzanie wsadowe.
- Tryb `CONTINUOUS`: przyjęcie i wydanie na poziomie iteracji.
- Tryb `CONTINUOUS + CHUNKED`: wstępne wypełnienie fragmentów przeplatanych dekodowaniem.

Dane wyjściowe pokazują całkowitą przepustowość (tokeny na wirtualną sekundę), średnią TTFT i P99 ITL. Wiersz `CONTINUOUS + CHUNKED` powinien dominować w ruchu mieszanym.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-vllm-scheduler-reader.md`. Biorąc pod uwagę konfigurację udostępniania (rozmiar wsadu, wykorzystanie pamięci KV, rozmiar wstępnego wypełnienia fragmentami, konfiguracja spekulacyjna), generuje diagnozę harmonogramu, która wskazuje, które z trzech ustawień domyślnych stanowi wąskie gardło i co należy dostroić.

## Ćwiczenia

1. Uruchom `code/main.py`. Porównaj `STATIC` z `CONTINUOUS` w przypadku obciążenia zawierającego mieszane krótkie i długie żądania. Skąd bierze się luka w przepustowości — wydajność wstępnego wypełniania, wydajność dekodowania czy opóźnienie końcowe?
2. Zmodyfikuj harmonogram zabawek, dodając `--max-num-batched-tokens`. Jaka jest właściwa wartość dla H100 z systemem Llama 3.3 70B FP8? (Wskazówka: jest to funkcja rozmiaru bloku KV i liczby wolnych bloków, a nie surowego HBM.)
3. Przeczytaj ponownie uwagi do wydania vLLM v0.18.0. Które kombinacje flag wzajemnie się wykluczają? Wymień je.
4. Oblicz straty spowodowane fragmentacją pamięci podręcznej KV dla śledzenia 1000 żądań ze średnimi 1500 tokenami wyjściowymi, standardowo 600 tokenów, w ramach (a) ciągłego przydzielania na żądanie przy maks. 8192, (b) PagedAttention z blokami 16 tokenów.
5. Wyjaśnij w jednym akapicie, dlaczego wstępne wypełnienie fragmentami pomaga w P99 ITL, ale nie zapewnia przepustowości w izolacji. Skąd w praktyce wynika korzyść w zakresie przepustowości?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| PagedUwaga | „sztuczka KV” | Alokator bloków o stałym rozmiarze dla pamięci podręcznej KV; fragmentacja <4% |
| Tabela blokowa | "tabela stron" | Mapa sekwencyjna od pozycji tokena logicznego do fizycznego bloku KV |
| Ciągłe dozowanie | „dynamiczne dozowanie, ale słuszne” | Decyzje o przyjęciu/zwolnieniu podejmowane w każdej iteracji dekodowania |
| Kawałki wstępnego wypełnienia | „podział wstępnego wypełnienia” | Podziel długie wypełnienie wstępne na kawałki o długości 512 tokenów przeplatane dekodowaniem |
| TTFT | „pierwszy raz symboliczny” | Wstępne wypełnienie + kolejka + sieć; zdominowany przez wstępne wypełnienie przy długich podpowiedziach |
| ITL | „opóźnienie między tokenami” | Czas pomiędzy kolejnymi tokenami dekodowania; zdominowany przez wielkość partii |
| Dobra wiadomość | „przepustowość spełniająca SLO” | Tokeny/s, gdzie każde żądanie nadal trafia do celów TTFT i ITL |
| Harmonogram V1 | „nowy harmonogram” | Harmonogram vLLM na rok 2026; Dekodowanie specyfikacji N-gramów to ścieżka kompatybilna z fragmentacją |
| `--gpu-memory-utilization` | „pokrętło pamięci” | Frakcja HBM zarezerwowana dla bloków KV po odważeniach i aktywacjach |

## Dalsze czytanie

- [dokumentacja vLLM — dekodowanie spekulatywne] (https://docs.vllm.ai/en/latest/features/spec_decode/) — oficjalne źródło informacji na temat zgodności chunked-prefill i spekulatywnego dekodowania.
— [Informacje o wydaniu vLLM (NVIDIA)](https://docs.nvidia.com/deeplearning/frameworks/vllm-release-notes/index.html) — Częstotliwość wydawania wydań na rok 2026 i zachowanie specyficzne dla wersji.
- [Blog vLLM — PagedAttention](https://blog.vllm.ai/2023/06/20/vllm.html) — oryginalny artykuł, który wciąż określa, jak myśleć o alokatorze.
- [Artykuł PagedAttention (arXiv:2309.06180)](https://arxiv.org/abs/2309.06180) — analiza fragmentacji i projektowanie harmonogramów.
- [Aleksa Gordic — Inside vLLM](https://www.aleksagordic.com/blog/vllm) — szczegółowy opis harmonogramu V1 z wykresami płomienia.