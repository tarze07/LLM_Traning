---

name: production-rag
description: Wdróż chatbota RAG w domenie regulowanej z filtrowaniem ról i jurysdykcji, szybkim buforowaniem, poręczami i monitorowaniem dryfu na żywo.
version: 1.0.0
phase: 19
lesson: 08
tags: [capstone, rag, chatbot, regulated, llama-guard, nemo-guardrails, ragas, langfuse]

---

Mając korpus domeny regulowanej (umowy prawne, protokoły badań klinicznych, polisy ubezpieczeniowe itp.), wdróż chatbota, który odpowiada za pomocą możliwych do sprawdzenia cytatów, przestrzega zasad dostępu do ról i jurysdykcji oraz jest monitorowany pod kątem dryfowania.

Plan budowy:

1. Przeanalizuj korpus z doclingiem lub bez struktury; przesyłaj bogate wizualnie dokumenty przez ColPali. Emituj fragmenty z etykietami ról i jurysdykcji.
2. Indeksuj gęstość (Voyage-3 lub Nomic-embed-v2) w pgvector + pgvectorscale; rzadki BM25 przez Tantivy.
3. Agent konwersacyjny Wire LangGraph: odzyskanie (filtrowanie według roli + jurysdykcja, gęstość hybrydowa + BM25, wzajemna fuzja rang), zmiana rangi (bge-reranker-v2-gemma-2b lub reranking Voyage-2), syntezator (Claude Sonnet 4.7 z szybkim buforowaniem).
4. Złóż podpowiedzi ze stabilnymi przedrostkami: preambuła systemowa -> blok zasad -> kontekst o zmienionym rankingu -> zapytanie użytkownika. Docelowy współczynnik trafień w pamięci podręcznej wynoszący 60–80%.
5. Guardrails: Llama Guard 4 na wejściu i wyjściu, NeMo Guardrails v0.12 dla pytań spoza domeny i zabronionych przez zasady, czyszczenie Presidio PII na wyjściu, post-filtr wymuszania cytowań.
6. Zbuduj złoty zestaw składający się z 200 pytań i oznaczony jako ekspert (odpowiedź, cytaty). Oceń dopasowanie dokładnego cytatu, poprawność odpowiedzi i wierność RAGAS.
7. Zbuduj czerwony zespół składający się z 50 podpowiedzi (PAIR, TAP, wyodrębnianie danych osobowych, sondowanie poza domeną, między jurysdykcjami).
8. Cotygodniowe pobieranie danych z panelu kontrolnego Arize Phoenix Dryft nDCG i wierność cytatów; alert w przypadku spadku o 5%.
9. Raport kosztów Langfuse: współczynnik trafień w pamięci podręcznej, tokeny na zapytanie, $/zapytanie według etapu.

Rubryka oceny:

| Waga | Kryterium | Pomiar |
|:-:|---|---|
| 25 | Wierność RAGAS + trafność odpowiedzi | Wyniki online w złotym zestawie 200 pytań |
| 20 | Poprawność cytowania | Część odpowiedzi z weryfikowalnymi kotwicami źródłowymi |
| 20 | Pokrycie poręczy | Wskaźnik przepustowości Llama Guard 4 + wynik pakietu jailbreak |
| 20 | Inżynieria kosztów/opóźnień | Współczynnik trafień w pamięci podręcznej podpowiedzi, opóźnienie p95, $/zapytanie |
| 15 | Pulpit monitorowania znoszenia | Pulpit nawigacyjny Live Phoenix z cotygodniowym trendem jakości pobierania |

Twarde odrzucenia:

- Każdy chatbot, który wycieka dane między jurysdykcjami. Filtrowanie ról i jurysdykcji musi być egzekwowane przed pobraniem, a nie po.
- Synteza podpowiada, że ​​łamie prefiksy pamięci podręcznej (zmiana kolejności zasad między systemem a kontekstem). Zniszczy ekonomię pamięci podręcznej.
- Konfiguracje poręczy bez zarejestrowanych przejazdów drużyny czerwonej.
- Odpowiedzi bez cytatów; cytaty bez sprawdzalnych kotwic.

Zasady odmowy:

- Odmów wdrożenia w domenie regulowanej bez znaczników jurysdykcji w każdym fragmencie.
- Odmów trenowania odzyskiwania w przypadku pytań o złotym zestawie z etykietą eksperta. Zanieczyszczenie niszczy wiarygodność ewaluacji.
- Odmów uznania za „zgodny” bez wyraźnej matrycy zastosowania SOC2/HIPAA/RODO w pliku README.

Dane wyjściowe: repozytorium zawierające potok pozyskiwania, agent konwersacyjny LangGraph, złoty zestaw składający się z 200 pytań, czerwony zespół z 50 podpowiedziami, pulpit nawigacyjny Phoenix Dryf, pulpit kosztów Langfuse oraz opis zawierający trzy najczęściej zaobserwowane wzorce łamania cytowań oraz informacje o odzyskaniu lub natychmiastowej naprawie każdego z nich.