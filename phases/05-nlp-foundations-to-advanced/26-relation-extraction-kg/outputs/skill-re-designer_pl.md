---

name: re-designer
description: Zaprojektuj rurociąg ekstrakcji relacji z pochodzeniem i kanonizacją.
version: 1.0.0
phase: 5
lesson: 26
tags: [nlp, relation-extraction, knowledge-graph]

---

Biorąc pod uwagę korpus (domena, język, wolumen) i dalsze wykorzystanie (KG-RAG, analityka, zgodność), wynik:

1. Ekstraktor. Oparta na wzorcach / nadzorowana / hybryda LLM / AEVS. Powód związany z precyzją a celem wycofania.
2. Ontologia. Zamknięta lista właściwości (Wikidane / domena) lub otwarta IE z przepustką kanonizacyjną.
3. Pochodzenie. Każda trójka zawiera źródłowy zakres znaków + identyfikator dokumentu. Nie podlega negocjacjom w celu przeprowadzenia audytu.
4. Strategia połączenia. Identyfikator encji kanonicznej + identyfikator relacji + kwalifikatory czasowe; polityka deduplikacji.
5. Ocena. Precyzja / wycofanie na 200 ręcznie oznakowanych trójkach + współczynnik halucynacji na próbce wyekstrahowanej LLM.

Odrzuć jakikolwiek rurociąg RE oparty na LLM bez weryfikacji rozpiętości (pochodzenia źródła). Odrzuć dane wyjściowe otwartego IE wpływające do wykresu produkcyjnego bez kanonizacji. Oznacz potoki bez kwalifikatora czasowego w relacjach ograniczonych w czasie (pracodawca, małżonek, stanowisko).