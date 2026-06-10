# Human-in-the-Loop: Zaproponuj, a następnie zatwierdź

> W 2026 roku wypracowano jasny konsensus wokół mechanizmu Human-in-the-Loop (HITL). Bezpieczna integracja z człowiekiem nie polega już na prostym schemacie: „agent pyta, użytkownik klika 'Zatwierdź'”. Standardem stał się wzorzec „zaproponuj, a następnie zatwierdź” (Propose-then-Commit). W tym modelu proponowane działanie jest zapisywane w trwałej bazie danych wraz z kluczem idempotencji. Użytkownikowi (recenzentowi) prezentowane są szczegółowe metadane: cel działania (intencja), pochodzenie danych wejściowych, zakres uprawnień, potencjalny zakres szkód (blast radius) oraz plan wycofania zmian. Operacja jest zatwierdzana dopiero po uzyskaniu jednoznacznej zgody recenzenta, a po jej wykonaniu system weryfikuje, czy oczekiwany skutek uboczny rzeczywiście nastąpił. Metoda ta ma ten sam cel i strukturę w różnych frameworkach (np. `interrupt()` z bazą PostgreSQL w LangGraph, `RequestInfoEvent` w Microsoft Agent Framework czy `waitForApproval()` w Cloudflare). Głównym zagrożeniem dla tego modelu jest bezrefleksyjne klikanie (tzw. mechaniczne zatwierdzanie/rubber-stamping) – metodą przeciwdziałania jest wdrożenie procedury wyzwanie-odpowiedź (Challenge-Response) z interaktywną listą kontrolną.

**Typ:** Ucz się
**Języki:** Python (stdlib, maszyna stanowa typu „zaproponuj, a następnie zatwierdź” z idempotencją)
**Warunki wstępne:** Faza 15 · 12 (Trwałe wykonanie), Faza 15 · 14 (Potykacze)
**Czas:** ~60 minut

## Problem

Agent planuje wykonanie akcji, a użytkownik musi podjąć decyzję o jej zatwierdzeniu lub odrzuceniu. Jeśli decyzja zapada natychmiastowo, prawdopodobnie nie została poprzedzona rzetelną analizą. Bezpieczeństwo wymaga ustrukturyzowanego procesu oceny – choć spowalnia on pracę, to gwarantuje niezawodność. Kluczowe wyzwanie inżynieryjne brzmi: jak zaprojektować ustrukturyzowany przegląd działań agenta, by zminimalizować narzut pracy użytkownika.

Wzorzec HITL z 2023 roku opierał się na prostych, synchronicznych komunikatach typu: „Agent chce wysłać e-mail do odbiorcy X o treści Y – czy zatwierdzasz?”. Po kliknięciu „Zatwierdź” system przechodził dalej, co stwarzało iluzję bezpieczeństwa. W praktyce użytkownicy szybko popadali w rutynę i zatwierdzali akcje bez czytania. Gdy agent popełniał kosztowny błąd, ścieżka audytu ujawniała długą listę bezmyślnych zatwierdzeń, których użytkownik nie potrafił wyjaśnić.

Nowoczesny wzorzec (Propose-then-Commit) opiera się na trwałym zapisie propozycji w bazie danych, dołączaniu ustrukturyzowanych metadanych oraz wymogu interaktywnego potwierdzenia. Taka architektura jest implementowana we wszystkich wiodących frameworkach pod różnymi nazwami: LangGraph `interrupt()`, Microsoft Agent Framework `RequestInfoEvent` czy Cloudflare `waitForApproval()`. Choć nazwy API się różnią, schemat działania pozostaje ten sam.

## Koncepcja

### Maszyna stanowa wzorca „zaproponuj, a następnie zatwierdź”

1. **Zaproponowanie akcji (Propose):** Agent zgłasza planowaną czynność. Propozycja jest zapisywana w trwałej bazie danych (PostgreSQL, Redis, Durable Objects) i zawiera:
   - **Intencję (Intent):** Wyjaśnienie, dlaczego agent chce wykonać tę akcję.
   - **Pochodzenie danych (Data Origin):** Wskazanie źródła (np. pliku, strony, inputu), które skłoniło agenta do podjęcia decyzji.
   - **Uprawnienia (Permissions):** Wykaz zasobów, plików lub punktów końcowych API, na które wpłynie akcja.
   - **Zakres szkód (Blast Radius):** Analizę najgorszego scenariusza awarii.
   - **Plan wycofania (Rollback Plan):** Instrukcję, jak cofnąć efekty uboczne w razie problemów.
   - **Klucz idempotencji (Idempotency Key):** Unikalny identyfikator propozycji chroniący przed powtórnym uruchomieniem tej samej operacji.
2. **Prezentacja (Expose):** Propozycja wraz z pełnymi metadanymi jest prezentowana człowiekowi pełniącemu rolę recenzenta (recenzentem musi być człowiek, a nie inny agent).
3. **Autoryzacja (Commit):** Po uzyskaniu świadomej zgody akcja jest wykonywana.
4. **Weryfikacja (Verify):** Po wykonaniu akcji system weryfikuje efekty uboczne w docelowym środowisku. Jeśli weryfikacja wykaże błąd, system zgłasza awarię i może automatycznie uruchomić procedury alarmowe.

### Klucz idempotencji

Brak klucza idempotencji przy wystąpieniu przejściowych błędów sieciowych może doprowadzić to podwójnego wykonania zatwierdzonej już akcji. Przykładowo: użytkownik zatwierdza transakcję „przelew 100 USD z konta A na B”. Następuje błąd sieciowy, po czym silnik orkiestracji wznawia proces. Użytkownik wydał zgodę tylko raz, ale przelew zostaje zrealizowany dwukrotnie. Klucz idempotencji jednoznacznie wiąże autoryzację z unikalnym identyfikatorem operacji, dzięki czemu ponowne uruchomienie kroku nie wywoła kolejnego przelewu (druga próba jest ignorowana).

To ten sam sprawdzony wzorzec idempotencji, który stosują systemy Stripe czy AWS. Jego wdrożenie w architekturze agentów jest wprost zalecane m.in. w wytycznych Microsoft Agent Framework.

### Trwałość stanu: wstrzymywanie procesów na czas decyzji

Oczekiwanie na decyzję człowieka (HITL) to specyficzny stan procesu, którego czasem trwania nie rządzi zegar systemowy agenta. Przepływ pracy zostaje wówczas zamrożony (patrz Lekcja 12). Po uzyskaniu zgody orkiestrator wznawia wykonywanie dokładnie od punktu wstrzymania. Z tego powodu frameworki takie jak LangGraph łączą metodę `interrupt()` z trwałymi bazami danych (np. PostgreSQL), rezygnując z przechowywania stanu wyłącznie w pamięci RAM. Dzięki temu zatwierdzenie operacji dokonane nawet po kilku dniach pozwala na bezproblemowe dokończenie zadania.

### Przeciwdziałanie bezrefleksyjnemu zatwierdzaniu (Rubber-stamping)

Tradycyjne interfejsy użytkownika z prostymi przyciskami „Zatwierdź” / „Odrzuć” sprzyjają nawykowemu klikaniu bez analizy. Skuteczną metodą obrony jest wdrożenie mechanizmu Challenge-Response, który wymaga od użytkownika zaznaczenia konkretnych opcji przed odblokowaniem przycisku zatwierdzenia. Przykład struktury:

- „[ ] Rozumiem, na jakie zasoby wpłynie ta operacja.”
- „[ ] Potwierdzam, że potencjalny zakres szkód (blast radius) jest akceptowalny.”
- „[ ] Sprawdziłem plan wycofania zmian w razie awarii.”

Nie jest to sztuczna biurokracja, lecz mechanizm wymuszający skupienie recenzenta. Jeśli użytkownik nie może z czystym sumieniem zaznaczyć wymaganych pól, powinien wstrzymać proces (eskalować problem) lub odrzucić propozycję. W badaniach Anthropic nad bezpieczeństwem agentów interaktywne listy kontrolne są wskazywane jako kluczowe narzędzie eliminujące problem rutynowych autoryzacji.

### Klasyfikacja operacji wymagających zatwierdzenia

Nie każda czynność wykonywana przez agenta wymaga zaangażowania człowieka. Standardowy podział obejmuje:

- **Operacje krytyczne (zawsze wymagające HITL):** Nieodwracalne operacje zapisu, transakcje finansowe, komunikacja wychodząca (wysyłanie e-maili, postów), modyfikacje produkcyjnej bazy danych, destrukcyjne operacje na systemie plików.
- **Operacje warunkowe (czasami wymagające HITL):** Modyfikacje lokalnych plików kodu, zmiany w środowisku stagingowym, operacje zapisu, które można łatwo cofnąć.
- **Operacje bezpieczne (nigdy niewymagające HITL):** Odczyt plików, listowanie zasobów, wywoływanie metod API typu read-only.

### Weryfikacja po wykonaniu operacji (Post-action Verification)

Samo pomyślne zatwierdzenie i uruchomienie operacji nie gwarantuje, że przyniosła ona oczekiwany skutek w systemie. Awarie sieci lub błędy synchronizacji (race conditions) mogą sprawić, że agent uzna zadanie za wykonane, podczas gdy backend nie zapisał zmian. Krok weryfikacyjny polega na ponownym odczytaniu zasobu po wykonaniu operacji w celu potwierdzenia jej sukcesu. To ten sam wzorzec, co klauzula `RETURNING` w zapytaniach SQL lub żądanie `GetObject` w AWS po wykonaniu `PutObject`.

### Zgodność z Artykułem 14 unijnej ustawy o sztucznej inteligencji (AI Act)

Artykuł 14 AI Act nakłada na systemy wysokiego ryzyka wymóg wdrożenia efektywnego nadzoru ludzkiego. Słowo „efektywny” wyklucza rutynowe zatwierdzanie bez weryfikacji. Model „zaproponuj, a następnie zatwierdź” połączony z procedurą Challenge-Response (interaktywną listą kontrolną) to standard, który pozwala na spełnienie wymogów Artykułu 14 (co zostało uwzględnione m.in. w dokumentacji zgodności Microsoft Agent Governance Toolkit).

## Przykład praktyczny

Skrypt `code/main.py` implementuje maszynę stanową wzorca „zaproponuj, a następnie zatwierdź” z użyciem biblioteki standardowej Pythona. Trwałym magazynem stanu jest plik JSON, a klucz idempotencji jest generowany jako hash parametrów sesji (`thread_id` oraz sygnatury akcji). Kod testowy symuluje trzy scenariusze: standardowe zatwierdzenie, ponowną próbę po awarii (która dzięki idempotencji nie wywołuje akcji powtórnie) oraz porównanie tradycyjnego zatwierdzania z procedurą Challenge-Response.

## Zadanie wdrożeniowe

Plik `outputs/skill-hitl-design.md` służy do weryfikacji przepływu HITL pod kątem poprawności wdrożenia wzorca „zaproponuj, a następnie zatwierdź”. Audytowi podlegają: zakres metadanych, implementacja idempotencji, obecność kroku weryfikacji oraz mechanizm listy kontrolnej.

## Ćwiczenia

1. Uruchom skrypt `code/main.py`. Potwierdź, że ponowna próba wykonania zatwierdzonej propozycji odczytuje stan z pliku i zapobiega powtórnemu uruchomieniu kodu. Następnie zmodyfikuj generator klucza idempotencji tak, aby dodawał aktualny znacznik czasu, i zaobserwuj błąd podwójnego wykonania akcji.
2. Rozbuduj strukturę propozycji o opcjonalne pole `rollback`. Zasymuluj przypadek, w którym krok weryfikacji kończy się niepowodzeniem, i wykaż automatyczne uruchomienie procedury wycofania zmian.
3. Przejrzyj strukturę zdarzenia `RequestInfoEvent` w pakiecie Microsoft Agent Framework. Wskaż jedno pole metadanych obecne w tym standardzie, którego brakuje w naszym prostym skrypcie testowym. Wyjaśnij, przed jakim zagrożeniem chroni to pole.
4. Zaprojektuj listę kontrolną Challenge-Response dla konkretnego scenariusza (np. „publikacja komunikatu na oficjalnym koncie firmy na platformie X”). Zdefiniuj trzy pytania, na które recenzent musi odpowiedzieć, i uzasadnij ich wybór.
5. Określ przypadek użycia, w którym tradycyjny, prosty komunikat z pytaniem o akceptację (bez trwałego zapisu stanu sesji) jest wystarczający. Uzasadnij swój wybór i określ poziom ryzyka, na jaki się godzisz.

## Kluczowe terminy

| Termin | Co mówią potocznie | Co to dokładnie oznacza |
|---|---|---|
| Zaproponuj, a następnie zatwierdź (Propose-then-Commit) | „Zatwierdzenie dwufazowe” | Wzorzec HITL: rejestracja propozycji + autoryzacja + weryfikacja skutków |
| Klucz idempotencji (Idempotency key) | „Token ponowienia” | Unikalny identyfikator operacji zapobiegający jej wielokrotnemu uruchomieniu |
| Pochodzenie danych (Data origin) | „Skąd to się wzięło” | Informacja o źródle danych wejściowych, które skłoniły agenta do wnioskowania |
| Zakres szkód (Blast radius) | „Najgorszy scenariusz” | Przewidywana skala potencjalnych szkód w przypadku błędu akcji |
| Rubber-stamping | „Bezmyślne zatwierdzanie” | Automatyczne klikanie zgody bez analizy metadanych |
| Challenge-Response | „Lista kontrolna” | Interaktywne pytania blokujące przycisk zgody do czasu ich potwierdzenia |
| RequestInfoEvent | „Standard MS Agent” | Trwałe żądanie autoryzacji z ustrukturyzowanymi metadanymi w Microsoft Agent Framework |
| `interrupt()` / `waitForApproval()` | „Prymitywy orkiestracji” | Metody wstrzymywania procesów na czas decyzji człowieka (LangGraph / Cloudflare) |

## Dalsza lektura

- [Microsoft Agent Framework — Człowiek w pętli](https://learn.microsoft.com/en-us/agent-framework/workflows/human-in-the-loop) — specyfikacja `RequestInfoEvent` i obsługa autoryzacji.
- [Agenci Cloudflare — Człowiek w pętli](https://developers.cloudflare.com/agents/concepts/human-in-the-loop/) — obsługa `waitForApproval()` i Durable Objects.
- [Anthropic — Pomiar autonomii agenta w praktyce](https://www.anthropic.com/research/measuring-agent-autonomy) — rola HITL w redukcji ryzyka w długich horyzontach pracy.
- [Unijna ustawa o sztucznej inteligencji – art. 14: Nadzór człowieka](https://artificialintelligenceact.eu/article/14/) — podstawa prawna dla systemów wysokiego ryzyka.
- [Anthropic — Konstytucja Claude'a (styczeń 2026 r.)](https://www.anthropic.com/news/claudes-constitution) — ramy nadzorcze i konstytucyjne dla modeli językowych.
