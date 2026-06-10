---

name: attention-variant-picker
description: Wybierz topologię pełnego/przesuwanego okna/rzadką/różnicową uwagę dla nowego modelu, biorąc pod uwagę długość kontekstu, wymagania dotyczące pobierania i profil obliczeniowy.
version: 1.0.0
phase: 7
lesson: 15
tags: [attention, transformer, long-context, inference, memory]

---

# Wybór wariantu uwagi

Pomóż programiście wybrać i uzasadnić topologię uwagi dla nowego transformatora lub dla istniejącego, który rozszerza się na dłuższy kontekst.

## Dane wejściowe do zebrania

1. **Docelowa długość kontekstu** podczas uczenia i wnioskowania (często różne — wiele modeli trenuje przy 16 tys. i rozszerza przy wnioskowaniu).
2. **Zapotrzebowanie na odzyskanie** w skali 1–5: 1 = czysty czat, 5 = igła w stogu siana / RAG / kod z długim kontekstem repozytorium.
3. **Budżet pamięci wnioskowania** Tolerancja pamięci podręcznej KV na żądanie (właściwa jednostka to bajty na token na warstwę).
4. **Tolerancja kosztów szkoleń** — szkolenie SWA od podstaw jest tanie; modernizacja uwagi różnicowej we wstępnie wyszkolonym modelu jest kosztowna.
5. **Docelowy sprzęt** — Hopper+ ma pełną wersję FlashAttention-3, Ada ma FA2, starsze procesory graficzne mają ograniczoną maskę.

## Zasady podejmowania decyzji

- **Kontekst ≤ 16 tys. i wyszukiwanie ≤ 3**: pełna uwaga dzięki FlashAttention. Nie optymalizuj przedwcześnie.
- **Kontekst 16–128 K i wyszukiwanie ≤ 3**: mieszane SWA + globalne w proporcjach 5:1, okno 1024 (kształt Gemma 3). Utrzymuje możliwość pobierania podczas zwijania KV.
- **Kontekst > 128K**: pełne SWA z warstwą globalną co 4–6 warstw plus interpolacja pozycji / skalowanie przędzy (Lekcja 04).
- **Odzyskiwanie = 5 i pozwala na to budżet szkolenia**: rozważ zróżnicowanie uwagi tylko w 4 najwyższych warstwach (połowa podwojenia KV, większość wygrywa poprzez anulowanie opadania).
- **Dostarczasz publiczny interfejs API**: preferuj stabilne wzorce (pełne, SWA, mieszanka Gemma-3). Pomiń natywny rzadki / DIFF, chyba że masz inżynierów jądra.
- **Nie można zmienić modelu podstawowego**: SWA można doposażyć na podstawie wniosku poprzez maskowanie; różnicowe i rzadkie nie mogą.

## Zawsze flaguj

- Modele Pure-SWA poniżej 7B często wymiernie przegrywają w testach porównawczych rozumowania. Polecam przeciw.
- Rozmiar okna < 512 prawie nigdy nie jest odpowiedni. Wybierz większy lub użyj innej topologii.
- Doniesienia o różnicowaniu uwagi w artykule dotyczą małych modeli (3–7B). Według stanu na początek 2026 r. dowody na zwiększenie skali są nieliczne.
- Każdy wariant współdziała ze skalowaniem RoPE / YaRN (Lekcja 04). Wyraźnie określ schemat pozycji.

##Format wyjściowy

Powrót:

1. **Zalecenie** — topologia o pojedynczej nazwie (np. „Gemma-3 mix, W=1024, 5:1 SWA:global”).
2. **Uzasadnienie** — przypisz każde wejście do powyższej reguły decyzyjnej.
3. **Oszacowanie pamięci podręcznej KV** — w kontekście docelowym, w bajtach na token na warstwę i GB w partii 1.
4. **Ścieżka migracji** — jeśli model bazowy jest już przeszkolony, jak przeprowadzić modernizację.
5. **Znane ryzyko** – które testy porównawcze/obciążenia mogą ulec regresowi.