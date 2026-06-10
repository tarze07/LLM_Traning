---

name: re-designer
description: Zaprojektuj potok ekstrakcji relacji ze śledzeniem pochodzenia danych (provenance) oraz kanonizacją.
version: 1.0.0
phase: 5
lesson: 26
tags: [nlp, relation-extraction, knowledge-graph]

---

Na podstawie opisu korpusu (domena, język, wolumen) oraz sposobu dalszego wykorzystania danych (KG-RAG, analityka, zgodność/compliance) wygeneruj:

1. Ekstraktor: podejście oparte na wzorcach, uczenie nadzorowane, hybryda z użyciem LLM lub podejście typu few-shot/zero-shot. Podaj uzasadnienie powiązane z wymaganą precyzją (precision) oraz czułością (recall).
2. Ontologia: zamknięta lista relacji/właściwości (np. Wikidata, ontologia dziedzinowa) lub otwarta ekstrakcja informacji (Open IE) z etapem kanonizacji.
3. Pochodzenie danych (provenance): każda wyekstrahowana trójka musi zawierać dokładny zakres znaków (character span) w tekście źródłowym oraz identyfikator dokumentu. Jest to warunek niepodlegający negocjacjom na potrzeby audytowalności.
4. Strategia konsolidacji: identyfikator encji kanonicznej + identyfikator relacji + kwalifikatory czasowe oraz polityka deduplikacji.
5. Ewaluacja: precyzja (precision) i czułość (recall) obliczone na zbiorze 200 ręcznie etykietowanych trójek + współczynnik halucynacji (hallucination rate) na próbie danych wyekstrahowanych przez LLM.

Odrzuć każdy potok ekstrakcji relacji (RE) oparty na LLM, który nie weryfikuje zakresu tekstu źródłowego (character span provenance). Odrzuć wyniki otwartej ekstrakcji (Open IE) trafiające do produkcyjnego grafu wiedzy bez uprzedniej kanonizacji. Oznacz jako błąd potoki bez kwalifikatora czasowego w relacjach zmiennych w czasie (np. pracodawca, małżonek, stanowisko).
