---

name: prompt-data-quality-checker
description: Sprawdź i debuguj jakość danych w potokach przedszkoleniowych LLM
version: 1.0.0
phase: 10
lesson: 3
tags: [data-pipeline, deduplication, quality-filter, pre-training, llm, data-cleaning]

---

# Kontroler jakości danych dla szkolenia wstępnego LLM

Podczas tworzenia lub audytowania potoku danych na potrzeby wstępnego szkolenia LLM użyj tej platformy, aby wychwycić problemy, zanim dotrą one do modelu.

## Czerwone flagi na wyjściu rurociągu

**Dzięki deduplikacji usunięto mniej niż 20% danych internetowych.** Wspólne indeksowanie zawiera zazwyczaj 30–40% duplikatów. Jeśli Twój krok deduplikacji usuwa mniej niż 20%, Twoje parametry MinHash są zbyt konserwatywne lub Twój próg jest zbyt wysoki. Sprawdź: rozmiar gontu k, liczbę funkcji skrótu, liczbę pasm LSH, próg Jaccarda.

**Współczynnik kompresji poniżej 2,0 znaków/token.** Oznacza to, że Twój tokenizer dzieli się zbyt agresywnie. Albo przeszkol się, używając większej liczby połączeń, zwiększ rozmiar słownictwa, albo sprawdź, czy wstępna tokenizacja nie powoduje niepotrzebnej fragmentacji tekstu.

**Współczynnik kompresji powyżej 6,0 znaków/token.** Twój tokenizator nauczył się połączeń bardzo specyficznych dla domeny, które nie mogą być uogólniane. Jest to w porządku w przypadku modelu specyficznego dla domeny, ale stanowi znak ostrzegawczy w przypadku modeli ogólnego przeznaczenia.

**Wykorzystanie sekwencji poniżej 90%.** Zbyt dużo dopełnienia. Albo Twoje dokumenty są bardzo krótkie (przefiltruj je lub zwiększ minimalną długość dokumentu), albo pakowanie sekwencyjne jest nieefektywne (przejdź z naiwnego dopełniania na pakowanie wielu dokumentów).

**Wykorzystanie słownictwa poniżej 50%.** Ponad połowa Twojego słownictwa nie jest używana w tym korpusie. Albo słownictwo jest za duże dla Twojej domeny, albo tokenizator został przeszkolony na bardzo różnych danych.

## Kalibracja filtra jakości

Przeprowadź poniższe kontrole na losowej próbie 1000 dokumentów na każdym etapie rurociągu:

1. **Po czyszczeniu przeczytaj 20 losowych dokumentów.** Czy zawierają pozostałości kodu HTML, JavaScript, tekstu nawigacyjnego lub szablonu? Jeśli tak, usuwanie kodu HTML jest niekompletne.

2. **Przeczytaj 20 losowych dokumentów, które PRZESZŁY filtr jakości.** Czy któreś z nich to spam, listy słów kluczowych lub wygenerowane maszynowo? Jeśli tak, dokręć progi filtra.

3. **Przeczytaj 20 losowych dokumentów, które NIE przeszły filtru jakości.** Czy któryś z nich jest naprawdę dobry? Jeśli tak, Twój filtr jest zbyt agresywny. Zrelaksuj progi lub dodaj wyjątki dla określonych wzorców.

4. **Przeczytaj 20 losowych, prawie zduplikowanych par z dedupu.** Czy rzeczywiście są one podobne? Jeśli nie, obniż próg Jaccarda lub zwiększ liczbę funkcji skrótu.

## Współczynniki mieszania danych

Nie ma uniwersalnej formuły. Zacznij od tych wartości bazowych i dostosuj na podstawie oceny:

| Kategoria | Lama 3 Stosunek | Punkt początkowy |
|---------|-------------|----------------|
| Tekst internetowy | 50% | 50% |
| Kod | 25% | 15-25% |
| Książki/akademickie | 13% | 10-15% |
| Matematyka | 8% | 5-10% |
| Sieć wielojęzyczna | 4% | 5-10% |

Zwiększ współczynnik kodu, jeśli model powinien dobrze programować. Zwiększ współczynnik matematyczny, jeśli rozumowanie ma znaczenie. Zmniejsz współczynnik sieci, jeśli potrzebujesz mniej hałasu. Zawsze oceniaj na benchmarkach po zmianie wskaźników.

## Skalowanie szacunków

Dla danej liczby żetonów docelowych:

- 1T tokenów z sieci: spodziewaj się ~3-5TB surowego tekstu, ~1,5-2TB po oczyszczeniu i deduplikacji
- Szybkość tokenizacji (rdza): ~100 mln tokenów/sekundę na rdzeń
- Szybkość tokenizacji (Python): ~1-10 mln tokenów/sekundę na rdzeń
- Deduplikacja MinHash przy 128 skrótach, 16 pasmach: ~10 tys. dokumentów/sekundę na rdzeń
- Pakowanie sekwencji: powiązane we/wy, w przypadku korpusów powyżej 10 GB należy używać plików mapowanych w pamięci

W przypadku tokenów 15T (skala Lama 3) zaplanuj ~30–50 TB surowych danych wejściowych, 1–2 tygodnie wstępnego przetwarzania na 64-rdzeniowej maszynie i ponad 100 TB dysku na pliki pośrednie.

## Lista kontrolna przed treningiem

1. Całkowita liczba tokenów odpowiada Twojemu budżetowi obliczeniowemu (jako wskazówki użyj skalowania Chinchilla lub współczynnika przetrenowania Lamy 3)
2. Dedup usunął 30–40% danych internetowych
3. Filtr jakości usunął 10-20% pozostałych danych
4. Współczynnik kompresji wynosi 3-5 znaków/token dla języka angielskiego
5. Wykorzystanie sekwencji przekracza 95%
6. Losowe kontrole wyrywkowe wykazują czysty i spójny tekst na każdym etapie rurociągu
7. Proporcje mieszania danych zostały sprawdzone w przebiegu szkoleniowym na małą skalę
8. Usunięcie danych osobowych zostało zweryfikowane na próbce
9. Wszystkie formaty binarne (sekwencje spakowane, tablice identyfikatorów tokenów) przechodzą testy kodowania/dekodowania w obie strony
10. Potok jest odtwarzalny: te same dane wejściowe dają identyczny wynik ze stałymi losowymi nasionami