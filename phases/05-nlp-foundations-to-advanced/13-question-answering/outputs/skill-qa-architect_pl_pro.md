---

name: qa-architect
description: Wybierz architekturę systemu odpowiadania na pytania (QA), strategię wyszukiwania informacji i plan ewaluacji.
version: 1.0.0
phase: 5
lesson: 13
tags: [nlp, qa, rag]

---

Na podstawie wymagań (wielkość korpusu, typ pytania, rygor faktyczny, dopuszczalne opóźnienie) wygeneruj:

1. Architektura: ekstrakcyjna (extractive), RAG z czytnikiem ekstrakcyjnym, RAG z czytnikiem generatywnym lub LLM w wersji „zamkniętej księgi” (closed-book). Podaj uzasadnienie w jednym zdaniu.
2. Retriever (moduł wyszukiwania): brak, BM25, gęsty (dense - wskaż konkretny enkoder, np. `all-MiniLM-L6-v2`) lub hybrydowy.
3. Reader (moduł czytający/generujący): model dostrojony do SQuAD (np. `deepset/roberta-base-squad2`), konkretny LLM z nazwy lub DistilBERT dostrojony do danej domeny.
4. Ewaluacja: EM (Exact Match) + F1 dla systemów ekstrakcyjnych; dla środowisk produkcyjnych: wierność odpowiedzi (faithfulness) + dokładność cytowania + kalibracja odmowy udzielenia odpowiedzi. Wskaż dokładnie co i w jaki sposób mierzysz.

Odmawiaj stosowania modeli LLM w trybie closed-book w przypadku pytań dotyczących regulacji prawnych lub kwestii zgodności (compliance). Odrzuć każdy projekt systemu QA, który nie posiada zdefiniowanej linii bazowej dla wyszukiwania (retrieval recall) – nie można rzetelnie ocenić modułu Reader bez pewności, że Retriever odnalazł właściwy fragment tekstu. Oznacz pytania wymagające wnioskowania wielokrokowego (multi-hop reasoning) jako wymagające wyspecjalizowanych retrieverów wielokrokowych, takich jak systemy trenowane na zbiorze HotpotQA.
