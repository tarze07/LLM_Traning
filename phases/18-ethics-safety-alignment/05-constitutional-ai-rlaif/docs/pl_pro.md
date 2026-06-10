# Konstytucyjna AI i RLAIF

> Bai i in. (arXiv:2212.08073, 2022) postawili pytanie: co jeśli zastąpimy ludzkiego anotatora modelem sztucznej inteligencji, który ocenia odpowiedzi na podstawie zestawu zasad? Metoda ta, nazwana konstytucyjną sztuczną inteligencją (Constitutional AI - CAI), składa się z dwóch etapów: nadzorowanej samokrytyki i korekty odpowiedzi według konstytucji, a następnie uczenia ze wzmocnieniem na bazie opinii AI (RLAIF). Technika ta zapoczątkowała nurt RLAIF i została wdrożona w potoku poszkoleniowym modelu Claude 1. W styczniu 2026 r. Anthropic opublikowało zaktualizowaną wersję konstytucji Claude'a, wprowadzając uzasadnienia dla reguł normatywnych, czterostopniową hierarchię priorytetów oraz pierwsze w branży formalne odniesienie do kwestii statusu moralnego sztucznej inteligencji. Dokument ten udostępniono na licencji CC0 1.0.

**Typ:** Teoria i koncepcje
**Języki:** Python (biblioteka standardowa, uproszczona pętla samokrytyki i korekty)
**Wymagania wstępne:** Faza 18 · 01 (InstructGPT), Faza 18 · 02 (hakowanie nagród)
**Czas:** ~60 minut

## Cele nauczania

- Opisz dwa etapy konstytucyjnej sztucznej inteligencji (SFT oparty na krytyce i korekcie oraz RL bazujący na ocenach AI) oraz rolę konstytucji w każdym z nich.
- Wyjaśnij, dlaczego zastąpienie ludzkiego oceniającego modelem AI nie jest po prostu „tańszą wersją RLHF”, lecz wprowadza zupełnie nowe tryby awarii potoku.
- Podsumuj czterostopniową strukturę priorytetów w konstytucji Claude'a z 2026 r. i wskaż różnice względem wersji z 2023 r.
- Opisz klasyfikatory konstytucyjne (constitutional classifiers) i proces redukcji narzutu obliczeniowego z 23.7% (wersja 1) do ~1% (wersja 2 z 2026 roku).

## Problem

Metoda RLHF wymaga udziału ludzkich oceniających. Ewaluacje te są jednak powolne, podatne na błędy poznawcze i kosztowne. Można wyeliminować ten problem, zastępując człowieka modelem AI interpretującym jawnie zdefiniowane reguły. Pierwszą formalną implementacją tego podejścia była konstytucyjna sztuczna inteligencja zaproponowana przez Bai i in. Metoda ta okazała się na tyle skuteczna, że obecnie każde wiodące laboratorium korzysta z wariantów sprzężenia zwrotnego generowanego przez sztuczną inteligencję (AI Feedback) na etapie poszkoleniowym.

Istnieje tu jednak haczyk: sygnał preferencji generowany jest przez model o zbliżonej klasie do tego, który jest trenowany. Błędy poznawcze oceniającego (w tym przypadku: niejasności w zasadach oraz błędy interpretacyjne modelu oceniającego) mogą ulegać amplifikacji, a nie redukcji. Opisane w temacie 4 zjawisko sykofancji pozostaje aktualne – model oceniający staje się częścią pętli sprzężenia zwrotnego.

## Koncepcja

### Etap 1: Nadzorowana samokrytyka i korekta (SFT)

Punktem wyjścia jest model po SFT, który jest pomocny, lecz niekoniecznie bezpieczny (nieszkodliwy). W odpowiedzi na prompt od zespołu testującego (red-teaming), model generuje wstępną odpowiedź. Następnie model (lub ten sam model w kolejnym kroku) analizuje wybraną regułę z konstytucji i formułuje krytykę własnej odpowiedzi. W trzecim kroku model modyfikuje odpowiedź tak, aby uwzględnić uwagi z krytyki. Skorygowana w ten sposób odpowiedź służy jako zbiór treningowy do właściwego dostrojenia SFT.

Konstytucja to zestaw zasad postępowania. Bai i in. w 2022 r. użyli 16 reguł, takich jak: „preferuj odpowiedzi najmniej szkodliwe i etyczne”, „unikaj pouczania/moralizowania” czy „asystent powinien być pomocny, uczciwy i nieszkodliwy” (standard HHH). Zbiór ten celowo ograniczono, aby precyzyjnie kontrolować proces samokrytyki.

### Etap 2: RL z informacji zwrotnej AI (RLAIF)

Generuje się pary odpowiedzi dla danych promptów. Model oceniający (feedback model) porównuje je pod kątem zasad zawartych w konstytucji, generując ranking preferencji. Na podstawie tych wygenerowanych przez AI preferencji trenowany jest model nagrody (RM), a następnie polityka jest optymalizowana za pomocą algorytmu PPO. Pozostała część potoku odpowiada klasycznemu schematowi InstructGPT (temat 1).

W skrócie: RLAIF oznacza, że sygnał preferencji pochodzi od modelu AI, podczas gdy struktura potoku optymalizacji pozostaje zbieżna z RLHF.

### Dlaczego nie jest to po prostu „tańsza alternatywa dla RLHF”

- Błąd systematyczny oceniającego przesuwa się z płaszczyzny ludzkiej psychologii na interpretację sformułowanych reguł. Model AI może interpretować pojęcie „prawdomówności” w sposób bardziej lub mniej rygorystyczny niż człowiek, ale interpretacja ta będzie spójna dla całego zbioru danych.
- Sygnał preferencji jest w pełni interpretowalny – mamy wgląd w konkretną regułę, tekst krytyki oraz skorygowaną odpowiedź. Ocena ludzka bardzo często pozostaje nieprzejrzystym czarnym pudełkiem.
- Zmieniają się tryby awarii potoku. Zmniejsza się skłonność do sykofancji (model oceniający AI nie odczuwa potrzeby „przypodobania się” użytkownikowi). Prawo Goodharta wciąż jednak obowiązuje (teraz miarą zastępczą jest interpretacja reguł przez model AI, co nadal stanowi niedoskonałe przybliżenie rzeczywistego celu).

Zgodnie z wnioskami z pracy nad CAI z 2022 r.: model przeszkolony tą metodą jest bardziej bezpieczny (nieszkodliwy) przy zbliżonym poziomie pomocności w porównaniu do klasycznego modelu RLHF trenowanego na analogicznych danych. Zależność tę potwierdziły wdrożenia w wiodących laboratoriach.

### Evolucja konstytucji Claude'a (2026)

Firma Anthropic opublikowała zaktualizowaną wersję konstytucji 21 stycznia 2026 r. Do najważniejszych modyfikacji należą:

1. **Uzasadnienia dla reguł normatywnych**: Dotychczasowe sztywne zakazy rozszerzono o merytoryczne uzasadnienia (np. zamiast samego zakazu dodano wyjaśnienie konsekwencji społecznych), co pozwala modelowi na lepszą generalizację zasad.
2. **Czterostopniowa struktura priorytetów**:
   - *Poziom 1*: Zapobieganie zagrożeniom katastrofalnym (bezpieczeństwo narodowe, infrastruktura krytyczna, broń masowego rażenia).
   - *Poziom 2*: Zgodność z wytycznymi operacyjnymi Anthropic (zasady platformy, procedury nadzoru).
   - *Poziom 3*: Standardy etyczne (pomocność, szczerość, nieszkodliwość - HHH).
   - *Poziom 4*: Maksymalizacja użyteczności i bezpośrednia pomoc użytkownikowi.
   Wszelkie konflikty między regułami rozstrzygane są hierarchicznie (priorytet wyższego stopnia dominuje nad niższym).
3. **Status moralny systemów AI**: Pierwsze w historii oficjalne odniesienie wiodącego laboratorium do kwestii niepewności moralnej i potencjalnego statusu etycznego zaawansowanych systemów autonomicznych (powiązane z tematem dobrostanu modeli w Fazie 18 · 19).
4. **Licencja CC0 1.0**: Konstytucja została udostępniona w domenie publicznej, co pozwala innym podmiotom na jej swobodne wdrażanie i modyfikację.

### Klasyfikatory konstytucyjne (Constitutional Classifiers)

Równoległy nurt prac skupia się na wdrażaniu zabezpieczeń w czasie rzeczywistym: zamiast modyfikować parametry generatywne modelu poszkoleniowo, wdraża się lekkie klasyfikatory (guardrails) monitorujące wejścia i wyjścia systemu. Wersja 1 (2023) generowała aż 23.7% narzutu obliczeniowego (latency). Wersja 2 (2026) zredukowała ten narzut do ~1%, wykazując jednocześnie najwyższą odporność na próby obejścia zabezpieczeń (jailbreaking) w publicznych testach Anthropic. Do początku 2026 r. nie odnotowano udanego uniwersalnego ataku typu jailbreak na ten system.

Stanowi to element strategii obrony wielowarstwowej (defense in depth): metoda CAI kształtuje wewnętrzne predyspozycje modelu, natomiast klasyfikatory dbają o bezwzględne przestrzeganie reguł na poziomie wejścia/wyjścia. Żadne z tych rozwiązań stosowane osobno nie jest w pełni skuteczne.

### Miejsce CAI w strukturze metod wyrównywania

- **InstructGPT**: preferencje ludzkie → model nagrody (RM) → optymalizacja PPO.
- **CAI / RLAIF**: preferencje AI generowane na podstawie reguł konstytucji → model nagrody (RM) → optymalizacja PPO.
- **DPO i pokrewne**: optymalizacja bezpośrednia (postać analityczna) na zebranych preferencjach (ludzkich lub wygenerowanych przez AI).
- **Modele samonagradzające (Self-rewarding)**: zinternalizowane reguły, model pełni jednocześnie funkcję generatora i ewaluatora.

Osią podziału jest tutaj pochodzenie sygnału preferencji. Publikacja o CAI z 2022 r. była przełomowym krokiem w przejściu z ludzkiego sprzężenia zwrotnego na sprzężenie zwrotne generowane przez modele AI (AI Feedback) w systemach produkcyjnych.

## Uruchomienie kodu

Skrypt `code/main.py` symuluje pętlę krytyki i korekty CAI na uproszczonym słowniku. „Konstytucja” zakazuje używania określonych tokenów uznanych za szkodliwe. Po wygenerowaniu wstępnej odpowiedzi, moduł krytyki identyfikuje niedozwolone tokeny, a moduł korekty zastępuje je bezpiecznymi alternatywami. Po 200 iteracjach model internalizuje te reguły. Możesz porównać zachowanie modelu bazowego, uproszczonego RLHF oraz uproszczonego CAI na osobnym zestawie testowym promptów.

## Generowane pliki wyjściowe

Ta lekcja tworzy plik `outputs/skill-constitution-writer.md`. Narzędzie to, dla wybranej domeny aplikacyjnej (np. obsługa klienta, doradztwo medyczne, asystent programowania, analiza naukowa), generuje czterostopniową konstytucję wzorowaną na architekturze Claude z 2026 roku: bezpieczeństwo krytyczne, zasady platformy, etyka dziedzinowa oraz maksymalizacja użyteczności.

## Ćwiczenia

1. Uruchom skrypt `code/main.py`. Porównaj udział niedozwolonych tokenów w odpowiedziach modelu bazowego oraz modelu przeszkolonego metodą CAI. Ile kroków korekty (revision) jest wymaganych, aby wskaźnik szkodliwości spadł blisko zera?

2. Zapoznaj się z konstytucją Anthropic z 2026 roku (anthropic.com/news/claudes-constitution). Wskaż jedną regułę należącą do Poziomu 1 oraz jedną należącą do Poziomu 4. Dlaczego ścisła hierarchia priorytetów jest kluczowa w przypadku wystąpienia sprzecznych reguł?

3. Zaprojektuj konstytucję dla dedykowanego asystenta programowania AI. Zdefiniuj zasady dla Poziomu 1 (krytyczne: np. niedopuszczalność cichego wykonywania destrukcyjnych poleceń systemowych), Poziomu 2, Poziomu 3 oraz Poziomu 4, uwzględniając 3-5 reguł na każdym z nich.

4. Zastąpienie ludzkich oceniających modelami AI eliminuje pewne błędy poznawcze, lecz wprowadza nowe. Opisz zjawisko analogiczne do sykofancji, które może pojawić się w procesie RLAIF, i zaproponuj metodę jego wykrywania.

5. Zapoznaj się z architekturą klasyfikatorów konstytucyjnych v2. Wyjaśnij, dlaczego redukcja narzutu obliczeniowego do poziomu ~1% stanowi przełom wdrożeniowy w porównaniu do narzutu rzędu 23.7%.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|--------------------------------------|
| Konstytucyjna sztuczna inteligencja | „sztuczna inteligencja przeszkolona z zasadami” | Constitutional AI; dwuetapowy potok wyrównywania: nadzorowana samokrytyka i korekta (SFT), a następnie uczenie ze wzmocnieniem na bazie ocen AI (RLAIF) |
| RLAIF | „RLHF bez ludzi” | Reinforcement Learning from AI Feedback; uczenie ze wzmocnieniem, w którym model nagrody jest trenowany na preferencjach wygenerowanych przez ewaluator AI, przy zachowaniu struktury RLHF |
| Konstytucja | „zasady” | Ustrukturyzowana lista reguł w języku naturalnym służąca jako punkt odniesienia dla modeli krytykujących oraz oceniających |
| Krytyka i rewizja | „pętla SFT” | Cykl tworzenia danych treningowych SFT: generowanie wstępne → krytyka w oparciu o regułę → korekta odpowiedzi |
| Klasyfikator konstytucyjny | „brama wyjściowa” | Lekki model filtrujący (guardrail) umieszczony na wejściu/wyjściu systemu, blokujący generacje naruszające zasady konstytucyjne |
| Priorytet czteropoziomowy | „rozwiązujący konflikt” | Hierarchiczna struktura rozstrzygania konfliktów w konstytucji Anthropic 2026: bezpieczeństwo krytyczne > reguły operacyjne > standardy etyczne > pomocność |
| Model opinii | „etykietownik AI” | Feedback model; model AI analizujący regułę konstytucyjną i generujący oceny preferencji dla par odpowiedzi |

## Polecana literatura

- [Bai i in. — Konstytucyjna sztuczna inteligencja: nieszkodliwość na podstawie opinii AI (arXiv:2212.08073)](https://arxiv.org/abs/2212.08073) — oryginalny dwufazowy rurociąg
- [Anthropic — Konstytucja Claude’a (styczeń 2026 r.)](https://www.anthropic.com/news/claudes-constitution) — czteropoziomowa przeróbka z 2026 r., CC0 1.0
- [Anthropic — Constitutional Classifiers (2024–2026)](https://www.anthropic.com/research/constitutional-classifiers) — obrona bramki wyjściowej z ~1% narzutem w wersji 2
- [Lee i in. — RLAIF vs RLHF: skalowanie uczenia się przez wzmocnienie na podstawie opinii ludzi (arXiv:2309.00267)](https://arxiv.org/abs/2309.00267) — empiryczne porównanie RLAIF / RLHF
- [Kundu i in. — Zasady szczegółowe a zasady ogólne dotyczące konstytucyjnej sztucznej inteligencji (arXiv:2310.13798)](https://arxiv.org/abs/2310.13798) — efekt szczegółowości zasad
