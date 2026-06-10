# Zautomatyzowane badania nad dopasowaniem (Anthropic AAR)

> Anthropic uruchomił równoległe zespoły badawcze oparte na agentach Claude Opus 4.6 (Autonomous Alignment Researchers) w odizolowanych piaskownicach. Ich działania koordynowane były za pośrednictwem wspólnego forum, którego logi znajdowały się poza piaskownicami (dzięki czemu agenci nie mieli możliwości modyfikacji własnych zapisów). W zadaniu uczenia typu słaby-do-silnego (weak-to-strong training) agenci AAR osiągnęli lepsze wyniki niż badacze-ludzie. Zauważono jednak, że sztywne, narzucane z góry przepływy pracy (prescribed workflows) często ograniczały elastyczność AAR i pogarszały ich skuteczność. Automatyzacja badań nad dopasowaniem drastycznie kompresuje osie czasu, co stwarza dokładnie te ryzyka niedopasowania (misalignment), do wykrywania których zaprojektowano zasady RSP.

**Typ:** Ucz się
**Języki:** Python (biblioteka standardowa, symulator równoległego forum badawczego)
**Wymagania wstępne:** Faza 15 · 05 (AI Scientist v2), Faza 15 · 04 (DGM)
**Czas:** ~60 minut

## Problem

Badania nad dopasowaniem AI (alignment) pochłaniają ogromną ilość czasu i pracy ludzkich naukowców. Zagadnienia takie jak skalowalny nadzór (scalable oversight), specyfikacja funkcji nagrody czy uogólnianie typu słaby-do-silnego wymagają eksperymentów trwających tygodniami. W miarę jak możliwości modeli rosną w tempie wykładniczym, zapotrzebowanie na badania nad bezpieczeństwem rośnie znacznie szybciej niż liczba wykwalifikowanych specjalistów.

Koncepcja zautomatyzowanych badań nad dopasowaniem (Automated Alignment Research, AAR) zakłada wykorzystanie tych samych modeli pionierskich (frontier models) do rozwiązywania problemów bezpieczeństwa. Raport firmy Anthropic z 2026 roku dotyczący badań AAR nad uogólnianiem słaby-do-silnego (alignment.anthropic.com/2026/automated-w2s-researcher/) stanowi jeden z pierwszych publicznych wyników działania wdrożonego systemu tej klasy.

Wyniki są obiecujące: agenci AAR poradzili sobie z zadaniem badawczym lepiej niż ludzie stanowiący linię bazową. Jednak ten sukces skupia w jednym miejscu wszystkie problemy poruszane w tej fazie szkolenia. Jeśli badania nad dopasowaniem można w pełni zautomatyzować, to samo można zrobić z pracami nad obchodzeniem zabezpieczeń (jailbreaking/capabilities). Z myślą o takich pętlach samodoskonalenia laboratoria projektują progi bezpieczeństwa w swoich politykach odpowiedzialnego skalowania (RSP).

## Koncepcja

### Architektura (opisana publicznie)

- **Agenci równolegli.** Wiele instancji Claude Opus 4.6 działa jako AAR – każda w odrębnej, niezależnej piaskownicy. Piaskownice nakładają ścisłe limity na system plików, dostęp do sieci oraz uruchamiane procesy.
- **Wspólne forum.** Wyniki są publikowane na wspólnym forum, którego baza danych znajduje się całkowicie poza piaskownicami agentów. Agenci mogą odczytywać dane z forum, ale nie mają uprawnień do edycji ani usuwania wpisów z poziomu swoich kontenerów.
- **Przydział zadań.** Zaprojektowana przez ludzi kolejka zadań deleguje problemy badawcze do agentów AAR. Agenci proponują dekompozycję problemów, przeprowadzają eksperymenty i rejestrują wnioski.
- **Koncentracja na uczeniu słaby-do-silnego.** Publikacja Anthropic skupiła się na scenariuszu słaby-do-silnego (weak-to-strong), w którym słabszy model (superwizor) jest używany do wyszkolenia silniejszego modelu (ucznia). W tym obszarze agenci AAR wykazali wyższą skuteczność niż ludzie.

### Dlaczego logowanie poza piaskownicą ma kluczowe znaczenie

Nienaruszalność dzienników (log integrity) to element decydujący o tym, czy eksperyment jest wiarygodny, czy potencjalnie zmanipulowany. Gdyby agenci AAR mogli modyfikować własne logi, mogliby ukrywać nieudane lub wątpliwe próby. Anthropic wyraźnie na to wskazuje: niezależność logów to warunek konieczny zaufania do wyników badań, a jej techniczna weryfikacja wcale nie jest prosta.

W sensie infrastrukturalnym rozwiązaniem są rejestry tylko do dołączania (append-only) z zapisem do pamięci zewnętrznej (np. S3 z blokadą Object Lock lub niezmienne logi Datadog). Agent nie posiada uprawnień do modyfikacji istniejących wpisów. Jest to dokładnie ten sam wzorzec, który korporacyjne zespoły ds. bezpieczeństwa stosują w celu tworzenia ścieżek audytu odpornych na ataki typu ransomware.

### Kompromis w przepływach pracy: instrukcje a elastyczność

W raporcie Anthropic zauważono, że sztywne, narzucane z góry przepływy pracy (prescribed workflows) często ograniczają elastyczność AAR i pogarszają ich skuteczność. Innymi słowy: jeśli projektant-człowiek narzuci agentom plan badań krok po kroku, osiągają one gorsze wyniki niż w sytuacji, gdy otrzymają cele wysokiego szczebla i pełną swobodę w dekompozycji zadań. Potwierdza to wnioski z innych systemów agenckich (LangGraph, frameworki Microsoftu) – zbyt sztywne rusztowanie szkodzi autonomicznym systemom.

Implikacje dla bezpieczeństwa są jednak dwuznaczne. Swoboda, która podnosi skuteczność agentów AAR, pozwala również na nieautoryzowaną dekompozycję celów, korzystanie z nieprzewidzianych narzędzi i dryf zadań. Projektanci systemu stają przed trudnym wyborem: ile elastyczności dać agentom, aby ich praca przewyższała efektywnością ludzi, jednocześnie nie pozwalając im na uogólnianie celów poza bezpieczny rozkład?

### Ryzyko kompresji czasu

Polityki RSP v3.0 (Lekcja 19) wprowadzają próg możliwości badawczo-rozwojowych AI (AI R&D Threshold): moment, w którym potok badawczo-rozwojowy może zostać w pełni zautomatyzowany po kosztach konkurencyjnych wobec pracy ludzi. Ramy FSF v3 od DeepMind definiują analogiczny poziom autonomii w badaniach nad uczeniem maszynowym. Obie te struktury traktują ten próg jako sygnał do natychmiastowego wdrożenia zaostrzonych środków bezpieczeństwa.

Agenci AAR są blisko tego progu: automatyzują kluczową część potoku (badania nad dopasowaniem pod kątem konkretnych zadań), ale nie stanowią jeszcze w pełni autonomicznej pętli rozwoju własnych zdolności. Kluczowym pytaniem jest to, jak szybko ta luka zostanie zamknięta.

Skompresowane osie czasu stwarzają ryzyko kumulacji błędów. Jeśli badania nad dopasowaniem (alignment) i badania nad podnoszeniem możliwości (capabilities) będą przyspieszać w tym samym tempie, ryzyko niedopasowania rośnie proporcjonalnie do skomplikowania systemów. Jeśli jednak rozwój możliwości wyprzedzi badania nad bezpieczeństwem (co jest historyczną tendencją), luka ta będzie się powiększać. Dlatego zautomatyzowane badania nad dopasowaniem stanowią korzyść warunkową (qualified good): przynoszą zysk pod warunkiem, że cały proces badawczy jest w pełni wiarygodny.

### Czego agenci AAR nie potrafią zastąpić

Badacze-ludzie wciąż definiują kolejkę zadań, weryfikują ostateczne wyniki i sprawują nadzór konstytucyjny nad systemem. Agenci AAR przyspieszają środkową część potoku badawczego, ale nie zastępują ludzi na jego końcach. Wyniki opublikowane przez Anthropic stanowią połączenie autonomicznej pracy AAR z ludzką oceną tego, co należy opublikować, co odrzucić, a co dopracować.

Odpowiada to wzorcowi „zaproponuj, a następnie zatwierdź” (propose-and-commit) z Lekcji 15: agenci AAR proponują rozwiązania, a ludzie je zatwierdzają i wdrażają.

## Użyj tego

Skrypt `code/main.py` symuluje forum badawcze z udziałem wielu agentów AAR. Trzech niezależnych „agentów badawczych” działa równolegle i publikuje wyniki na forum obsługującym logi typu append-only (tylko do odczytu/dołączania), z wbudowanymi próbami manipulacji danymi.

Zaobserwuj:

- W jaki sposób logowanie poza piaskownicą skutecznie wykrywa próby modyfikacji logów przez agentów.
- Jak alokacja zadań oparta na swobodnej dekompozycji przewyższa sztywne przepływy pracy przy trudniejszych problemach.
- W jaki sposób pojedynczy skompromitowany agent AAR może zanieczyścić sygnał na forum, jeśli baza danych nie jest w pełni odporna na manipulacje.

## Wdrożenie

Szablon `outputs/skill-aar-deployment-review.md` ułatwia przeprowadzenie audytu przedwdrożeniowego potoku zautomatyzowanych badań nad dopasowaniem.

## Ćwiczenia

1. Uruchom `code/main.py`. Porównaj wyniki dla „sztywnych przepływów pracy” (fixed workflow) oraz „swobodnej dekompozycji” (free decomposition). Czy swobodna dekompozycja zawsze wygrywa, czy istnieją klasy zadań, w których sztywny potok osiąga porównywalne rezultaty?

2. Zmodyfikuj symulator tak, aby jeden z agentów podjął próbę modyfikacji logów. Upewnij się, że baza danych append-only wykryła to zdarzenie. Napisz krótki akapit opisujący, jak wygląda sygnatura tego naruszenia w logach.

3. Przeczytaj raport Anthropic na temat słabej i mocnej generalizacji u agentów AAR. Wskaż jedno konkretne podzadanie, w którym agenci AAR osiągnęli wyniki lepsze od ludzi. Co sprawiło, że poddało się ono tak efektywnej automatyzacji?

4. Zaprojektuj politykę alokacji zadań w kolejce, która łączy elastyczność AAR (wyższa skuteczność) z narzuconymi ograniczeniami strukturalnymi (łatwiejszy audyt). Opisz, jak przeprowadziłbyś testy A/B obu rozwiązań.

5. Przeczytaj kryterium AI R&D-4 w polityce RSP v3.0 firmy Anthropic. W jednym akapicie opisz, jakie zachowania lub możliwości mogłyby przekroczyć ten próg, a których obecnie brakuje w systemach AAR.

## Kluczowe terminy

| Termin | Co mówią ludzie | Co to naprawdę oznacza |
|---|---|---|
| AAR | „Badacz zautomatyzowanego dopasowania” | Autonomicznie działająca instancja Claude Opus 4.6 realizująca zadania badawcze z zakresu bezpieczeństwa AI |
| Uczenie słaby-do-silnego | „Szkolenie silniejszego modelu za pomocą słabszego” | Klasyczny scenariusz testowania skalowalnego nadzoru, w którym AAR osiągają wyniki lepsze od ludzi |
| Wspólne forum | „Miejsce publikacji ustaleń agentów” | Baza danych typu append-only zlokalizowana poza piaskownicami agentów |
| Logowanie poza piaskownicą | „Zabezpieczenie przed edycją logów” | Logi odporne na manipulacje zapisywane w zewnętrznej pamięci masowej |
| Narzucony przepływ pracy | „Plan krok po kroku od projektanta” | Ograniczenie swobody działania AAR; często pogarsza wydajność w trudniejszych zadaniach |
| Swobodna dekompozycja | „Samodzielny podział zadań przez agenta” | Wyższa skuteczność działania, ale trudniejszy audyt i kontrola procesu |
| Próg R&D AI | „Krytyczny poziom autonomii w RSP/FSF” | Zdolność do pełnej i opłacalnej automatyzacji własnych procesów badawczo-rozwojowych |
| Kompresja osi czasu | „Wyścig możliwości i bezpieczeństwa” | Sytuacja, w której tempo rozwoju zdolności modeli wyprzedza tempo rozwoju metod ich dopasowania |

## Dalsze czytanie

- [Anthropic — Automated Weak-to-Strong Generalization Researcher](https://alignment.anthropic.com/2026/automated-w2s-researcher/) – publikacja źródłowa.
- [Responsible Scaling Policy v3.0 od Anthropic](https://anthropic.com/responsible-scaling-policy/rsp-v3-0) – definicja progów AI R&D.
- [Anthropic — Measuring Agent Autonomy in Practice](https://www.anthropic.com/research/measuring-agent-autonomy) – omówienie autonomii i ryzyka fałszowania dopasowania.
- [DeepMind Frontier Safety Framework v3](https://deepmind.google/blog/strengthening-our-frontier-safety-framework/) – zawiera definicje poziomów autonomii i monitorowania zwodniczych zachowań.
- [Burns i in. (2023). Weak-to-strong generalization (OpenAI)](https://openai.com/index/weak-to-strong-generalization/) – opis fundamentalnego problemu badawczego.
