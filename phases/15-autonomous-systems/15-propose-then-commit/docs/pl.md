# Human-in-the-Loop: Zaproponuj, a następnie zatwierdź

> Konsensus na rok 2026 w sprawie HITL jest konkretny. To nie jest tak, że „agent pyta, użytkownik klika „Zatwierdź”. Jest to metoda „zaproponuj, a następnie zatwierdź”: proponowana akcja jest utrwalana w trwałym magazynie z kluczem idempotencji; ujawnione recenzentowi z zamiarem, pochodzeniem danych, dotkniętymi uprawnieniami, promieniem wybuchu i planem wycofania; popełnione dopiero po pozytywnym potwierdzeniu; zweryfikowane po wykonaniu, aby potwierdzić, że efekt uboczny rzeczywiście wystąpił. `interrupt()` firmy LangGraph oraz punkt kontrolny PostgreSQL, `RequestInfoEvent` firmy Microsoft Agent Framework i `waitForApproval()` firmy Cloudflare mają ten sam kształt. Kanonicznym trybem niepowodzenia jest zatwierdzenie pieczątką: „Zatwierdzić?” zostanie kliknięty bez sprawdzania. Udokumentowane łagodzenie to wyzwanie i odpowiedź z wyraźną listą kontrolną.

**Typ:** Ucz się
**Języki:** Python (stdlib, maszyna stanowa typu „zaproponuj, a następnie zatwierdź” z idempotencją)
**Warunki wstępne:** Faza 15 · 12 (Trwałe wykonanie), Faza 15 · 14 (Potykacze)
**Czas:** ~60 minut

## Problem

Agent podejmuje akcję. Użytkownik musi zdecydować: zatwierdzić lub nie. Jeśli decyzja jest natychmiastowa, prawdopodobnie nie jest to recenzja. Jeśli decyzja jest ustrukturyzowana, jest powolna, ale wiarygodna. Pytanie inżynieryjne brzmi: jak przeprowadzić ustrukturyzowany przegląd po ścieżce najmniejszego oporu.

Wzorzec HITL z 2023 r. był synchronicznym monitem: „Agent chce wysłać wiadomość e-mail do X z treścią Y — zatwierdzić?” Użytkownik klika Zatwierdź. Wszyscy uważają, że system jest bezpieczny. W praktyce powierzchnia ta jest mocno oznaczona: użytkownicy zatwierdzają szybko, zatwierdzenia niewiele przewidują, a gdy agent popełni błąd, ścieżka audytu pokazuje długą historię zatwierdzeń, której użytkownik nie może sobie przypomnieć.

Wzorzec 2026 – zaproponuj, a następnie zatwierdź – przenosi HITL na trwałe podłoże, dołącza uporządkowane metadane i wymaga pozytywnego zatwierdzenia. Każdy zestaw SDK agenta zarządzanego ma wersję: LangGraph `interrupt()`, Microsoft Agent Framework `RequestInfoEvent`, Cloudflare `waitForApproval()`. Nazwy API są różne; kształt nie.

## Koncepcja

### Maszyna stanu typu „zaproponuj, a następnie zatwierdź”.

1. **Zaproponuj.** Agent przedstawia proponowaną akcję. Utrzymywał się w trwałym sklepie (PostgreSQL, Redis, Durable Object). Zawiera:
   - intencja (dlaczego agent to robi)
   - pochodzenie danych (jakie źródło doprowadziło do tej propozycji)
   - dotknięte uprawnienia (które zakresy/pliki/punkty końcowe)
   - promień wybuchu (jaki jest najgorszy przypadek)
   - plan wycofania (jeśli został zatwierdzony, jak to cofnąć)
   - klucz idempotencji (unikalny dla każdej propozycji; ponowne przesłanie zwraca ten sam rekord)
2. **Powierzchnia.** Recenzent widzi propozycję ze wszystkimi metadanymi. Recenzentem jest osoba (a nie sam agent recenzujący).
3. **Zatwierdzenie.** Pozytywne potwierdzenie. Akcja zostaje wykonana.
4. **Sprawdź.** Po wykonaniu działanie niepożądane jest odczytywane i potwierdzane. Jeśli etap weryfikacji zakończy się niepowodzeniem, system jest w znanym złym stanie i włącza się alert.

### Klucz idempotencji

Bez klucza idempotentności ponowna próba po przejściowym niepowodzeniu może spowodować podwójne wykonanie zatwierdzonej akcji. Konkretny przykład: użytkownik zatwierdza „przeniesienie 100 dolarów z A do B”. Sygnały sieciowe. Ponowne próby przepływu pracy. Użytkownik zatwierdził raz, ale transfer jest wykonywany dwukrotnie. Klucz idempotencji wiąże zgodę z pojedynczym, unikalnym skutkiem ubocznym; druga egzekucja jest nieskuteczna.

Jest to ten sam wzorzec idempotencji, którego używają interfejsy API Stripe i AWS. Ponowne użycie go do zatwierdzenia agentów jest wyraźnie określone w dokumentacji Microsoft Agent Framework.

### Trwałość: dlaczego zatwierdzenia trwają dłużej niż procesy

Poczekalnia na zatwierdzenie jest częścią państwa, do której agent nie należy. Przepływ pracy jest wstrzymany (Lekcja 12). Po otrzymaniu zatwierdzenia przepływ pracy zostaje wznowiony dokładnie od tego momentu. Właśnie dlatego LangGraph łączy `interrupt()` z punktami kontrolnymi PostgreSQL, a nie tylko stanem w pamięci — zatwierdzenie dwa dni później nadal stwierdza, że ​​przepływ pracy jest nienaruszony.

### Zatwierdzenia pieczątką i ograniczanie ryzyka związanego z wyzwaniem i odpowiedzią

Domyślny interfejs użytkownika HITL (przyciski „Zatwierdź” / „Odrzuć”) zapewnia szybkie zatwierdzanie bez prawdziwej recenzji. Udokumentowane środki łagodzące: lista kontrolna wyzwań i odpowiedzi, która wymaga pozytywnych odpowiedzi na określone pytania przed włączeniem przycisku Zatwierdź. Kształt betonu:

- „Czy rozumiesz, jakiego zasobu to dotyczy? [ ]”
- „Czy sprawdziłeś, czy promień wybuchu jest akceptowalny? [ ]”
- „Czy masz plan wycofania, jeśli to się nie powiedzie? [ ]”

Nie biurokracja sama w sobie – funkcja wymuszająca. Recenzent, który nie może zaznaczyć odpowiednich pól, albo prosi o wyjaśnienia (eskalacja), albo odmawia (bezpieczne ustawienie domyślne). Badania Anthropic dotyczące bezpieczeństwa agentów wyraźnie przytaczają HITL oparty na liście kontrolnej jako środek łagodzący wzorce zatwierdzania pieczątką.

### Co liczy się jako wynikowe

Nie każde działanie wymaga zaproponowania, a następnie zatwierdzenia. Wytyczne na rok 2026:

- **Działania następcze** (zawsze HITL): nieodwracalne zapisy, transakcje finansowe, komunikacja wychodząca, zmiany w produkcyjnej bazie danych, destrukcyjne operacje na systemie plików.
- **Działania odwracalne** (czasami HITL): edycja plików lokalnych, zmiany środowiska pomostowego, zapisy odwracalne z wyraźnym wycofaniem.
- **Odczyty i inspekcje** (nigdy HITL): czytanie pliku, wyświetlanie zasobów, wywoływanie API tylko do odczytu.

### Weryfikacja po akcji

„Zatwierdzenie przebiegło” to nie to samo, co „wystąpił efekt uboczny”. Warunki podziału sieci i wyścigu mogą spowodować, że przepływ pracy uzna, że ​​się powiódł, podczas gdy zaplecze nie przetrwało. Krok weryfikacji powoduje ponowne odczytanie zasobu docelowego po zatwierdzeniu w celu potwierdzenia. Jest to ten sam wzorzec, co transakcje w bazie danych z klauzulami `RETURNING` lub `GetObject` AWS po `PutObject`.

### Ustawa UE o sztucznej inteligencji, art. 14

Artykuł 14 nakłada obowiązek skutecznego nadzoru człowieka nad systemami sztucznej inteligencji wysokiego ryzyka w UE. „Efektywny” nie jest dekoracyjny. Język regulacyjny wyraźnie wyklucza wzory pieczątek. Metoda „zaproponuj, a następnie zatwierdź” z wyzwaniem i odpowiedzią to kształt, który przetrwa kontrolę z art. 14 w dokumentacji zgodności zestawu narzędzi Microsoft Agent Governance Toolkit.

## Użyj tego

`code/main.py` implementuje maszynę stanu typu „zaproponuj, a następnie zatwierdź” w stdlib Python. Trwały sklep to plik JSON. Klucz idempotencji to skrót (thread_id, action_signature). Sterownik symuluje trzy przypadki: czysty proces zatwierdzania, ponowną próbę po przejściowym niepowodzeniu (które nie może zostać wykonane dwukrotnie) oraz niewykonanie zobowiązania w porównaniu z przepływem typu wyzwanie i odpowiedź.

## Wyślij to

`outputs/skill-hitl-design.md` przegląda proponowany przepływ pracy HITL pod kątem kształtu „zaproponuj, a następnie zatwierdź” i zaznacza brakujące warstwy metadanych, idempotencji, weryfikacji lub warstwy wyzwanie-odpowiedź.

## Ćwiczenia

1. Uruchom `code/main.py`. Potwierdź, że ponowna próba zatwierdzonej propozycji wykorzystuje trwały zapis i nie jest wykonywana ponownie. Teraz zmień klucz idempotencji, tak aby zawierał znacznik czasu i wyświetlał podwójne wykonanie ponownej próby.

2. Rozszerz rekord propozycji o pole `rollback`. Symuluj wykonanie, którego etap weryfikacji kończy się niepowodzeniem. Pokaż automatyczne uruchamianie wycofania.

3. Przeczytaj dokumentację `RequestInfoEvent` programu Microsoft Agent Framework. Zidentyfikuj jedno pole metadanych, które zawiera interfejs API i którego brakuje w silniku zabawki. Dodaj go i wyjaśnij, przed czym chroni.

4. Zaprojektuj listę kontrolną wyzwań i odpowiedzi dla konkretnego działania (np. „opublikuj post na publicznym koncie na Twitterze”). Na jakie trzy pytania musi odpowiedzieć recenzent? Dlaczego te trzy?

5. Wybierz jeden przypadek, w którym synchroniczny komunikat „Zatwierdzić?” wystarczyłaby zachęta (nie jest potrzebny trwały magazyn). Wyjaśnij dlaczego i podaj klasę ryzyka, którą akceptujesz.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|---|---|---|
| Zaproponuj, a następnie zatwierdź | „Zatwierdzenie dwufazowe” | Utrwalona propozycja + pozytywne zatwierdzenie + weryfikacja |
| Klucz idempotencji | „Token umożliwiający ponowną próbę” | Unikalne na propozycję; druga egzekucja bez operacji |
| Pochodzenie danych | „Skąd to się wzięło” | Konkretna treść źródłowa, która doprowadziła do wniosku |
| Promień wybuchu | „Najgorszy przypadek” | Zakres skutku w przypadku niepowodzenia działania |
| Pieczątka | „Szybka akceptacja” | Kliknięcie przycisku „Zatwierdź” bez prawdziwej recenzji |
| Wyzwanie i odpowiedź | „Lista kontrolna wymuszania” | Recenzent musi pozytywnie odpowiedzieć na konkretne pytania |
| Zdarzenie żądania informacji | „Prymitywny program MS Agent Framework” | Trwałe żądanie HITL ze strukturalnymi metadanymi |
| `interrupt()` / `waitForApproval()` | „Prymitywy frameworka” | Odpowiedniki LangGraph / Cloudflare o tym samym kształcie |

## Dalsze czytanie

- [Microsoft Agent Framework — Człowiek w pętli](https://learn.microsoft.com/en-us/agent-framework/workflows/human-in-the-loop) — `RequestInfoEvent`, trwałe zatwierdzenia.
- [Agenci Cloudflare — Człowiek w pętli](https://developers.cloudflare.com/agents/concepts/human-in-the-loop/) — `waitForApproval()` i trwałe obiekty.
- [Anthropic — Pomiar autonomii agenta w praktyce](https://www.anthropic.com/research/measuring-agent-autonomy) — HITL jako środek łagodzący ryzyko długoterminowe.
– [Unijna ustawa o sztucznej inteligencji – art. 14: Nadzór człowieka](https://artificialintelligenceact.eu/article/14/) – podstawa regulacyjna dotycząca systemów wysokiego ryzyka.
– [Anthropic – Konstytucja Claude’a (styczeń 2026 r.)](https://www.anthropic.com/news/claudes-constitution) – ramy konstytucyjne dotyczące nadzoru.