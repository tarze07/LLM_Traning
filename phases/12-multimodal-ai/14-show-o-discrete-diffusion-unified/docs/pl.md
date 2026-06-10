# Zunifikowane modele Show-o i Discrete-Diffusion

> Transfuzja łączy w sobie reprezentacje ciągłe i dyskretne. Show-o (Xie i in., sierpień 2024) idzie w drugą stronę: tokeny tekstowe wykorzystują przyczynowe przewidywanie następnego tokenu, tokeny obrazowe wykorzystują zamaskowane dyskretne dyfuzję w duchu MaskGIT. Obydwa znajdują się w jednym transformatorze z hybrydową maską uwagi. Wynik ujednolica VQA, zamianę tekstu na obraz, malowanie i generowanie mieszanej modalności w jednym szkielecie, jeden tokenizator na modalność, jedno formułowanie strat (następny token rozszerzony o maskowane przewidywanie). Ta lekcja dotyczy projektu Show-o — dlaczego zamaskowana dyskretna dyfuzja jest równoległym, kilkuetapowym generatorem obrazu — i kontrastuje z Transfusion i Emu3.

**Typ:** Ucz się
**Języki:** Python (stdlib, próbnik z maskowaną dyskretną dyfuzją)
**Wymagania:** Faza 12 · 13 (Transfuzja)
**Czas:** ~120 minut

## Cele nauczania

- Wyjaśnij zamaskowane dyskretne rozproszenie: harmonogram, który maskuje tokeny w jednolity sposób, a następnie prosi transformator o ich odzyskanie.
- Porównaj równoległe dekodowanie obrazu (Show-o, MaskGIT) z autoregresyjnym dekodowaniem obrazu (Chameleon, Emu3) pod względem szybkości i jakości.
- Nazwij trzy zadania Pokaż uchwyty w jednym punkcie kontrolnym: T2I, VQA, malowanie obrazu.
- Wybierz harmonogram maskowania (cosinus, liniowy, obcięty) i uzasadnij jego wpływ na jakość próbki.

## Problem

Trening dwóch strat w Transfusion działa, ale ma trudniejszą dynamikę – ciągła strata dyfuzyjna występuje w innej skali numerycznej niż dyskretna strata NTP. Równoważenie wag strat to wyszukiwanie hiperparametrów. Architektura jest efektywna, ale złożona.

Odpowiedź Show-o: zachowaj dyskretność obu modalności (jak Chameleon), ale generuj obrazy równolegle poprzez zamaskowane dyskretne rozproszenie, a nie sekwencyjnie. Celem szkolenia staje się pojedyncza prognoza zamaskowanego tokenu, która w naturalny sposób uogólnia przewidywanie następnego tokenu.

## Koncepcja

### Zamaskowana dyskretna dyfuzja (MaskGIT)

Oryginalny Chang i in. (2022) Sztuczka MaskGIT jest elegancka. Zacznij od całkowicie zamaskowanego obrazu (każdy token ma specjalny identyfikator `<MASK>`). Na każdym etapie przewiduj równolegle wszystkie zamaskowane tokeny, następnie zachowaj najbardziej pewne przewidywania z góry K i ponownie zamaskuj resztę. Po ~8-16 iteracjach wszystkie tokeny są wypełniane. Harmonogram określający liczbę tokenów do zdemaskowania w każdym kroku — harmonogramy cosinusów działają dobrze.

Trening jest prosty: próbkuj współczynnik maskowania równomiernie z [0, 1], zastosuj go do tokenów VQ obrazu, wytrenuj transformator, aby odzyskał zamaskowane. Dokładnie to, co BERT zrobił dla tekstu, przeskalowanego do generowania obrazu.

### Show-o: jeden transformator, maska hybrydowa

Show-o umieszcza MaskGIT w transformatorze modelu języka przyczynowego. Maska uwagi to:

- Tokeny tekstowe: przyczynowe (standardowe LLM).
- Tokeny obrazu: w pełni dwukierunkowe w obrębie bloku obrazu (dzięki czemu zamaskowane tokeny mogą widzieć każdy inny token obrazu podczas przewidywania).
- Tekst na obraz: tekst odpowiada wcześniejszym obrazom, obraz odpowiada wcześniejszemu tekstowi.

Trening na zmianę:
1. Standardowy NTP w sekwencjach tekstowych.
2. Próbki T2I: tekst → obraz z tokenami zamaskowanego obrazu, utrata przewidywania tokena zamaskowanego.
3. Próbki VQA: obraz → tekst z tokenami zamaskowanego tekstu (tak naprawdę to po prostu NTP).

Ujednolicona strata to entropia krzyżowa na tokenach `<MASK>`, która obejmuje zarówno tekst NTP (tylko ostatni token jest „maskowany”), jak i dyfuzję zamaskowanego obrazu (losowy podzbiór jest maskowany).

### Próbkowanie równoległe

Show-o generuje obraz w ~16 krokach zamiast ~1000 (autoregresja na token) lub ~20 (dyfuzja). Na każdym etapie przewidywaj równolegle wszystkie zamaskowane tokeny; popełnij najwyższego K, pewny siebie; powtarzać.

Porównaj:
- Chameleon / Emu3 (autoregresja na tokenach): N_tokens przechodzi do przodu, zazwyczaj 1024-4096 na obraz.
- Transfuzja (ciągła dyfuzja): ~20 kroków, każdy z pełnym przejściem transformatora.
- Show-o (zamaskowana dyskretna dyfuzja): ~16 kroków, każdy z pełnym przejściem transformatora.

Show-o jest szybszy niż Chameleon w modelach o podobnej skali, mniej więcej odpowiada liczbie kroków transfuzji przy niższym koszcie na krok (dyskretne logity słownictwa vs ciągła utrata MSE).

### Zadania w jednym punkcie kontrolnym

Show-o obsługuje cztery zadania przy wnioskowaniu, wybrane w formacie podpowiedzi:

- Generowanie tekstu: standardowe wyjście tekstowe autoregresyjne.
- VQA: wejście obrazu, wyjście tekstu.
- T2I: tekst wprowadzany, obraz wysyłany poprzez maskowaną dyskretną dyfuzję.
- Inmalowanie: obraz z zamaskowanymi żetonami, uzupełnij.

Możliwość malowania jest dostępna bezpłatnie po szkoleniu w zakresie przewidywania maskowanego. Zamaskuj obszar siatki tokenów VQ, podaj resztę i podpowiedź tekstową, przewiduj zamaskowane tokeny.

### Harmonogram maskowania

Harmonogram liczby tokenów do zdemaskowania w każdym kroku kształtuje jakość. Show-o zaleca cosinus:

```
mask_ratio(t) = cos(pi * t / (2 * T))   # t = 0..T
```

W kroku 0 wszystkie tokeny są maskowane (stosunek 1,0). W etapie T nikt nie był zamaskowany. Cosinus koncentruje masę na stosunkach średniego zakresu, gdzie przewidywanie dostarcza najwięcej informacji. Harmonogramy liniowe również działają, ale szybciej się stabilizują.

### Pokaż-o2

Show-o2 (kontynuacja 2025, arXiv 2506.15564) skaluje Show-o: większa baza LLM, lepszy tokenizer, ulepszony harmonogram masek. Ten sam schemat architektoniczny.

### Gdzie siedzi Show-o

W taksonomii 2026:

- Tokeny dyskretne + NTP: Chameleon, Emu3. Proste, ale powolne wnioskowanie.
- Dyskretne tokeny + maskowana dyfuzja: Show-o, MaskGIT, LlamaGen, Muse. Próbkowanie równoległe, nadal stratne przez tokenizer.
- Ciągłe + dyfuzyjne: Transfuzja, MMDiT, DiT. Najwyższa jakość, bardziej kompleksowe szkolenie.
- Ciągłe + dopasowanie przepływu w VLM: JanusFlow, InternVL-U. Najnowszy.

Wybierz według zadania: Pokaż, kiedy chcesz T2I + malowanie + VQA w jednym otwartym modelu z rozsądną szybkością; Transfuzja, gdy jakość jest najważniejsza i możesz sobie pozwolić na instalację hydrauliczną z dwiema stratami.

## Użyj tego

`code/main.py` symuluje próbkowanie Show-o:

- Siatka zabawek złożona z 16 żetonów VQ.
- Próbny „transformator”, który przewiduje logity na podstawie podpowiedzi i aktualnie zdemaskowanych tokenów.
- Równoległe maskowane próbkowanie w 8 krokach z harmonogramem cosinus.
- Drukuje stany pośrednie (ewolucja wzoru maski) i tokeny końcowe.

Uruchom go i obserwuj, jak maska ​​stopniowo się rozpuszcza.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-unified-gen-model-picker.md`. Biorąc pod uwagę produkt, który wymaga zarówno zrozumienia (VQA, napisy), jak i generowania (T2I, malowanie) z ograniczeniem otwartych wag, wybiera pomiędzy rodziną Show-o, rodziną Transfusion/MMDiT i rodziną Emu3 / Chameleon z konkretnymi kompromisami.

## Ćwiczenia

1. Zamaskowane dyskretne próbki dyfuzyjne w ~16 krokach. Dlaczego nie 1? Co się zepsuje, jeśli zdemaskujesz wszystko w kroku 0?

2. Malowanie jest bezpłatne i ma maskowane rozproszenie. Zaproponuj przypadek użycia produktu (rzeczywisty lub hipotetyczny), w którym obraz Show-o pokonuje specjalistyczny model.

3. Harmonogram cosinusowy a harmonogram liniowy: prześledź liczbę niezamaskowanych tokenów na krok dla T=8. Co jest bardziej zrównoważone?

4. Obraz Show-o o wymiarach 512x512 to 1024 tokeny. Przy vocab K=16384 model emituje 1024 * log2(16384) = 14336 bitów (~1,75 KiB) danych. Wyniki stabilnej dyfuzji 512*512*24 bity = 6 291 456 bitów (~768 KiB) surowych pikseli. Jaki jest stopień kompresji i jaką jakość kupuje?

5. Przeczytaj LamaGen (arXiv:2406.06525). Czym różni się warunkowy klasowo model obrazu autoregresyjnego LlamaGen od zamaskowanego podejścia Show-o?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|--------------------------------------|
| Zamaskowana dyskretna dyfuzja | „W stylu MaskGIT” | Szkolenie w zakresie przewidywania tokenów maskowanych; podczas wnioskowania iteracyjnie demaskuj najbardziej pewne przewidywania |
| Cosinus harmonogram | „Zdemaskuj harmonogram” | Zanik współczynnika maski w krokach wnioskowania; koncentruje wzrost pewności w średnim zakresie |
| Dekodowanie równoległe | „Wszystkie tokeny na raz” | Każdy krok przewiduje pełną sekwencję zamaskowanych tokenów w jednym przebiegu do przodu, a następnie zatwierdza górne K |
| Uwaga hybrydowa | „Przyczynowy + dwukierunkowy” | Maska, która jest przyczynowa na tokenach tekstowych i dwukierunkowa w blokach obrazu |
| Malarstwo | „Generowanie uzupełnień” | Warunek na obrazie z zamaskowanymi żetonami, przewiduj brakujące; wolne od celu szkolenia |
| Wskaźnik zaangażowania | „Top-K na krok” | Ile tokenów zostało uznanych za „ukończone” na iterację; kontroluje wnioskowanie a kompromis w zakresie jakości |

## Dalsze czytanie

- [Xie i in. — Show-o (arXiv:2408.12528)](https://arxiv.org/abs/2408.12528)
- [Show-o2 (arXiv:2506.15564)](https://arxiv.org/abs/2506.15564)
- [Chang i in. — MaskGIT (arXiv:2202.04200)](https://arxiv.org/abs/2202.04200)
- [Sun i in. — LamaGen (arXiv:2406.06525)](https://arxiv.org/abs/2406.06525)
- [Chang i in. — Muse (arXiv:2301.00704)](https://arxiv.org/abs/2301.00704)