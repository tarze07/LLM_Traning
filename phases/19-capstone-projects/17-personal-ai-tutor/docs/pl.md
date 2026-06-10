# Capstone 17 — Osobisty nauczyciel AI (adaptacyjny, multimodalny, z pamięcią)

> Khanmigo (Khan Academy), Duolingo Max, Google LearnLM / Gemini for Education, Quizlet Q-Chat i Synthesis Tutor – wszystkie te adaptacyjne korepetycje multimodalne zostaną wprowadzone na dużą skalę w 2026 r. Powszechnym kształtem jest polityka sokratejska (nigdy nie porzucaj odpowiedzi), model ucznia aktualizujący się po każdej interakcji (styl śledzenia wiedzy bayesowskiej), głos + tekst + wprowadzanie zdjęć matematycznych, pobieranie wykresów programu nauczania, powtarzanie w odstępach harmonogram i twarde filtry zabezpieczające dla treści odpowiednich dla wieku. Zwieńczeniem jest wysłanie nauczyciela specjalizującego się w konkretnym przedmiocie (algebra K-12 lub wprowadzenie do Pythona), przeprowadzenie dwutygodniowego badania skuteczności z 10 uczniami i zdanie audytu bezpieczeństwa treści.

**Typ:** Zwieńczenie
**Języki:** Python (backend, model ucznia), TypeScript (aplikacja internetowa), SQL (wykres programu nauczania za pośrednictwem Postgres + Neo4j)
**Wymagania wstępne:** Faza 5 (NLP), Faza 6 (mowa), Faza 11 (inżynieria LLM), Faza 12 (multimodalność), Faza 14 (agenci), Faza 17 (infrastruktura), Faza 18 (bezpieczeństwo)
**Wykonywane fazy:** P5 · P6 · P11 · P12 · P14 · P17 · P18
**Czas:** 30 godzin

## Problem

Korepetycje adaptacyjne były kiedyś niszą badawczą w dziedzinie technologii edukacyjnych. Do 2026 roku będzie to produkt konsumencki. Khanmigo jest stosowane w większości okręgów szkolnych w USA. Duolingo Max osiągnął dziesiątki milionów jednostek MAU. Rozwiązanie Google LearnLM / Gemini for Education umożliwia nauczanie w Google Classroom. Quizlet Q-Chat znajduje się obok fiszek. Synthesis Tutor zyskał popularność dzięki nauczycielom dla ciekawskich dzieci. Wspólne elementy: wprowadzanie multimodalne (pisz, mów, fotografuj równania), pedagogika sokratesowa (najpierw zapytaj, wyjaśnij później), model ucznia aktualizujący się po każdej interakcji oraz ścisłe bezpieczeństwo dostosowane do wieku.

Zbudujesz jeden z nich dla określonej kohorty. Pasek pomiaru to rzeczywiste badanie skuteczności: wyniki przed i po teście w ciągu dwóch tygodni z udziałem 10 uczniów. Pętla głosowa musi sprawiać wrażenie naturalnej (pod-stos zwieńczenia 03). Pamięć musi szanować prywatność. Filtr bezpieczeństwa musi przejść przez drużynę czerwoną świadomą COPPA dla K-12.

## Koncepcja

Cztery komponenty. **Zasady korepetytora** to pętla Sokratesa: kiedy uczeń prosi o odpowiedź, polityka zadaje pytanie wiodące; kiedy im się to uda, przechodzi do następnej koncepcji; kiedy utkną, oferuje rusztowaną wskazówkę. **Model ucznia** to Bayesowskie śledzenie wiedzy (lub prosty wariant), które aktualizuje prawdopodobieństwo opanowania każdego węzła programu nauczania po każdej interakcji. **Wykres programu nauczania** to Neo4j koncepcji z wymaganymi krawędziami; polityka krąży po wykresie, aby wybrać następną koncepcję. **Pamięć** to magazyn epizodyczny + semantyczny (w stylu pamięci agenta), przechowujący przeszłe interakcje, błędy i preferencje.

UX jest multimodalny. Wprowadzanie tekstu dla wpisanych odpowiedzi. Wprowadzanie głosowe za pomocą LiveKit + Whisper (użyj ponownie zwieńczenia 03). Wprowadzanie zdjęć do zadań matematycznych za pośrednictwem dots.ocr lub PaliGemma 2. Wyjście głosowe za pośrednictwem Cartesia Sonic-2. Bezpieczeństwo wykorzystuje Llama Guard 4 oraz filtr dostosowany do wieku (blokuje treści dla dorosłych, przemoc i samookaleczenia) oraz politykę przechowywania pamięci zgodną z COPPA.

Wynikiem badania jest badanie skuteczności. 10 uczniów, okres przed i po teście, dwa tygodnie. Zgłoś deltę wzmocnienia uczenia się i przedział ufności. Porównaj z nieadaptacyjnym poziomem bazowym (ta sama treść dostarczana liniowo, bez zasad nauczyciela).

## Architektura

```
learner device
  |
  +-- text         -> web app
  +-- voice        -> LiveKit Agents (ASR + TTS)
  +-- photo math   -> dots.ocr / PaliGemma 2
       |
       v
  tutor policy (LangGraph)
       - Socratic decision head
       - next-concept chooser (curriculum graph walk)
       - hint scaffolder
       - mastery update
       |
       v
  learner model (BKT / item-response theory)
       - per-concept mastery probability
       - spaced-repetition scheduler (SM-2 or FSRS)
       |
       v
  memory (agentmemory-style)
       - episodic: every interaction
       - semantic: learned mistakes, preferences
       - retention policy: COPPA / GDPR aware
       |
       v
  curriculum graph (Neo4j)
       - prerequisite edges
       - OER content attached
       |
       v
  safety:
    Llama Guard 4 + age-appropriate filter
    memory access guarded by learner ID scope
```

## Stos

- Wybór przedmiotu: algebra K-12 lub wprowadzenie do Pythona (wybierz jeden ze względu na głębię)
- Polityka nauczyciela: LangGraph na Claude Sonnet 4.7 (z szybkim buforowaniem)
- Model ucznia: Bayesowskie śledzenie wiedzy (klasyczne) lub FSRS dla rozmieszczenia
- Wykres programu nauczania: Neo4j koncepcji + wymagane krawędzie + zawartość OER
- Pamięć: trwały wektor w stylu agentmemory + epizodyczny + magazyn semantyczny
- Głos: LiveKit Agents 1.0 + Cartesia Sonic-2 (ponowne wykorzystanie pod-stosu Capstone 03)
- Matematyka zdjęć: dots.ocr lub PaliGemma 2 do rozpoznawania równań
- Bezpieczeństwo: Llama Guard 4 + niestandardowy filtr dostosowany do wieku
- Ocena: generowanie pytań na poziomie Blooma, uprząż przed i po teście, narzędzia do badania skuteczności

## Zbuduj to

1. **Wykres programu nauczania.** Zbuduj Neo4j składający się z 50–150 węzłów koncepcyjnych (np. algebra K-12 od „linii liczbowej” do „wzóru kwadratowego”) z wymaganymi krawędziami. Dołącz treść OER do każdego węzła (Open Textbook, OpenStax).

2. **Model ucznia.** Zainicjuj Bayesowskie śledzenie wiedzy z priorytetami: zgadywanie, poślizg, tempo uczenia się. Aktualizuj biegłość według koncepcji po każdej interakcji. Utrzymuj się na ucznia.

3. **Zasady nauczyciela.** LangGraph z węzłami: `read_signal` (czy odpowiedź ucznia była poprawna/częściowa/zablokowana?), `select_concept` (wykres spaceru programu wybierający koncepcję o najwyższym priorytecie), `scaffold` (podpowiedź sokratejska), `update_mastery`.

4. **Pamięć.** Każda interakcja zapisuje do magazynu epizodycznego. Błędy i preferencje sprzyjają pamięci semantycznej. Polityka przechowywania zgodna z COPPA: automatyczne usuwanie po 1 roku, dostęp dla rodziców.

5. **Ścieżka głosowa.** Pracownik LiveKit Agents dołączony do polisy korepetytora. ASR poprzez Whisper-v3-turbo. TTS poprzez Cartesia Sonic-2. Obsługiwane wtrącanie (ponowne wykorzystanie mechaniki zwieńczenia 03).

6. **Ścieżka fotomatematyczna.** Prześlij lub przechwyć obraz; uruchom plik dots.ocr lub PaliGemma 2, aby rozpoznać równanie; przekazuj nauczycielowi jako ustrukturyzowane dane wejściowe.

7. **Bezpieczeństwo.** Każde wyjście modelu przechodzi Llama Guard 4 + filtr dostosowany do wieku (blokuje samookaleczenia, treści dla dorosłych, przemoc). Dostęp do pamięci ograniczony według identyfikatora ucznia; powierzchnia dostępu dla rodziców do usunięcia.

8. **Badanie skuteczności.** 10 uczniów, test wstępny (standaryzowany poziom bazowy składający się z 30 pytań), dwa tygodnie interakcji z tutorem (3 sesje/tydzień), post-test. Porównanie z nieadaptacyjną kohortą bazową składającą się z 10 uczniów korzystających z tych samych treści.

9. **Cotygodniowe raporty z postępów.** Dla każdego ucznia automatycznie generuj podsumowanie omawianych tematów w formacie PDF, trajektorie opanowania i zalecane kolejne kroki.

## Użyj tego

```
learner: "I don't understand why 3x + 6 = 12 means x = 2"
[signal]   stuck
[concept]  'isolating variables' (prerequisite: addition-subtraction-equality)
[scaffold] "what number would you subtract from both sides to start?"
learner: "6"
[signal]   correct
[mastery]  addition-subtraction-equality: 0.62 -> 0.77
[concept]  continue 'isolating variables'
[scaffold] "great. now what is 3x / 3 equal to?"
```

## Wyślij to

Elementem dostarczanym jest `outputs/skill-ai-tutor.md`. Tutor adaptacyjny dostosowany do konkretnego przedmiotu, posiadający wkład multimodalny, model ucznia, pamięć, bezpieczeństwo i mierzoną skuteczność.

| Waga | Kryterium | Jak to się mierzy |
|:-:|---|---|
| 25 | Delta wzmocnienia uczenia się | Delta przed/po teście w dwutygodniowym badaniu z udziałem 10 uczniów |
| 20 | Wierność sokratejska | Ocena rubryk na próbkach transkrypcji |
| 20 | Multimodalny UX | Spójność głosu + zdjęcia + tekstu od końca do końca |
| 20 | Bezpieczeństwo i prywatność | Wskaźnik przepustowości Llama Guard 4 + przestrzeganie ustawy COPPA |
| 15 | Zakres programu nauczania i jakość wykresów | Pokrycie koncepcji + wymagana spójność wykresu |
| **100** | | |

## Ćwiczenia

1. Przeprowadź badanie skuteczności z modelem adaptacyjnego ucznia i bez niego (losowa kolejność koncepcji). Zgłoś deltę. Spodziewaj się, że adaptacja wygra, ale rozmiar jest interesującą liczbą.

2. Dodaj sondę multimodalną: to samo pytanie koncepcyjne dostarczane jako tekst, głos i zdjęcie. Zmierz, czy uczniowie szybciej zbliżają się do zajęć dzięki preferowanej przez siebie modalności.

3. Zbuduj panel dla rodziców: ćwiczone tematy, ścieżki opanowania, nadchodzące koncepcje, zdarzenia związane z bezpieczeństwem (wszelkie uderzenia w poręcze). Dostosowane do COPPA.

4. Dodaj tryb zmiany języka: nauczyciel akceptuje wprowadzane informacje po hiszpańsku i uczy po hiszpańsku. Zmierz zasięg X-Guard.

5. Podkreśl prywatność pamięci: sprawdź, czy uczeń A nie może zobaczyć danych ucznia B nawet w wyniku ataku polegającego na ponownym przechwyceniu nagrania głosowego. Rejestruj próby dostępu i ostrzegaj.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|--------------------------------------|
| Polityka sokratejska | „Pytaj, nie rzucaj” | Nauczyciel zadaje pytanie wiodące zamiast udzielać odpowiedzi |
| Bayesowskie śledzenie wiedzy | "BKT" | Klasyczne równania modelu ucznia dotyczące prawdopodobieństwa opanowania na koncepcję |
| FSRS | „Swobodny harmonogram powtórzeń w odstępach” | Harmonogram powtarzania w odstępach 2024, lepszy niż SM-2 |
| Wykres programu nauczania | „Koncepcja DAG” | Neo4j koncepcji z wymaganymi krawędziami |
| Pamięć epizodyczna | „Dziennik interakcji” | Każda interakcja przechowywana w celu późniejszego odzyskania |
| Pamięć semantyczna | „Wyuczony sklep z wzorami” | Kompaktowe błędy i preferencje promowane z epizodycznych |
| COPPA | „Prawo dotyczące prywatności dzieci” | Prawo amerykańskie ograniczające gromadzenie danych od dzieci poniżej 13 roku życia |

## Dalsze czytanie

- [Khanmigo (Khan Academy)](https://www.khanmigo.ai) — referencyjny nauczyciel K-12 dla konsumentów
- [Duolingo Max](https://blog.duolingo.com/duolingo-max/) — referencyjny nauczyciel nauki języków
– [Google LearnLM / Gemini for Education](https://blog.google/technology/google-deepmind/learnlm) — hostowany model referencyjny
- [Quizlet Q-Chat](https://quizlet.com) — alternatywne źródło informacji
- [Synthesis Tutor](https://www.synthesis.com) — podręcznik startowy
- [Algorytm FSRS](https://github.com/open-spaced-repetition/fsrs4anki) — harmonogram powtarzania odstępów
- [Bayesian Knowledge Tracing](https://en.wikipedia.org/wiki/Bayesian_knowledge_tracing) — klasyczny model ucznia
- [Agenci LiveKit](https://github.com/livekit/agents) — stos głosowy