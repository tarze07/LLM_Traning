# Agenci generatywni i symulacja zachowań emergentnych

> Park i in. (2023, UIST '23, arXiv:2304.03442) stworzyli wirtualne miasteczko **Smallville** – piaskownicę zamieszkaną przez 25 agentów z trzyczęściową architekturą: **strumień pamięci** (rejestr w języku naturalnym), **refleksja** (synteza wyższego poziomu, którą agent generuje na podstawie własnego strumienia pamięci) oraz **plan** (ogólne zachowanie zaplanowane na dany dzień, a następnie uszczegółowione plany podrzędne). Przełomowym rezultatem było zorganizowanie imprezy walentynkowej: u jednego z agentów umieszczono informację początkową (seed) „chce urządzić imprezę walentynkową”. Bez dalszego narzucania scenariusza agent ten wygenerował zaproszenia, które rozeszły się po całej społeczności, uzgodniono daty, a impreza doszła do skutku – mimo że pozostałych 24 agentów zaczynało bez jakiejkolwiek wiedzy o planowanym wydarzeniu. Analiza ablacyjna wykazała, że do zachowania wiarygodności agentów niezbędne są wszystkie trzy komponenty. Do udokumentowanych błędów zaliczają się naruszenia norm przestrzennych (wchodzenie do zamkniętych sklepów, jednoczesne korzystanie z jednoosobowych łazienek). Jest to architektura referencyjna dla symulacji agentowych oraz społecznej ewaluacji systemów wieloagentowych w roku 2026.

**Typ:** Ucz się + Buduj
**Języki:** Python (stdlib)
**Wymagania wstępne:** Faza 16 · 04 (model pierwotny), faza 16 · 13 (pamięć współdzielona)
**Czas:** ~75 minut

## Problem

Większość systemów wieloagentowych to zespoły działające według ściśle określonych scenariuszy: plany są tworzone przez planistów, kod pisany przez koderów, a recenzje pisane przez recenzentów. Sprawdza się to w przypadku dobrze zdefiniowanych zadań, ale nie pozwala na uzyskanie emergentnych, nieskryptowanych zachowań, które pojawiają się, gdy agenci posiadają pamięć, priorytety i działają w otwartym świecie. Badania naukowe, symulacje społeczne, a coraz częściej także sztuczna inteligencja w grach wymagają tego drugiego podejścia.

Architektura Smallville stanowi dla niego punkt odniesienia. Przed publikacją Parka i in. (2023) najlepsze symulacje agentów opierały się na prostym odtwarzaniu scenariuszy; obecnie ten schemat jest domyślnym standardem dla agentów generatywnych w otwartych światach. Tworząc symulację agentową w 2026 roku, należy albo zastosować trzy komponenty Smallville, albo wyraźnie uzasadnić rezygnację z nich.

## Koncepcja

### Trzy komponenty

**Strumień pamięci.** Rejestr obserwacji, działań, przemyśleń i planów, do którego dane można wyłącznie dopisywać. Każdy wpis zawiera znacznik czasu, typ, opis w języku naturalnym oraz pochodne metadane: **aktualność** (recency), **ważność** (importance – samodzielna ocena agenta w skali 1-10) oraz **trafność** (relevance – podobieństwo cosinusowe do bieżącego zapytania).

```
[2026-02-14 09:12:03] observation: Isabella Rodriguez asked me if I like jazz
[2026-02-14 09:14:22] reflection:   I enjoy long conversations about music
[2026-02-14 10:05:00] plan:         Attend Isabella's Valentine's Day party tonight
```

Pobieranie wspomnień (retrieval) łączy w sobie trzy składowe: `score = w_recency * e^(-decay * age) + w_importance * importance + w_relevance * cos_sim`. Wpisy o najwyższych wynikach (top-k) są przekazywane do bieżącego promptu.

**Refleksja.** Okresowo (co N wspomnień lub w reakcji na ważne zdarzenia) agent generuje syntezy wyższego rzędu na podstawie ostatnich doświadczeń. Wpisy z refleksjami trafiają z powrotem do strumienia pamięci i mogą być pobierane tak samo jak zwykłe wspomnienia. W ten sposób agenci budują uogólnienia i głębsze zrozumienie (understandings) – odpowiednik długoterminowych przekonań w tej architekturze.

**Plan.** Dekompozycja odgórna. Najpierw powstaje ogólny plan dnia („idź do pracy, zjedz kolację z Klausem”), potem plany godzinowe, a na końcu plany na poziomie konkretnych działań. Plany te podlegają rewizji: jeśli nowa obserwacja koliduje z planem, agent modyfikuje dany segment planu.

### Dlaczego wszystkie trzy komponenty są ważne (analiza ablacyjna)

Park i in. przeprowadzili analizę ablacyjną, wyłączając kolejno obserwacje, refleksje i planowanie. Każde z tych wyłączeń negatywnie wpływało na wiarygodność zachowań:

- Bez **obserwacji** agent traci kontekst i działa w oparciu o nieaktualne przekonania.
- Bez **refleksji** agent nie potrafi tworzyć przekonań wyższego rzędu, a jego interakcje pozostają powierzchowne.
- Bez **planu** zachowanie agenta zamienia się w chaotyczne reakcje na bodźce, a długoterminowe cele znikają.

Oceny wiarygodności wystawiane przez sędziów kompetentnych były najwyższe przy aktywnych wszystkich trzech komponentach; wyłączenie dowolnego z nich powodowało wyraźny spadek jakości.

### Przykład: Organizacja imprezy walentynkowej

U jednej z agentek (Isabella Rodriguez) umieszczono cel początkowy: „chce zorganizować imprezę walentynkową w Hobbs Cafe 14 lutego o godzinie 17:00”. Pozostałych 24 agentów nie otrzymało takiej instrukcji wstępnej (seed). W trakcie kolejnych symulowanych dni:

1. Plan Isabelli uwzględnia zapraszanie innych osób.
2. Każde zaproszenie staje się obserwacją zapisaną w strumieniu pamięci zaproszonego agenta.
3. Refleksje zaproszonych agentów prowadzą do wniosku: „Isabella organizuje imprezę”.
4. Plany kolejnych agentów zaczynają uwzględniać „pójście na imprezę 14 lutego”.
5. Agenci dzielą się tą informacją z innymi agentami. Wieść o przyjęciu rozprzestrzenia się bez centralnej koordynacji.
6. 14 lutego o 17:00 grupa agentów spotyka się w Hobbs Cafe.

Mamy tu do czynienia z emergencją w sensie technicznym: zachowanie na poziomie całego systemu (wspólna impreza) wyłoniło się z lokalnych interakcji (dwustronne rozmowy + indywidualne planowanie) bez udziału jakiegokolwiek centralnego koordynatora.

### Udokumentowane tryby błędów (failure modes)

Park i in. wyszczególnili następujące problemy:

- **Naruszenia norm przestrzennych i społecznych.** Agenci wchodzą do zamkniętych sklepów, próbują jednocześnie korzystać z tej samej jednoosobowej łazienki lub jedzą posiłki w miejscach do tego nieprzeznaczonych. Model językowy nie potrafi samodzielnie wywnioskować norm społeczno-przestrzennych na podstawie samej geometrii środowiska.
- **Przepełnienie pamięci.** Długie przebiegi symulacji prowadzą do lawinowego wzrostu kosztów wyszukiwania wspomnień. Praktyczne rozwiązanie: okresowa kompresja pamięci (podsumowywanie i usuwanie zbędnych wpisów) oraz wygaszanie wspomnień o niskiej ważności.
- **Halucynacje w refleksjach.** Refleksje mogą tworzyć relacje lub fakty, które nie mają odzwierciedlenia w rzeczywistym strumieniu pamięci. Środki zaradcze: dołączanie identyfikatorów źródłowych wspomnień do promptów generujących refleksje i ich weryfikacja podczas pobierania.

Są to typowe problemy produkcyjne, z którymi mierzy się każda symulacja agentowa w 2026 roku.

### Zasady implementacji architektury trójelementowej

1. **Pamięć tylko do odczytu i dopisywania (append-only).** Nigdy nie modyfikuj istniejących wpisów. Ewentualne sprostowania powinny być zapisywane jako nowe wpisy.
2. **Lekka ocena ważności.** Odpytuj LLM o ocenę ważności zdarzenia w skali 1-10 bezpośrednio podczas jego zapisywania. Wynik ten należy zapisać w pamięci podręcznej.
3. **Wyszukiwanie oparte na rankingu, a nie na filtrowaniu.** Wybierz top-k wpisów na podstawie sumarycznego wyniku rankingu. Unikaj sztywnych filtrów, które mogą prowadzić do utraty kontekstu.
4. **Okresowe wyzwalanie refleksji.** Proces refleksji powinien uruchamiać się, gdy suma ważności nowych, nieprzetworzonych wspomnień przekroczy określony próg (np. 150).
5. **Segmentowa rewizja planów.** Jeśli nowa obserwacja stoi w sprzeczności z dotychczasowym planem, zregeneruj wyłącznie kolidujący fragment, a nie całą strukturę planu.

### Zastosowania agentów generatywnych poza Smallville

Literatura naukowa i wdrożenia z lat 2024–2026 rozwijają tę architekturę w kierunku:

- **Społecznych symulacji wieloagentowych na potrzeby analiz rynkowych i politycznych.** Populacje agentów zbliżone to Smallville symulują zachowania użytkowników reagujących na nowe funkcje produktów. Jest to proces szybszy niż tradycyjne testy A/B, choć jego dokładność bywa dyskusyjna.
- **Sztucznej inteligencji NPC w grach.** Gry RPG wykorzystujące agentów w stylu Smallville generują unikalne wątki fabularne zamiast powtarzalnych, oskryptowanych zadań.
- **Nowych wzorców ewaluacji agentów.** Zamiast prostej skuteczności w wykonywaniu zadań, kluczową miarą staje się wiarygodność i długoterminowa spójność zachowań.

Oryginalna architektura pozostaje punktem odniesienia. Nowsze rozwiązania modyfikują poszczególne elementy (np. wprowadzają wektorowe bazy danych, refleksję RAG czy neurosymboliczne planowanie), ale zachowują podstawową, trójskładnikową strukturę.

### Znaczenie dla inżynierii systemów wieloagentowych

Projekt Smallville udowodnił, że zachowania emergentne w populacjach agentów można osiągnąć stosunkowo niskim kosztem, jeśli odpowiednio zaprojektuje się architekturę systemu. Obecnie rozwiązanie to jest z powodzeniem replikowane przy użyciu modeli open source (mniejsze modele LLM tracą na wiarygodności stopniowo, a nie gwałtownie). Każdy system produkcyjny wymagający **emergentnych zachowań społecznych** opiera się na tym schemacie. Z kolei systemy nakierowane na **precyzyjne wykonywanie zadań** korzystają raczej z omówionych wcześniej wzorców typu nadzorca-wykonawca czy sztywnego podziału ról.

## Zbuduj to

Skrypt `code/main.py` implementuje wspomniane trzy komponenty w standardowej bibliotece Pythona przy użyciu uproszczonych reguł (bez odpytywania rzeczywistego LLM). Demo odtwarza uproszczoną wersję przyjęcia walentynkowego:

- `MemoryStream` – rejestr append-only obsługujący obliczanie aktualności, ważności i trafności.
- `reflect(stream)` – uproszczony mechanizm refleksji nad ostatnimi ważnymi wspomnieniami.
- `plan(agent_state)` – generowanie planów dziennych i godzinowych w oparciu o aktualne przekonania.
- Scenariusz: 5 agentów. Agent 1 rozpoczyna z celem „organizacja imprezy o 17:00”. W kolejnych krokach symulacji informacja o zaproszeniu rozprzestrzenia się, a agenci gromadzą się w jednym miejscu.

Uruchom:

```
python3 code/main.py
```

Oczekiwany wynik: logi z kolejnych kroków symulacji. Przed zakończeniem symulacji co najmniej 3 z 5 agentów powinno uwzględnić imprezę w swoim planie i pojawić się na miejscu. Jedna informacja początkowa (seed) prowadzi do skoordynowanego działania bez centralnego sterowania.

## Użyj tego

Plik `outputs/skill-simulation-designer.md` zawiera projekt symulacji opartej na agentach generatywnych: definiuje liczbę agentów, strukturę pamięci, częstotliwość refleksji, horyzont planowania oraz metryki ewaluacji.

## Wdrożenie produkcyjne

Zasady tworzenia symulacji produkcyjnych:

- **Pamięć to baza danych.** Do obsługi produkcyjnej skali wybierz dedykowane rozwiązanie (wektorową bazę danych, PostgreSQL). Rozwiązania działające w pamięci RAM (in-memory) z biblioteki standardowej nadają się wyłącznie do prototypowania.
- **Loguj ścieżkę pobierania wspomnień (retrieval trace).** Dla każdego działania agenta zapisz kluczowe wspomnienia, które je wywołały. Ułatwi to debugowanie systemu.
- **Kontroluj budżet tokenów per agent.** Procesy wyszukiwania, refleksji i planowania dla każdego agenta w każdym kroku symulacji (tick) generują liczne zapytania do LLM. Przy dużej liczbie agentów i kroków koszty mogą drastycznie wzrosnąć.
- **Okresowo kompresuj pamięć.** Podsumowuj stare zdarzenia i usuwaj wpisy o niskiej ważności. Polityka retencji danych to kluczowa decyzja architektoniczna.
- **Jawnie wykrywaj naruszenia norm przestrzennych i społecznych.** Architektura agentów generatywnych nie zapewnia ich automatycznego przestrzegania.

## Ćwiczenia

1. Uruchom `code/main.py`. Potwierdź, że na imprezie gromadzi się co najmniej 3 agentów. Zwiększ liczbę agentów do 10 – czy zachowanie emergentne nadal występuje?
2. Usuń krok refleksji. Jak zmienia się zachowanie agentów? Porównaj wyniki z wnioskami z analizy ablacyjnej w pracy Parka i in. (2023).
3. Wprowadź konkurencyjny cel początkowy (np. „Klaus chce wygłosić wykład naukowy o 17:00”). Czy agenci podzielą się na grupy, czy jeden z celów zdominuje symulację? Jakie czynniki o tym decydują?
4. Dodaj ograniczenia przestrzenne: Hobbs Cafe może pomieścić maksymalnie 4 agentów. Czy symulacja radzi sobie z przepełnieniem w sposób kontrolowany, czy też pojawia się błąd analogiczny do korzystania z tej samej jednoosobowej łazienki?
5. Przeczytaj rozdział 6 (eksperymenty nad zachowaniami emergentnymi) w pracy Parka i in. (arXiv:2304.03442). Wskaż jedno zachowanie, którego nie da się odtworzyć w Twojej uproszczonej wersji. Który element architektury wymagałby rozbudowy?

## Kluczowe terminy

| Termin | Co się potocznie mówi | Co to właściwie oznacza |
|---|---|---|
| Strumień pamięci (Memory Stream) | „Dziennik agenta” | Rejestr typu append-only (wyłącznie do dopisywania) zawierający obserwacje, działania, przemyślenia i plany. |
| Aktualność (Recency) | „Jak świeże jest wspomnienie” | Wynik wyliczany za pomocą wykładniczego zaniku na podstawie wieku wpisu. |
| Ważność (Importance) | „Jak istotne jest to dla agenta” | Samodzielna ocena w skali 1-10 dokonywana przez agenta podczas zapisu. Wynik jest buforowany. |
| Trafność (Relevance) | „Jak bardzo pasuje do zapytania” | Podobieństwo cosinusowe między wektorami osadzeń (embeddings) zapytania i wspomnienia. |
| Refleksja (Reflection) | „Przekonanie wyższego rzędu” | Synteza wygenerowana z ostatnich wspomnień, zapisywana w strumieniu jako nowe wspomnienie. |
| Plan (Plan) | „Harmonogram dnia/godziny/akcji” | Hierarchiczna struktura planu (od ogółu do szczegółu) z możliwością rewizji w razie sprzecznych obserwacji. |
| Smallville | „Miasteczko z eksperymentu Parka” | Środowisko symulacyjne dla 25 agentów, w którym zaobserwowano emergencję organizacji imprezy walentynkowej. |
| Wiarygodność (Believability) | „Ocena realizmu” | Wskaźnik określający stopień, w jakim zachowanie agenta wydaje się naturalne i ludzkie dla zewnętrznych sędziów. |

## Dalsze czytanie

- [Park i in. – Generative Agents: Interactive Simulacra of Human Behavior](https://arxiv.org/abs/2304.03442) – oryginalna publikacja naukowa
- [Strona artykułu na UIST '23](https://dl.acm.org/doi/10.1145/3586183.3606763) – oficjalne miejsce publikacji
- [Repozytorium kodu Smallville](https://github.com/joonspk-research/generative_agents) – oryginalna implementacja
- [Hayes-Roth 1985 – A Blackboard Architecture for Control](https://www.sciencedirect.com/science/article/abs/pii/0004370285900639) – podwaliny pod systemy agentowe o strukturyzowanej pamięci
