# AI Scientist v2 — badania autonomiczne na poziomie warsztatu

> Aplikacja AI Scientist v2 firmy Sakana (Yamada i in., arXiv:2504.08066) obsługuje pełną pętlę badawczą: hipoteza, kod, eksperymenty, liczby, opis, przesłanie. Jest to pierwszy system, w którym wygenerowano recenzję w formie papierowej podczas warsztatów ICLR 2025. Niezależna ocena (Beel i in.) wykazała, że ​​42% eksperymentów zakończyło się niepowodzeniem z powodu błędów w kodowaniu, a przeglądy literatury często błędnie określały ustalone koncepcje jako nowatorskie. Własne dokumenty Sakany ostrzegają, że baza kodu wykonuje kod napisany przez LLM i zalecają izolację Dockera. Chodzi o obie połowy tego obrazu.

**Typ:** Ucz się
**Języki:** Python (stdlib, zabawka na maszynie stanowej z pętlą badawczą)
**Wymagania wstępne:** Faza 15 · 03 (AlphaEvolve), Faza 15 · 04 (DGM)
**Czas:** ~60 minut

## Problem

Badania są zadaniem otwartym. W odróżnieniu od wyszukiwania algorytmicznego AlphaEvolve lub samodzielnej modyfikacji DGM opartej na benchmarkach, wynik badania nie ma kryterium poprawności sprawdzalnego maszynowo. Artykuł oceniają recenzenci, a nie testy jednostkowe. To sprawia, że ​​pętla jest trudniejsza do zamknięcia i bardziej wartościowa, jeśli jest zamknięta, ponieważ badania to miejsce, w którym liczy się postęp.

AI Scientist v1 (Sakana, 2024) zamknął pętlę, zaczynając od szablonów stworzonych przez człowieka. LLM przeprowadził eksperymenty na stałym rusztowaniu. AI Scientist v2 (Yamada i in., 2025) usuwa wymagania dotyczące szablonów, używając agentycznego wyszukiwania drzewa z pętlą krytyki modelu języka wizyjnego. System generuje pomysły, realizuje eksperymenty, tworzy dane liczbowe, pisze artykuł i wykonuje iteracje na podstawie opinii recenzentów.

Werdykt recenzji: jeden artykuł wygenerowany w wersji 2 został przyjęty na warsztaty ICLR 2025 (z ujawnieniem). Werdykt niezależnej oceny: system jest daleki od niezawodności. Obydwa są prawdziwe.

## Koncepcja

### Architektura

1. **Generowanie pomysłów.** LLM proponuje pomysły badawcze uwarunkowane tematem i wcześniejszą literaturą. v1 używane szablony; wersja 2 wykorzystuje przeszukiwanie agentowe w przestrzeni hipotez.
2. **Kontrola nowości.** Etap wyszukiwania literatury sprawdza, czy pomysł został opublikowany. Jest to etap, na którym ocena Beela i wsp. wykazała błędne oznakowanie – ustalone metody często uznawane są za nowatorskie.
3. **Plan eksperymentu.** Agent sporządza protokół eksperymentu i pisze kod.
4. **Wykonanie.** Kod działa w piaskownicy. Błędy są przekazywane z powrotem do pętli ponawiania. Z pomiarów Beela i wsp. wynika, że ​​na tym etapie 42% eksperymentów zakończyło się niepowodzeniem z powodu błędów w kodowaniu.
5. **Generowanie figur.** Model wizjonersko-językowy odczytuje wygenerowane liczby i przepisuje je dla przejrzystości. To był kluczowy dodatek techniczny wersji 2.
6. **Zapis.** LLM przygotowuje artykuł, który następnie ocenia z wewnętrznym recenzentem.
7. **Opcjonalnie: złożenie.** Artykuł jest przesyłany do miejsca.

### Co oznacza wynik akceptacji warsztatu

Jeden artykuł wygenerowany w wersji 2 przeszedł recenzję podczas warsztatów ICLR 2025. Autorzy ujawnili komitetowi programowemu pochodzenie artykułu. Akceptacja jest punktem danych; nie jest to licencja na twierdzenie, że system „przeprowadza badania”.

Ważny kontekst: artykuły warsztatowe są niżej niż artykuły z konferencji głównej. Recenzja partnerska jest głośna; niewielka część zgłoszeń jest akceptowana każdego dnia. Jeden sukces to dowód koncepcji, a nie twierdzenie o niezawodności. Artykuł Nature 2026 dokumentuje pętlę od końca do końca, a jego współautorem są badacze-ludzi; nie jest tak, że „system napisał artykuł w Nature”.

### Co wykazała niezależna ocena

Beel i in. (arXiv:2502.14297) przeprowadził ocenę zewnętrzną. Główne ustalenia:

- **Niepowodzenie eksperymentów.** 42% eksperymentów zakończyło się niepowodzeniem z powodu błędów w kodowaniu (zły import, niedopasowanie kształtu, niezdefiniowane zmienne). Pętla ponawiania prób złapała niektóre, nie wszystkie.
- **Błędne oznakowanie nowości.** Etap wyszukiwania literatury często oznaczał ustalone koncepcje jako nowatorskie. Jest to badawczy odpowiednik halucynacji.
- **Rozbieżność w jakości prezentacji.** Krytyka postaci w języku wizyjnym doprowadziła do uzyskania efektów wizualnych na poziomie publikacyjnym, maskujących podstawowe słabości eksperymentu.

Ostatnie ustalenie jest istotne dla tej fazy. System, który generuje przekonujące wyniki bez przeprowadzenia przekonujących badań, jest bardziej niebezpieczny, a nie bezpieczniejszy, niż system, który w oczywisty sposób zawodzi. Ocena musi dotrzeć do leżących u podstaw twierdzeń, a nie zatrzymywać się na liczbach.

### Problem ucieczki z piaskownicy

Własne repozytorium Sakany README ostrzega:

> Ze względu na charakter tego oprogramowania, które wykonuje kod wygenerowany przez LLM, nie możemy zagwarantować bezpieczeństwa. Istnieje ryzyko związane z niebezpiecznymi pakietami, niekontrolowanym dostępem do sieci i uruchamianiem niezamierzonych procesów. Używaj na własne ryzyko i rozważ izolację Dockera.

Jest to operacyjny kształt autonomii w niezweryfikowanej domenie. LLM pisze kod; kod działa; kod może zrobić wszystko, co może zrobić proces. Bez piaskownicy, która na stałe ogranicza działania systemu plików, sieci i procesów, każdy samodzielny agent badawczy może wydobywać dane, palić obliczenia lub samodzielnie je przepisywać.

Historia piaskownicy AlphaEvolve jest łatwiejsza, ponieważ jej oceniający jest ścisły. Pętla AI Scientist v2 uruchamia otwarty kod z otwartymi celami. Dlatego potrzebuje silniejszej izolacji (minimum Docker; preferowany seccomp / gVisor) i ręcznego przeglądu każdego zgłoszenia, zanim opuści ono system.

### Gdzie v2 znajduje się na stosie granicznym

| Systemu | Cel | Rodzaj wyniku | Oceniający | Znana awaria |
|---|---|---|---|---|
| AlphaEvolve | algorytmy | kod | jednostka + punkt odniesienia | ograniczony rygorem oceniającego |
| DGM | rusztowanie agenta | kod | Ławka SWE | hakowanie nagród |
| Naukowiec AI v2 | prace badawcze | tekst + kod + cyfry | recenzja partnerska (słaba) | niepowodzenia eksperymentów, błędne oznakowanie, słabość polskiego maskowania |

v2 ma najsłabszy automatyczny ewaluator ze wszystkich trzech, najszerszą powierzchnię wyjściową i najkrótszą ścieżkę do publicznych artefaktów. Kontrole operacyjne (piaskownica, przegląd, ujawnianie) wykonują większość pracy związanej z bezpieczeństwem.

## Użyj tego

`code/main.py` symuluje pętlę v2 jako maszynę stanów: pomysł → sprawdzenie nowości → eksperyment → rysunek → zapis → recenzja → zaakceptuj lub powtórz. Każdy stan ma konfigurowalne prawdopodobieństwo awarii pobrane z Beel et al. ustalenia. Uruchom symulator dla N pętli i policz:

- Ile pomysłów zostało zgłoszonych.
- Ile zgłoszeń miałoby krytyczną, eksperymentalną wadę, którą kryje wypolerowany papier.
- W jaki sposób budżety ponownych prób wpływają na jakość i wydajność.

## Wyślij to

`outputs/skill-ai-scientist-sandbox-review.md` to dwupunktowa lista kontrolna przeglądu wszystkiego, co zostało wyprodukowane przez agenta pętli badawczej, zanim opuści ono piaskownicę.

## Ćwiczenia

1. Uruchom `code/main.py` z parametrami domyślnymi. Jaka część przebiegów pętli daje „czysty” papier? Jaka część daje artykuł z wadą polegającą na niepowodzeniu eksperymentu, którą krytyka postaci dopracowała?

2. Domyślne wartości już wykorzystują 42% / 25% Beela i wsp. Uruchom ponownie za pomocą `--experiment-failure 0.20 --novelty-mislabel 0.10`, a następnie za pomocą `--experiment-failure 0.60 --novelty-mislabel 0.40`. W jaki sposób dopracowana, ale wadliwa część przesuwa się pomiędzy dwoma seriami?

3. Przeczytaj repozytorium AI Scientist v2 firmy Sakana README na temat wymagań piaskownicy. Wymień dwa dodatkowe ograniczenia (poza Dockerem), które zastosowałbyś w przypadku wielodniowego autonomicznego uruchomienia.

4. Przeczytaj Beela i in. Sekcja 4 dotycząca luki w jakości prezentacji. Zaprojektuj jeden dodatkowy ewaluator, który będzie wychwytywał dopracowane, ale eksperymentalnie wadliwe dokumenty.

5. Zaproponuj protokół przeglądu ludzkiego dla wyników pracowników badawczych, który będzie skalowalny lepiej niż „doktorant czyta każdą pracę”. Zidentyfikuj wąskie gardło i zaprojektuj wokół niego.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|---|---|---|
| Naukowiec AI v1 | „Agent badawczy Sakany wzorowany na szablonie” | Wypełnione eksperymenty na stałym rusztowaniu |
| Naukowiec AI v2 | „Agent badawczy bez szablonów” | Przeszukiwanie drzewa agentów z krytyką postaci VLM |
| Przeszukiwanie drzewa agentów | „Branżowy agent badawczy” | Rozwija wiele planów eksperymentów równolegle; suszone śliwki według wewnętrznego krytyka |
| Krytyka języka wizyjnego | „Polerowanie VLM na figurach” | Model multimodalny odczytuje liczby i przepisuje je dla przejrzystości |
| Wyszukiwanie literatury | „Sprawdzanie nowości” | Wyszukuje wcześniejsze prace, aby potwierdzić nowość pomysłu — udokumentowane jako błędne oznaczenie |
| Polskie maskowanie | „Ładny papier, zepsute badania” | Jakość prezentacji przewyższa jakość eksperymentalną; ukrywa słabości |
| Ucieczka z piaskownicy | „Wybucha kod LLM” | Kod wykonywany przez agenta robi rzeczy, których projektant pętli nie zamierzał |

## Dalsze czytanie

- [Yamada i in. (2025). The AI ​​Scientist-v2](https://arxiv.org/abs/2504.08066) — artykuł.
- [Blog Sakany na temat publikacji Nature 2026](https://sakana.ai/ai-scientist-nature/) — podsumowanie dostawcy w kontekście recenzji.
- [Beel i in. (2025). Niezależna ocena The AI ​​Scientist](https://arxiv.org/abs/2502.14297) — numery ocen zewnętrznych.
– [Artykuł Sakana AI Scientist v1](https://arxiv.org/abs/2408.06292) — poprzednik oparty na szablonie.
– [Anthropic — Pomiar autonomii agentów AI](https://www.anthropic.com/research/measuring-agent-autonomimy) — szersze spojrzenie na agentów zajmujących się badaniami otwartymi.