# STAR, V-STAR, Quiet-STAR — Rozumowanie samouka

> Najmniejsza możliwa pętla samodoskonalenia znajduje się w uzasadnieniu. Model generuje łańcuch myślowy, zatrzymuje te, które prowadzą do prawidłowych odpowiedzi, i dostraja je. Czyli STAR. V-STAR dodaje weryfikator, dzięki czemu wybór czasu wnioskowania jest lepszy. Quiet-STAR przedstawia uzasadnienie w każdym tonie. Wszystkie trzy działają. Żadne z nich nie jest magiczne — pętla zachowuje każdy skrót, który trafił do właściwej odpowiedzi.

**Typ:** Ucz się
**Języki:** Python (stdlib, symulator pętli bootstrap)
**Wymagania wstępne:** Faza 13 · 01-03 (Rozumowanie i CoT), Faza 15 · 01 (kadrowanie długoterminowe)
**Czas:** ~60 minut

## Problem

Prostym sposobem nauczenia modelu rozumowania jest zebranie zapisanych przez człowieka śladów rozumowania. Jest to kosztowne, powolne i ograniczone ilością wysokiej jakości łańcucha myślowego, jaki ludzie są skłonni napisać.

STaR (Self-Taught Reasoner, Zelikman i in., 2022) pyta: co się stanie, jeśli model napisze własne uzasadnienia i porówna je ze znanymi odpowiedziami? Pętla to:

1. Wypróbuj ślad rozumowania i odpowiedź.
2. Jeśli ostateczna odpowiedź jest prawidłowa, zachowaj ślad.
3. Dostosuj zachowane ślady.
4. Powtórz.

To działa. Zarówno GSM8K, jak i CommonsenseQA uległy poprawie bez nowych adnotacji ludzkich. Ale pętla ma wbudowaną tendencję: wszelkie uzasadnienie, które dało właściwą odpowiedź, zostaje zachowane, niezależnie od tego, czy samo rozumowanie było rozsądne. V-STAR (Hosseini i in., 2024) łata to za pomocą wyuczonego weryfikatora; Quiet-STAR (Zelikman i in., 2024) uogólnia tę koncepcję na wewnętrzne przesłanki dotyczące poszczególnych tokenów.

## Koncepcja

### STAR: bootstrap tego, co zadziałało

Zacznij od modelu podstawowego z pewną słabą zdolnością rozumowania. W przypadku każdego problemu szkoleniowego podaj uzasadnienie i odpowiedź. Jeśli odpowiedź pasuje do etykiety, zachowaj potrójną wartość (problem, uzasadnienie, odpowiedź). Dopracuj model na przechowywanym zestawie. Powtarzać.

Jeden zwrot ma znaczenie. Jeśli model nigdy nie będzie w stanie poprawnie rozwiązać problemu, pętla nie będzie mogła się na nim uczyć. STaR dodaje **racjonalizację**: w przypadku problemów, w których model zawodzi, wprowadź poprawną odpowiedź jako wskazówkę i ponownie poproś model o przedstawienie uzasadnienia, które do tego prowadzi. Do zbioru uczącego dodawane są zracjonalizowane przesłanki.

Wynik w oryginalnej pracy (Zelikman i in., 2022): podstawowy model GPT-J poprawił się na GSM8K z 5,8% do 10,7% poprzez powtarzane rundy STaR z racjonalizacją — bezwzględnie około 5 punktów procentowych. W CommonsenseQA wyszkolony STaR GPT-J 6B osiągnął 72,5%, co jest porównywalne z dostrojonym GPT-3 175B (~73%) — około 30 razy większym modelem wytrenowanym na podstawie ręcznie opatrzonych komentarzy.

### V-STaR: przeszkol weryfikatora z DPO

STAR odrzuca błędne uzasadnienia. Hosseini i in. (2024) zaobserwowali, że są to również dane: każda para (uzasadnienie „czy to jest poprawne”) może wyszkolić weryfikatora. Używają bezpośredniej optymalizacji preferencji zarówno w przypadku poprawnych, jak i niepoprawnych rozwiązań, aby zbudować ranking. W momencie wnioskowania pobierz N uzasadnień i wybierz najlepszy wybór weryfikatora.

Zgłaszana delta: +4 do +17 punktów procentowych w porównaniu z wcześniejszymi wartościami bazowymi samodoskonalenia w GSM8K i MATH, przy czym większość zysków wynika z wykorzystania weryfikatora do wyboru czasu wnioskowania, a nie do dodatkowego dostrajania generatora.

### Quiet-STAR: wewnętrzne uzasadnienie dotyczące każdego tokenu

Zelikmana i in. (2024) zapytali: co się stanie, jeśli model nauczy się generować krótkie wewnętrzne uzasadnienie w każdej pozycji symbolicznej, a nie tylko między problemem a odpowiedzią? Quiet-STAR szkoli model tak, aby emitował ukrytą „myśl” przed każdym przewidywanym tokenem, a następnie łączy przewidywanie uwzględniające myśli z przewidywaniem bazowym na podstawie wyuczonej wagi.

Wynik: Mistral 7B uzyskał absolutną, zerową poprawę w przypadku GSM8K z 5,9% do 10,9% i CommonsenseQA z 36,3% do 47,2% bez dostrajania specyficznego dla zadania. Model nauczył się, „kiedy myśleć” — twarde tokeny uzyskują dłuższe wewnętrzne uzasadnienia; łatwe nie dostają prawie żadnego.

### Dlaczego wszyscy trzej tak samo troszczą się o bezpieczeństwo

Wszystkie trzy metody wykorzystują ostateczną odpowiedź jako sygnał gradientu. Uzasadnienie, które prowadzi do właściwej odpowiedzi poprzez błędne rozumowanie – wykorzystując skrót, zgadując lub używając nieuogólniającego wzorca – zostaje pozytywnie wzmocnione. W przypadku problemów z dystrybucją skrót działa. W przypadku problemów z dystrybucją przerywa cicho.

Weryfikator V-STAR łagodzi skutki, ucząc się oceniania uzasadnień, ale weryfikator jest szkolony w oparciu o ten sam zestaw etykiet. Może nauczyć się przedkładać dobrze sformatowane błędne rozumowanie nad szczerą niepewność. Bezpieczniejszy projekt polega na połączeniu danych w stylu STaR z (a) modelami nagród nadzorowanymi przez proces (nagradzającymi kroki pośrednie, a nie tylko odpowiedzi) i (b) wyczekiwaną oceną OOD, która łamie proste skróty.

### Porównanie

| Metoda | Sygnał treningowy | Koszt wnioskowania | Marnowanie danych | Znany tryb awarii |
|---|---|---|---|---|
| GWIAZDA | zachowaj (uzasadnienie, odpowiedź), jeśli jest poprawne | 1x | odrzuca wszystkie błędne uzasadnienia | uzasadnienie skrótów |
| GWIAZDA + racjonalizacja | powyżej + podpowiedź poprawnych odpowiedzi | 1x | mniej | zracjonalizowane przesłanki mogą być nieprawdopodobne |
| V-GWIAZDA | STaR + weryfikator DPO z obu klas | Nx (najlepszy z N) | minimalne | weryfikator może wzmocnić pewność, że się mylisz |
| Cicha Gwiazda | uzasadnienie na token + waga mieszania | 1,5-3x | minimalne | nadal gradient warunkowy odpowiedzi |

### Gdzie to się znajduje na stosie na rok 2026

STAR jest stary. Jednak wzór ten pojawi się ponownie wszędzie w latach 2025–2026. RL w weryfikowalnych problemach matematycznych (DeepSeek-R1, Kimi-k1.5, o1) to sygnał gradientowy STAR z uwarunkowaną odpowiedzią, przeskalowany w górę. Modele nagród procesowych (Lightman i in., 2023; „Sprawdźmy krok po kroku” OpenAI) stanowią alternatywę nadzorowaną przez proces. AlphaEvolve (lekcja 3) to STAR oznaczający kod, z ewaluatorem programu zamiast etykiety. Maszyna Darwina Godela (lekcja 4) jest gwiazdą dla samego rusztowania agenta.

Zrozumienie STAR sprawia, że ​​wszystkie z nich klikają. Jest to minimalna realna pętla samodoskonalenia.

## Użyj tego

`code/main.py` uruchamia symulowaną pętlę STAR w zabawkowym zadaniu arytmetycznym. Możesz obejrzeć:

- Jak dokładność wzrasta w przypadku rund ładowania początkowego.
- Jak wkradają się skróty: symulator zawiera „leniwą” klasę uzasadnienia, która w 40% przypadków uzyskuje właściwą odpowiedź, ale źle generalizuje. Obserwuj, czy STAR je trzyma.
- W jaki sposób weryfikator (w stylu V-STAR) pomaga w wnioskowaniu, ale nie może w pełni oczyścić skrótów wprowadzonych podczas szkolenia.

## Wyślij to

`outputs/skill-star-loop-reviewer.md` pomaga Ci przeprowadzić audyt proponowanego potoku rozumowania samouka, zanim zaczniesz go szkolić.

## Ćwiczenia

1. Uruchom symulator. Ustaw częstotliwość skrótu na zero, a następnie na 0,4. Jak bardzo końcowa dokładność różni się między dwoma seriami, mimo że w obu seriach osiągnięto > 90% rozkładu treningowego?

2. Dodaj wyciągnięty test OOD do symulatora. Narysuj problemy z innej dystrybucji i oceń model bootstrap zarówno w zbiorach dystrybucyjnych, jak i OOD. Oblicz różnicę.

3. Przeczytaj artykuł Quiet-STAR (arXiv:2403.09629), część 3. Wyjaśnij w trzech zdaniach symbol „końca myśli” i głowicę mieszającą.

4. Porównaj filtr typu „zachowaj poprawność” STAR z alternatywą nadzorowaną przez proces, która nagradza każdy uzasadniony krok niezależnie. Zidentyfikuj różnicę w kosztach etykietowania i prawdopodobną różnicę w jakości.

5. Zaprojektuj jedną ewaluację, która uwzględniałaby uzasadnienie skrótów we wdrożonym modelu. Nie musi być idealne — musi łamać najprostsze skróty, które wzmocniłaby pętla STAR.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|---|---|---|
| GWIAZDA | „Rozumujący samouk” | Dostosuj wygenerowane przez model uzasadnienia, które dają prawidłowe odpowiedzi; powtórz |
| Racjonalizacja | „Podpowiedziana ponowna próba” | Wpisz poprawną odpowiedź i ponownie poproś o uzasadnienie problemów, które zawodzą w modelu podstawowym |
| V-GWIAZDA | „Gwiazda Weryfikatora” | DPO – przeszkol weryfikatora w zakresie zarówno prawidłowych, jak i niepoprawnych uzasadnień, użyj go do wyboru czasu wnioskowania |
| Cicha Gwiazda | „Uzasadnienia dotyczące poszczególnych tokenów” | Generuj ukryte myśli na każdej pozycji żetonu; wymieszać z prognozą bazową |
| Gradient warunkowy odpowiedzi | „Sygnał oparty na wynikach” | Pętla treningowa nagradza ostateczne odpowiedzi, a nie kroki rozumowania |
| Model nagrody procesowej | „Weryfikator krokowy” | Model nagrody trenowany pod kątem poprawności poszczególnych kroków, a nie wyniku — kontrastuje ze STAR |
| Uzasadnienie skrótu | „Właściwa odpowiedź, błędne rozumowanie” | Uzasadnienie, które dociera do etykiety poprzez nieuogólniający wzorzec; STAR trzyma te |

## Dalsze czytanie

- [Zelikman i in. (2022). STAR: Bootstrapping Reasoning With Reasoning](https://arxiv.org/abs/2203.14465) — artykuł oryginalny.
- [Hosseini i in. (2024). V-STAR: Weryfikatory szkoleniowe dla samouków](https://arxiv.org/abs/2402.06457) — dodaje weryfikator DPO do wyboru czasu wnioskowania.
- [Zelikman i in. (2024). Quiet-STAR: Modele językowe mogą nauczyć się myśleć przed mówieniem](https://arxiv.org/abs/2403.09629) — wewnętrzne uzasadnienie poszczególnych tokenów.
- [Lightman i in. (2023). Sprawdźmy krok po kroku](https://arxiv.org/abs/2305.20050) — modele nagrody procesu, alternatywny sygnał gradientu.
- [Artykuł DeepSeek-R1 (arXiv:2501.12948)](https://arxiv.org/abs/2501.12948) — RL na temat sprawdzalnych zadań, STaR przeskalowany do szkolenia pionierskiego.