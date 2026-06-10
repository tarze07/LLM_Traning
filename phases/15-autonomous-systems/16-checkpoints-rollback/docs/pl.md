# Punkty kontrolne i wycofanie

> Każde przejście stanu wykresu utrzymuje się. Kiedy pracownik ulegnie awarii, jego dzierżawa wygasa i inny pracownik rozpoczyna pracę w ostatnim punkcie kontrolnym. Trwałe obiekty Cloudflare utrzymują stan przez wiele godzin lub tygodni. Zaproponuj, a następnie zatwierdź (Lekcja 15) definiuje plan wycofywania dla każdej akcji. Weryfikacja po działaniu zamyka pętlę. Artykuł 14 unijnej ustawy o sztucznej inteligencji nakłada obowiązek skutecznego nadzoru człowieka w przypadku systemów wysokiego ryzyka – w praktyce oznacza to, że w punktach kontrolnych musi istnieć możliwość sprawdzania, należy przeprowadzać próby wycofywania zmian, a ścieżka audytu musi przetrwać wdrożenie. Tryb ostrej awarii: bez kluczy idempotencji i sprawdzania warunków wstępnych, ponowna próba po przejściowym niepowodzeniu może spowodować podwójne wykonanie już zatwierdzonej akcji. Weryfikacja po działaniu jest tym, co go wyłapuje.

**Typ:** Ucz się
**Języki:** Python (stdlib, punkt kontrolny i maszyna stanu wycofywania)
**Wymagania wstępne:** Faza 15 · 12 (Trwałe wykonanie), Faza 15 · 15 (Zaproponuj, a następnie zatwierdź)
**Czas:** ~60 minut

## Problem

Trwałe wykonanie (Lekcja 12) umożliwia wznowienie działania agenta, który uległ awarii. Opcja „Zaproponuj, a następnie zatwierdź” (Lekcja 15) umożliwia audyt zatwierdzonego działania. Łączy je ta lekcja: co się stanie, gdy zatwierdzona akcja zostanie wykonana częściowo, ulegnie awarii i zostanie wznowiona? Kiedy uruchamiane jest wycofywanie zmian i wobec jakiego stanu?

Prawdziwe systemy łączą to inaczej:

- **LangGraph** punkty kontrolne przy każdym przejściu stanu wykresu do PostgreSQL. W przypadku awarii pracownika dzierżawa zostaje zwolniona, a inny pracownik wznawia pracę w najnowszym punkcie kontrolnym. Przepływy pracy wstrzymują się w dniu `interrupt()`, który sam w sobie jest kontynuowany.
- **Trwałe obiekty Cloudflare** utrzymują stan poszczególnych kluczy przez wiele godzin lub tygodni. Umieść obliczenia w pamięci dla zatwierdzonego działania.
- **Microsoft Agent Framework** udostępnia elementy podstawowe `Checkpoint` w interfejsie API przepływu pracy; powtórka plus idempotencja obejmuje ponowne próby.

W każdym przypadku kombinacja, która faktycznie działa, to: klucz idempotencji (zapobiega podwójnemu wykonaniu) + sprawdzenie warunków wstępnych (stan jest nadal tym, co zatwierdziliśmy) + weryfikacja po akcji (efekt uboczny faktycznie wystąpił) + wycofywanie w przypadku niepowodzenia weryfikacji.

## Koncepcja

### Każde przejście trwa

Przejście do stanu wykresu to dowolny krok, który przenosi przepływ pracy z jednego nazwanego stanu do drugiego. Naiwne implementacje utrzymują się tylko w określonych punktach zatwierdzeń; wdrożenia produkcyjne utrzymują się przy każdym przejściu. Koszt (kilka dodatkowych zapisów) jest niewielki w porównaniu ze wzrostem niezawodności (powtórka ląduje w dowolnym miejscu, odzyskiwanie dzierżawy jest precyzyjne).

### Odzyskiwanie leasingu

W przypadku awarii procesu roboczego przepływ pracy nie zostaje utracony; dzierżawa (krótkotrwałe roszczenie, że ten pracownik wykonuje ten przebieg) po prostu wygasa. Inny pracownik wybiera najnowszy punkt kontrolny i wznawia pracę. Mechanizm dzierżawy pozwala systemom produkcyjnym przetrwać wdrażanie w trybie ciągłym bez utraty pracy wykonywanej w trakcie lotu.

### Idempotencja plus warunki wstępne

Sama idempotencja nie wystarczy. Rozważmy: przepływ pracy został zatwierdzony do „przeniesienia $100 from A to B when balance > $1000”. Przepływ pracy zostaje zatwierdzony, ulega awarii w połowie wykonywania i zostaje wznowiony. Jeśli zaznaczony zostanie tylko klucz idempotentności i wykonanie zostanie wznowione, transfer zostanie uruchomiony raz (poprawnie). Należy jednak pamiętać, że między awarią a wznowieniem saldo A spada do 500 USD w wyniku innego przepływu pracy. Kontrola idempotencji nadal przebiega pomyślnie; warunek wstępny nie. Bez sprawdzenia warunków wstępnych wysyłamy debet.

Każde wynikające z tego działanie wymaga obu:

- **Klucz idempotencji**: zapobiega podwójnemu wykonaniu.
- **Kontrola warunków wstępnych**: potwierdza, że ​​stan jest nadal zgodny z zatwierdzonym.

### Weryfikacja po akcji

„Narzędzie zwróciło 200” nie jest weryfikacją. Prawdziwa weryfikacja ponownie odczytuje stan docelowy i potwierdza, że ​​efekt uboczny faktycznie wystąpił. Wzory:

- Aktualizacja bazy danych: `UPDATE ... RETURNING *`, następnie potwierdź, że zwrócony wiersz odpowiada zamierzonemu stanowi.
- Wysyłanie wiadomości e-mail: po przesłaniu sprawdź folder Wysłane pod kątem identyfikatora wiadomości.
- Zapis pliku: przeczytaj plik i zahaszuj go.
- Wywołanie API: kontynuacja `GET` na zasobie docelowym.

Jeśli weryfikacja nie powiedzie się, przepływ pracy jest w znanym złym stanie. Włącza się funkcja Rollback.

### Plany wycofania

Każde kolejne działanie w trybie „zaproponuj, a następnie zatwierdź” (lekcja 15) niesie ze sobą plan wycofania. Typy:

- **Wycofanie w paśmie**: bezpośrednie odwrócenie efektu ubocznego (`DELETE` po `INSERT`, `Send-correction-email` po wysłaniu).
- **Transakcja kompensacyjna**: nowa akcja neutralizująca oryginał (standardowy wzór SAGA).
- **Wycofywanie poza pasmem**: zaalarmuj człowieka, wstrzymaj przepływ pracy, pozostaw zły stan do zbadania.

We wniosku należy podać nazwę wycofania bez operacji („nie możemy tego cofnąć”). Akcje bez wycofywania wymagają silniejszego HITL w momencie zatwierdzenia (Lekcja 15: wyzwanie i odpowiedź).

### Ustawa UE o sztucznej inteligencji, art. 14, czytanie operacyjne

Artykuł 14 wymaga „skutecznego nadzoru człowieka” w przypadku systemów wysokiego ryzyka. Z operacyjnego punktu widzenia realizatorzy odczytują to jako:

- Punkty kontrolne mogą być sprawdzane przez audytora.
- Wycofywania są ćwiczone (przetestowane od początku do końca przynajmniej raz).
— Ścieżka audytu przetrwa wdrożenie (zaplecze punktu kontrolnego nie jest tymczasowe).
- Nieudane weryfikacje są sygnalizowane, a nie dyskretnie rejestrowane.

Przepływ pracy, który ulega awarii w połowie zatwierdzenia, wznawia i kończy efekt uboczny bez ścieżki weryfikacji i wycofania, nie przechodzi testu zgodnie z art. 14.

### Tryb ostrej awarii: podwójne wykonanie

Najczęstszy incydent produkcyjny w tej przestrzeni:

1. Akcja zatwierdzona, klucz idempotencji k.
2. Rozpoczyna się zatwierdzanie, wykonuje się, zwraca 200.
3. Przepływ pracy ulega awarii przed utrzymaniem statusu „zaangażowany”.
4. Wznowienie przepływu pracy; widzi „zatwierdzony, ale niezatwierdzony”; wykonuje ponownie.
5. Efekt uboczny uruchamia się dwukrotnie.

Środki zaradcze: utrzymuj zamiar „w locie” przed wykonaniem, wykonaj za pomocą klucza idempotencji, a następnie oznacz jako „zatwierdzony” dopiero po pomyślnej weryfikacji po akcji. Jeśli akcja zostanie uruchomiona, a zapis statusu nie powiedzie się, należy sprawdzić i (jeśli to konieczne) uruchomić ponownie. Jeśli zapis stanu się powiedzie, a akcja nie powiedzie się, weryfikujesz i uruchamiasz dokładnie raz za pośrednictwem ścieżki odzyskiwania.

## Użyj tego

`code/main.py` implementuje przepływ pracy z punktami kontrolnymi z idempotencją, warunkami wstępnymi, weryfikacją i wycofywaniem. Sterownik symuluje cztery scenariusze: czyste uruchomienie, ponowna próba po awarii (przechwycenie idempotencji), niepowodzenie warunku wstępnego (przepływ pracy zostaje przerwany bez uruchomienia), niepowodzenie weryfikacji (uruchamia się wycofanie).

## Wyślij to

`outputs/skill-rollback-rehearsal.md` projektuje test wycofywania zmian dla proponowanego przepływu pracy i sprawdza zaplecze punktu kontrolnego pod kątem trwałości ścieżki audytu.

## Ćwiczenia

1. Uruchom `code/main.py`. Sprawdź cztery scenariusze. W przypadku awarii podczas zatwierdzenia potwierdź, że akcja zostanie uruchomiona dokładnie raz w przypadku kolejnych prób.

2. Zmodyfikuj wzorzec „najpierw zaznacz jako wykonane, a potem zrób to”, tak aby zapis stanu był uruchamiany po akcji. Uruchom ponownie scenariusz awarii. Zmierz liczbę zduplikowanych działań.

3. Zaprojektuj plan wycofywania dla konkretnego działania produkcyjnego (np. „opublikuj na kanale Slack”). Klasyfikuj jako wewnątrzpasmowe, kompensacyjne i pozapasmowe. Uzasadnij wybór.

4. Wybierz jeden schemat działania, jaki znasz. Zidentyfikuj każdą zmianę stanu. Oznacz każdy wymóg trwałości (utrzymuj się / nie utrzymuj się). Policz te, których obecnie nie utrzymujesz.

5. Przećwiczony test wycofywania zmian: zaprojektuj kompleksowy test, który uruchamia rzeczywisty przepływ pracy, powoduje jego awarię i potwierdza uruchomienie ścieżki wycofywania. Co potwierdza test?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|---|---|---|
| Punkt kontrolny | "Zapisz punkt" | Każde przejście stanu wykresu utrzymuje się w trwałym magazynie |
| Wynajem | „Roszczenie pracownika” | Krótkotrwałe twierdzenie, że pracownik wykonuje przebieg; wygasa w przypadku awarii |
| Warunek | „Brama Państwa” | Twierdzenie, że stan jest w dalszym ciągu zgodny z zatwierdzonym działaniem |
| Weryfikacja po akcji | „Przeczytaj ponownie czek” | Potwierdź, że efekt uboczny rzeczywiście wystąpił w systemie docelowym |
| Wycofywanie w paśmie | „Bezpośrednie cofnięcie” | Odwróć efekt uboczny za pomocą operacji odwrotnej |
| Transakcja kompensacyjna | „SAGA cofnij” | Nowa akcja neutralizująca oryginał |
| Oznacz jako pierwsze | „Kolejność zapisu stanu” | Utrzymaj status zatwierdzenia przed powrotem z zatwierdzenia |
| Artykuł 14 | „Nadzór ludzki w ramach unijnej ustawy o sztucznej inteligencji” | Operacyjne: punkty kontrolne, do których można wysyłać zapytania, przećwiczone wycofywanie, ścieżka audytowalna |

## Dalsze czytanie

- [Microsoft Agent Framework — Checkpointing i HITL](https://learn.microsoft.com/en-us/agent-framework/workflows/human-in-the-loop) — prymitywy punktów kontrolnych i odzyskiwanie dzierżawy.
- [Agenci Cloudflare — Człowiek w pętli](https://developers.cloudflare.com/agents/concepts/human-in-the-loop/) — Trwałe obiekty jako substrat stanu.
– [Unijna ustawa o sztucznej inteligencji – art. 14: Nadzór człowieka](https://artificialintelligenceact.eu/article/14/) – podstawa regulacyjna.
- [Anthropic — Pomiar autonomii agenta w praktyce](https://www.anthropic.com/research/measuring-agent-autonomy) — ramy niezawodności dla długoterminowych przepływów pracy.
- [Anthropic — Claude Code Agent SDK: pętla agenta](https://code.claude.com/docs/en/agent-sdk/agent-loop) — kształt przepływu pracy dla procedur Claude Code.