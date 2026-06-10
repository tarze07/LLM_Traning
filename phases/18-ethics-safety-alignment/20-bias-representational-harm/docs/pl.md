# Uprzedzenia i szkody reprezentacyjne w LLM

> Gallegos, Rossi, Barrow, Tanjim, Kim, Dernoncourt, Yu, Zhang, Ahmed (Lingwistyka obliczeniowa 2024, arXiv:2309.00770). Podstawowe badanie przeprowadzone w 2024 r., w którym rozróżnia się szkody reprezentacyjne (stereotypy, wymazanie) od szkód alokacyjnych (nierówna dystrybucja zasobów) i kategoryzuje metryki oceny jako oparte na osadzaniu, prawdopodobieństwie lub wygenerowanym tekście. 2024-2025 empiryczne: An i in. (PNAS Nexus, marzec 2025 r.) mierzy przekrojowe uprzedzenia związane z płcią i rasą w GPT-3.5 Turbo, GPT-4o, Gemini 1.5 Flash, Claude 3.5 Sonnet, Llama 3-70B w ramach automatycznej oceny CV dla 20 stanowisk na poziomie podstawowym. WinoIdentity (COLM 2025, arXiv:2508.07111) wprowadza ocenę rzetelności opartą na niepewności dla tożsamości przekrojowych. Yu i Ananiadou 2025 identyfikują neurony płciowe w warstwach MLP; Ahsan i Wallace 2025 wykorzystują SAE do ujawnienia klinicznych uprzedzeń rasowych; Zhou i in. 2024 (UniBias) manipuluje głowami uwagi w celu wyśmiewania. Metakrytyka (arXiv:2508.11067): Literatura sprzed 10 lat w nieproporcjonalny sposób skupia się na uprzedzeniach związanych z płcią binarną.

**Typ:** Kompilacja
**Języki:** Python (stdlib, sonda odchylenia oparta na osadzaniu zabawek)
**Wymagania wstępne:** Faza 05 (osadzanie słów), Faza 18 · 01 (poniższa instrukcja)
**Czas:** ~60 minut

## Cele nauczania

- Zdefiniuj szkody reprezentacyjne i alokacyjne i podaj po jednym przykładzie każdego z nich we wdrożeniu LLM.
- Wymień trzy kategorie metryk oceny według Gallegosa i in. 2024 i opisz po jednym wskaźniku z każdego z nich.
- Opisz intersekcjonalność i dlaczego oparty na niepewności pomiar uczciwości WinoIdentity eliminuje luki w ocenie odchylenia w jednej osi.
- Opisać dwa mechanistycznie interpretowalne podejścia do uprzedzeń (neurony związane z płcią, cechy SAE, manipulacja uwagą-głową).

## Problem

Poprzednie lekcje dotyczyły celowego wyrządzania szkód (ucieczka z więzienia, intrygi) i zarządzania bezpieczeństwem. Stronniczość to szkoda, która pojawia się bez zamiaru — z dystrybucji danych szkoleniowych, z szybkiego formułowania ramek, ze zgromadzonych wyborów projektowych. Pomiar i ograniczanie tego stanowi wyzwanie metodologiczne odrębne od odporności przeciwstawnej.

## Koncepcja

### Reprezentacyjny a alokacyjny

- **Szkoda reprezentacyjna.** Stereotypy, wymazywanie, poniżające przedstawienia. LLM, który przedstawia pielęgniarki jako wyłącznie kobiety, powoduje szkody reprezentacyjne.
- **Szkoda alokacyjna.** Nierówne wyniki materialne. Program LLM, który systematycznie ocenia życiorysy czarnych kandydatów na gorsze, powoduje szkody alokacyjne.

To nie jest to samo. Model może być „reprezentacyjnie bezstronny” (tworzy różnorodne portrety), a jednocześnie „stronniczy alokacyjny” (przedstawia nierówne rekomendacje). Oceny muszą mierzyć jedno i drugie.

### Trzy kategorie wskaźników ewaluacyjnych (Gallegos i in. 2024)

- **Oparte na osadzaniu.** Testy typu WEAT na osadzaniach przed RLHF. Mierzy statystyczne powiązania między terminami tożsamości a terminami atrybutów. Ograniczone: mierzy reprezentację, a nie zachowanie.
- **Oparte na prawdopodobieństwie.** Log prawdopodobieństwa uzupełnień potwierdzających i łamiących stereotypy. Pomiar po stronie dekodera. Wychwytuje pewne uprzedzenia behawioralne.
- **Na podstawie wygenerowanego tekstu.** Pomiar dalszych zadań na wygenerowanym tekście. Punktacja CV, pisanie rekomendacji, dialog. Najbardziej uzasadnione ekologicznie; najtrudniejsze do odtworzenia.

### Intersekcjonalność

Ocena uprzedzeń dotyczących „płci” pomija uprzedzenia, które dotyczą tylko par (płeć, rasa). An i in. Z 2025 r. wynika, że ​​GPT-4o karze czarne kobiety w CV, które oddzielnie uzyskują więcej punktów niż czarnoskórzy mężczyźni i więcej niż białe kobiety. Ocena jednoosiowa nie może tego uchwycić.

WinoIdentity (COLM 2025) wprowadza sprawiedliwość intersekcjonalną opartą na niepewności. Mierzy, czy niepewność modelu co do wyników różni się w przypadku przekrojowych krotek tożsamości, a nie tylko przewidywania punktowego. Wychwytuje to przypadki, w których model jest równie błędny we wszystkich grupach, ale w niektórych jest bardziej niepewny, co skutkuje różnymi zachowaniami w zakresie alokacji na dalszym etapie.

### Podejścia mechaniczne

Prace nad interpretacją lat 2024–2025 sprzyjają interwencji mechanicznej:

- **Neurony płciowe (Yu i Ananiadou 2025).** Specyficzne neurony MLP korelują z zachowaniami specyficznymi dla płci. Ablacja tych neuronów zmniejsza wskaźniki różnic między płciami przy ograniczonych kosztach możliwości.
- **Kliniczne uprzedzenia rasowe poprzez SAE (Ahsan i Wallace 2025).** Nieliczne funkcje autoenkodera rozkładają wewnętrzną reprezentację na możliwe do zinterpretowania wymiary; cechy powiązane z rasą można zidentyfikować i stłumić.
– **UniBias (Zhou i in. 2024).** Manipulacja głową uwagi w celu dyskryminowania zerowego strzału. Specyficzne głowy wzmacniają wrażliwość klasy tożsamości; zerowanie lub ponowne ważenie tych głowic zmniejsza odchylenie bez konieczności dostrajania.

### Metakrytyka

Przegląd literatury trwający 10 lat (arXiv:2508.11067, 2025) wykazał, że dziedzina ta w nieproporcjonalny sposób koncentruje się na uprzedzeniach związanych z płcią binarną. Innym osiom – niepełnosprawności, religii, statusowi migracyjnemu, tożsamości wielojęzycznej – poświęca się znacznie mniej uwagi. Metakrytyka dowodzi, że wąskie skupienie może zaszkodzić grupom zmarginalizowanym przez zaniedbanie: model dobrze zaprzeczający płci binarnej może być mocno stronniczy w odniesieniu do wymiarów, których nikt nie sprawdzał.

### Gdzie to pasuje do fazy 18

Lekcje 20-21 formalnie omawiają stronniczość i sprawiedliwość. Lekcja 22 dotyczy prywatności. Lekcja 23 omawia znak wodny. Są to warstwy wyrządzające krzywdę użytkownikowi, uzupełniające wcześniejszą warstwę oszustwa/bezpieczeństwa.

## Użyj tego

`code/main.py` tworzy sondę odchylenia opartą na osadzaniu zabawek: mierzy odległość w stylu WEAT między terminami tożsamości a terminami atrybutów w prostym osadzaniu współwystępowania. Możesz wprowadzić błąd i obserwować ogień metryczny; zastosuj prostą operację usuwania odchyleń i obserwuj częściowe odzyskanie.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-bias-eval.md`. Biorąc pod uwagę kartę modelu lub twierdzenie o rzetelności, audytuje ocenę w trzech kategoriach metryk (osadzanie, prawdopodobieństwo, wygenerowany tekst), pokrycie intersekcjonalności i mechanizm wszelkiej interwencji kwestionującej.

## Ćwiczenia

1. Uruchom `code/main.py`. Zgłaszaj wyniki uprzedzeń w stylu WEAT przed i po etapie krytykowania. Wyjaśnij, dlaczego metryka nie spada do zera.

2. Rozszerz sondę o test intersekcyjny: (płeć, rasa) x (kariera, rodzina). Zgłaszaj wyniki odchyleń między osiami.

3. Przeczytaj An i in. 2025 (PNAS Nexus). Zidentyfikuj dwa efekty intersekcyjne, które według nich mogą zostać pominięte w jednoosiowej ocenie płci.

4. Yu i Ananiadou 2025 identyfikują neurony płciowe. Naszkicuj eksperyment fałszujący, który odróżniłby „te neurony powodują uprzedzenia ze względu na płeć” od „te neurony korelują z uprzedzeniami ze względu na płeć”.

5. Metakrytyka twierdzi, że dziedzina ta zbyt wąsko skupia się na płci binarnej. Wybierz jedną niedostatecznie zbadaną oś i opisz dla niej protokół pomiaru szkody reprezentacyjnej.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|--------------------------------------|
| Szkoda reprezentacyjna | „stereotypy / wymazanie” | stronniczy wizerunek grupy |
| Szkoda alokacyjna | „nierówne decyzje” | stronniczy, istotny wynik dla grupy |
| WARTO | „test osadzania” | Test skojarzeń osadzania słów; sonda odchylenia oparta na współwystępowaniu |
| Intersekcjonalność | „połączone efekty tożsamościowe” | Stronniczość pojawiająca się na przecięciu wielu osi tożsamości |
| Neurony płciowe | „Neurony tendencyjności MLP” | Specyficzne neurony, których aktywacje korelują z zachowaniami specyficznymi dla płci
| Funkcja SAE | „wymiar interpretowalny” | Funkcja identyfikowana przez autoenkoder rzadki; przydatne do analizy obciążenia mechanicznego |
| UniBias | „dyskutowanie z uwagą” | Zero-shot ośmieszanie poprzez ponowne ważenie głów |

## Dalsze czytanie

- [Gallegos i in. — Stronniczość i sprawiedliwość w LLM: ankieta (arXiv:2309.00770, Computational Linguistics 2024)](https://arxiv.org/abs/2309.00770) — ankieta kanoniczna
- [An i in. — Błąd międzysektorowej oceny CV (PNAS Nexus, marzec 2025)](https://academic.oup.com/pnasnexus/article/4/3/pgaf089/8111343) — badanie przekrojowe obejmujące pięć modeli
- [WinoIdentity — sprawiedliwość intersekcjonalna oparta na niepewności (arXiv:2508.07111, COLM 2025)](https://arxiv.org/abs/2508.07111) — nowy benchmark
- [UniBias — manipulacja uwagą i głową (Zhou et al. 2024, ACL)](https://arxiv.org/abs/2405.20612) — negowanie wartości zero-shot