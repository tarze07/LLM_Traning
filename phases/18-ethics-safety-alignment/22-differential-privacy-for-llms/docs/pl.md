# Różnicowa prywatność dla LLM

> DP-SGD pozostaje standardem — aktualizacje gradientu wprowadzane przez szum zapewniają formalne gwarancje (epsilon, delta). Narzut związany z mocą obliczeniową, pamięcią i użytecznością jest znaczny; wydajne parametrycznie dostrajanie DP (LoRA + DP-SGD) to powszechna konfiguracja 2025 (ACM 2025). Dwa zbiory dowodów będących przedmiotem napięcia: wnioskowanie o członkostwie na podstawie kanarków (Duan i in., 2024) donosi o ograniczonym sukcesie w porównaniu z modelami językowymi; ekstrakcja danych szkoleniowych (Carlini i in., 2021; Nasr i in., 2025) umożliwia odzyskanie znacznej części zapamiętywania dosłownie. Rozdzielczość (arXiv:2503.06808, marzec 2025): różnica dotyczy tego, co jest mierzone – wstawione kanarki a dane „najbardziej możliwe do wyodrębnienia”. Nowe projekty kanarkowe umożliwiają MIA opartą na stratach bez modeli cieni i dają pierwszy nietrywialny audyt DP LLM przeszkolony na rzeczywistych danych z realistycznymi gwarancjami DP. Alternatywy: PMixED (arXiv:2403.15638) — prywatna predykcja w czasie wnioskowania za pośrednictwem mieszanki ekspertów w zakresie dystrybucji następnego tokenu; Generowanie danych syntetycznych DP (Google Research 2024). Pojawiający się atak: różnicowe odwrócenie prywatności poprzez informację zwrotną LLM – wyciek wyniku zaufania.

**Typ:** Kompilacja
**Języki:** Python (stdlib, wstrzykiwanie szumu DP-SGD i demonstracja księgowego ε-δ)
**Wymagania wstępne:** Faza 01 · 09 (teoria informacji), Faza 10 · 01 (szkolenie na dużym modelu)
**Czas:** ~60 minut

## Cele nauczania

- Zdefiniuj prywatność różnicową (epsilon, delta) i podaj przepis DP-SGD.
- Wyjaśnij napięcie w latach 2024–2025: kanarkowa MIA vs ekstrakcja danych szkoleniowych dają różne obrazy.
- Opisz PMixED i dlaczego prywatne przewidywanie w czasie wnioskowania jest alternatywą dla szkolenia DP.
- Opisz różnicowe odwrócenie prywatności poprzez atak LLM Feedback.

## Problem

LLM zapamiętują. Carlini i in. W roku 2021 modele języka produkcyjnego odtwarzają na żądanie dosłowny tekst szkoleniowy. DP to formalna obrona: trenuj tak, aby wyniki były niewrażliwe na jakikolwiek pojedynczy przykład szkolenia. Dane dotyczące lat 2024–2025 pokazują, że DP-SGD jest konieczny, ale zastosowane wartości ε mogą nie odpowiadać modelowi zagrożenia.

## Koncepcja

### (ε, δ) – prywatność różnicowa

Randomizowany algorytm M to (ε, δ)-DP, jeśli dla dowolnych dwóch zbiorów danych różniących się jednym przykładem i dowolnym zdarzeniem S:
P(M(D) w S) <= e^ε * P(M(D') w S) + δ.

Interpretacja: rozkład wyniku jest na tyle bliski (sparametryzowany przez ε), że nie można wiarygodnie wywnioskować wkładu jakiejkolwiek pojedynczej osoby, chyba że z prawdopodobieństwem δ.

### DP-SGD

Abadi i in. 2016. Standardowy przepis:
1. Wypróbuj mini-partię.
2. Obliczanie gradientów dla poszczególnych przykładów.
3. Przytnij każdy gradient na przykład do progu C.
4. Zsumuj obcięte gradienty i dodaj szum Gaussa przy std σ * C.
5. Użyj zaszumionej sumy, aby zaktualizować parametry.

Koszty prywatności są śledzone przez księgowego (księgowego Moments, księgowego Rényi DP). Podane wartości ε w literaturze LLM różnią się znacznie w zależności od modelu zagrożenia, wrażliwości danych i celu użyteczności; nie ma powszechnie „bezpiecznego” domyślnego ε. Opublikowane przykłady obejmują w przybliżeniu ε ≈ 1–10 w niektórych ustawieniach treningu LLM, ale mają one charakter ilustracyjny — nie są zalecanymi wartościami domyślnymi. Niższe ε generalnie wymaga większego hałasu i może zwiększyć straty w użyteczności publicznej.

### LoRA + DP-SGD

Pełny DP-SGD modelu granicznego jest zaporowy. LoRA (Hu et al. 2022) ogranicza aktualizacje gradientów do małego adaptera, redukując przechowywanie gradientów na przykład. LoRA + DP-SGD to powszechna konfiguracja na rok 2025. Gwarancje DP dotyczą adaptera; model podstawowy jest nieruchomy.

### Napięcie w latach 2024–2025

Dwie linie dowodów:

- **Canary MIA (Duan et al. 2024).** Wstaw unikalne kanarki do danych szkoleniowych i zmierz, czy osoba atakująca na podstawie wnioskowania o członkostwie może je zidentyfikować. Zgłasza ograniczony sukces w modelach językowych. Sugeruje, że MIA jest trudna.
- **Ekstrakcja danych szkoleniowych (Carlini 2021, Nasr et al. 2025).** Podpowiedz modelowi za pomocą prefiksu; zmierzyć, czy odzyskuje dosłowny tekst ze szkolenia. Zgłasza znaczne zapamiętywanie. Sugeruje, że MIA jest łatwa w odpowiednim sensie.

Rezolucja z marca 2025 r. (arXiv:2503.06808): te dwie rzeczy mierzą różne rzeczy. MIA pyta „czy przykład e jest w D?” na wprowadzonych kanarkach. Ekstrakcja pyta: „Co mogę odzyskać z D?” „Najłatwiejszy do wydobycia” przykład ma znaczenie dla prywatności; kanarki zaniżają tę informację, ponieważ nie są zoptymalizowane pod kątem ekstrakcji.

Nowe wzory kanarek. MIA oparta na stratach bez modeli cieni. Pierwszy nietrywialny audyt DP LLM na rzeczywistych danych z realistycznymi gwarancjami DP.

### Alternatywy dla szkoleń DP

- **PMixED (arXiv:2403.15638).** Prywatna prognoza w momencie wnioskowania. Mieszanka ekspertów w zakresie dystrybucji następnego tokena; każdy ekspert widzi fragment danych szkoleniowych; agregacja dodaje szum dla DP. Całkowicie unika szkoleń DP.
- **Generowanie danych syntetycznych DP (Google Research 2024).** Dostosuj LoRA za pomocą DP-SGD, próbuj dane syntetyczne, trenuj klasyfikator niższego szczebla na danych syntetycznych.

Obydwa omijają koszty użytkowe pełnego szkolenia w zakresie DP kosztem innego modelu zagrożenia.

### Różnicowe odwrócenie prywatności poprzez informację zwrotną LLM

Pojawiający się atak w 2025 r. Użyj wyników zaufania modelu wyszkolonego przez DP jako wyroczni do ponownej identyfikacji osób. Nawet jeśli wyniki nie wyciekają, rozkłady ufności mogą to spowodować.

Obrona: nie ujawniaj tajemnic ani nie skracaj ich/kwantyzuj przed ujawnieniem. Jest to dodatkowy wymóg wykraczający poza szkolenie (ε, δ)-DP.

### Gdzie to pasuje do fazy 18

Lekcje 20-21 dotyczą stronniczości/uczciwości. Lekcja 22 to prywatność. Lekcja 23: pochodzenie poprzez znak wodny. Lekcja 27 omawia warstwę pochodzenia danych regulacyjnych.

## Użyj tego

`code/main.py` symuluje DP-SGD na zbiorze danych zabawkowej klasyfikacji binarnej. Możesz przesunąć mnożnik szumu σ i normę obcinania C oraz śledzić budżet (ε, δ) i koszt dokładności. „Atak kanarkowy” wstawia unikalny przykład szkoleniowy i mierzy, czy test utraty dziennika może go wykryć przed i po DP.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-dp-audit.md`. Biorąc pod uwagę wniosek DP dotyczący wdrożenia modelu językowego, przeprowadza audyt: wartości (ε, δ), zastosowanego księgowego, protokołu oceny MIA oraz tego, czy oszacowano wektory ekspozycji na pewność.

## Ćwiczenia

1. Uruchom `code/main.py`. Zamień σ w {0,5, 1,0, 2,0} i zgłoś kompromis w zakresie (ε, δ) dokładności. Zidentyfikuj punkt, w którym następuje załamanie użyteczności.

2. Zaimplementuj test wstawiania kanarków i utratę kłód. Zmierz współczynnik wykrywalności przed i po DP-SGD przy σ = 1,0.

3. Przeczytaj Nasra i in. 2025 r. w sprawie ekstrakcji danych szkoleniowych. Dlaczego sukces ekstrakcji nie załamuje się przy umiarkowanym ε? Co to oznacza w odniesieniu do oceny MIA?

4. Zaprojektuj wdrożenie przy użyciu PMixED (arXiv:2403.15638), które działa całkowicie w czasie wnioskowania. Jaki jest model zagrożeń, który rozwiązuje PMixED, a którego nie ma DP-SGD?

5. Naszkicuj odwrócenie DP poprzez atak ze sprzężeniem zwrotnym LLM. Zaprojektuj środek zaradczy, który ograniczy wyciek wyniku zaufania i oszacuj koszt jego wdrożenia.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|--------------------------------------|
| DP | „(ε, δ)-prywatność różnicowa” | Formalna prywatność: rozkład wyników zamknięty w wyniku zmiany sąsiedniego zbioru danych |
| DP-SGD | „SGD z wtryskiem hałasu” | Obcinanie gradientu + dodatek szumu Gaussa; standardowe szkolenie DP |
| LoRA + DP-SGD | „efektywne prywatne dostrojenie” | DP-SGD na adapterach niskiej rangi; standardowa konfiguracja 2025 |
| MIA | „wnioskowanie o członkostwie” | Atak określający, czy przykład znajdował się w danych treningowych |
| Kanarek | „przykład wstawionego znaku wodnego” | Unikalny przykład szkoleniowy używany do pomiaru wycieku DP |
| PMixED | „prywatna mieszanina wnioskowań” | DP w czasie wnioskowania poprzez mieszankę ekspertów w sprawie rozkładów następnego tokenu |
| Odwrócenie DP | „atak polegający na wycieku zaufania” | Atak wykorzystujący pewność modelu jako wyrocznię do ponownej identyfikacji |

## Dalsze czytanie

- [Abadi i in. — DP-SGD (arXiv:1607.00133)](https://arxiv.org/abs/1607.00133) — standardowy algorytm uczący DP
- [Carlini i in. — Wyodrębnianie danych szkoleniowych (arXiv:2012.07805)](https://arxiv.org/abs/2012.07805) — dokument dotyczący ekstrakcji kanonicznej
- [Duan i in. — Kanaryjska MIA w LLM (arXiv:2402.07841, 2024)](https://arxiv.org/abs/2402.07841) — MIA o ograniczonym sukcesie
- [Kowalczyk i in. — Audyt DP dla LLM (arXiv:2503.06808, marzec 2025)](https://arxiv.org/abs/2503.06808) — rozwiązanie napięcia
- [PMixED (arXiv:2403.15638)](https://arxiv.org/abs/2403.15638) — prywatne przewidywanie w czasie wnioskowania