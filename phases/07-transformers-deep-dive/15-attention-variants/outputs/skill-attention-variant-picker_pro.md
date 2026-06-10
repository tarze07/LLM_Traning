---

name: attention-variant-picker
description: Wybierz topologię uwagi (pełna/przesuwne okno/rzadka/różnicowa) dla nowego modelu, biorąc pod uwagę długość kontekstu, wymagania dotyczące wyszukiwania informacji oraz profil obliczeniowy.
version: 1.0.0
phase: 7
lesson: 15
tags: [attention, transformer, long-context, inference, memory]

---

# Wybór wariantu mechanizmu uwagi

Pomóż programiście wybrać i uzasadnić topologię uwagi dla nowego transformatora lub dla istniejącego, którego kontekst jest rozszerzany.

## Dane wejściowe do zebrania

1. **Docelowa długość kontekstu** podczas uczenia (treningu) i wnioskowania (często są one różne — wiele modeli trenuje się przy 16k, a rozszerza przy wnioskowaniu).
2. **Zapotrzebowanie na wyszukiwanie informacji (retrieval)** w skali 1–5: 1 = prosty czat, 5 = igła w stogu siana (needle in a haystack) / RAG / analiza długiego kodu z repozytorium.
3. **Budżet pamięci dla wnioskowania** – tolerancja rozmiaru pamięci podręcznej KV (KV Cache) na zapytanie (właściwa jednostka to bajty na token na warstwę).
4. **Tolerancja kosztów treningu** – trenowanie SWA (Sliding Window Attention) od podstaw jest tanie; wdrożenie uwagi różnicowej (differential attention) w gotowym, pre-trenowanym modelu jest kosztowne.
5. **Docelowy sprzęt** – procesory Hopper+ wspierają pełną wersję FlashAttention-3, Ada wspiera FA2, natomiast starsze procesory GPU mają ograniczone wsparcie dla masek.

## Zasady podejmowania decyzji

- **Kontekst ≤ 16k i wyszukiwanie ≤ 3**: Pełna uwaga (Full Attention) za pomocą FlashAttention. Unikaj przedwczesnej optymalizacji.
- **Kontekst 16k–128k i wyszukiwanie ≤ 3**: Hybryda SWA + uwaga globalna w stosunku 5:1, rozmiar okna 1024 (podobnie jak w Gemma 3). Pozwala to zachować zdolność wyszukiwania informacji przy jednoczesnej redukcji rozmiaru KV.
- **Kontekst > 128k**: Pełne SWA z warstwą globalną co 4–6 warstw oraz interpolacja pozycji / skalowanie YaRN (Lekcja 04).
- **Wyszukiwanie = 5 przy odpowiednim budżecie na trening**: Rozważ zastosowanie uwagi różnicowej (differential attention) wyłącznie w ostatnich 4 warstwach (zmniejsza to KV Cache o połowę, a większość zalet wynika z eliminacji szumów).
- **Udostępnianie publicznego API**: Preferuj sprawdzone, stabilne architektury (pełna uwaga, SWA, hybryda Gemma-3). Unikaj niestandardowych rzadkich (sparse) lub różnicowych (diff) rozwiązań, chyba że dysponujesz inżynierami piszącymi dedykowane jądra (kernels) CUDA.
- **Brak możliwości modyfikacji modelu bazowego**: SWA można wdrożyć na etapie wnioskowania poprzez maskowanie; uwagi różnicowej i rzadkiej nie da się dodać w ten sposób.

## Zawsze ostrzegaj (Zwróć uwagę na)

- Modele oparte wyłącznie na SWA (Pure-SWA) o rozmiarze poniżej 7B często radzą sobie wyraźnie gorzej w benchmarkach badających rozumowanie. Odradzamy takie rozwiązanie.
- Rozmiar okna < 512 prawie nigdy nie jest odpowiedni. Wybierz większy rozmiar lub zastosuj inną architekturę.
- Doniesienia naukowe o skuteczności uwagi różnicowej dotyczą głównie małych modeli (3–7B). Według stanu na początek 2026 roku dowody na skalowalność tej metody są nieliczne.
- Każdy z wariantów współdziała ze skalowaniem RoPE / YaRN (Lekcja 04). Wyraźnie określ schemat kodowania pozycji.

## Format wyjściowy

Zwróć:

1. **Rekomendacja** – konkretna nazwa architektury (np. „hybryda Gemma-3, W=1024, stosunek 5:1 SWA:global”).
2. **Uzasadnienie** – odniesienie każdego parametru wejściowego do powyższych reguł decyzyjnych.
3. **Oszacowanie pamięci KV Cache** – w docelowym kontekście, wyrażone w bajtach na token na warstwę oraz w GB dla batch size = 1.
4. **Ścieżka migracji** – instrukcja, jak przeprowadzić adaptację, jeśli model bazowy został już wytrenowany.
5. **Znane ryzyka** – wskazanie, które benchmarki lub zadania mogą odnotować pogorszenie wyników (regresję).
