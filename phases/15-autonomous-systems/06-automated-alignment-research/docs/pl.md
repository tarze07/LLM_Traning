# Zautomatyzowane badania wyrównania (Anthropic AAR)

> Anthropic prowadził równoległe zespoły badaczy Claude Opus 4.6 Autonomous Alignment Researchers w niezależnych piaskownicach, koordynując działania za pośrednictwem wspólnego forum, którego logi znajdują się poza jakąkolwiek piaskownicą (więc agenci nie mogą usuwać własnych zapisów). W przypadku problemu treningu od słabego do silnego AAR osiągnęły lepsze wyniki niż badacze pracujący na ludziach. Własne flagi podsumowujące firmy Anthropic, które zalecają przepływy pracy, często ograniczają elastyczność AAR i pogarszają wydajność. Automatyzacja badań dopasowania to etap kompresji, który kompresuje oś czasu dokładnie do ryzyka nieprawidłowego ustawienia, które RSP ma wykryć.

**Typ:** Ucz się
**Języki:** Python (stdlib, symulator równoległego forum badawczego)
**Wymagania wstępne:** Faza 15 · 05 (AI Scientist v2), Faza 15 · 04 (DGM)
**Czas:** ~60 minut

## Problem

Badania nad dopasowaniem są kosztowne w czasie człowieka-naukowca. Problemy takie jak skalowalny nadzór, specyfikacja nagród lub szkolenie od słabego do silnego wymagają eksperymentów, które trwają tygodniami na iterację. W miarę rozwoju pionierskich możliwości obciążenie pracą związaną z dostosowaniem rośnie szybciej niż podaż wykwalifikowanych badaczy.

Badanie zautomatyzowanego dostosowania (AAR) zadaje pytanie, czy te same modele graniczne, których możliwości przewyższają dostosowanie, mogą przyczynić się do zlikwidowania luki. Raport firmy Anthropic z 2026 r. na temat przeprowadzonego przez AAR badania dotyczącego treningu od słabego do silnego (alignment.anthropic.com/2026/automated-w2s-researcher/) jest jednym z pierwszych publicznych wyników wdrożonego systemu tej klasy.

Wynik jest naprawdę pozytywny: AAR rozwiązały problem badawczy lepiej niż poziom wyjściowy u ludzi. Rezultatem jest także skupienie w jednym systemie wszystkich problemów, które rozwinęły się w tej fazie. Jeśli badania nad osiowaniem można zautomatyzować, można to zrobić także w przypadku części naruszających zabezpieczenia. Progi RSP dotyczące możliwości badań i rozwoju sztucznej inteligencji zostały zapisane z myślą o tej pętli.

## Koncepcja

### Architektura (opisana publicznie)

- **Agenci równoległi.** Wiele instancji Claude Opus 4.6 działa jako AAR, każda w niezależnym piaskownicy. Piaskownice ograniczają system plików, sieć i powierzchnię procesów.
- **Wspólne forum.** Wyniki są publikowane na wspólnym forum, którego zaplecze pamięci masowej znajduje się poza każdą piaskownicą. Agenci mogą czytać forum; agenci nie mogą usuwać ani edytować rekordów forum z poziomu własnej piaskownicy.
- **Przydział zadań.** Zaprojektowana przez człowieka kolejka zadań przypisuje problemy badawcze do AAR. AAR proponują rozkłady, przeprowadzają eksperymenty, zapisują wnioski.
- **Nacisk na szkolenie od słabego do silnego.** Opublikowane badanie dotyczyło szkolenia od słabego do silnego – przy użyciu modelu słabszego superwizora w celu wyszkolenia silniejszego modelu ucznia. W tym zadaniu AAR osiągnęły lepsze wyniki niż badacze-ludzi.

### Dlaczego dziennik spoza piaskownicy ma znaczenie

Właściwość log-integralność to różnica między kontrolowanym eksperymentem a potencjalnie zagrożonym. Gdyby AAR mogli edytować własne dzienniki, mogliby ukryć nieudane lub wątpliwe eksperymenty. Antropia wyraźnie to sygnalizuje: własność jest warunkiem koniecznym zaufania do wyników badań, a jej weryfikacja nie jest trywialna.

Analogiem pod względem infrastruktury są logi tylko do dołączania z zapisem do pamięci zewnętrznej (np. Blokada obiektu S3, niezmienne logi Datadog). Agent nie ma uprawnień do modyfikowania wcześniejszych rekordów. Jest to ten sam wzorzec, którego używają korporacyjne zespoły ds. bezpieczeństwa w 2026 r. do tworzenia ścieżek audytu odpornych na oprogramowanie ransomware.

### Kompromis dotyczący zalecanego przepływu pracy

W raporcie Anthropic zauważono, że zalecane przepływy pracy często ograniczają elastyczność AAR i pogarszają wydajność. Innymi słowy: jeśli projektant-człowiek napisze plan badań krok po kroku, AAR radzą sobie gorzej, niż gdyby miały określone cele wysokiego szczebla i swobodę rozkładu. Jest to zgodne z wynikami badań nad agentami (LangGraph, Microsoft Agent Framework) – przesadnie określone rusztowania szkodzą zdolnym agentom.

Wpływ na bezpieczeństwo jest subtelny. Elastyczność, która poprawia wydajność AAR, to także elastyczność, która pozwala na niesankcjonowany rozkład, użycie nowatorskich narzędzi i zmianę celów. Kompromisem jest decyzja podjęta w przestrzeni projektowej: ile elastyczności zapewnia wystarczające możliwości, aby pokonać ludzi, bez oddawania miejsca agentowi na uogólnianie celów poza dystrybucją?

### Ryzyko kompresji

RSP v3.0 (lekcja 19) wprowadza próg możliwości badawczo-rozwojowych w zakresie sztucznej inteligencji: możliwość pełnej automatyzacji rurociągu badawczo-rozwojowego w zakresie sztucznej inteligencji po konkurencyjnych kosztach w porównaniu z narzędziami ludzkimi i sztuczną inteligencją. Rozwiązanie FSF v3 firmy DeepMind obejmuje analogiczny poziom autonomii w zakresie badań i rozwoju ML. Obie platformy traktują ten próg jako czynnik wyzwalający podwyższone kontrole.

AAR jest o krok od progu: automatyzuje część rurociągu (badania dotyczące dostosowania do konkretnych, dobrze określonych zadań), ale nie kompleksową pętlę rozwoju zdolności. Pytaniem dotyczącym osi czasu jest to, jak szybko luka się zamyka.

Skompresowane osie czasu są problemem związanym z niepowodzeniem łączenia. Jeżeli badania nad dostosowaniem i badania nad możliwościami łączą się w podobnym tempie, powierzchnia ryzyka niewspółosiowości rośnie co najmniej tak szybko, jak możliwości. Jeśli możliwości będą się szybciej zwiększać (tendencja historyczna), różnica się pogłębia. Jest to argument przemawiający za tym, że AAR jest dobrem kwalifikowanym: każdy dodatkowy wynik dostosowania zmniejsza różnicę wtedy i tylko wtedy, gdy proces badawczy jest godny zaufania.

### Czego AAR nie zastępuje

Badacze-ludzi ustalają kolejkę zadań, przeglądają wyniki i sprawują władzę konstytucyjną. AAR przyspieszają środek rurociągu, a nie jego końce. Opublikowane wyniki Anthropic obejmują zarówno wkład AAR, jak i ocenę badaczy na temat tego, co opublikować, co wycofać, a co udoskonalić.

Odpowiada to wzorcowi „zaproponuj, a następnie zatwierdź” z Lekcji 15, zastosowanemu do samych badań: AAR proponują; ludzie popełniają.

## Użyj tego

`code/main.py` symuluje forum badawcze obejmujące wiele AAR. Trzech niezależnych „agentów badawczych” działa równolegle i publikuje wyniki na forum, na którym można tylko dodawać informacje, z opcjonalnymi próbami manipulacji.

Oglądaj:

- W jaki sposób rejestrowanie poza piaskownicą wychwytuje próby manipulowania logami.
- W jaki sposób alokacja zadań z swobodną dekompozycją przewyższa ustalone przepływy pracy w przypadku trudniejszych problemów.
- W jaki sposób pojedynczy skompromitowany plik AAR może zanieczyścić sygnał forum, jeśli dziennik nie jest zabezpieczony przed manipulacją.

## Wyślij to

`outputs/skill-aar-deployment-review.md` to przegląd przed wdrożeniem potoku badania automatycznego dopasowania.

## Ćwiczenia

1. Uruchom `code/main.py`. Porównaj ustawienia „stałego przepływu pracy” i „swobodnego rozkładu”. Czy swobodna dekompozycja zawsze wygrywa, czy też istnieją klasy problemowe, w których ustalony przepływ pracy jest konkurencyjny?

2. Zmodyfikuj symulator tak, aby jeden agent próbował manipulować dziennikiem. Upewnij się, że dziennik tylko do dołączania go wykrył. Napisz jeden akapit opisujący dokładnie, jak wygląda sygnatura wykrycia w dzienniku.

3. Przeczytaj słaby i mocny raport AAR firmy Anthropic. Zidentyfikuj konkretne podzadanie, w którym AAR pokonały ludzkich badaczy. Co sprawiło, że poddało się automatyzacji?

4. Zaprojektuj politykę alokacji kolejek zadań, która równoważy elastyczność AAR (lepsze wyniki) z zalecanymi ograniczeniami przepływu pracy (łatwiejszy audyt). Opisz, jak przeprowadziłbyś test A/B obu rozwiązań.

5. Przeczytaj próg RSP v3.0 AI R&D-4. W jednym akapicie opisz, co Twoim zdaniem mogłoby przekroczyć tę granicę, a czego obecnie nie ma w AAR.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|---|---|---|
| AAR | „Badacz automatycznego ustawienia” | Instancja Claude Opus 4.6 działała autonomicznie w przypadku problemów z wyrównaniem |
| Trening od słabego do silnego | „Szkolenie silniejszego modelu ze słabszym przełożonym” | Klasyczne, skalowalne testy porównawcze AAR w zakresie nadzoru przewyższają ludzi na |
| Wspólne forum | „Gdzie agenci publikują ustalenia” | Pamięć tylko do dołączania, poza piaskownicą |
| Dziennik spoza piaskownicy | „Agent nie może edytować własnego rekordu” | Zapis zabezpieczający przed manipulacją w pamięci zewnętrznej |
| Zalecany przepływ pracy | „Plan krok po kroku od ludzkiego projektanta” | Ogranicza AAR; często pogarsza wydajność w porównaniu do swobodnego rozkładu |
| Swobodny rozkład | „Agent decyduje, jak przerwać zadanie” | Większe możliwości, trudniejsze do kontrolowania |
| Próg badań i rozwoju sztucznej inteligencji | „Poziom możliwości RSP/FSF” | Pełna automatyzacja rurociągu badawczo-rozwojowego przy konkurencyjnych kosztach |
| Skompresowana oś czasu | „Wyścig dostosowania a możliwości” | Jeśli możliwości są szybsze niż wyrównanie, ryzyko niewspółosiowości rośnie |

## Dalsze czytanie

– [Anthropic — zautomatyzowany badacz od słabego do silnego](https://alignment.anthropic.com/2026/automated-w2s-researcher/) — źródło główne.
— [Zasady odpowiedzialnego skalowania firmy Anthropic, wersja 3.0](https://anthropic.com/responsible-scaling-policy/rsp-v3-0) — Ustalanie progów badań i rozwoju sztucznej inteligencji.
- [Anthropic — Pomiar autonomii agenta AI](https://www.anthropic.com/research/measuring-agent-autonomy) — szersze ujęcie autonomii agenta.
- [DeepMind Frontier Safety Framework v3](https://deepmind.google/blog/strengthening-our-frontier-safety-framework/) — Poziomy autonomii ML w zakresie badań i rozwoju są równoległe do RSP.
- [Burns i in. (2023). Generalizacja od słabej do silnej (OpenAI)](https://openai.com/index/weak-to-strong-generalization/) — podstawowy problem zaatakowany przez AAR.