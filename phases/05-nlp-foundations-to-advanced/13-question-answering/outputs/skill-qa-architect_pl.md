---

name: qa-architect
description: Wybierz architekturę kontroli jakości, strategię wyszukiwania i plan oceny.
version: 1.0.0
phase: 5
lesson: 13
tags: [nlp, qa, rag]

---

Biorąc pod uwagę wymagania (wielkość korpusu, typ pytania, ograniczenie faktów, budżet opóźnień), wynik:

1. Architektura. Ekstrakcyjny, RAG z czytnikiem ekstrakcyjnym, RAG z czytnikiem generatywnym lub LLM z zamkniętą księgą. Powód w jednym zdaniu.
2. Retriever. Brak, BM25, gęsty (nazwij enkoder jak `all-MiniLM-L6-v2`) lub hybrydowy.
3. Czytelnik. Model dostrojony do SQuAD (`deepset/roberta-base-squad2`), LLM według nazwy lub DistilBERT dostrojony do domeny.
4. Ocena. EM + F1 dla wskaźników wydobywczych; dokładność odpowiedzi + dokładność cytowania + kalibracja odmowy do produkcji. Nazwij, co i w jaki sposób mierzysz.

Odmawiaj zamkniętych odpowiedzi LLM na pytania regulacyjne lub wrażliwe na zgodność. Odrzuć jakikolwiek system kontroli jakości bez linii bazowej polegającej na odzyskaniu-przypomnieniu (nie możesz ocenić czytelnika, nie wiedząc, że aporter znalazł właściwy fragment). Oznacz pytania, które wymagają rozumowania wieloskokowego, jako wymagające wyspecjalizowanych aporterów wieloskokowych, takich jak systemy przeszkolone przez HotpotQA.