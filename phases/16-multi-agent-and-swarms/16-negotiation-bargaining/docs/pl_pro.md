# Negocjacje i procesy przetargowe w systemach wieloagentowych

> Agenty negocjują podział zasobów, ceny, alokację zadań oraz warunki umów. Stan wiedzy i benchmarków (na rok 2026) dostarcza jasnych wniosków: praca NegotiationArena (arXiv:2402.05863) wykazuje, że modele LLM mogą zwiększyć swoje zyski o ok. 20% poprzez manipulację profilem osobowościowym (np. symulowanie pośpiechu lub desperacji); badanie „Measuring Bargaining Abilities” (arXiv:2402.15813) dowodzi, że rola kupującego jest znacznie trudniejsza niż sprzedawcy, a proste skalowanie modeli nie przynosi poprawy. Autorzy tej ostatniej pracy, wdrażając architekturę **OG-Narrator** (połączenie deterministycznego generatora ofert z narratorem LLM), podnieśli wskaźnik skuteczności transakcji z 26,67% do aż 88,88%. Z kolei w wielkoskalowym konkursie autonomicznych negocjacji (arXiv:2503.06416), obejmującym ok. 180 tys. symulacji, wykazano, że agenty **ukrywające swój łańcuch myśli (hidden Chain of Thought)** osiągają lepsze wyniki dzięki zatajeniu strategii przed oponentami. Według badań Bhattacharya et al. (2025) bazujących na wskaźnikach Harvard Negotiation Project, model Llama-3 był najskuteczniejszy w zawieraniu umów, Claude-3 wykazywał najbardziej agresywną postawę, a GPT-4 był najbardziej sprawiedliwy. W tej lekcji zaimplementujemy protokół Contract Net Protocol (prekursor standardu FIPA, Lekcja 02), połączymy kupującego i sprzedawcę opartych na LLM, wdrożymy dekompozycję w stylu OG-Narrator i zmierzymy wpływ decyzji architektonicznych na wskaźnik zawieranych transakcji.

**Typ:** Ucz się + Buduj
**Języki:** Python (biblioteka standardowa)
**Wymagania wstępne:** Faza 16 · 02 (Dziedzictwo FIPA-ACL), Faza 16 · 09 (Równoległe sieci roju)
**Czas:** ~75 minut

## Problem

Dwóch agentów musi uzgodnić cenę. Pozostawieni samym sobie z czysto językowymi promptami LLM zawierają transakcje ze stosunkowo niską skutecznością (ok. 27% dla ściśle zdefiniowanych parametrów transakcji w arXiv:2402.15813). Skalowanie modeli nie rozwiązuje tego problemu: GPT-4 nie wykazuje strukturalnej przewagi nad GPT-3.5 w procesach decyzyjnych, a jedynie lepiej posługuje się samym językiem negocjacji.

Kluczowym problemem jest fakt, że modele LLM łączą w sobie dwie różne role: podejmowanie decyzji o wysokości oferta oraz językową oprawę tej oferty. Architektura OG-Narrator rozdziela te odpowiedzialności: deterministyczny generator ofert wylicza optymalne wartości liczbowe, natomiast LLM odpowiada wyłącznie za sformułowanie naturalnej wypowiedzi. Dzięki temu wskaźnik zawieranych transakcji wzrasta do ok. 89%.

Potwierdza to klasyczną zasadę projektowania systemów wieloagentowych: kluczem do sukcesu jest oddzielenie mechanizmu decyzyjnego od warstwy komunikacyjnej. Protokół Contract Net (FIPA, 1996; Smith, 1980) stanowi referencyjne rozwiązanie dla rynków zadań. Łącząc go z LLM w roli narratora, otrzymujemy nowoczesną, zautomatyzowaną platformę alokacji zadań.

## Koncepcja

### Contract Net w zarysie

Protokół Contract Net zaproponowany przez Smitha w 1980 r. działa następująco: **koordynator (manager)** publikuje **zaproszenie do składania ofert (call for proposal - cfp)**; **oferenci (bidders)** odpowiadają komunikatami zawierającymi ich propozycje (**propose**); koordynator wybiera najkorzystniejszą ofertę, wysyłając potwierdzenie akceptacji (**accept-proposal**) do zwycięzcy oraz odrzucenie (**reject-proposal**) do pozostałych uczestników. Zwycięzca przystępuje do realizacji zadania. Opcjonalnie oferent może odmówić składania propozycji za pomocą komunikatu **refuse**. Organizacja FIPA skodyfikowała ten schemat jako standard `fipa-contract-net`.

### Dlaczego OG-Narrator wygrywa

W pracy „Measuring Bargaining Abilities of LLMs” (arXiv:2402.15813) zaobserwowano, że:

- Modele LLM często naruszają reguły negocjacji (np. proponując ceny pozbawione sensu lub ignorując strefę możliwego porozumienia — ZOPA oponenta).
- Wykazują słabe zakotwiczenie (akceptują niekorzystne pierwsze oferty, a ich kontroferty opierają się na symbolicznych, a nie strategicznych ustępstwach).
- Samo skalowanie parametrów modelu nie eliminuje tych wad. Większe modele generują bardziej przekonujący tekst, lecz powielają te same błędy strategiczne.

Dekompozycja w architekturze OG-Narrator:

```
            ┌──────────────────┐         ┌──────────────────┐
  stan    → │ generator ofert  │ cena  → │  narrator LLM    │ → komunikat
            │ (deterministyczny)│        │ (redaguje tekst  │
            │                  │         │  w stylu ludzkim)│
            └──────────────────┘         └──────────────────┘
```

Generator ofert bazuje na klasycznych modelach teorii gier: np. model negocjacji Rubinsteina, strategia Zeuthena lub proste podejście typu wet za wet (tit-for-tat) dostosowane do cen. LLM pełni rolę narratora: ubiera wyliczoną cenę w naturalny i profesjonalny komunikat.

Wskaźnik zawieranych transakcji rośnie, ponieważ:
- Proponowane ceny mieszczą się w strefie porozumienia (ZOPA).
- Punkty zakotwiczenia wynikają ze strategii matematycznej, a nie z emocjonalnego wpływu promptu.
- Model LLM realizuje zadanie, w którym jest najlepszy: generowanie spójnego i naturalnego tekstu.

### Wnioski z projektu NegotiationArena

arXiv:2402.05863 stanowi kluczowy punkt odniesienia. Najważniejsze wnioski:

- Modele LLM mogą zwiększyć zyski z transakcji o ok. 20% poprzez przyjęcie dedykowanego profilu (np. „zależy mi na sprzedaży przed końcem tygodnia”). Strategiczne pozycjonowanie profilu jest potężną taktyką.
- Agenty nastawione na uczciwą współpracę są łatwo wykorzystywane przez oponentów o profilu agresywnym; obrona przed tym wymaga wdrożenia mechanizmów kontrargumentacji.
- Symetryczne pary agentów mają tendencję do zawierania transakcji o nierównomiernym podziale zysków w ok. 40% testowanych scenariuszy.

Nie oznacza to, że LLM są kiepskimi negocjatorami. Zjawisko to wynika z faktu, że modele LLM negocjują zbyt podobnie do ludzi — powielając ludzkie błędy poznawcze, które oponenci mogą łatwo wykorzystać.

### Ukrywanie łańcucha myśli (Hidden Chain of Thought)

W ramach wielkoskalowego konkursu negocjacji autonomicznych (arXiv:2503.06416) przeprowadzono ok. 180 tys. symulacji. Zwycięskie strategie opierały się na ukrywaniu procesu wnioskowania przed oponentem:

- Jeśli agent generuje widoczne dla oponenta przemyślenia typu „zgodzę się maksymalnie na 75 USD, moja cena rezerwacji to 70 USD”, druga strona natychmiast wykorzysta tę informację.
- Najbardziej skuteczne agenty kalkulują strategię w prywatnym obszarze roboczym (scratchpad), a publiczny kanał komunikacji zawiera wyłącznie ofertę z niezbędną oprawą językową.

Wpisuje się to w klasyczną teorię gier (np. twierdzenie Aumanna z 1976 r. o zgodności informacji): ujawnienie wyceny rezerwowej niszczy pozycję negocjacyjną. Modele LLM nie mają wbudowanej intuicji bezpieczeństwa informacji i chętnie wypisują swoje ograniczenia w ogólnodostępnym łańcuchu myśli (Chain of Thought), czyniąc je widocznymi dla oponentów.

Wniosek inżynieryjny: bezwzględnie rozdzielaj prywatny obszar wnioskowania (CoT/scratchpad) od publicznych komunikatów wysyłanych do partnera.

### Harvard Negotiation Project (2025) — rankingi modeli

Wyniki oceny zachowań modeli LLM w oparciu o kryteria Harvardu:

- **Llama-3** okazała się najskuteczniejsza w domykaniu transakcji (najwyższy wskaźnik sukcesu oraz zyskowność).
- **Claude-3** wykazywał najbardziej agresywną postawę (wysokie punkty zakotwiczenia, niechęć do ustępstw).
- **GPT-4** dążył do sprawiedliwego podziału (najniższe dysproporcje w zyskach stron).

Są to dane z 2025 roku. Kluczowy wniosek nie dotyczy tego, który model jest najlepszy w danej chwili, ale faktu, że różne modele posiadają odmienne, wbudowane style negocjacji. Heterogeniczność zespołu (Lekcja 15) pozwala wykorzystać te różnice jako zaletę.

### Alokacja zadań za pomocą Contract Net i LLM

Współczesna adaptacja protokołu Contract Net w systemach agentowych:

1. Agent koordynujący (manager) dzieli złożone zadanie na mniejsze komponenty.
2. Rozsyła zaproszenie do składania ofert (`cfp`) z opisem wymagań do agentów wykonawczych (workers).
3. Agenty wykonawcze zwracają swoje propozycje w formacie: `(price, eta, confidence)`, gdzie cena może być wyrażona w tokenach, mocy obliczeniowej lub jednostkach monetarnych.
4. Koordynator wybiera najkorzystniejsze oferty (jednego lub wielu wykonawców) i przydziela zadania.
5. Agenty, których oferty zostały odrzucone, mogą aplikować do innych dostępnych zadań.

Model tem z powodzeniem skaluje się do ponad 100 wykonawców, ponieważ koordynacja opiera się na komunikatach asynchronicznych (pub/sub), a nie na synchronicznej dyskusji na czacie. Wzorce te są powszechnie stosowane w Microsoft Agent Framework oraz zaawansowanych procesach w LangGraph.

### Wielostronne negocjacje z ukrytymi preferencjami

W publikacjach z konferencji NeurIPS 2024 przedstawiono wielostronne negocjacje oparte na **ukrytych preferencjach** (private payoffs) i **progach satysfakcji**. Każdy z uczestników posiada unikalny profil zysków, który pozostali muszą wywnioskować wyłącznie z przebiegu konwersacji. Uogólnia to klasyczne negocjacje dwustronne do problemu tworzenia koalicji wielostronnych, co ma kluczowe znaczenie przy projektowaniu dynamicznych rynków zadań.

### Złota zasada: rozdział narracji od mechanizmu decyzyjnego

Zasada inżynieryjna wyłaniająca się ze wszystkich badań negocjacyjnych brzmi:

> Używaj LLM do prowadzenia dialogu, ale nie pozwól LLM obliczać wartości ofert.

Jeśli oferta wymaga konkretnych liczb (cena, czas wykonania, wolumen), wyliczaj je za pomocą deterministycznych algorytmów na podstawie stanu gry, a modelowi LLM zlecaj wyłącznie ubranie tych danych w tekst. W przypadku ofert strukturyzowanych (np. podział ról, plany projektowe) pozwól LLM przygotować propozycję, ale przed wysłaniem zwaliduj ją ze schematem i sprawdź reguły biznesowe.

## Zbuduj to

Plik `code/main.py` zawiera implementację:

- Klas `ContractNetManager`, `ContractNetTask`, `Bid` — koordynator i licytanci, rozsyłanie cfp, zbieranie ofert i przydział zadań.
- Funkcji `og_narrator_bargain(state, rng)` — algorytm kupującego w stylu OG-Narrator: deterministyczne ustępstwo według strategii Zeuthena dążące do konsensusu.
- Funkcji `seller_response(state, rng)` — deterministyczny generator kontrofert sprzedawcy (stanowiący logiczną bazę dla obu stylów).
- Funkcji `naive_llm_bargain(state, rng)` — symulacja licytatora opartego wyłącznie na LLM (generującego niestabilne ceny, często wykraczające poza ZOPA).
- Systemu pomiarowego: wskaźnik sukcesu transakcji na bazie ponad 1000 iteracji ze zmiennymi cenami rezerwowymi.

Uruchomienie:

```bash
python3 code/main.py
```

Oczekiwany wynik: wskaźnik sukcesu dla naiwnego modelu LLM wynosi ok. 65-75%, podczas gdy dla modelu OG-Narrator sięga ok. 85-95%. Różnica 15-25 punktów procentowych to strukturalna korzyść płynąca z rozdzielenia logiki decyzyjnej od generowania tekstu. Program wypisuje również przykładową alokację zadań w sieci Contract Net dla trzech oferentów.

## Zastosowanie

Plik `outputs/skill-bargainer-designer.md` definiuje metodologię projektowania systemów negocjacyjnych: podział ról na kalkulację i narrację, separację prywatnych notatników od wiadomości publicznych oraz monitorowanie wskaźników sukcesu transakcji.

## Wdrożenie produkcyjne

Lista kontrolna dla systemów negocjacyjnych:

- **Prywatny scratchpad (notatnik).** Stan wewnętrzny (np. cena maksymalna, BATNA) nigdy nie może trafić do kontekstu widocznego dla oponenta.
- **Deterministyczne wyliczanie ofert.** Wszelkie liczby (ceny, terminy, wolumeny) obliczaj programistycznie; nie zlecaj ich szacowania modelom LLM.
- **Walidacja ofert wejściowych.** Sprawdzaj oferty oponentów pod kątem zgodności ze schematem JSON i regułami biznesowymi (ZOPA) na granicy systemu.
- **Limity rund.** Narzuć sztywny limit 3-5 rund negocjacyjnych; w przypadku impasu przekaż sprawę do arbitrażu.
- **Monitorowanie metryk.** Śledź wskaźniki skuteczności transakcji oraz rozkład zysków stron. Spadek skuteczności sygnalizuje dryf modelu lub zmianę strategii oponentów.
- **Logowanie odrzuconych ofert.** Zapisuj przyczyny odrzucenia propozycji w sieci Contract Net, aby zapewnić transparentność procesu alokacji zadań.

## Ćwiczenia

1. Uruchom `code/main.py`. Potwierdź przewagę architektury OG-Narrator nad naiwnym modelem LLM i odczytaj różnicę w skuteczności transakcji.
2. Zaimplementuj modyfikację profilu opartą na pozycjonowaniu (arXiv:2402.05863): niech kupujący symuluje pośpiech w generowanym tekście (np. „muszę dokonać zakupu do piątku”), zachowując niezmieniony generator ofert. Sprawdź, jak wpływa to na wskaźnik transakcji i ostateczną cenę.
3. Zaimplementuj pełne ukrywanie łańcucha myśli: zdefiniuj zmienną przechowującą prywatne kalkulacje agenta i upewnij się, że nie jest ona przekazywana do oponenta. Zasymuluj wyciek tych danych (np. poprzez błędne przekazanie zmiennej) i zaobserwuj konsekwencje.
4. Rozszerz protokół Contract Net o obsługę aukcji z N licytantami i ceną minimalną (reserve price). Zaprojektuj algorytm wyboru oferty przez managera uwzględniający kompromis między ceną a deklarowaną jakością wykonania.
5. Bazując na wynikach Harvard Negotiation Project (2025), zaimplementuj dwie różne osobowości agentów (agresywną i ugodową). Przeprowadź symulacje w parach symetrycznych i asymetrycznych, mierząc dysproporcje w podziale zysków.

## Kluczowe terminy

| Termin | Obiegowe określenie | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Contract Net | „Rynek zadań” | Protokół Smitha (1980) i FIPA (1996): zapytanie (cfp) + propozycja (propose) + akceptacja/odrzucenie. |
| ZOPA | „Obszar porozumienia” | Zakres cenowy pomiędzy ceną maksymalną kupującego a ceną minimalną sprzedającego. |
| BATNA | „Najlepsza alternatywa” | Najkorzystniejsze działanie, jakie można podjąć w przypadku braku porozumienia. Określa próg opłacalności transakcji. |
| OG-Narrator | „Kalkulator + Pisarz” | Architektura dzieląca proces na deterministyczne wyliczanie ofert oraz redagowanie tekstu przez LLM. |
| Strategia Zeuthena | „Ustępstwo oparte na ryzyku” | Klasyczny algorytm negocjacyjny wyliczający ustępstwa na podstawie szacowanego ryzyka zerwania rozmów. |
| Negocjacje Rubinsteina | „Model naprzemiennych ofert” | Teoretyczny model negocjacji wieloturnowych z uwzględnieniem czynnika dyskontującego czas. |
| Ukrywanie CoT | „Prywatny scratchpad” | Przechowywanie procesu wnioskowania w prywatnym obszarze pamięci w celu ochrony strategii negocjacyjnej (arXiv:2503.06416). |
| Pozycjonowanie profilu | „Manipulacja osobowością” | Zmiana stylu wypowiedzi (np. symulowanie desperacji) w celu uzyskania lepszych warunków transakcji (arXiv:2402.05863). |

## Literatura uzupełniająca

- [NegotiationArena](https://arxiv.org/abs/2402.05863) — praca naukowa analizująca wpływ pozycjonowania profili na zyski z negocjacji.
- [Measuring Bargaining Abilities of LLMs](https://arxiv.org/abs/2402.15813) — publikacja opisująca przewagi architektury OG-Narrator oraz trudności w roli kupującego.
- [Large-Scale Autonomous Negotiation Competition](https://arxiv.org/abs/2503.06416) — analiza 180 tys. negocjacji wykazująca kluczowe znaczenie ukrywania łańcucha myśli.
- [LLMs for Interactive Stakeholder Negotiation (NeurIPS 2024)](https://proceedings.neurips.cc/paper_files/paper/2024/file/984dd3db213db2d1454a163b65b84d08-Paper-Datasets_and_Benchmarks_Track.pdf) — gry wielostronne oparte na ukrytych preferencjach.
- [Smith 1980 — The Contract Net Protocol](https://ieeexplore.ieee.org/document/1675516) — klasyczna praca naukowa definiująca protokół alokacji zadań w systemach rozproszonych.
