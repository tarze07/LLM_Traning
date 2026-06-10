# Punkty kontrolne i wycofanie

> Każda zmiana stanu w grafie przepływu pracy jest trwale zapisywana. W przypadku awarii procesu roboczego (worker) jego dzierżawa (lease) wygasa, a kolejne zadanie podejmuje inny worker, startując od ostatniego zapisanego punktu kontrolnego (checkpoint). Systemy takie jak Cloudflare Durable Objects pozwalają na utrzymanie tego stanu przez wiele godzin, a nawet tygodni. Wzorzec „zaproponuj, a następnie zatwierdź” (Lekcja 15) wymaga zdefiniowania planu wycofania zmian (rollback plan) dla każdego działania, a weryfikacja po wykonaniu operacji zamyka pętlę kontrolną. Artykuł 14 unijnej ustawy o sztucznej inteligencji (AI Act) nakłada wymóg efektywnego nadzoru ludzkiego nad systemami wysokiego ryzyka. W wymiarze technicznym oznacza to konieczność umożliwienia audytu punktów kontrolnych, regularnego testowania procedur wycofywania zmian oraz zapewnienia odporności ścieżki audytu na aktualizacje oprogramowania. Najpoważniejszym scenariuszem awarii jest podwójne wykonanie operacji: bez kluczy idempotencji i weryfikacji warunków wstępnych ponowne uruchomienie procesu po awarii sieci może wywołać zatwierdzoną już akcję powtórnie. Kluczowym mechanizmem obronnym chroniącym przed tym zagrożeniem jest weryfikacja stanu po wykonaniu działania.

**Typ:** Ucz się
**Języki:** Python (stdlib, punkt kontrolny i maszyna stanu wycofywania)
**Wymagania wstępne:** Faza 15 · 12 (Trwałe wykonanie), Faza 15 · 15 (Zaproponuj, a następnie zatwierdź)
**Czas:** ~60 minut

## Problem

Trwałe wykonanie (Lekcja 12) umożliwia wznowienie pracy agenta po awarii, a wzorzec „zaproponuj, a następnie zatwierdź” (Lekcja 15) pozwala na weryfikację planowanych działań przed ich uruchomieniem. Niniejsza lekcja łączy te zagadnienia: co dzieje się, gdy zatwierdzona akcja zostanie wykonana tylko częściowo, proces ulegnie awarii, a następnie zostanie wznowiony? W jakich okolicznościach powinno zostać uruchomione wycofanie zmian (rollback) i do jakiego stanu należy wówczas przywrócić system?

Wiodące frameworki rozwiązują te wyzwania w następujący sposób:

- **LangGraph:** Zapisuje punkty kontrolne przy każdej zmianie stanu grafu bezpośrednio w bazie PostgreSQL. W przypadku awarii workera jego dzierżawa wygasa, a zadanie przejmuje inny worker, startując od najświeższego punktu kontrolnego. Procesy są wstrzymywane metodą `interrupt()`, która sama w sobie zapisuje aktualny stan.
- **Cloudflare Durable Objects:** Utrzymują stan powiązany z konkretnymi kluczami przez wiele godzin lub tygodni, umożliwiając wykonywanie operacji in-memory dla zatwierdzonych akcji.
- **Microsoft Agent Framework:** Udostępnia natywny obiekt `Checkpoint` w ramach API przepływu pracy. W połączeniu z idempotencją pozwala to na bezpieczną obsługę powtórzeń (replays).

Niezależnie od frameworka, w pełni bezpieczna sekwencja operacji wymaga połączenia: klucza idempotencji (ochrona przed zduplikowanym uruchomieniem) + weryfikacji warunków wstępnych (potwierdzenie, że stan systemu nie zmienił się od momentu autoryzacji) + weryfikacji po wykonaniu akcji (potwierdzenie sukcesu operacji) + procedury wycofania zmian (w przypadku negatywnej weryfikacji).

## Koncepcja

### Trwały zapis każdego kroku

Zmiana stanu grafu (transition) to dowolny krok przenoszący przepływ pracy z jednego nazwanego stanu do kolejnego. Uproszczone (naiwne) architektury zapisują stan systemu tylko w wybranych punktach krytycznych (np. przed autoryzacją); profesjonalne wdrożenia produkcyjne utrwalają stan przy każdym kroku. Koszt wydajnościowy (dodatkowe operacje zapisu do bazy) jest znikomy w porównaniu z ogromnym wzrostem niezawodności – pozwala to na precyzyjne odtwarzanie sesji od dowolnego punktu oraz stabilne przekazywanie dzierżaw procesów.

### Zarządzanie dzierżawami (Lease Recovery)

Gdy proces roboczy (worker) ulegnie awarii, zadanie nie zostaje utracone. Dzierżawa (lease – krótkoterminowa blokada zasobu potwierdzająca, że dany worker przetwarza sesję) wygasa. System automatycznie przydziela zadanie innemu workerowi, który wznawia pracę na bazie ostatniego punktu kontrolnego. Mechanizm dzierżaw pozwala środowiskom produkcyjnym na bezproblemowe przeprowadzanie wdrożeń (np. rolling updates) bez ryzyka przerwania aktywnych procesów w tle.

### Łączenie idempotencji z warunkami wstępnymi

Sama ochrona przed wielokrotnym wykonaniem (idempotencja) to za mało. Rozważmy przykład: przepływ pracy został zatwierdzony do wykonania operacji: „przelej 100 USD z konta A na B pod warunkiem, że saldo A > 1000 USD”. Zadanie zostaje autoryzowane, ale w trakcie pracy następuje awaria i restart procesu. Jeśli orkiestrator zweryfikuje jedynie klucz idempotencji i przejdzie to wykonania akcji, przelew zostanie zrealizowany poprawnie dokładnie raz. Co jednak, jeśli w krótkim czasie między awarią a restartem saldo konta A spadło do 500 USD z powodu innej, niezależnej transakcji? Weryfikacja idempotencji przebiegnie pomyślnie, ale warunek wstępny (saldo > 1000 USD) nie zostanie spełniony. Bez ponownej weryfikacji warunku wstępnego wykonamy nieautoryzowany debet.

Każde kluczowe działanie agenta musi być zabezpieczone dwutorowo:

- **Kluczem idempotencji:** Zapobiega powtórnemu uruchomieniu tej samej transakcji.
- **Weryfikacją warunków wstępnych (Pre-conditions):** Potwierdza, że stan systemu przed samym wykonaniem fizycznej operacji jest zgodny z założeniami autoryzacji.

### Weryfikacja po wykonaniu operacji (Post-action Verification)

Odebranie statusu sukcesu z API (np. kod statusu HTTP 200) nie stanowi rzeczywistej weryfikacji. Bezpieczny system musi odczytać docelowy stan zasobów i sprawdzić, czy oczekiwana modyfikacja doszła do skutku. Przykładowe techniki:

- **Modyfikacja bazy danych:** Użycie klauzuli `UPDATE ... RETURNING *` i weryfikacja, czy zwrócone rekordy są zgodne z oczekiwaniami.
- **Komunikacja e-mail:** Sprawdzenie bazy wysłanych wiadomości pod kątem obecności unikalnego identyfikatora wiadomości (Message ID).
- **Zapis plików:** Odczytanie utworzonego lub zmodyfikowanego pliku i weryfikacja jego sumy kontrolnej (hash).
- **Integracje API:** Wykonanie dodatkowego zapytania typu `GET` do docelowego zasobu w celu weryfikacji stanu.

Jeśli test weryfikacyjny wykaże błąd, system przechodzi w tryb awarii i automatycznie uruchamia procedurę wycofania zmian (rollback).

### Procedury wycofania zmian (Rollback Plans)

Zgodnie z wzorcem „zaproponuj, a następnie zatwierdź” (Lekcja 15), każda propozycja operacji wywołującej skutki uboczne musi zawierać zdefiniowany plan wycofania zmian. Wyróżniamy metody:

- **Wycofanie bezpośrednie (In-band Rollback):** Bezpośrednie odwrócenie operacji (np. zapytanie `DELETE` po wcześniejszym `INSERT` lub wysłanie e-maila korygującego).
- **Transakcja kompensacyjna (Compensating Transaction):** Uruchomienie nowej transakcji neutralizującej skutki pierwotnej operacji (klasyczny wzorzec SAGA).
- **Obsługa ręczna (Out-of-band Rollback):** Natychmiastowe wstrzymanie procesu, wygenerowanie powiadomienia dla administratora (HITL) i pozostawienie systemu do ręcznej analizy.

W dokumentacji projektu należy wprost oznaczyć operacje, których nie da się cofnąć (tzw. no-op rollback). Akcje niemożliwe do wycofania wymagają wdrożenia szczególnie restrykcyjnych procedur Challenge-Response przy autoryzacji przez człowieka (patrz Lekcja 15).

### Praktyczna interpretacja wymogów Artykułu 14 AI Act

Z technicznego punktu widzenia wymóg „efektywnego nadzoru ludzkiego” nad systemami wysokiego ryzyka (Artykuł 14 unijnej ustawy o AI) implikuje następujące zasady:

- Stan punktów kontrolnych (checkpoints) must być czytelny i możliwy do zbadania przez audytorów.
- Procedury wycofania zmian (rollbacks) muszą być regularnie testowane (przynajmniej raz od początku do końca).
- Ścieżka audytu musi być trwała i odporna na aktualizacje systemu (bazy danych dla punktów kontrolnych nie mogą być efemeryczne).
- Wszelkie błędy weryfikacji po wykonaniu akcji muszą generować jawne alarmy (nie mogą być jedynie zapisywane w ukrytych logach).

Dowolny proces, który ulega awarii w trakcie autoryzacji, a po restarcie dokończy operację bez weryfikacji i procedury wycofania zmian, nie spełnia kryteriów bezpieczeństwa wymaganych przez AI Act.

### Scenariusz awarii: Podwójne wykonanie operacji

Typowy błąd wdrożeniowy w systemach produkcyjnych przebiega następująco:

1. Akcja zostaje zatwierdzona z kluczem idempotencji `k`.
2. Operacja startuje, wykonuje się pomyślnie i zwraca status OK.
3. Silnik orkiestracji ulega awarii *przed* zapisaniem statusu „wykonano” (committed) w bazie danych.
4. Po restarcie proces widzi status „zatwierdzony, ale niewykonany” i uruchamia akcję ponownie.
5. Efekt uboczny zostaje wywołany dwukrotnie.

**Metoda obrony:** Zapisz status „w locie” (in-flight) przed uruchomieniem akcji, wykonaj operację z użyciem klucza idempotencji, a status „zakończono” (committed) zapisz w bazie *dopiero po* pomyślnej weryfikacji docelowego stanu systemu. Jeśli operacja zostanie wykonana, lecz zapis statusu końcowego się nie powiedzie, system weryfikuje faktyczny stan środowiska i w razie potrzeby koryguje dane. Jeśli zapis stanu w locie przebiegnie pomyślnie, ale samo wykonanie akcji zgłosi błąd, silnik uruchamia procedurę odzyskiwania stanu dokładnie raz.

## Przykład praktyczny

Skrypt `code/main.py` implementuje przepływ pracy z punktami kontrolnymi, idempotencją, weryfikacją warunków wstępnych oraz procedurą wycofania zmian. Kod testowy symuluje cztery scenariusze: standardowe uruchomienie, ponowne uruchomienie po awarii (wykrycie idempotencji), niepowodzenie weryfikacji warunku wstępnego (przerwanie sesji bez zmian) oraz niepowodzenie weryfikacji po akcji (automatyczne wycofanie zmian).

## Zadanie wdrożeniowe

Plik `outputs/skill-rollback-rehearsal.md` służy do zaprojektowania testu wycofywania zmian w proponowanym przepływie pracy oraz do weryfikacji bazy danych pod kątem odporności ścieżki audytu.

## Ćwiczenia

1. Uruchom skrypt `code/main.py`. Przeanalizuj cztery scenariusze testowe. Upewnij się, że w przypadku awarii podczas operacji zapisu akcja zostanie wykonana dokładnie raz przy próbach wznowienia sesji.
2. Zmodyfikuj kolejność operacji na: „najpierw zapisz stan jako zakończony, a potem wykonaj akcję”. Uruchom scenariusz awarii i zaobserwuj konsekwencje dla spójności danych.
3. Zaprojektuj procedurę wycofania zmian dla konkretnej operacji produkcyjnej (np. „publikacja komunikatu na kanale Slack”). Sklasyfikuj kroki jako bezpośrednie (in-band), kompensacyjne oraz manualne. Uzasadnij wybór strategii.
4. Wybierz znany przepływ pracy w swoim projekcie. Zidentyfikuj każdą zmianę stanu i okreśł wymóg trwałości (czy stan musi być zapisany trwale [tak/nie]). Wskaż kroki, które obecnie nie są prawidłowo utwalane.
5. Zaprojektuj scenariusz testu wycofywania zmian (Rollback Rehearsal): przygotuj koncepcję testu typu end-to-end, który uruchamia przepływ pracy, celowo wywołuje błąd w trakcie zapisu i weryfikuje automatyczne uruchomienie procedur wycofania. Określ, jakie warunki sukcesu musi spełnić ten test.

## Kluczowe terminy

| Termin | Co mówią potocznie | Co to dokładnie oznacza |
|---|---|---|
| Punkt kontrolny (Checkpoint) | „Punkt zapisu” | Trwałe zapisanie stanu grafu przepływu pracy w bazie danych |
| Dzierżawa (Lease) | „Blokada workera” | Krótkoterminowa blokada sesji przypisana to konkretnego workera; wygasa po awarii |
| Warunek wstępny (Pre-condition) | „Weryfikacja stanu wejściowego” | Potwierdzenie, że stan środowiska wciąż odpowiada założeniom autoryzacji |
| Weryfikacja po akcji | „Kontrola końcowa” | Odczytanie docelowego zasobu w celu weryfikacji faktycznego efektu operacji |
| Wycofanie bezpośrednie (In-band) | „Cofnięcie operacji” | Odwrócenie skutków ubocznych poprzez uruchomienie akcji przeciwnej |
| Transakcja kompensacyjna | „Wycofanie SAGA” | Uruchomienie nowej operacji neutralizującej skutki pierwotnego kroku |
| Zapis stanu w locie (In-flight marking) | „Kolejność zapisu statusu” | Trwałe oznaczenie operacji jako będącej w toku przed fizycznym jej wykonaniem |
| Artykuł 14 (AI Act) | „Nadzór ludzki” | Regulacyjny wymóg audytowalności punktów kontrolnych oraz testowania procedur wycofania |

## Dalsza lektura

- [Microsoft Agent Framework — Checkpointing i HITL](https://learn.microsoft.com/en-us/agent-framework/workflows/human-in-the-loop) — mechanizmy punktów kontrolnych i zarządzanie dzierżawami.
- [Agenci Cloudflare — Człowiek w pętli](https://developers.cloudflare.com/agents/concepts/human-in-the-loop/) — Durable Objects jako baza stanów.
- [Unijna ustawa o sztucznej inteligencji – art. 14: Nadzór człowieka](https://artificialintelligenceact.eu/article/14/) — szczegóły regulacji.
- [Anthropic — Pomiar autonomii agenta w praktyce](https://www.anthropic.com/research/measuring-agent-autonomy) — ramy niezawodności dla złożonych agentów.
- [Anthropic — Claude Code Agent SDK: pętla agenta](https://code.claude.com/docs/en/agent-sdk/agent-loop) — specyfikacja przepływów pracy i harmonogramowania.
