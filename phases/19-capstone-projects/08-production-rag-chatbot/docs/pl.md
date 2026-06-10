# Capstone 08 — Chatbot produkcyjny RAG dla branży regulowanej

> Harvey, Glean, Mendable i LlamaCloud będą miały ten sam kształt produkcyjny w 2026 r. Pozyskiwanie za pomocą doclingu lub Unstructured i ColPali w celu uzyskania efektów wizualnych. Wyszukiwanie hybrydowe. Zmień rangę za pomocą bge-reranker-v2-gemma. Syntetyzuj za pomocą Claude Sonnet 4.7, używając szybkiego buforowania przy współczynniku trafień 60-80%. Strażnik z Llamą Guard 4 i poręczami NeMo. Obejrzyj z Langfuse i Phoenixem. Oceń za pomocą RAGAS w złotym zestawie składającym się z 200 pytań. Zbuduj go w domenie regulowanej (prawnej, klinicznej, ubezpieczeniowej), a zwieńczeniem będzie złoty zestaw, czerwona drużyna i deska rozdzielcza driftu.

**Typ:** Zwieńczenie
**Języki:** Python (potok + API), TypeScript (interfejs czatu)
**Wymagania wstępne:** Faza 5 (NLP), Faza 7 (transformatory), Faza 11 (inżynieria LLM), Faza 12 (multimodalność), Faza 17 (infrastruktura), Faza 18 (bezpieczeństwo)
**Wykonywane fazy:** P5 · P7 · P11 · P12 · P17 · P18
**Czas:** 30 godzin

## Problem

RAG w domenie regulowanej (umowy prawne, protokoły badań klinicznych, polisy ubezpieczeniowe) to najczęściej wysyłana forma produkcji w 2026 r., ponieważ zwrot z inwestycji jest oczywisty, a stawka konkretna. Harvey (Allen & Overy) zbudował go w celach prawnych. Mendable ma charakter dokumentów deweloperskich. Glean obejmuje wyszukiwanie korporacyjne. Wzorzec jest następujący: pozyskiwanie wysokiej jakości, pobieranie hybryd ze zmianą rangi, synteza z wymuszaniem cytowań i natychmiastowym buforowaniem, ochrona z wieloma warstwami bezpieczeństwa i ciągłe monitorowanie dryfu.

Twarde części nie są modelem. Obejmują one zgodność z jurysdykcją (HIPAA, RODO, SOC2), możliwość audytu na poziomie cytatów, kontrolę kosztów (szybkie buforowanie zapewnia 60–90% rabatu, gdy wskaźnik trafień jest wysoki), wykrywanie halucynacji za pomocą wierności RAGAS i wykrywanie dryfu, gdy dokumenty źródłowe są aktualizowane bez nadrabiania zaległości przez indeks. To zwieńczenie prosi Cię o wysłanie tego wszystkiego w złotym zestawie składającym się z 200 pytań, obok zestawu drużyny czerwonej.

## Koncepcja

Rurociąg ma dwie strony. **Przetwarzanie**: docling lub Unstructured analizuje dokumenty strukturalne; ColPali obsługuje bogate wizualnie; fragmenty otrzymują podsumowania, tagi i etykiety dostępu oparte na rolach. Wektory trafiają do pgvector + pgvectorscale (poniżej 50M wektorów) lub Qdrant Cloud; obok biegnie rzadki BM25. **Rozmowa**: LangGraph obsługuje pamięć i wieloobrotowość; każde zapytanie uruchamia pobieranie hybrydowe, zmienia ranking za pomocą bge-reranker-v2-gemma-2b, syntetyzuje za pomocą Claude Sonnet 4.7 (w pamięci podręcznej), przekazuje dane wyjściowe przez Llama Guard 4 i NeMo Guardrails i emituje odpowiedź zakotwiczoną w cytatach.

Stos eval ma cztery warstwy. **Złoty zestaw** (200 oznaczonych Q/A z cytatami) za poprawność. **Zespół czerwony** (uciekanie z więzienia, próby wyodrębnienia danych osobowych, pytania poza domeną) ze względów bezpieczeństwa. **RAGAS** dla wierności / trafności odpowiedzi / precyzji kontekstu automatycznie co turę. **Deska rozdzielcza driftu** (Arize Phoenix) co tydzień ogląda jakość odzyskiwania i wynik halucynacji.

Szybkie buforowanie to dźwignia kosztów. Claude 4.5+ i GPT-5+ obsługują monity systemu buforowania + pobrany kontekst. Przy współczynniku trafień 60–80% koszt zapytania spada 3–5 razy. Potok musi być zaprojektowany pod kątem stabilnych prefiksów (najpierw monit systemowy + kontekst o zmienionym rankingu), aby osiągnąć wysoki współczynnik trafień w pamięci podręcznej.

## Architektura

```
documents (contracts, protocols, policies)
      |
      v
docling / Unstructured parse + ColPali for visuals
      |
      v
chunks + summaries + role-labels + jurisdiction tags
      |
      v
pgvector + pgvectorscale  +  BM25 (Tantivy)
      |
query + role + jurisdiction
      |
      v
LangGraph conversational agent
   +--- retrieve (hybrid)
   +--- filter by role + jurisdiction
   +--- rerank (bge-reranker-v2-gemma-2b or Voyage rerank-2)
   +--- synthesize (Claude Sonnet 4.7, prompt cached)
   +--- guard (Llama Guard 4 + NeMo Guardrails + Presidio output PII scrub)
   +--- cite + return
      |
      v
eval:
  RAGAS faithfulness / answer_relevance / context_precision (online)
  Langfuse annotation queue (sampled)
  Arize Phoenix drift (weekly)
  red team suite (pre-release)
```

## Stos

- Przetwarzanie: Unstructured.io lub docling dla dokumentów strukturalnych; ColPali do bogatych wizualnie plików PDF
- Vector DB: pgvector + pgvectorscale poniżej 50M wektorów; Inaczej chmura Qdrant
- Rzadki: Tantivy BM25 z obciążnikami polowymi
- Orkiestracja: Przepływy pracy LlamaIndex (przyjmowanie) + LangGraph (rozmowa)
- Re-ranker: bge-reranker-v2-gemma-2b hostowany samodzielnie lub hostowany rerank-2 Voyage
- LLM: Claude Sonnet 4.7 z szybkim buforowaniem; awaryjna Lama 3.3 70B na własnym serwerze
- Eval: RAGAS 0.2 online, DeepEval dla halucynacji i pakietów jailbreak
- Obserwowalność: Langfuse na własnym serwerze z kolejką adnotacji; Arize Phoenix do driftu
- Guardrails: klasyfikator wejścia/wyjścia Llama Guard 4, polityka NeMo Guardrails v0.12, peeling Presidio PII
- Zgodność: etykiety dostępu oparte na rolach na fragmentach; znaczniki jurysdykcji dla RODO/HIPAA

## Zbuduj to

1. **Przetwarzanie.** Przeanalizuj swój korpus (1000-10000 dokumentów w przypadku poważnej kompilacji) za pomocą opcji Unstructured lub Docling. W przypadku zeskanowanych stron zawierających dużo treści wizualnych kieruj się przez ColPali. Twórz fragmenty zawierające podsumowania, etykiety ról i znaczniki jurysdykcji.

2. **Indeks.** Gęste osadzenie (Voyage-3 lub Nomic-embed-v2) w pgvector + pgvectorscale. Indeks boczny BM25 za pośrednictwem Tantivy. Filtry ról i jurysdykcji jako ładunek.

3. **Odzyskiwanie hybrydowe.** Najpierw filtruj według roli i jurysdykcji; następnie równoległy gęsty + BM25; połączyć się z wzajemną fuzją rang; top-20 do zmiany rankingu; top-5 do syntezatorów.

4. **Synteza z buforowaniem podpowiedzi.** Podpowiedź systemowa + zasady statyczne w nagłówku pamięci podręcznej; zmieniono ranking kontekstu na rozszerzenie pamięci podręcznej; pytanie użytkownika jako sufiks niezapisany w pamięci podręcznej. Docelowy współczynnik trafień w pamięci podręcznej na poziomie 60–80% w stanie ustalonym.

5. **Poręcze.** Strażnik Lamy 4 na wejściu; Szyny NeMo Guardrails blokują pytania spoza domeny lub tematy zabronione przez zasady; Presidio usuwa przypadkowe informacje umożliwiające identyfikację na wyjściu; Filtr końcowy wymuszający cytowanie.

6. **Złoty zestaw.** 200 par pytań i odpowiedzi oznaczonych przez eksperta dziedzinowego symbolem (odpowiedź, cytaty). Agent oceniający dopasowanie dokładnego cytatu, poprawność odpowiedzi, wierność (RAGAS).

7. **Zespół czerwonych.** 50 monitów przeciwnika: jailbreaki (PAIR, TAP), próby eksfiltracji danych osobowych, wycieki poza domeną, między jurysdykcjami. Oceniaj za pomocą pozytywnego/negatywnego wyniku i dotkliwości.

8. **Panel Drift.** Arize Phoenix co tydzień monitoruje jakość wyszukiwania (nDCG, wierność cytowań). Alarm w przypadku spadku o 5%.

9. **Raport kosztów.** Langfuse: współczynnik trafień w buforowaniu podpowiedzi, tokeny na zapytanie, podział $/zapytanie według etapów.

## Użyj tego

```
$ chat --role=analyst --jurisdiction=GDPR
> what is the data-retention obligation for EU user profiles under our contract?
[retrieve]  hybrid top-20 filtered to GDPR + analyst-role
[rerank]    top-5 kept
[synth]     claude-sonnet-4.7, cache hit 74%, 0.8s
answer:
  The contract (Section 12.4, Master Services Agreement dated 2024-03-11)
  obligates EU user profile deletion within 30 days of termination per GDPR
  Article 17. The DPA amendment (DPA-v2.1, Section 5) extends this to 14 days
  for "restricted" category data.
  citations: [MSA-2024-03-11 s12.4, DPA-v2.1 s5]
```

## Wyślij to

`outputs/skill-production-rag.md` opisuje element dostarczany. Chatbot domeny regulowanej wdrożony z etykietami zgodności, przeszedł przez rubrykę i zaobserwowano poprzez monitorowanie dryfu na żywo.

| Waga | Kryterium | Jak to się mierzy |
|:-:|---|---|
| 25 | Wierność RAGAS + trafność odpowiedzi | Wyniki online na złotym zestawie (200 pytań/odpowiedzi) |
| 20 | Poprawność cytowania | Część odpowiedzi z weryfikowalnymi kotwicami źródłowymi |
| 20 | Pokrycie poręczy | Wskaźnik przepustowości Llama Guard 4 + wyniki pakietu jailbreak |
| 20 | Inżynieria kosztów/opóźnień | Współczynnik trafień w pamięci podręcznej podpowiedzi, opóźnienie p95, $/zapytanie |
| 15 | Pulpit monitorowania znoszenia | Pulpit nawigacyjny na żywo Phoenix z cotygodniowym trendem jakości pobierania |
| **100** | | |

## Ćwiczenia

1. Utwórz drugi wycinek korpusu podlegający innej jurysdykcji (np. HIPAA obok RODO). Zademonstruj filtrowanie ról i jurysdykcji zapobiegające wyciekom krzyżowym w sondzie składającej się z 20 pytań obejmującej różne jurysdykcje.

2. Zmierz współczynnik trafień w pamięci podręcznej podpowiedzi w ciągu tygodnia ruchu produkcyjnego. Zidentyfikuj, które zapytania łamią prefiks pamięci podręcznej. Restrukturyzacja.

3. Dodaj pamięć wieloobrotową z buforem podsumowującym o pojemności 10 tys. tokenów. Zmierz, czy wierność spada wraz z rozwojem rozmowy.

4. Zamień Claude Sonnet 4.7 na Llama 3.3 70B hostowany samodzielnie. Zmierz $/zapytanie i deltę wierności.

5. Dodaj tryb „niepewny”: jeśli najwyższe wyniki w rankingu są poniżej progu, agent zamiast odpowiadać, mówi „Nie mam pewnych cytatów”. Zmierz redukcję fałszywej pewności.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|--------------------------------------|
| Natychmiastowe buforowanie | „System buforowany + kontekst” | Funkcja Claude/OpenAI: buforowane tokeny prefiksów przecenione o 60-90% przy trafieniu |
| RAGA | „Oceniający RAG” | Automatyczna ocena wierności, trafności odpowiedzi, precyzji kontekstu |
| Złoty zestaw | „Oznaczone ewaluacją” | Ponad 200 pytań i odpowiedzi oznaczonych przez ekspertów z cytatami; podstawowa prawda |
| Znacznik jurysdykcji | „Etykieta zgodności” | Zakres RODO/HIPAA/SOC2 dołączony do fragmentów; wymuszane przez filtr pobierania |
| Wierność cytatów | „Uziemiony wskaźnik odpowiedzi” | Część roszczeń popartych możliwymi do odzyskania zakresami źródeł |
| Dryf | „Spadek jakości pobierania” | Cotygodniowa zmiana wyniku nDCG lub cytowań; próg alarmowy 5% |
| Zespół czerwony | „Ewaluacja kontradyktoryjna” | Przedpremierowe jailbreak, ekstrakcja danych osobowych, sondy poza domeną |

## Dalsze czytanie

- [Harvey AI](https://www.harvey.ai) — stos referencyjny legalnej produkcji
- [Glean Enterprise Search](https://www.glean.com) — odniesienie do RAG w skali przedsiębiorstwa
- [Dokumentacja do naprawienia](https://mendable.ai) — dokumentacja deweloperska RAG
- [LlamaCloud Parse + Index](https://docs.llamaindex.ai/en/stable/examples/llama_cloud/llama_parse/) — zarządzane pozyskiwanie
- [Antropiczne buforowanie podpowiedzi](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching) — odniesienie do dźwigni kosztów
- [Dokumentacja RAGAS 0.2](https://docs.ragas.io/) — kanoniczny framework eval RAG
- [Arize Phoenix](https://github.com/Arize-ai/phoenix) — obserwowalność dryfu referencyjnego
- [Llama Guard 4](https://ai.meta.com/research/publications/llama-guard-4/) — klasyfikator bezpieczeństwa 2026
- [NeMo Guardrails v0.12](https://docs.nvidia.com/nemo-guardrails/) — ramy polityki dotyczącej kolei