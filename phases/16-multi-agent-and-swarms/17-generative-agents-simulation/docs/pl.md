# Agenci generatywni i symulacja wschodzących

> Park i in. 2023 (UIST '23, arXiv:2304.03442) zaludniony **Smallville**, piaskownica złożona z 25 agentów, z trzyczęściową architekturą: **strumień pamięci** (dziennik w języku naturalnym), **refleksja** (synteza wyższego poziomu, którą agent generuje na temat własnego strumienia) i **plan** (zachowanie na poziomie dziennym, a następnie plany podrzędne). Przełomowym rezultatem było pojawienie się imprezy walentynkowej: jeden agent zasypany informacją „chce urządzić imprezę walentynkową” bez dalszego pisania scenariusza, wyprodukował zaproszenia rozesłane po całej populacji, skoordynował daty i impreza się odbyła — od 24 agentów, którzy rozpoczęli nie mając o tym wiedzy. Ablacje pokazują, że do wiarygodności wymagane są wszystkie trzy elementy. Udokumentowane awarie to błędy norm przestrzennych (wchodzenie do zamkniętych sklepów, wspólne korzystanie z jednoosobowych łazienek). Jest to architektura referencyjna dla symulacji agentowych i wieloagentowej oceny społecznej w roku 2026.

**Typ:** Ucz się + Buduj
**Języki:** Python (stdlib)
**Wymagania wstępne:** Faza 16 · 04 (model pierwotny), faza 16 · 13 (pamięć współdzielona)
**Czas:** ~75 minut

## Problem

Większość systemów wieloagentowych to zespoły o ściśle określonych skryptach: plany planistów, kody koderów, recenzje recenzentów. Działa to w przypadku dobrze zdefiniowanych zadań. Nie obejmuje wyłaniających się, nieskryptowanych zachowań, które pojawiają się, gdy agenci mają pamięć, priorytety i otwarty świat. Badania, symulacje społeczeństwa i coraz częściej sztuczna inteligencja w grach potrzebują tego drugiego rodzaju.

Architektura Smallville jest dla niego punktem odniesienia. Do Parku 2023 najlepsze symulacje agentów opierały się na płytkich naśladowcach scenariusza; po nim wzór jest domyślny dla agentów generatywnych w otwartych światach. Jeśli tworzysz symulację agenta w 2026 r., albo używasz trzech komponentów Smallville, albo wyraźnie uzasadniasz, dlaczego tego nie robisz.

## Koncepcja

### Trzy komponenty

**Strumień pamięci.** Dziennik obserwacji, działań, przemyśleń i planów, który można tylko dodać. Każdy wpis ma znacznik czasu, typ, opis (język naturalny) i pochodne metadane: **aktualność**, **ważność** (samodzielna ocena 1-10 przez agenta) i **trafność** (cosinus podobieństwo do bieżącego zapytania).

```
[2026-02-14 09:12:03] observation: Isabella Rodriguez asked me if I like jazz
[2026-02-14 09:14:22] reflection:   I enjoy long conversations about music
[2026-02-14 10:05:00] plan:         Attend Isabella's Valentine's Day party tonight
```

Odzyskiwanie pamięci łączy w sobie trzy wyniki: `score = w_recency * e^(-decay * age) + w_importance * importance + w_relevance * cos_sim`. Top-k wpisów wprowadza bieżący monit.

**Refleksja.** Okresowo (co N wspomnień lub w przypadku ważnych wydarzeń) agent generuje syntezy wyższego rzędu na podstawie ostatnich wspomnień. Wpisy refleksji wracają do strumienia i można je odzyskać jak każdą inną pamięć. W ten sposób agenci budują „porozumienia” – odpowiednik długoterminowych przekonań w architekturze.

**Plan.** Rozkład odgórny. Najpierw plan dnia w ogólnych zarysach („idź do pracy, zjedz kolację z Klausem”). Potem plany godzinowe. Następnie plany na poziomie działania. Plany podlegają rewizji: gdy obserwacja jest sprzeczna z planem, agent ponownie planuje dany segment.

### Dlaczego wszystkie trzy są ważne (ablacja)

Parka i in. przeprowadził ablacje, porzucając każdą obserwację, refleksję i plan. Każda ablacja szkodzi wiarygodności:

- Bez **obserwacji** agent traci kontekst i działa w oparciu o przestarzałe przekonania.
- Bez **refleksji** agent nie może tworzyć przekonań wyższego rzędu; interakcje pozostają płytkie.
- Bez **planu** zachowanie staje się reaktywnym hałasem; cele znikają.

Wyniki wiarygodności uzyskane od osób oceniających są najwyższe we wszystkich trzech przypadkach; upuszczenie któregokolwiek powoduje mierzalną regresję.

### Pojawienie się Walentynek

Jedna z agentek, Isabella Rodriguez, zostaje rozstawiona z celem „chce urządzić imprezę walentynkową w Hobbs Cafe 14 lutego o 17:00”. 24 pozostałych agentów nie otrzymuje takiego materiału siewnego. W symulowanych dniach:

1. Plan Izabeli obejmuje zapraszanie ludzi.
2. Każde zaproszenie staje się obserwacją w strumieniu pamięci sąsiada.
3. Refleksja sąsiadki rodzi przekonania: „Izabela urządza imprezę”.
4. Plan sąsiada uwzględnia „przyjęcie 14 lutego”.
5. Sąsiedzi mówią innym sąsiadom. Zaproszenie rozprzestrzenia się bez centralnej koordynacji.
6. 14 lutego o 17:00 kilku agentów spotyka się w Hobbs Cafe.

Jest to pojawienie się w sensie technicznym: zachowanie na poziomie systemu (partia) powstało w wyniku lokalnych interakcji (zaproszenia dwustronne + indywidualne planowanie) bez centralnego koordynatora.

### Udokumentowane tryby awarii

Parka i in. wyraźnie udokumentować:

- **Błędy norm przestrzennych.** Agenci wchodzą do zamkniętych sklepów. Agenci próbują korzystać z tej samej jednoosobowej łazienki. Agenci jedzą w pomieszczeniach nieprzeznaczonych do spożywania posiłków. Model nie wnioskuje norm społeczno-fizycznych z samego środowiska.
- **Przepełnienie pamięci.** Głębokie przebiegi symulacyjne powodują wzrost kosztów odzyskiwania pamięci. Praktyczne rozwiązanie: okresowe zagęszczanie pamięci (podsumuj i oczyść) i zanikanie wpisów o małej ważności.
- **Halacynacja refleksyjna.** Refleksje mogą stworzyć relacje, które nie istnieją w strumieniu pamięci. Środki zaradcze: uwzględnij identyfikatory pamięci źródłowej w monitach o refleksję i sprawdź w momencie pobierania.

Są to tryby awarii istotne dla produkcji: dziedziczy je każda symulacja agenta 2026.

### Trzyskładnikowe zasady implementacji

1. **Pamięć służy tylko do dopisywania.** Nigdy nie mutuj wpisu pamięci. Korekty to nowe wpisy.
2. **Oceny ważności są tanie.** Zadzwoń do LLM, aby ocenić ważność od 1 do 10 w momencie pisania. Zapisz wynik w pamięci podręcznej.
3. **Wyszukiwanie jest rankingowane, a nie filtrowane.** Top-k według łącznego wyniku; nie używaj twardych filtrów (które tracą kontekst).
4. **Odbicie odbywa się okresowo.** Wyzwalane, gdy suma ważności nieprzetworzonych wspomnień przekracza próg (np. 150).
5. **Plany podlegają rewizji.** Kiedy nowa obserwacja jest sprzeczna z planem, zregeneruj tylko dany segment, a nie cały plan.

### Agenci generatywni poza Smallville

Literatura uzupełniająca na lata 2024–2026 rozszerza tę architekturę:

- **Wieloagentowa symulacja społeczna na potrzeby badań politycznych/rynkowych.** Populacje podobne do Smallville symulują zachowania użytkowników w odpowiedzi na funkcje. Szybciej niż testy A/B; dokładność jest kwestionowana.
- **Sztuczna inteligencja NPC do gier.** Gry RPG z agentami Smallville tworzą nowe historie zamiast zadań opartych na scenariuszu.
- **Wzorce oceny agenta generatywnego.** Zamiast dokładności zadania, miarą staje się wiarygodność + spójność zachowania w długim okresie.

Architektura jest punktem odniesienia. Rozszerzenia zamieniają komponenty (przechowywanie wektorów pamięci, refleksja wzmocniona odzyskiwaniem, plan neurosymboliczny), ale zachowują trzyczęściową strukturę.

### Dlaczego ma to znaczenie w przypadku inżynierii wieloagentowej

Smallville jest dowodem na to, że pojawienie się wielu agentów jest tanie, jeśli komponenty są odpowiednie. Architektura została teraz zreplikowana w modelach open source (mniejsze LLM tracą wiarygodność z wdziękiem, a nie gwałtownie). Każdy system produkcyjny, który wymaga **wyłaniających się zachowań społecznych**, wykorzystuje ten kształt. Każdy system wymagający **ścisłego wykonania zadania** wykorzystuje wzorce nadzorcy/role/prymitywy z wcześniejszej fazy.

## Zbuduj to

`code/main.py` implementuje trzy komponenty w stdlib Python z zasadami agenta skryptowego (bez prawdziwego LLM). Demo odtwarza w miniaturze przyjęcie walentynkowe:

- `MemoryStream` — dziennik z możliwością dołączenia i sprawdzeniem aktualności/ważności/trafności.
- `reflect(stream)` — scenariuszowa refleksja nad niedawnymi ważnymi wspomnieniami.
- `plan(agent_state)` — plany na poziomie dnia i godziny oparte na bieżących przekonaniach.
- Scenariusz: 5 agentów. Agent 1 zaczyna od „imprezy o 17:00”. W przypadku symulowanych taktów zaproszenie rozprzestrzenia się, a agenci zbiegają się.

Uruchom:

```
python3 code/main.py
```

Oczekiwany wynik: ślad po zaznaczeniu. Do ostatniego zaznaczenia co najmniej 3 z 5 agentów pokazuje imprezę w swoim planie i spotykają się w miejscu imprezy. Pojedyncze ziarno spowodowało skoordynowane przybycie bez żadnego koordynatora.

## Użyj tego

`outputs/skill-simulation-designer.md` projektuje symulację agenta generatywnego: liczba agentów, schemat pamięci, częstotliwość refleksji, horyzont planu i metryka oceny.

## Wyślij to

Zasady symulacji produkcji:

- **Pamięć jest bazą danych.** Wybierz prawdziwy sklep (wektor DB, Postgres) w odpowiedniej skali. Stdlib w pamięci jest przeznaczony dla prototypów.
- **Zapisz ślad odzyskiwania.** Dla każdej akcji zarejestruj najważniejsze wspomnienia, które ją spowodowały. To jest twoja zdolność debugowania.
- **Tokeny budżetu na agenta.** Odzyskanie + odbicie + plan każdego agenta na tick to wywołania O(k) LLM. N agentów × T tików × liczba połączeń na tik może przyćmić Twój budżet.
- **Okresowo zmniejszaj pamięć.** Podsumuj i oczyść wpisy o małej ważności. Polityka przechowywania to decyzja projektowa, a nie szczegół.
- **Wykrywaj wyraźnie naruszenia norm przestrzennych/społecznych**. Architektura ich nie uczy.

## Ćwiczenia

1. Uruchom `code/main.py`. Potwierdź, że na imprezie zbiega się co najmniej 3 agentów. Zwiększ liczbę agentów do 10 — czy pojawienie się nadal ma miejsce?
2. Usuń krok refleksji. Jak wygląda zachowanie? Mapa do znaleziska po ablacji w Parku 2023.
3. Przedstaw konkurencyjny, rozstawiony cel („Klaus chce wygłosić wykład badawczy o 17:00”). Czy agenci dzielą się, czy może dominuje jeden cel? Co o tym decyduje?
4. Dodaj ograniczenia przestrzenne: Hobbs Cafe może pomieścić maksymalnie 4 agentów. Czy symulacja radzi sobie z przepełnieniem z wdziękiem, czy też trafia w schemat awarii „łazienka dla jednej osoby”?
5. Przeczytaj Park i in. (arXiv:2304.03442) Sekcja 6 (eksperymenty z zachowaniem wschodzącym). Wskaż jedno zachowanie, którego nie da się odtworzyć na Twojej miniaturze. Który element architektury wymagałby ulepszenia?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Strumień pamięci | „Dziennik agenta” | Tylko dołącz dziennik obserwacji, działań, przemyśleń, planów. |
| Aktualność | „Jak nowa jest pamięć” | Wynik zaniku wykładniczego według wieku. |
| Znaczenie | „Jak bardzo zależy agentowi” | Samodzielna ocena 1-10 w momencie pisania. Buforowane. |
| Trafność | „Jak powiązane z bieżącym zapytaniem” | Podobieństwo cosinusowe (oparte na osadzaniu). |
| Odbicie | „Wiara wyższego rzędu” | Synteza wygenerowana z niedawnych wspomnień, ponownie przyswojona jako nowe wspomnienie. |
| Zaplanuj | „Rozkład dnia/godziny/akcji” | Drzewo planu z góry na dół. Możliwość korekty, gdy obserwacje są sprzeczne. |
| Smallville | „Piaskownica Park 2023” | Symulacja z udziałem 25 agentów, która doprowadziła do pojawienia się Walentynek. |
| Wiarygodność | „Miernik jakości” | Wynik osoby oceniającej, czy zachowanie wydaje się wiarygodnym czynnikiem. |

## Dalsze czytanie

- [Park i in. — Agenci generatywni: interaktywne symulakry ludzkich zachowań](https://arxiv.org/abs/2304.03442) — architektura referencyjna
– [strona artykułu UIST '23](https://dl.acm.org/doi/10.1145/3586183.3606763) — miejsce publikacji
- [Wersja kodu Smallville](https://github.com/joonspk-research/generative_agents) — odniesienie do implementacji Pythona
- [Hayes-Roth 1985 — A Blackboard Architecture for Control] (https://www.sciencedirect.com/science/article/abs/pii/0004370285900639) — stan techniki dotyczący agentów pamięci strukturalnej