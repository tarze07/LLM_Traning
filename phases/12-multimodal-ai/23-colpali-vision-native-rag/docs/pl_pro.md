# ColPali i systemy Vision-Native RAG

> Klasyczny system RAG konwertuje pliki PDF na tekst, dzieli go na fragmenty (chunks), generuje dla nich wektory osadzeń (embeddings) i zapisuje je w bazie. Każdy z tych kroków niesie za sobą ryzyko utratę informacji: proces OCR pomija grafiki i wykresy, podział na fragmenty może rozbić wiersze tabeli, a tekstowe wektory osadzeń ignorują kontekst geometryczny i liczby. Twórcy ColPali (Faysse i in., lipiec 2024) postawili prostsze pytanie: po co w ogóle wyodrębniać tekst? Lepiej bezpośrednio wygenerować reprezentacje (embeddings) obrazu strony za pomocą PaliGemma, zastosować mechanizm późnej interakcji (Late Interaction) wzorowany na ColBERT do wyszukiwania i dzięki temu w pełni zachować układ graficzny, ilustracje, czcionki oraz formatowanie dokumentu. Wyniki benchmarków pokazują wzrost dokładności o 20–40% w porównaniu do tekstowego RAG na dokumentach bogatych wizualnie. Rozwiązania takie jak ColQwen2, ColSmol czy VisRAG rozwinęły ten schemat. W tej lekcji poznamy koncepcję Vision-Native RAG i zbudujemy uproszczony indeksator na wzór ColPali.

**Typ:** Teoria / Wdrożenie
**Języki:** Python (biblioteka standardowa, indeksator wielowektorowy + kalkulator MaxSim)
**Wymagania wstępne:** Faza 11 (Inżynieria LLM — podstawy RAG), Faza 12 · 05 (LLaVA)
**Czas:** ~180 minut

## Cele kształcenia

- Wyjaśnienie różnic między wyszukiwaniem opartym na dwukoderach (bi-encoders, jeden wektor na dokument) a wyszukiwaniem z późną interakcją (Late Interaction, wiele wektorów na dokument).
- Opisanie operacji MaxSim w ColBERT oraz sposobu, w jaki ColPali rozszerza ją z tokenów tekstowych na patche (fragmenty) obrazu.
- Implementacja uproszczonego indeksatora w stylu ColPali: strona → wektory osadzeń patchy → obliczanie MaxSim na podstawie wektorów zapytania → zwrócenie najlepiej dopasowanych stron (top-k).
- Porównanie potoku ColPali + generator Qwen2.5-VL z klasycznym tekstowym RAG + GPT-4 w analizie faktur i raportów finansowych.

## Problem

Stosowanie tekstowego RAG dla plików PDF odrzuca większość istotnych informacji pozatekstowych. Przykładowo: wzrost przychodów w raporcie finansowym jest najczęściej prezentowany na wykresie; kluczowe wyniki badań medycznych znajdują się na zdjęciach diagnostycznych z adnotacjami; a obecność podpisów na umowie prawnej wynika z układu geometrycznego dokumentu, a nie samej treści znakowej.

Typowy potok tekstowego RAG:

1. PDF → konwersja na tekst (poprzez OCR lub biblioteki pdftotext).
2. Podział tekstu na fragmenty (np. 300–500 tokenów).
3. Przetworzenie fragmentów przez dwukoder (generowanie jednego wektora na fragment).
4. Zapytanie użytkownika → generowanie wektora → podobieństwo cosinusowe → wybór top-k fragmentów.
5. Przekazanie fragmentów i zapytania do LLM.

Jest to potok o pięciu krokach niosących straty informacji. Wykresy nie są analizowane, struktura tabel ulega zniszczeniu, układ wielokolumnowy zostaje spłaszczony do jednej linii, a opisy rysunków znikają.

ColPali eliminuje te wady: pomija etap OCR i bezpośrednio indeksuje obrazy stron. Wykorzystuje wyszukiwanie oparte na późnej interakcji (Late Interaction) z ColBERT, co pozwala modelowi porównywać zapytanie tekstowe z konkretnymi, drobnymi fragmentami (patchami) obrazu strony w czasie rzeczywistym.

## Koncepcja

### Koncepcja ColBERT (2020)

Model ColBERT (Khattab i Zaharia, arXiv:2004.12832) to pionierska metoda wyszukiwania informacji w tekście. Zamiast generowania jednego wektora dla całego dokumentu, przypisuje on osobny wektor do każdego pojedynczego tokenu. W momencie zapytania:

- Tokeny zapytania są kodowane do postaci zestawu wektorów ($N_q$ wektorów).
- Tokeny dokumentu są zakodowane i zapisane w bazie ($N_d$ wektorów).
- Ostateczny wynik dopasowania obliczany jest jako suma maksymalnych podobieństw cosinusowych każdego tokenu zapytania do wszystkich tokenów dokumentu: $\sum_{i} \max_{j} \text{cos}(q_i, d_j)$.

Jest to tak zwana operacja **MaxSim**. Każdy token zapytania niejako wybiera i dopasowuje się do najbardziej powiązanego semantycznie tokenu w dokumencie.

Zalety: precyzyjne dopasowanie semantyczne na poziomie pojedynczych pojęć. Wady: przechowywanie wielu wektorów ($N_d$) dla każdego dokumentu generuje wysokie wymagania pamięciowe.

### Działanie ColPali

ColPali (Faysse i in., arXiv:2407.01449) przenosi koncepcję późnej interakcji (Late Interaction) z tekstu na obrazy dokumentów:

- Każda strona dokumentu jest przetwarzana przez enkoder wizyjny (np. PaliGemma) do postaci wektorów patchy (fragmentów obrazu): $N_p$ wektorów na stronę.
- Zapytanie tekstowe użytkownika jest kodowane do postaci zestawu wektorów tokenów: $N_q$ wektorów.
- Wynik dopasowania = $\sum_{i} \max_{j} \text{cos}(q_i, p_j)$, czyli operacja MaxSim na tokenach tekstowych zapytania i wektorach patchy obrazu strony.
- Wybierane są najlepiej pasujące strony (top-k) o najwyższej sumie podobieństw.

W fazie indeksowania system przetwarza każdą stronę dokumentu przez enkoder i zapisuje wektory jej patchy. W fazie wyszukiwania system koduje zapytanie tekstowe użytkownika, szybko oblicza MaxSim względem wszystkich zapisanych stron i zwraca te o najwyższym wyniku.

Zalety: kompletne pominięcie etapu OCR, co podnosi dokładność o 20–40% w przypadku dokumentów o złożonej strukturze graficznej. Wektory patchy bez problemu reprezentują układ przestrzenny oraz elementy graficzne.

Wady: duży narzut pamięciowy ($N_p$ wektorów o wymiarze D na stronę). Wymagania te można jednak skutecznie zredukować, stosując kwantyzację produktową (Product Quantization – PQ lub OPQ).

### ColQwen2 i ColSmol

- **ColQwen2** (Illuin Technology, 2024–2025): Zastępuje model PaliGemma nowocześniejszym koderem Qwen2-VL, co przynosi wyższą precyzję wyszukiwania i lepszą obsługę tekstów wielojęzycznych.
- **ColSmol:** Lekka odmiana modelu (skala ~1B parametrów) zoptymalizowana pod kątem wdrażania na urządzeniach lokalnych i słabszych kartach GPU.

### VisRAG

VisRAG (Yu i in., arXiv:2410.10594) reprezentuje inne podejście: zamiast operacji MaxSim na wielu patchach, koder VLM agreguje całą stronę dokumentu do pojedynczego wektora osadzenia (podejście dwukoderowe).
- Zalety: szybsze indeksowanie, znacznie niższe zużycie pamięci bazy wektorowej.
- Wady: słabsza skuteczność wyszukiwania drobnych detali w porównaniu do ColPali.

Wybór zależy od skali systemu: ColPali oferuje najwyższą precyzję, a VisRAG pozwala na łatwiejsze skalowanie.

### M3DocRAG

M3DocRAG (Cho i in., arXiv:2411.04952) rozszerza wyszukiwanie wielomodalne o zadania wnioskowania na wielu stronach i wielu dokumentach jednocześnie. Odnajduje kluczowe strony w różnych dokumentach i buduje z nich dynamiczny, wielostronicowy kontekst dla właściwego modelu VLM.

### Benchmark ViDoRe (Visual Document Retrieval Benchmark)

ViDoRe to standardowy benchmark oceny systemów wyszukiwania dokumentów na podstawie obrazów. Obejmuje analizę raportów finansowych, publikacji naukowych, rejestrów administracyjnych, dokumentacji medycznej oraz instrukcji technicznych. Kluczowym miernikiem jest nDCG@5.

ColPali-v1 osiąga w nim wynik ~80% nDCG@5, podczas gdy klasyczny tekstowy RAG na tych samych dokumentach plasuje się w granicach ~50-60%.

### Pełny potok Vision-Native RAG

1. **Indeksowanie:** PDF → renderowanie obrazów stron → kodowanie przez PaliGemma → zapisanie wektorów patchy w bazie.
2. **Wyszukiwanie:** Zapytanie tekstowe → kodowanie do wektorów tokenów → obliczenie MaxSim względem bazy stron → wybór najlepiej pasujących stron (top-k).
3. **Generowanie:** Obrazy wybranych stron + zapytanie użytkownika → model VLM (np. Qwen2.5-VL lub Claude) → ostateczna odpowiedź tekstowa.

Potok ten całkowicie eliminuje etap OCR, tabele, rysunki, wykresy i układ graficzny są analizowane bezpośrednio z pikseli.

### Analiza zapotrzebowania na pamięć (Storage Math)

Rozważmy 50-stronicowy raport roczny przy 729 wektorach patchy na stronę i wymiarze osadzenia równym 128:
- **ColPali:** $50 \times 729 \times 128 \times 4 \text{ bajty} = \sim 18 \text{ MB}$ surowych danych ($\sim 4 \text{ MB}$ po kompresji PQ).
- **Tekstowy RAG:** 50 fragmentów $\times 768 \text{ wymiarów} \times 4 \text{ bajty} = \sim 150 \text{ KB}$.

ColPali wymaga ok. 30-krotnie więcej przestrzeni dyskowej. Zastosowanie kompresji PQ/OPQ pozwala zredukować tę różnicę do akceptowalnego poziomu 5–10x.

### Kiedy tekstowy RAG zachowuje przewagę

- Dokumenty zawierające wyłącznie czysty tekst bez żadnych tabel czy schematów (np. artykuły z Wikipedii). Tekstowy RAG jest w tym przypadku prostszy i tańszy we wdrożeniu.
- Systemy przechowujące miliony dokumentów, w których koszty bazy wektorowej są głównym ograniczeniem budżetowym.
- Restrykcyjne wymogi prawne nakazujące przechowywanie i przeszukiwanie dokładnych, znakowych transkrypcji OCR.

W pozostałych obszarach – raporty finansowe, dokumenty prawne, schematy techniczne – Vision-Native RAG staje się standardem.

## Zastosowanie w kodzie

Plik `code/main.py` realizuje następujące zadania:
- Zawiera makiety enkodera patchy: mapuje obraz strony na tablicę reprezentacji wektorowych.
- Implementuje obliczanie wskaźnika MaxSim (w stylu ColBERT) na podstawie wektorów zapytania oraz patchy strony.
- Indeksuje 5 przykładowych stron, przetwarza 3 zapytania testowe i zwraca najlepiej dopasowane strony wraz z punktacją.

## Rezultat

Do tej lekcji dołączono dokument `outputs/skill-vision-rag-designer.md`. Ułatwia on dobór architektury (ColPali, ColQwen2, VisRAG czy tradycyjny tekstowy RAG) oraz szacuje zapotrzebowanie na przestrzeń dyskową w zależności od specyfiki bazy dokumentów.

## Ćwiczenia

1. Oblicz zapotrzebowanie na pamięć (dla danych surowych oraz po kompresji PQ z parametrem 8x) dla 200-stronicowego dokumentu przy 729 wektorach patchy na stronę i wymiarze osadzenia 128.
2. Wyjaśnij, czym różni się operacja MaxSim $\sum_{i} \max_{j} \text{cos}(q_i, p_j)$ od prostego wyznaczenia średniej podobieństwa cosinusowego między wszystkimi wektorami. Jakie korzyści to przynosi?
3. ColPali indeksuje strony na poziomie patchy (fragmentów obrazu). Co uległoby zmianie (i z jakimi kompromisami), gdybyśmy zamiast tego indeksowali stronę na poziomie pojedynczych słów (jak w ColBERT)?
4. Zaprojektuj architekturę systemu RAG dla bazy 1 miliona stron dokumentów z limitem opóźnienia wyszukiwania wynoszącym 500 ms na zapytanie. Wybierz między ColQwen2 a VisRAG i uzasadnij swoją decyzję.
5. Przeczytaj publikację o modelu M3DocRAG (arXiv:2411.04952). Opisz mechanizm wielostronicowej atencji i wskaż, czym różni się on od wyszukiwania pojedynczych stron w ColPali.

## Kluczowe pojęcia

| Termin | Potoczne określenie | Co to dokładnie oznacza |
| :--- | :--- | :--- |
| **Późna interakcja (Late Interaction)** | „Wyszukiwanie ColBERT” | Metoda wyszukiwania porównująca wektory poszczególnych tokenów/patchy na etapie zapytania (MaxSim), zamiast agregacji dokumentu do jednego wektora. |
| **MaxSim** | „Maksymalne podobieństwo” | Operacja przypisująca każdemu tokenowi zapytania najbardziej do niego zbliżony patch dokumentu i sumująca te najwyższe podobieństwa. |
| **Dwukoder (Bi-encoder)** | „Model jednowektorowy” | Architektura kodująca całą stronę lub dokument do postaci pojedynczego wektora; szybka, ale gubi drobne szczegóły. |
| **Wielowektorowy (Multi-vector)** | „Wiele wektorów na stronę” | Podejście przechowujące zestaw wektorów ($N_p$) dla każdego dokumentu, co zwiększa skuteczność wyszukiwania kosztem pamięci bazy. |
| **Osadzanie patchy (Patch embedding)** | „Cechy obrazu strony” | Reprezentacja wektorowa małego fragmentu obrazu strony wygenerowana przez enkoder wizyjny. |
| **ViDoRe** | „Benchmark Vision RAG” | Zestaw testów porównawczych dedykowany do oceny systemów wyszukiwania informacji na dokumentach graficznych. |
| **Kwantyzacja PQ (Product Quantization)** | „Kompresja wektorów” | Algorytm kompresji wektorów bazy, redukujący zużycie pamięci (ok. 8-krotnie) przy minimalnym spadku precyzji wyszukiwania. |

## Literatura uzupełniająca

- [Faysse i in. — ColPali (arXiv:2407.01449)](https://arxiv.org/abs/2407.01449)
- [Khattab i Zaharia — ColBERT (arXiv:2004.12832)](https://arxiv.org/abs/2004.12832)
- [Yu i in. — VisRAG (arXiv:2410.10594)](https://arxiv.org/abs/2410.10594)
- [Cho i in. — M3DocRAG (arXiv:2411.04952)](https://arxiv.org/abs/2411.04952)
- [Strona projektu illuin-tech/colpali na GitHubie](https://github.com/illuin-tech/colpali)
