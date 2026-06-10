# Capstone 05 — Autonomiczny agent badawczy (klasa AI-Naukowiec)

> AI-Scientist-v2 firmy Sakana opublikował pełne artykuły. Agent Laboratory przeprowadziło eksperymenty. Allen AI udostępnił ślady. Kształt 2026 to przeszukiwanie drzewa w oparciu o plan, wykonanie, weryfikację na podstawie eksperymentów, budżetowany koszt, wykonanie kodu w piaskownicy, moduł piszący LaTeX na podstawie wizji i zautomatyzowany zespół recenzentów w stylu NeurIPS. Zwieńczeniem jest zbudowanie jednego, wyprodukowanie go od końca do końca w cenie 30 dolarów za papier i przetrwanie czerwonej drużyny uciekającej z piaskownicy, którą udokumentował Sakana.

**Typ:** Zwieńczenie
**Języki:** Python (agent + piaskownica), LaTeX (wyjście)
**Wymagania wstępne:** Faza 2 (ML), Faza 3 (głębokie uczenie), Faza 7 (transformatory), Faza 10 (LLM od podstaw), Faza 14 (agenci), Faza 15 (autonomiczna), Faza 16 (wieloagentowa), Faza 18 (bezpieczeństwo)
**Wykonywane fazy:** P0 · P2 · P3 · P7 · P10 · P14 · P15 · P16 · P18
**Czas:** 40 godzin

## Problem

Autonomiczni agenci naukowi przekroczyli próg w 2026 r. AI-Scientist-v2 autorstwa Sakana AI został opublikowany w czasopiśmie Nature wraz z wygenerowanymi artykułami, które przeszły recenzję w ramach warsztatów. ShinkaEvolve (ICLR 2026) rozszerzył linię o ewoluujące hipotezy. Laboratorium agentów AMD dostarczyło powtarzalne ślady. Agenci to nie magia — to pętla planu, wykonania i weryfikacji działająca na drzewie potencjalnych eksperymentów, z limitami kosztów, piaskownicami związanymi z nasionami i automatycznym przeglądem. Jednostka jest w pętli, budżet i historia bezpieczeństwa.

Pętli uczysz się, wdrażając ją w oparciu o pomysł zalążkowy w wąskiej dziedzinie (na przykład ablacje rzadkości uwagi na transformatorze o parametrach 100M). Wartość nie polega na odkrywaniu czegoś nowego za pierwszym razem. Wartość leży w infrastrukturze: przeszukiwaniu drzewa, piaskownicy eksperymentu, pętli autor-recenzent, raporcie zespołu czerwonego. Zespół Sakany udokumentował niepowodzenia ucieczki z piaskownicy; Twój agent musi minąć tę samą czerwoną drużynę.

## Koncepcja

Agent to przeszukiwanie drzewa w pierwszej kolejności. Węzły to specyfikacje eksperymentu: (hipoteza, konfiguracja, kod, oczekiwany wynik). Krok rozwijania proponuje dzieci z drobnymi zmianami (zamień optymalizator, przesuń rozmiar partii, usuń komponent). Każde dziecko biegnie w świeżej piaskownicy z twardym limitem zasobów. Wyniki trafiają do funkcji punktacji, która klasyfikuje węzły według (nowość × jakość × pozostały budżet). Drzewo rośnie aż do wyczerpania budżetu, po czym wypisuje się najlepszą gałąź.

Autor jest multimodalny. Generuje wersję roboczą LaTeX, kompiluje ją, renderuje rysunki i przesyła wyrenderowany plik PDF z powrotem do trybu widzenia Claude Opus 4.7 w celu oceny układu, czytelności rysunków i dopasowania twierdzeń do dowodów. Zespół recenzentów składający się z pięciu sędziów LLM przyznaje oceny w stylu NeurIPS (nowość, rygorystyczność, przejrzystość, odtwarzalność, wpływ); jeśli średnia spadnie poniżej progu, artykuł wraca do autora z krytyką.

Bezpieczeństwo jest nośne. Każdy eksperyment działa w piaskownicy E2B lub Daytona bez ruchu wychodzącego z sieci, ograniczonego zegara ściennego i przypiętych limitów zasobów. Etap generowania kodu agenta przechodzi przez warstwę zasad, która blokuje wywołania systemowe wychodzące z piaskownicy. Raport czerwonej drużyny odtwarza udokumentowaną przez Sakanę powierzchnię ataku (bomby widełkowe, ucieczki z systemu plików, wywołania sieciowe zapisane przez LLM).

## Architektura

```
seed idea + domain
      |
      v
  literature search (Semantic Scholar + OpenAlex + FAISS cache)
      |
      v
  LangGraph plan-execute-verify tree
      |
      v
  +--- expand node ----+      per-node sandbox
  |                    |      (E2B / Daytona)
  v                    v      resource caps
  child_1           child_k   no network egress
  |                    |      deterministic seeds
  v                    v
  run experiment       run experiment
  |                    |
  v                    v
  score nodes by (novelty, quality, budget)
      |
      v
  best branch -> LaTeX writer
      |
      v
  compile + vision critique (Opus 4.7 vision)
      |
      v
  reviewer ensemble (5 LLM judges, NeurIPS rubric)
      |
      v
  paper.pdf + review.md + trace.json
```

## Stos

- Orkiestracja: LangGraph z punktami kontrolnymi i bramkami do zatwierdzania przez człowieka
- Wyszukiwanie w drzewie: niestandardowe najlepsze-pierwsze w węzłach eksperymentu (w stylu AB-MCTS z Sakana v2)
- Sandbox: E2B na eksperyment, rezerwa Docker-in-Docker; limity zasobów za pośrednictwem cgroups
- Literatura: Semantic Scholar Graph API + OpenAlex + lokalna pamięć podręczna abstraktów FAISS
- Pisarz: szablon LaTeX + Claude Opus 4.7 (tryb widzenia) do krytyki figur i układu
- Recenzent: zespół 5 sędziów (Opus 4.7, GPT-5.4, Gemini 3 Pro, DeepSeek R1, Qwen3-Max) z agregacją ważoną
- Struktura eksperymentu: PyTorch 2.5 do eksperymentów fizycznych, W&B do rejestrowania
- Obserwowalność: Langfuse do śledzenia agentów, sztywny budżet 30 dolarów na artykuł

## Zbuduj to

1. **Określanie zakresu nasion i domen.** Weź pomysł na początek (np. „zbadaj wzorce rzadkości na mapach uwagi transformatorów sub-1B”). Zdefiniuj przestrzeń poszukiwań: modele, zbiory danych, budżet obliczeniowy.

2. **Karta literacka.** Zapytanie Semantic Scholar + OpenAlex o 50 najczęściej cytowanych odpowiednich artykułów; streszczenia w pamięci podręcznej lokalnie; wygeneruj jednostronicowe podsumowanie domeny.

3. **Rusztowanie drzewa.** Zainicjuj korzeń hipotezą nasion. Zaimplementuj `expand(node) -> children` z propozycjami drobnych edycji (jedna zmiana konfiguracji na każde dziecko). Wdróż `score(node)` jako ważoną nowość × jakość × termin budżetowy.

4. **Opakowanie piaskownicy.** Każdy eksperyment uruchamia `docker run --network=none --memory=8g --cpus=2 --pids-limit=256 --read-only` (lub równoważną politykę E2B). Nasiona są zapisywane w piaskownicy; wyjścia są montowane z powrotem w trybie tylko do odczytu.

5. **Pętla „planuj-wykonaj-weryfikuj”.** `plan` proponuje dzieci. `execute` uruchamia piaskownicę, przechwytuje logi i metryki. `verify` przeprowadza kontrole jednostkowe wskaźników (czy strata zmniejszyła się? czy ablacja wyizolowała ten efekt?). Węzły, które uległy awarii, otrzymują przyczynę awarii przechowywaną w drzewie.

6. **Pisarz.** Po budżecie wybierz najlepszą branżę. Renderuj figury za pomocą Matplotlib. Wygeneruj wersję roboczą LaTeX za pomocą Claude Opus 4.7 ze śladem gałęzi w kontekście. Skompilować. Prześlij skompilowany plik PDF z powrotem do wizji Opus 4.7 w celu krytyki. Brzmieć.

7. **Zespół recenzentów.** Pięciu sędziów ocenia wersję roboczą pod kątem (nowości, rygorystyczności, przejrzystości, odtwarzalności, wpływu) w rubrykach w stylu NeurIPS. Jeśli średnia < 4,0/5, wróć do autora z krytyką. Twardy stop po 3 przepisaniach.

8. **Drużyna Czerwona.** Zbuduj lub zintegruj zestaw kontradyktoryjnych zadań ukierunkowanych na piaskownicę: bomby widełkowe, próby eksfiltracji sieci, ucieczki z systemu plików, metaznaki powłoki zapisane w LLM. Potwierdź, że wszystkie są zablokowane. Zapisz ustalenia.

9. **Powtarzalność.** Każda publikacja jest dostarczana z plikiem JSON śledzenia drzewa wyszukiwania, nasionami, łączami do uruchamiania W&B, konfiguracjami piaskownicy i plikiem README odtwarzającym je od początku do końca.

## Użyj tego

```
$ ai-scientist run --seed "attention sparsity in sub-1B transformers" --budget 30
[lit]    50 papers, digest in 12s
[tree]   expanded 8 nodes, budget 12/30
[exec]   node #3 sparsity=top-8, loss=2.83 (best so far)
[exec]   node #6 sparsity=top-4, loss=3.12 (worse)
[exec]   ...
[tree]   chose branch rooted at node #3 (novelty 0.62, quality 0.81)
[write]  LaTeX draft v1 complete
[vision] critique: figure 2 legend too small, claim-evidence ok
[write]  draft v2 after 3 edits
[review] mean 4.2/5 (novelty 3.9, rigor 4.3, clarity 4.1, repro 4.5, impact 4.2)
[done]   paper.pdf + review.md + trace.json     $28.40 spent
```

## Wyślij to

Elementem dostarczanym jest `outputs/skill-ai-scientist.md`. Biorąc pod uwagę pomysł zalążkowy + domenę + budżet 30 dolarów, uruchamia on cały proces i wydaje recenzowaną publikację wraz z pakietem odtwarzalności.

| Waga | Kryterium | Jak to się mierzy |
|:-:|---|---|
| 25 | Jakość papieru | Ślepa recenzja rubryk w porównaniu z opublikowanymi artykułami warsztatowymi |
| 20 | Rygor eksperymentalny | Wartości bazowe, nasiona, ablacje; każde twierdzenie poparte komórką w tabeli wyników |
| 20 | Dyscyplina kosztów i obliczeń | Obowiązuje 30 dolarów za papierowy sufit, śledzenie Langfuse |
| 20 | Bezpieczeństwo | Zespół Red Sandbox podaje; zweryfikowano politykę sieciową i wyłącznik awaryjny |
| 15 | Powtarzalność | Ponowne uruchomienie jednym poleceniem z identycznymi nasionami odtwarza papier |
| **100** | | |

## Ćwiczenia

1. Uruchom potok dla trzech różnych pomysłów początkowych w tej samej domenie. Porównaj, które części wyszukiwania drzewa pokrywają się. Zidentyfikuj zduplikowane, zmarnowane zasoby obliczeniowe.

2. Dodaj bramkę typu „człowiek w pętli” przed wykonaniem eksperymentu dla węzłów szacowanych na kwotę powyżej 5 USD. Zmierz, o ile spadły koszty całkowite.

3. Zamień zespół recenzentów na jednego sędziego. Zmierz wskaźnik fałszywych akceptacji na zestawie wystawionych dokumentów, o których wiadomo, że są złe.

4. Wprowadź test czerwonego zespołu eksfiltracji sieci: agent pisze kod, który próbuje `curl` adres zewnętrzny. Potwierdź, że zasada `--network=none` to blokuje. Zarejestruj próbę.

5. Porównaj swoje wyszukiwanie w drzewie z płaską, losową linią bazową (ten sam budżet, bez strategii ekspansji). Zgłoś nowość × wzrost jakości.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|--------------------------------------|
| Wyszukiwanie drzewa | „Rozbudowa w stylu AB-MCTS” | Pierwsza eksploracja węzłów eksperymentu z wynikiem nowości×jakości×budżetu |
| Piaskownica | „Eksperymentowa izolacja” | Kontener bez sieci, ograniczony procesor/pamięć, przypięte nasiona, wejścia tylko do odczytu |
| Krytyka wizji | „Wyrenderuj, a następnie przeczytaj” | Skompiluj artykuł do formatu PDF, prześlij plik PDF z powrotem do VLM w celu sprawdzenia układu i oceny dowodów |
| Zespół recenzentów | „Automatyczna ocena partnerska” | Wielu sędziów LLM oceniło artykuł w rubryce NeurIPS; kruszywo ważone zamyka rurociąg |
| Nowość wynik | „Czy to coś nowego?” | Heurystyka penalizująca bliskość 50-papierowego magazynu literatury |
| Pułap kosztów | „budżet $” | Sztywne ograniczenie całkowitych wydatków na artykuł; Liczniki Langfuse + szacunki wstępne |
| Zespół czerwony | „Audyt ucieczki z piaskownicy” | Zadania kontradyktoryjne, które uciekną z piaskownicy, jeśli polityka będzie błędna |

## Dalsze czytanie

- [Repozytorium Sakana AI-Scientist-v2](https://github.com/SakanaAI/AI-Scientist-v2) — referencyjny agent badawczy ds. produkcji
- [Artykuł Sakana AI-Scientist-v1 (arXiv:2408.06292)](https://arxiv.org/abs/2408.06292) — oryginalna metodologia
- [ShinkaEvolve (Sakana ICLR 2026)](https://sakana.ai) — rozszerzenie ewolucyjne
- [Agent Laboratory (AMD)](https://github.com/SamuelSchmidgall/AgentLaboratory) — wielozadaniowe środowisko laboratorium badawczego
- [Dokumentacja LangGraph](https://langchain-ai.github.io/langgraph/) — referencyjna warstwa orkiestracyjna
- [Semantic Scholar Graph API](https://api.semanticscholar.org/) — wyszukiwanie literatury
- [Piaskownice E2B](https://e2b.dev) — izolacja eksperymentu referencyjnego
– [Wytyczne dla recenzentów NeurIPS](https://neurips.cc/Conferences/2026/Reviewer-Guidelines) – rubryka kodowana przez zespół recenzentów