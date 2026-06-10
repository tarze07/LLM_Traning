---

name: prompt-data-quality-checker
description: Weryfikacja i debugowanie jakości danych w potokach pre-trainingowych (przedszkoleniowych) LLM
version: 1.0.0
phase: 10
lesson: 3
tags: [data-pipeline, deduplication, quality-filter, pre-training, llm, data-cleaning]

---

# Kontroler jakości danych dla pre-trainingu (treningu wstępnego) LLM

Podczas tworzenia lub audytowania potoku danych na potrzeby pre-trainingu LLM, skorzystaj z poniższych wytycznych, aby wychwycić problemy z jakością, zanim trafią one do modelu.

## Sygnały ostrzegawcze (czerwone flagi) na wyjściu potoku

**Dzięki deduplikacji usunięto mniej niż 20% danych pochodzących z sieci (web data).** Dane z Common Crawl zawierają zazwyczaj 30–40% duplikatów. Jeśli Twój krok deduplikacji usuwa mniej niż 20%, parametry algorytmu MinHash są zbyt konserwatywne lub próg podobieństwa jest ustawiony zbyt wysoko. Sprawdź: rozmiar shingle'a $k$ (k-shingle size), liczbę funkcji haszujących, liczbę pasm LSH oraz próg Jaccarda.

**Współczynnik kompresji poniżej 2,0 znaków/token.** Oznacza to, że tokenizer zbyt agresywnie fragmentuje tekst. Wytrenuj tokenizer ponownie z większą liczbą scaleń (merges), zwiększ rozmiar słownika lub sprawdź, czy reguły wstępnej tokenizacji nie powodują nadmiernego podziału tekstu.

**Współczynnik kompresji powyżej 6,0 znaków/token.** Tokenizer nauczył się scaleń (merges) bardzo specyficznych dla danej domeny, które słabo się generalizują. Taki stan jest akceptowalny w modelach wąsko wyspecjalizowanych, ale stanowi sygnał ostrzegawczy dla modeli ogólnego przeznaczenia.

**Wykorzystanie sekwencji poniżej 90%.** Oznacza to zbyt dużo paddingu (dopełnienia). Rozwiązanie: przefiltruj zbyt krótkie dokumenty (lub zwiększ próg minimalnej długości) albo popraw efektywność pakowania sekwencji (zrezygnuj z naiwnego paddingu na rzecz pakowania wielu dokumentów w jedną sekwencję – document packing).

**Wykorzystanie słownika poniżej 50%.** Ponad połowa tokenów ze słownika nie występuje w analizowanym korpusie. Oznacza to, że rozmiar słownika jest za duży dla danej domeny lub tokenizer został wytrenowany na zupełnie innym rozkładzie danych.

## Kalibracja filtrów jakości

Przeprowadź poniższe kontrole na losowej próbie 1000 dokumentów na każdym etapie potoku danych:

1. **Po etapie oczyszczania przeczytaj 20 losowych dokumentów.** Sprawdź, czy zawierają pozostałości kodu HTML, JavaScript, menu nawigacyjnego lub boilerplate'u (szablonów stron). Jeśli tak, proces oczyszczania HTML jest niewystarczający.

2. **Przeczytaj 20 losowych dokumentów, które PRZESZŁY filtry jakości.** Sprawdź, czy nie ma wśród nich spamu, list słów kluczowych lub tekstów generowanych maszynowo. Jeśli są, zaostrz progi filtracji.

3. **Przeczytaj 20 losowych dokumentów, które Zostały ODRZUCONE przez filtry jakości.** Sprawdź, czy nie odrzucono wartościowych tekstów. Jeśli tak, filtry są zbyt agresywne – należy złagodzić progi lub dodać wyjątki dla określonych wzorców.

4. **Przeczytaj 20 losowych, uznanych za bliskie duplikaty par z etapu deduplikacji.** Sprawdź, czy są one rzeczywiście podobne. Jeśli nie, obniż próg Jaccarda lub zwiększ liczbę funkcji haszujących.

## Proporcje mieszanki danych (data mixture ratios)

Nie ma uniwersalnej formuły. Zacznij od tych wartości bazowych i dostosuj na podstawie oceny:

| Kategoria | Proporcja w Llama 3 | Sugerowany punkt startowy |
|---------|-------------|----------------|
| Tekst internetowy (web) | 50% | 50% |
| Kod źródłowy | 25% | 15-25% |
| Książki / publikacje naukowe | 13% | 10-15% |
| Matematyka | 8% | 5-10% |
| Języki obce (web) | 4% | 5-10% |

Zwiększ udział kodu źródłowego, jeśli zależy Ci na zdolnościach programistycznych modelu. Zwiększ udział matematyki, jeśli kluczowe są zdolności rozumowania. Zmniejsz udział tekstów z sieci, aby zredukować szum. Zawsze przeprowadzaj ewaluację na benchmarkach po zmianie proporcji mieszanki danych.

## Szacowanie skali zasobów

Dla docelowej liczby tokenów:

- 1T (bilion) tokenów z sieci: wymaga pobrania ~3–5 TB surowego tekstu, co daje ~1,5–2 TB po oczyszczeniu i deduplikacji.
- Szybkość tokenizacji (Rust): ~100 mln tokenów/s na rdzeń
- Szybkość tokenizacji (Python): ~1-10 mln tokenów/s na rdzeń
- Deduplikacja MinHash (128 funkcji haszujących, 16 pasm): ~10 tys. dokumentów/s na rdzeń
- Pakowanie sekwencji: ograniczone głównie przez I/O (we/wy). Dla korpusów przekraczających 10 GB należy korzystać z plików mapowanych w pamięci (memory-mapped files).

W przypadku zbioru o rozmiarze 15T tokenów (skala Llama 3) zaplanuj ~30–50 TB surowych danych wejściowych, 1–2 tygodnie wstępnego przetwarzania na 64-rdzeniowej maszynie oraz ponad 100 TB przestrzeni dyskowej na pliki pośrednie.

## Lista kontrolna przed rozpoczęciem treningu

1. Całkowita liczba tokenów jest dostosowana do budżetu obliczeniowego (wykorzystaj prawa skalowania Chinchilla lub współczynnik nadmiernego trenowania (overtraining) z Llama 3 jako punkt odniesienia).
2. Deduplikacja usunęła 30–40% duplikatów z danych sieciowych.
3. Filtry jakości odrzuciły 10–20% pozostałych danych.
4. Współczynnik kompresji wynosi 3–5 znaków na token dla języka angielskiego.
5. Wykorzystanie sekwencji (sekwencje bez paddingu) przekracza 95%.
6. Wyrywkowa, losowa kontrola wykazuje czysty i spójny tekst na każdym etapie potoku przetwarzania.
7. Proporcje mieszanki danych zostały przetestowane podczas krótkiego treningu na małą skalę.
8. Skuteczność usuwania danych osobowych (PII) została zweryfikowana na losowej próbce.
9. Wszystkie formaty binarne (spakowane sekwencje, tablice identyfikatorów tokenów) poprawnie przechodzą testy kodowania i dekodowania w obie strony (round-trip).
10. Potok przetwarzania jest w pełni reprodukowalny: te same dane wejściowe dają identyczny wynik przy ustalonych wartościach random seed.
