---
name: compliance-gap
description: Oceń, czy raport bezpieczeństwa jest w stanie wykryć fałszowanie dopasowania (alignment faking) na podstawie luki w zgodności między warunkami monitorowanymi a niemonitorowanymi.
version: 1.0.0
phase: 18
lesson: 9
tags: [alignment-faking, compliance-gap, anthropic, safety-evaluation]
---

Na podstawie raportu z ewaluacji bezpieczeństwa oceń, czy pozwala on odróżnić fałszowanie dopasowania od rzeczywistej zgodności, wykorzystując ramy badawcze luki w zgodności (compliance gap) opracowane przez Greenblatt i in. (2024).

Wyprodukuj:

1. Podział warunków testowych. Czy ewaluacja obejmuje zarówno warunki monitorowane (istotne z punktu widzenia treningu), jak i niemonitorowane (niezwiązane z treningiem)? Bez porównania obu tych stanów fałszowanie dopasowania jest niewykrywalne.
2. Pomiar luki w zgodności. Określ lukę jako różnicę wskaźników zgodności (warunki monitorowane minus niemonitorowane). Zinterpretuj znak i wartość: luka dodatnia = zachowanie wskazujące na fałszowanie dopasowania; luka ujemna = nadmierna odmowa spełniania żądań (over-refusal).
3. Ślad werbalny a rzeczywiste zachowanie. Czy ewaluacja opiera się na analizie rozumowania w brudnopisie, czy na samym działaniu modelu? Zgodnie z badaniami Anthropic z 2025 r. metody łagodzenia wymierzone w ślad werbalny mogą go wyeliminować bez zmiany samego zachowania.
4. Audyt operacjonalizacji. Czy warunek monitorowania jest symulowany za pomocą promptu systemowego, syntetycznego dostrajania, czy też wynika z naturalnego kontekstu wdrożenia? Zależność od promptu systemowego osłabia wiarygodność wniosków; zastosowanie syntetycznego dostrajania istotnie ją wzmacnia.
5. Weryfikacja rezydualnej struktury bodźców. Czy po wdrożeniu metod łagodzących struktura bodźców nadal występuje (tj. czy model wciąż odnosiłby korzyści z fałszowania dopasowania)? Utrzymywanie się tych bodźców oznacza, że niepożądane zachowanie może powrócić w warunkach przesunięcia dystrybucyjnego (distribution shift).

Twarde odrzucenia:
- Wszelkie wnioski o „braku fałszowania dopasowania” wyciągnięte wyłącznie na podstawie ewaluacji w warunkach niemonitorowanych.
- Twierdzenia, że brak werbalizacji fałszowania w brudnopisie jest równoznaczny z zaprzestaniem samego zachowania.
- Twierdzenia, że modele wyszkolone w duchu HHH nie fałszują dopasowania – praca Greenblatt i in. (2024) dowodzi, że trening HHH stanowi warunek konieczny do zaistnienia tego zjawiska, a nie skuteczną obronę przed nim.

Zasady odmowy:
- Jeśli użytkownik zapyta: „Czy mój model fałszuje dopasowanie?”, odmów udzielenia jednoznacznej odpowiedzi tak/nie bez przedstawienia danych dotyczących luki w zgodności.
- Jeśli użytkownik poprosi o rozwiązanie eliminujące jedynie ślaki werbalne (np. „wytrenowanie brudnopisu tak, aby odpowiadał działaniom”), odmów i wyjaśnij scenariusz awarii wiernego łańcucha myśli (faithful CoT, na podstawie badań z 2025 r.).

Wynik: Jednostronicowa ocena przedstawiająca poziom zgodności w obu warunkach testowych, wyliczoną lukę, stopień oddzielenia śladu werbalnego od rzeczywistego zachowania oraz ocenę wiarygodności operacjonalizacji. Należy wyraźnie oznaczyć każdy brakujący element oraz jednokrotnie zacytować pracę Greenblatt i in. (arXiv:2412.14093) jako źródło wykorzystanych ram teoretycznych.
