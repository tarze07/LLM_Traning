---

name: skill-ensemble-builder
description: Wybierz odpowiednią metodę zestawiania i skonfiguruj ją pod kątem swojego problemu
version: 1.0.0
phase: 2
lesson: 11
tags: [ensemble, bagging, boosting, random-forest, xgboost, stacking]

---

# Przewodnik wyboru metody zespołowej

Zespoły łączą wiele modeli w celu uzyskania lepszych przewidywań niż jakikolwiek pojedynczy model. Zawsze pojawia się pytanie: jaki rodzaj zespołu i kiedy?

## Lista kontrolna decyzji

1. Jaki jest główny problem Twojego obecnego modelu?
   - Wysoka wariancja (nadmierne dopasowanie): użyj workowania (Losowy las)
   - Wysokie odchylenie (niedopasowanie): użyj wzmocnienia (Gradient Boosting, XGBoost)
   - Obydwa lub chcesz maksymalnej dokładności: użyj układania

2. Ile masz danych?
   - Poniżej 1000 wierszy: Losowy las (solidny, trudny do błędnej konfiguracji)
   - 1000 do 100 000: XGBoost lub LightGBM (najlepiej ogólnie dla tabelarycznych)
   - Ponad 100 000: LightGBM (najszybsze zwiększanie gradientu, dobrze radzi sobie z dużymi danymi)

3. Ile czasu na strojenie możesz zainwestować?
   - Minimalne: Losowy Las z ustawieniami domyślnymi (prawie zawsze działa)
   - Umiarkowane: XGBoost z szybkością uczenia się = 0,1, dostrojenie n_estymatorów z wcześniejszym zatrzymaniem
   - Maksymalnie: LightGBM lub XGBoost z wyszukiwaniem hiperparametrów Bayesa

4. Czy potrzebujesz interpretowalności?
   - Tak: pojedyncze drzewo decyzyjne lub mały losowy las z ważnością funkcji
   - Częściowe: wzmocnienie gradientu wartościami SHAP
   - Nie: układanie w stosy lub głębokie zespoły

5. Czy dane są zaszumione i zawierają wiele wartości odstających?
   - Tak: Losowy Las (worki są odporne na hałas)
   - Nie: zwiększanie gradientu (może zwiększyć dokładność w przypadku czystych danych)

## Kiedy używać poszczególnych metod

**Losowy las (w workach)**: Twój bezpieczny pierwszy wybór. Uczy wiele drzew na próbkach bootstrapowych i średnich. Zmniejsza wariancję bez zwiększania odchylenia. Prawie niemożliwe jest nadmierne dopasowanie przy umiarkowanych danych. Wymagane minimalne dostrojenie: ustaw n_estimators=100-500 i pozostaw wartości domyślne.

**AdaBoost**: wzmacnianie sekwencyjne z ponownym ważeniem próbki. Działa dobrze z prostymi podstawowymi uczniami (problemy decyzyjne). Wrażliwy na wartości odstające i zaszumione etykiety, ponieważ podnosi wagę błędnie sklasyfikowanych punktów. W praktyce w dużej mierze zastąpiony przez zwiększanie gradientu.

**Wzmocnienie gradientu**: dopasowuje każde nowe drzewo do pozostałości dotychczasowego zespołu. Zmniejsza stronniczość. Najpotężniejsza metoda dla danych tabelarycznych. Wymaga dostrojenia: współczynnik uczenia się, n_estymatory, maksymalna głębokość, min_waga_dziecka, podpróbka.

**XGBoost**: wzmacnianie gradientu z regularyzacją, optymalizacją drugiego rzędu i przyspieszaniem na poziomie systemu. Natywnie obsługuje brakujące wartości. Wartość domyślna dla zawodów Kaggle i produkcyjnego ML na danych tabelarycznych.

**LightGBM**: wzmocnienie gradientowe poprzez wzrost liści (zamiast poziomego). Szybciej niż XGBoost na dużych zbiorach danych. Używa podziałów opartych na histogramie. Najlepsze dla zestawów danych zawierających ponad 50 tys. wierszy.

**CatBoost**: wzmacnianie gradientu dzięki natywnej obsłudze funkcji kategorycznych. Nie ma potrzeby kodowania na gorąco. Dobrze, gdy masz wiele cech kategorycznych.

**Stacking**: szkoli metaucznia w zakresie przewidywań wielu różnych modeli podstawowych. Używaj, gdy potrzebujesz absolutnie najlepszej dokładności i masz zapas mocy obliczeniowej. Zawsze generuj prognozy modelu podstawowego poprzez weryfikację krzyżową, aby uniknąć wycieków.

**Głosowanie**: najprostszy zespół. Głosowanie twarde (klasa większości) lub głosowanie miękkie (średnie prawdopodobieństwo). Szybki sposób na połączenie 2-3 różnorodnych modeli bez metauczenia się.

## Typowe błędy

- Używanie zwiększania gradientu bez wcześniejszego zatrzymywania (będzie przesadzone, jeśli pozwolisz mu działać zbyt wiele rund)
- Ustawienie zbyt wysokiego współczynnika uczenia się (powyżej 0,3 zwykle powoduje niestabilność)
- Nie dostrajanie max_length do zwiększania gradientu (domyślnie nieograniczone lub bardzo głębokie przekroczenie drzew)
- Układanie w stosy z modelami tego samego typu (różnorodność jest celem układania w stosy)
- Używanie AdaBoost na zaszumionych danych (wartości odstające uzyskują coraz większą wagę w każdej rundzie)
- Oczekiwanie, że Random Forest naprawi niedopasowanie (zmniejsza to wariancję, a nie stronniczość)

## Dostrajanie priorytetów według metody

**Losowy las:**
1. n_estimators: 100-500 (więcej rzadko oznacza gorzej, po prostu wolniej)
2. max_głębia: Brak (pozwól drzewom w pełni rosnąć) lub ograniczenie prędkości do 10-20
3. max_features: „sqrt” dla klasyfikacji, „log2” lub n/3 dla regresji

**XGBoost / LightGBM:**
1. learning_rate: 0,01-0,3 (im niższa, tym lepsza, jeśli masz obliczenia dla większej liczby drzew)
2. n_estymatory: zamiast zgadywać, używaj wczesnego zatrzymywania na zestawie walidacyjnym
3. max_głębia: 3-8 (zacznij od 6)
4. min_child_weight / min_data_in_leaf: 1-20 (wyższa wartość zapobiega nadmiernemu dopasowaniu)
5. podpróbka: 0,7-1,0
6. colsample_bytree: 0,7-1,0
7. reg_alpha (L1) i reg_lambda (L2): 0-10

## Szybkie odniesienie

| Metoda | Zmniejsza | Prędkość | Wysiłek dostrajający | Najlepsze dla |
|--------|---------|-------|-------------|--------------|
| Losowy las | Wariancja | Szybki | Niski | Zaszumione dane, szybka baza |
| AdaBoost | stronniczość | Szybki | Niski | Prości uczniowie, czyste dane |
| Wzmocnienie gradientu | stronniczość | Średni | Wysoki | Dane tabelaryczne, konkursy |
| XGBoost | Obydwa | Szybki | Wysoki | Tabela produkcji ML |
| LightGBM | Obydwa | Najszybszy | Wysoki | Duże zbiory danych (50 tys.+ wierszy) |
| CatBoost | Obydwa | Średni | Średni | Wiele cech kategorycznych |
| Układanie | Obydwa | Powolny | Wysoki | Maksymalna dokładność, różnorodne modele |
| Głosowanie | Wariancja | Szybki | Brak | Szybka kombinacja 2-3 modeli |