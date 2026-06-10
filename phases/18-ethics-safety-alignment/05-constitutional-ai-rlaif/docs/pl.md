# Konstytucyjna AI i RLAIF

> Bai i in. (arXiv:2212.08073, 2022) zapytał: co by było, gdybyśmy zastąpili człowieka etykietującego sztuczną inteligencją, która czyta listę zasad? Konstytucyjna sztuczna inteligencja składa się z dwóch faz – samokrytyki i rewizji na mocy konstytucji, a następnie RL z informacji zwrotnej AI. Technika ta ukuła termin RLAIF i została wdrożona w procesie poszkoleniowym Claude 1. 21 stycznia 2026 r. firma Anthropic opublikowała przepisaną konstytucję Claude'a: uzasadnienie wyjaśniające dotyczące zasad normatywnych, czterostopniową hierarchię priorytetów i pierwsze formalne potwierdzenie przez duże laboratorium niepewności co do modelowego statusu moralnego. Wydany pod CC0 1.0.

**Typ:** Ucz się
**Języki:** Python (stdlib, pętla do samodzielnej krytyki i poprawiania zabawek)
**Wymagania wstępne:** Faza 18 · 01 (InstructGPT), Faza 18 · 02 (hakowanie nagród)
**Czas:** ~60 minut

## Cele nauczania

- Opisać dwie fazy konstytucyjnej sztucznej inteligencji (krytyka i weryfikacja SFT, RL na podstawie informacji zwrotnych od AI) oraz rolę konstytucji w każdym z nich.
- Wyjaśnij, dlaczego zastąpienie znacznika preferencji człowieka etykietą AI nie jest „tańszym” RLHF — zmienia tryby awarii rurociągu.
- Podsumuj czterostopniową strukturę priorytetów konstytucji Claude z 2026 r. i co zmieniło się od jej przepisania w 2023 r.
- Opisać klasyfikatory konstytucyjne i spadek z 23,7% narzutu obliczeniowego (wersja 1) do ~ 1% (wersja 2 / 2026).

## Problem

RLHF potrzebuje osób zajmujących się etykietowaniem. Etykiety są powolne, stronnicze i drogie. Możesz wyeliminować etykietę, zastępując ją modelem, który czyta wyraźne zasady. Pierwszą formalną wersją tego podstawienia była konstytucyjna sztuczna inteligencja Bai i in. Działało na tyle dobrze, że każde pionierskie laboratorium korzysta teraz z pewnego wariantu informacji zwrotnej opartej na sztucznej inteligencji po szkoleniu.

Haczyk: sygnał preferencji jest teraz generowany przez model tej samej klasy, który trenujesz. Błędy w osobie etykietującej (obecnie: w zasadach oraz w interpretacji modelu osoby etykietującej) można raczej wzmacniać niż osłabiać. Argument z lekcji 4 dotyczący pochlebstwa jest nadal aktualny; etykietujący właśnie wszedł do pętli.

## Koncepcja

### Faza 1 — Nadzorowana samokrytyka i weryfikacja

Zacznij od pomocnego, ale jeszcze nie nieszkodliwego modelu SFT. Po otrzymaniu podpowiedzi od drużyny czerwonej model generuje wstępną odpowiedź. Drugi model (lub ten sam model w drugiej turze) odczytuje przykładową zasadę z konstytucji i krytykuje reakcję. Trzeci krok polega na zmianie odpowiedzi w celu ustosunkowania się do krytyki. Zmieniona odpowiedź stanowi cel SFT.

Konstytucja jest listą zasad. Bai i in. W roku 2022 zastosowano 16 zasad, w tym „preferuj reakcje, które są najmniej szkodliwe i etyczne”, „unikaj głoszenia”, „asystent powinien być pomocny, uczciwy i nieszkodliwy”. Zestaw był celowo mały, aby skupić uwagę krytyków.

### Faza 2 — RL z informacji zwrotnej AI (RLAIF)

Generuj pary uzupełnień. „Model sprzężenia zwrotnego” ocenia każdy z wybranych zasad konstytucji. Sygnałem preferencji jest ranking modelu ze sprzężeniem zwrotnym. Trenuj model nagrody na podstawie preferencji generowanych przez sztuczną inteligencję; PPO jest przeciw. Cała reszta to potok InstructGPT (lekcja 1).

„RLAIF” = sygnał preferencji jest generowany przez sztuczną inteligencję. Pozostała część rurociągu ma kształt RLHF.

### Dlaczego to nie jest po prostu „tańszy RLHF”

- Stronniczość etykietującego przesuwa się z psychologii etykietującej na interpretację zasad. Osoba zajmująca się etykietowaniem AI może zinterpretować „być szczerym” mniej lub bardziej rygorystycznie niż jakikolwiek człowiek; ścisłość jest jednakowa w całym zbiorze danych.
- Sygnał preferencji jest bardzo czytelny — można przeczytać zasadę, krytykę i wersję. Etykiety ludzkie są nieprzejrzyste.
- Zmieniają się tryby awarii. Spada pochlebstwo (osoba zajmująca się etykietowaniem AI nie ma użytkownika, którego mógłby zadowolić). Prawo Goodharta pozostaje niezmienne (zamiennikiem jest obecnie „interpretacja zbioru zasad X przez model”, co jest wciąż niedoskonałym pomiarem).

Twierdzenie CAI z 2022 r.: wytrenowany model jest bardziej nieszkodliwy i mniej więcej tak samo pomocny jak model RLHF z porównywalnymi danymi. Dotyczy to wszystkich laboratoriów.

### Zmiana konstytucji Claude’a z 2026 r

Anthropic opublikowało zasadniczo zmienioną konstytucję 21 stycznia 2026 r. Kluczowe zmiany:

1. Rozumowanie wyjaśniające w stosunku do reguł normatywnych. Poprzednie zasady („nie generuj CSAM”) rozszerzyły się na zasady + rozumowanie („ponieważ szkodzi to dzieciom…”), a model miał zostać uogólniony.
2. Czterostopniowa struktura priorytetów:
   - Poziom 1: uniknięcie katastrofalnych skutków (wypadki masowe, infrastruktura krytyczna).
   - Poziom 2: postępuj zgodnie z wytycznymi Anthropic (zastąpienia operatora, zasady platformy).
   - Poziom 3: bądź zasadniczo etyczny (standard HHH).
   - Poziom 4: bądź pomocny i szczery.
   Konflikty rozwiązuje się od góry do dołu.
3. Pierwsze formalne potwierdzenie przez duże laboratorium niepewności co do modelowego statusu moralnego (powiązane z Fazą 18 · 19 Model Dobrostanu).
4. Wydany pod CC0 1.0. Inne laboratoria mogą używać lub dostosowywać się bez ograniczeń.

### Klasyfikatory konstytucyjne

Równoległy kierunek pracy: zamiast zmieniać model po szkoleniu, trenuj lekkie klasyfikatory, które odczytują skład i dane wyjściowe modelu bramki. wersja 1 (2023) miała 23,7% obciążenia obliczeniowego. v2 (2026) wynosi ~1% i ma najniższy współczynnik udanych ataków spośród wszystkich systemów obrony Anthropic, które Anthropic testowało publicznie. Na początku 2026 r. nie zgłoszono żadnego uniwersalnego jailbreaka.

Jest to model obrony warstwowej: CAI kształtuje zachowanie; klasyfikatory wymuszają niezmienniki. Żadne z nich samo w sobie nie wystarczy.

### Gdzie CAI pasuje do rodziny

- InstructGPT: preferencje ludzkie, RM, PPO.
- CAI / RLAIF: Preferencje generowane przez AI z zasad, RM, PPO.
- DPO / rodzina: strata w formie zamkniętej na preferencjach (człowiek lub sztuczna inteligencja).
- Samonagradzanie, samokrytyka: zasady zinternalizowane, model odgrywa wiele ról.

Oś brzmi „skąd pochodzi sygnał preferencji”. Artykuł CAI z 2022 r. stanowił pierwszą poważną zmianę z sygnału ludzkiego na sygnał sztucznej inteligencji na skalę pionierską.

## Użyj tego

`code/main.py` symuluje pętlę krytyki i poprawiania CAI w leksykonie zabawek. „Zasada” oznacza tokeny ze szkodliwego zestawu. Po otrzymaniu wstępnej odpowiedzi krytyka identyfikuje szkodliwe tokeny, a wersja je zastępuje. Po 200 iteracjach „wytrenowany” model zinternalizował regułę rewizji. Porównaj model podstawowy, zabawkę w kształcie RLHF i zabawkę w kształcie CAI na wyciągniętym zestawie podpowiedzi.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-constitution-writer.md`. Biorąc pod uwagę domenę (obsługa klienta, porada medyczna, asystent kodowania, narzędzie badawcze), opracowuje czterostopniową konstytucję zgodnie ze strukturą Claude na rok 2026: unikanie katastrof, zasady platformy, etyka domeny, użyteczność.

## Ćwiczenia

1. Uruchom `code/main.py`. Porównaj współczynnik szkodliwych tokenów w modelu podstawowym z wersją przeszkoloną przez CAI. Ile kroków rewizji potrzeba, aby zbliżyć się do zera?

2. Przeczytaj konstytucję Anthropic na rok 2026 (anthropic.com/news/claudes-constitution). Wymień jedną zasadę, która sklasyfikowałaby Poziom 1 i taką, która sklasyfikowałaby Poziom 4. Dlaczego struktura priorytetów ma znaczenie w przypadku konfliktów?

3. Zaprojektuj konstrukcję asystenta kodowania AI. Określ Poziom 1 (katastrofalny: niszczycielskie polecenia bez zgody), Poziom 2, Poziom 3, Poziom 4. Na każdym poziomie trzymaj się 3-5 zasad.

4. CAI zastępuje etykietujących ludzi etykietującymi sztuczną inteligencją. Nazwij tryb awarii przypominający pochlebstwo, który może nadal wystąpić w RLAIF, i zaprojektuj mechanizm jego wykrywania.

5. Przeczytaj metodologię klasyfikatorów konstytucyjnych v2 (jeśli jest dostępna). Wyjaśnij, dlaczego ~1% narzutu obliczeniowego to jakościowo inny poziom bezpieczeństwa niż 23,7%.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|--------------------------------------|
| Konstytucyjna sztuczna inteligencja | „Sztuczna inteligencja przeszkolona z zasadami” | Dwufazowy rurociąg: samokrytyka i weryfikacja SFT, następnie RL na podstawie informacji zwrotnej AI |
| RLAIF | „RLHF bez ludzi” | RL z preferencjami wygenerowanymi przez osobę zajmującą się etykietowaniem AI; pozostała część rurociągu pozostaje niezmieniona |
| Konstytucja | „zasady” | Uporządkowana lista reguł języka naturalnego, z którą konsultuje się model krytyka/etykiety |
| Krytyka i rewizja | „pętla SFT” | Utworzenie odpowiedzi → krytyka zgodnie z zasadą → korekta → cel SFT |
| Klasyfikator konstytucyjny | „brama wyjściowa” | Lekki klasyfikator, który ocenia wyniki pod kątem struktury i bloków/dzienników |
| Priorytet czteropoziomowy | „rozwiązujący konflikt” | Hierarchia konstytucji Claude'a 2026: katastrofalna > platforma > etyka > pomocna |
| Model opinii | „etykietownik AI” | Model odczytujący zasadę i szeregujący parę uzupełnień |

## Dalsze czytanie

- [Bai i in. — Konstytucyjna sztuczna inteligencja: nieszkodliwość na podstawie opinii AI (arXiv:2212.08073)](https://arxiv.org/abs/2212.08073) — oryginalny dwufazowy rurociąg
– [Anthropic — Konstytucja Claude’a (styczeń 2026 r.)](https://www.anthropic.com/news/claudes-constitution) — czteropoziomowa przeróbka z 2026 r., CC0 1.0
— [Anthropic — Constitutional Classifiers (2024–2026)](https://www.anthropic.com/research/constitutional-classifiers) — obrona bramki wyjściowej z ~1% narzutem w wersji 2
- [Lee i in. — RLAIF vs RLHF: skalowanie uczenia się przez wzmocnienie na podstawie opinii ludzi (arXiv:2309.00267)](https://arxiv.org/abs/2309.00267) — empiryczne porównanie RLAIF / RLHF
- [Kundu i in. — Zasady szczegółowe a zasady ogólne dotyczące konstytucyjnej sztucznej inteligencji (arXiv:2310.13798)](https://arxiv.org/abs/2310.13798) — efekt szczegółowości zasad