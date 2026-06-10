# Karty modeli, systemów i zestawów danych

> Trzy formaty dokumentacji zapewniają przejrzystość AI. Karty Modeli (Mitchell et al. 2019) — etykiety żywieniowe dla modeli: dane treningowe, ilościowe analizy zdezagregowane, względy etyczne, zastrzeżenia; jedynie 0,3% kart z modelem Przytulonej Twarzy dokumentuje względy etyczne (Oreamuno i in. 2023). Arkusze danych dla zbiorów danych (Gebru et al. 2018, CACM) — motywacja, skład, proces gromadzenia, etykietowanie, dystrybucja, utrzymanie; analogia do arkusza danych elektroniki. Karty danych (Pushkarna i in., Google 2022) — modułowe, warstwowe detale (teleskopowe, peryskopowe, mikroskopowe) jako obiekty graniczne dla różnorodnych czytelników. Zmiany w latach 2024–2025: automatyczne generowanie poprzez LLM (CardGen, Liu i in. 2024); szczegóły karty modelu korelują ze wzrostem pobierania plików o 29% na HF (Liang i in. 2024); weryfikowalne atesty (Laminator, Duddu i in. 2024); uzupełnienia w raportach dotyczących zrównoważonego rozwoju dla węgla/wody (Jouneaux i in., lipiec 2025 r.); Pojawiają się karty regulacyjne UE/ISO. Karty systemowe (Sidhpurwala 2024; Przejrzystość na poziomie metasystemu; „Blueprints of Trust” arXiv:2509.20394) — kompleksowa dokumentacja systemu AI obejmująca możliwości bezpieczeństwa, ochronę przed natychmiastowym wstrzyknięciem, wykrywanie eksfiltracji danych, zgodność z wartościami ludzkimi.

**Typ:** Kompilacja
**Języki:** Python (stdlib, karta modelu + arkusz danych + generator kart systemowych)
**Wymagania wstępne:** Faza 18 · 18 (ramy bezpieczeństwa), Faza 18 · 24 (przepisy)
**Czas:** ~60 minut

## Cele nauczania

- Opisz oryginalne dzieło Mitchella i in. Karta modelu 2019 oraz Gebru i in. Arkusz danych 2018.
- Opisać teleskopowe/peryskopowe/mikroskopowe ułożenie kart danych.
- Opisać karty systemowe i ich kompleksowe pokrycie.
- Proszę wskazać trzy zmiany na lata 2024–2025 (automatyczne wytwarzanie energii, weryfikowalne atesty, raportowanie dotyczące zrównoważonego rozwoju).

## Problem

Ramy regulacyjne (lekcja 24) i zasady bezpieczeństwa laboratorium (lekcja 18) wymagają dokumentacji. Formaty dokumentacji ewoluowały od specyficznej dla modelu (karty modeli), przez specyficzne dla zbioru danych (arkusze danych), aż po specyficzne dla systemu (karty systemowe). Każdy z nich dotyczy innego zakresu przejrzystości. Prace w zakresie automatyzacji i weryfikowalnej atestacji prowadzone w latach 2024–2025 rozwiązują długotrwały problem z przyjęciem.

## Koncepcja

### Karty modeli (Mitchell et al. 2019)

Sekcje:
- Szczegóły modelu.
- Przeznaczenie.
- Czynniki (istotne czynniki demograficzne lub środowiskowe do oceny).
- Metryki.
- Dane ewaluacyjne.
- Dane treningowe.
- Analizy ilościowe (w podziale na czynniki).
- Względy etyczne.
- Zastrzeżenia i zalecenia.

Problem adopcyjny: Oreamuno i in. Kontrola kart modeli Hugging Face przeprowadzona w 2023 r. wykazała, że ​​tylko 0,3% dokumentów dokumentuje względy etyczne.

### Arkusze danych dla zbiorów danych (Gebru et al. 2018)

Analogia do elektroniki i arkusza danych. Sekcje:
- Motywacja (dlaczego utworzono zbiór danych).
- Skład (co się w nim znajduje).
- Proces zbierania (jak został złożony).
- Etykietowanie (jeśli dotyczy).
- Zastosowania (zamierzone, zabronione, ryzyko).
- Dystrybucja.
- Konserwacja.

Opublikowano w CACM 2021. Arkusz danych stanowi dokumentację poprzedzającą; karta modelu zależy od dokładności arkusza danych.

### Karty danych (Pushkarna i in., Google 2022)

Modułowe, warstwowe detale. Trzy poziomy powiększenia:
- **Teleskopowy.** Podsumowanie wysokiego poziomu dla laików.
- **Peryskopowy.** Przegląd średniego poziomu dla praktyków ML.
- **Mikroskopijne.** Szczegółowa dokumentacja na poziomie funkcji dla audytorów.

Ramy obiektu granicznego: różni czytelnicy wydobywają różne informacje z tego samego dokumentu.

### Karty systemowe

Zakres: kompleksowy system AI obejmujący model + stos bezpieczeństwa + kontekst wdrożenia. Sekcje zazwyczaj obejmują:
- Możliwości bezpieczeństwa.
- Ochrona przed natychmiastowym wstrzyknięciem.
- Wykrywanie eksfiltracji danych.
- Zgodność z ustalonymi wartościami ludzkimi.
- Reagowanie na incydenty.

Sidhpurwala 2024 i Meta zapewniają przejrzystość na poziomie systemu. „Blueprints of Trust” (arXiv:2509.20394) formalizuje Kartę Systemową jako uzupełnienie warstwy rozmieszczania Kart Modeli.

### Zmiany w latach 2024–2025

- **CardGen (Liu i in. 2024).** Automatyczne generowanie kart modeli za pośrednictwem LLM; zgłasza wyższą obiektywność niż wiele kart autorstwa człowieka na standardowych polach Mitchell 2019.
- **Korelacja pobierania (Liang i in. 2024).** Szczegółowe karty modeli korelują z nawet o 29% wyższą szybkością pobierania na HF — presja na przyjęcie jest obecnie napędzana przez rynek, a nie tylko przez zgodność.
- **Laminator (Duddu et al. 2024).** Weryfikowalne atesty za pomocą sprzętowego TEE / podpisów kryptograficznych — dzięki temu model karty może przenosić dowód roszczenia, a nie tylko reklamację.
- **Zrównoważony rozwój (Jouneaux i in., lipiec 2025 r.).** Dodatki dotyczące śladu węglowego, wodnego i obliczeniowego śladu energetycznego; pojawiające się standardy ISO.
- **Karty regulacyjne.** Ustawa UE o sztucznej inteligencji (Lekcja 24) Kodeks postępowania GPAI W rozdziale dotyczącym przejrzystości wymagane są karty modelowe jako artefakt zgodności.

### Gdzie to pasuje do fazy 18

Lekcje 24-25 dotyczą warstw regulacyjnych i CVE. Lekcja 26 to warstwa dokumentacji. Lekcja 27 dotyczy zarządzania danymi szkoleniowymi, co stanowi początek arkusza danych. Lekcja 28 to ekosystem badawczy, który generuje oceny, o których mowa w kartach.

## Użyj tego

`code/main.py` generuje kartę minimalnego modelu, arkusz danych i kartę systemową na potrzeby wdrożenia zabawki. Każdy z nich ma kanoniczną strukturę sekcji. Możesz sprawdzić format i porównać trzy zakresy.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-card-audit.md`. Biorąc pod uwagę kartę modelu, arkusz danych lub kartę systemową, sprawdza pokrycie sekcji, dezagregację numeryczną i obecność sprawdzalnych atestów.

## Ćwiczenia

1. Uruchom `code/main.py`. Sprawdź wygenerowane karty. Zidentyfikuj sekcje, które są słabe (tylko symbol zastępczy) i określ, jakie dowody je wzmocnią.

2. Rozszerz kartę modelową o ilościową analizę zdezagregowaną w dwóch grupach demograficznych (Lekcja 20).

3. Przeczytaj Oreamuno i in. 2023 r. przy wskaźniku przyjęcia wynoszącym 0,3%. Zaproponuj jedną zmianę strukturalną w specyfikacji modelu karty, która zwiększyłaby przyjęcie względów etycznych.

4. Laminator (Duddu et al. 2024) wykorzystuje TEE do weryfikowalnych atestów. Zaprojektuj pole karty modelu, które zawiera kryptograficzne potwierdzenie wyniku oceny i opisz rolę weryfikatora.

5. Napisz kartę systemową (kartę systemową, a nie kartę modelową) dla jednego ze swoich poprzednich projektów lub hipotetycznego wdrożenia. Zidentyfikuj sekcję o najwyższej wartości dla audytorów zewnętrznych.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|--------------------------------------|
| Karta modelu | „karta Mitchella” | Mitchell i in. Dokumentacja standardowa 2019 dla modeli ML |
| Arkusz danych | „arkusz danych Gebru” | Gebru i in. Standardowa dokumentacja zbiorów danych 2018 |
| Karta danych | „karta Pushkarna” | Dokumentacja danych modułowych i warstwowych Google 2022 |
| Karta systemowa | "karta rozstawienia" | Kompleksowa dokumentacja systemu AI, w tym stos bezpieczeństwa |
| Obiekt graniczny | „różni czytelnicy, jeden dokument” | Ramy kart danych: ten sam dokument służy różnym odbiorcom |
| Sprawdzalne poświadczenie | "Atest Laminatora" | Dowód kryptograficzny lub TEE dołączony do roszczenia dokumentacyjnego |
| Pole zrównoważonego rozwoju | „ślad węglowy / wodny” | Pojawiający się dodatek w 2025 r. dotyczący rachunkowości środowiskowej |

## Dalsze czytanie

- [Mitchell i in. — Karty modeli do raportowania modeli (arXiv:1810.03993, FAT* 2019)](https://arxiv.org/abs/1810.03993) — karta modelu kanonicznego
- [Gebru i in. — Arkusze danych dla zbiorów danych (CACM 2021, arXiv:1803.09010)](https://arxiv.org/abs/1803.09010) — arkusz danych
- [Pushkarna i in. — Karty danych (Google 2022)](https://arxiv.org/abs/2204.01075) — warstwowa dokumentacja danych
- [Sidhpurwala i in. — Plany zaufania (arXiv:2509.20394)](https://arxiv.org/abs/2509.20394) — Formalizacja karty systemowej