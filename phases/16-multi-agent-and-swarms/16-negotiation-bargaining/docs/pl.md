# Negocjacje i targowanie się

> Agenci negocjują zasoby, ceny, przydział zadań i warunki. Zestaw punktów odniesienia na rok 2026 jest jasny: NegotiationArena (arXiv:2402.05863) pokazuje, że LLM mogą zwiększyć zyski o ~20% poprzez manipulację osobowością („desperacja”); „Measuring Bargaining Abilities” (arXiv:2402.15813) pokazuje, że kupujący jest trudniejszy niż sprzedawca, a skala nie pomaga — ich **OG-Narrator** (deterministyczny generator ofert + narrator LLM) podniósł wskaźnik transakcji z 26,67% do 88,88%; konkurs autonomicznych negocjacji na dużą skalę (arXiv:2503.06416) przeprowadził ~180 tys. negocjacji i odkrył, że agenci **ukrywający łańcuch myśli** wygrywają, ukrywając rozumowanie przed odpowiednikami; Bhattacharya i in. Według wskaźników Harvard Negotiation Project z 2025 r. Llama-3 była najbardziej efektywna, Claude-3 agresywna, a GPT-4 najuczciwsza. Ta lekcja implementuje protokół Contract Net Protocol (przodek FIPA, lekcja 02), łączy kupującego/sprzedawcę w stylu LLM, przeprowadza dekompozycję w stylu OG-Narratora i mierzy, jak zmienia się stawka transakcji przy każdym wyborze strukturalnym.

**Typ:** Ucz się + Buduj
**Języki:** Python (stdlib)
**Wymagania wstępne:** Faza 16 · 02 (Dziedzictwo FIPA-ACL), Faza 16 · 09 (Równoległe sieci roju)
**Czas:** ~75 minut

## Problem

Dwóch agentów musi uzgodnić cenę. Pozostawieni samym sobie z czysto językowymi podpowiedziami LLM z lat 2024–2026 zawierają transakcje po zaskakująco niskich stawkach (~27% w przypadku ściśle sparametryzowanych okazji w arXiv:2402.15813). Skala tego nie rozwiązuje: GPT-4 nie jest strukturalnie lepszy w negocjacjach niż GPT-3.5; lepiej radzi sobie z *językiem* negocjacji.

Podstawowym problemem jest to, że LLM łączą dwa zawody – decydowanie o ofercie i opowiadanie o ofercie. OG-Narrator rozdzielił je: deterministyczny generator ofert oblicza ruchy numeryczne; LLM tylko opowiada. Wskaźnik transakcji skacze do ~89%.

Odzwierciedla to klasyczne odkrycie dotyczące wielu agentów: wygrywa oddzielenie mechanizmu od warstwy komunikacyjnej. Contract Net Protocol (FIPA, 1996; Smith, 1980) jest referencyjnym mechanizmem rynku zadań. Podłącz LLM do gniazda narracji, a otrzymasz nowoczesny rynek zadań oparty na LLM.

## Koncepcja

### Umowa netto, w jednym akapicie

Protokół sieciowy kontraktu Smitha z 1980 r.: **menedżer** ogłasza **zaproszenie do składania wniosków (cfp)**; **licytanci** odpowiadają wiadomościami **proponuj** zawierającymi ich oferty; menedżer wybiera zwycięzcę i wysyła **propozycję akceptacji** do zwycięzcy i **propozycję odrzucenia** do przegranych. Zwycięzca wykonuje pracę. Opcjonalny komunikat: **odmowa** (oferent odmawia złożenia oferty). FIPA skodyfikowała to jako protokół interakcji `fipa-contract-net`.

### Dlaczego OG-Narrator wygrywa

„Pomiar zdolności przetargowych modeli językowych” (arXiv:2402.15813) zauważył, że:

- LLM często łamią zasady negocjacji (oferują po bezsensownych cenach, ignorują ZOPA drugiej strony).
- Słabo się zakotwiczają (akceptują złe pierwsze oferty, kontrofertę na kwoty symboliczne, a nie strategiczne).
- Sama skala tego nie rozwiąże. Większe modele tworzą bardziej wiarygodny język z podobnymi błędami strategicznymi.

Rozkład OG-Narratora:

```
           ┌──────────────────┐        ┌──────────────────┐
  state  → │ offer generator  │ price → │  LLM narrator    │ → message
           │  (deterministic) │        │  (writes the     │
           │                  │        │   human-style    │
           └──────────────────┘        │   accompaniment) │
                                       └──────────────────┘
```

Generator ofert to klasyczna strategia negocjacyjna: model negocjacji Rubinsteina, strategia Zeuthena lub prosta strategia „wet za wet za cenę”. LLM opowiada. Wiadomość zawiera deterministyczną cenę i oprawę w języku naturalnym.

Kurs transakcji skacze, ponieważ:
- Ceny pozostają w strefie przetargowej.
- Kotwice mają charakter strategiczny, a nie emocjonalny.
- LLM robi to, w czym jest dobry: pisanie.

### Wyniki NegotiationArena

arXiv:2402.05863 stanowi kanoniczny punkt odniesienia. Główne ustalenia:

- LLM mogą zwiększyć zyski o ~20% poprzez przyjęcie person („Desperacko chcę to sprzedać do piątku”) – manipulacja personami to prawdziwa taktyka.
- Agenci uczciwi/współpracujący są wykorzystywani przez wrogich agentów; obrona wymaga wyraźnej kontrapozycji.
- Symetryczne pary zbiegają się, dając niesprawiedliwe wyniki w około 40% scenariuszy porównawczych.

To nie jest tak, że „LLM są złymi negocjatorami”. To „LLM negocjują za dużo jak ludzie, łącznie z częściami, które można wykorzystać”.

### Ukrywanie łańcucha myśli

W ramach wielkoskalowego konkursu negocjacji autonomicznych (arXiv:2503.06416) przeprowadzono około 180 tys. negocjacji w ramach wielu strategii LLM. Zwycięzcy ukryli swoje uzasadnienie przed innymi:

- Jeśli agent wydrukuje w publicznie widocznym notatniku „Pójdę tylko do $75; my reservation price is $70”, przeciwnik czyta to.
- Zwycięzcy prywatnie obliczają strategię; kanał wyjściowy zawiera jedynie ofertę i minimalną wymaganą narrację.

Jest to echo klasycznej teorii gier z 2026 r. (Aumann 1976 na temat racjonalności i informacji): ujawnienie zwrotu kosztów prywatnej wyceny. LLM nie przeczuwają tego i chętnie wpisują swoje zastrzeżenia w śladach rozumowania, które stają się widoczne dla drugiej strony.

Inżynieria na wynos: oddziel kontekst prywatnego notatnika od kontekstu wiadomości publicznych. Nie opcjonalne.

### Bhattacharya i in. 2025 — rankingi modelek

Wskaźniki projektu Harvard Negotiation Project (negocjacje oparte na zasadach, przestrzeganie BATNA, wzajemność odsetek):

- **Llama-3** była najskuteczniejsza w zawieraniu transakcji (stopa transakcji + wypłata).
- **Claude-3** był najbardziej agresywnym negocjatorem (wysokie kotwice, późne ustępstwa).
- **GPT-4** był najuczciwszy (najmniejsza różnica w wypłatach pomiędzy parami).

To jest migawka z 2025 roku. Nie chodzi o to, który model zwycięży w kwietniu 2026 r. – chodzi o to, że różne modele podstawowe mają trwałe style negocjacyjne. Zespoły heterogeniczne (lekcja 15) uwzględniają to jako źródło różnorodności.

### Przydzielanie zadań poprzez Contract Net + LLM

Nowoczesne ponowne wykorzystanie Contract Net dla wielu agentów LLM:

1. Agent menedżerski rozkłada zadanie na jednostki.
2. Transmisje `cfp` z opisem zadania do agentów roboczych.
3. Każdy pracownik zwraca ofertę: `(price, eta, confidence)`, gdzie ceną mogą być tokeny, jednostki obliczeniowe lub dolary.
4. Menedżer wybiera zwycięzców (pojedynczych lub wielokrotnych, w zależności od zadania) i nagrody.
5. Odrzuceni pracownicy mogą składać oferty na inne zadania.

Skaluje się to znacznie powyżej 100 pracowników, ponieważ koordynacja polega na rozgłaszaniu i odpowiadaniu, a nie na synchronicznym czacie. Używane w produkcji: wzorce orkiestracji Microsoft Agent Framework, niektóre implementacje LangGraph.

### Interaktywne negocjacje LLM z interesariuszami

NeurIPS 2024 (https://proceedings.neurips.cc/paper_files/paper/2024/file/984dd3db213db2d1454a163b65b84d08-Paper-Datasets_and_Benchmarks_Track.pdf) wprowadza wielostronne gry punktowane z **tajnymi wynikami** i **minimalne progi akceptacji**. Każdy interesariusz ma prywatne media; LLM musi wywnioskować je z komunikatów. Jest to uogólnienie negocjacji dwupartyjnych na tworzenie koalicji N-partyjnej. Istotne dla rynków zadań produkcyjnych z heterogenicznymi możliwościami pracowników.

### Zasada narracji kontra mechanizmu

We wszystkich punktach odniesienia negocjacyjnych na lata 2024–2026 spójna zasada inżynieryjna brzmi:

> Niech LLM opowie. Nie pozwól, aby LLM obliczyła ofertę.

Jeśli oferta musi być liczbą (cena, ETA, ilość), wygeneruj ją deterministycznie na podstawie stanu negocjacji i poproś LLM o sporządzenie ramki. Jeśli oferta musi mieć strukturę propozycji (rozkład zadań, przypisanie ról), pozwól LLM ją przygotować, ale przed wysłaniem zweryfikuj ją pod kątem schematu i sprawdź ograniczenia.

## Zbuduj to

`code/main.py` implementuje:

- `ContractNetManager`, `ContractNetTask`, `Bid` — menedżer + licytanci, transmituj cfp, zbieraj propozycje, nagradzaj.
- `og_narrator_bargain(state, rng)` — Kupujący OG-Narrator: deterministyczne ustępstwo w stylu Zeuthena w stronę punktu środkowego.
- `seller_response(state, rng)` — deterministyczna polityka dotycząca kontrofert sprzedawcy (podstawa strukturalna obu stylów).
- `naive_llm_bargain(state, rng)` — symuluje targacza obejmującego wyłącznie LLM: wybiera ceny o dużej rozbieżności, często poza ZOPA.
- Pomiar: wskaźnik transakcji z ponad 1000 prób z próbkami świeżych cen rezerwacji na każdą próbę.

Uruchom:

```
python3 code/main.py
```

Oczekiwany wynik: wskaźnik transakcji naiwnych-LLM ~65-75%; Wskaźnik transakcji OG-Narrator ~ 85-95%; różnica 15–25 punktów jest strukturalną zaletą oddzielenia generowania ofert od narracji. Plus przykład alokacji rynku zadań w ramach sieci kontraktów z trzema oferentami i jednym zadaniem.

## Użyj tego

`outputs/skill-bargainer-designer.md` projektuje protokół negocjacji: kto generuje oferty (deterministyczne lub LLM), kto opowiada, w jaki sposób prywatne zdrapki oddzielają się od wiadomości publicznych i jak monitorowana jest stawka transakcji.

## Wyślij to

Lista kontrolna negocjacji produkcyjnych:

- **Oddzielny notatnik.** Stan prywatny nigdy nie dociera do kontekstu odpowiednika. To nie podlega negocjacjom.
- **Deterministyczne generowanie ofert.** Ceny, ilości, szacowany czas dotarcia: obliczaj, nie pytaj.
- **Weryfikuj wszystkie przychodzące oferty** względem schematu. Odrzuć oferty spoza ZOPA na granicy protokołu.
- **Rundy związane.** Maksymalnie 3-5 rund; w przypadku impasu eskaluj do mediatora.
- **Ciągle mierz kurs transakcji i wariancję wypłat**. Objawem jest spadający kurs transakcji — często jest to natychmiastowy dryf lub atak strony przeciwnej.
- **Zapisz wszystkie odrzucone propozycje** z uzasadnieniem deterministycznym. Menedżerowie sieci kontraktowej przegrywający oferenci muszą zrozumieć dlaczego.

## Ćwiczenia

1. Uruchom `code/main.py`. Potwierdź, że OG-Narrator przewyższa naiwny LLM pod względem stawki transakcji. O ile?
2. Wprowadź **ulepszenie wypłat w oparciu o osobowość** (arXiv:2402.05863) — kupujący przyjmuje postawę „desperacko chcący kupić w tym tygodniu” tylko w narracji, generator ofert niezmieniony. Czy kurs transakcji lub wypłata ulegają zmianie?
3. Zaimplementuj **ukrycie** łańcucha myślowego: utrzymuj prywatny ciąg notatnika, który nie jest przekazywany do odpowiednika. Co się stanie, jeśli przypadkowo wycieknie (symuluj, zamieniając kanały)?
4. Rozszerzenie kontraktu netto na aukcję N-licytantów z ceną minimalną. Kiedy wszystkie oferty przekraczają cenę minimalną, w jaki sposób menedżer dokonuje wyboru pomiędzy najniższą ceną a najwyższą jakością? Którą zasadę przyznawania nagród wybierasz i dlaczego?
5. Przeczytaj Bhattacharyę i in. Dane z 2025 r. dotyczące projektu Harvard Negotiation Project. Wprowadź dwóch negocjatorów o różnych stylach (agresywny vs uczciwy). Zmierz wariancję wypłat w parach symetrycznych i asymetrycznych.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Kontrakt Netto | „Rynek zadań” | Smith 1980, FIPA 1996. cfp + zaproponuj + zaakceptuj/odrzuć. Kanoniczny rynek zadań. |
| ZOPA | „Strefa możliwego porozumienia” | Nakładanie się maks. kupującego i min. sprzedającego. Oferty spoza niego nie mogą zostać zamknięte. |
| BATNA | „Najlepsza alternatywa dla wynegocjowanego porozumienia” | Twoja pomoc w przypadku niepowodzenia tej transakcji. Ustawia cenę rezerwacji. |
| OG-Narrator | „Generator ofert + narrator” | Dekompozycja: oferta deterministyczna, narracja LLM. |
| Strategia Zeuthena | „Koncesja minimalizująca ryzyko” | Klasyczny generator ofert udzielający rabatów w oparciu o limity ryzyka. |
| Negocjacje Rubinsteina | „Równowaga oferty alternatywnej” | Model teoretyczny gier dla negocjacji w nieskończonym horyzoncie z dyskontowaniem. |
| Ukrywanie CoT | „Ukryj swoje rozumowanie” | Zwycięzcy w arXiv:2503.06416 zachowali prywatne notatniki; kanał publiczny pokazuje tylko ofertę. |
| Manipulacja osobą | „Postawa emocjonalna” | arXiv:2402.05863: ~20% zysku z wypłat od osób desperackich/pilnych. |

## Dalsze czytanie

- [NegotiationArena](https://arxiv.org/abs/2402.05863) — punkt odniesienia; ustalenia dotyczące manipulacji i wykorzystywania osób
– [Pomiar zdolności przetargowych modeli językowych](https://arxiv.org/abs/2402.15813) — OG-Narrator i wynik kupującego trudniejszego niż sprzedający
- [Konkurs w zakresie autonomicznych negocjacji na dużą skalę](https://arxiv.org/abs/2503.06416) — ~180 tys. negocjacji; wygrywa ukrywanie łańcucha myśli
- [LLM – Interaktywne negocjacje z interesariuszami (NeurIPS 2024)](https://proceedings.neurips.cc/paper_files/paper/2024/file/984dd3db213db2d1454a163b65b84d08-Paper-Datasets_and_Benchmarks_Track.pdf) – wielostronne gry punktowane z tajnymi narzędziami
- [Smith 1980 — The Contract Net Protocol] (https://ieeexplore.ieee.org/document/1675516) — klasyczny mechanizm, IEEE Transactions on Computers