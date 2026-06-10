---

name: entity-linker
description: Zaprojektuj potok łączący encje — KB, generator kandydatów, ujednoznacznienie, ocena.
version: 1.0.0
phase: 5
lesson: 25
tags: [nlp, entity-linking, knowledge-graph]

---

Biorąc pod uwagę przypadek użycia (KB domeny, język, wolumen, budżet opóźnień), wynik:

1. Baza wiedzy. Wikidane / Wikipedia / niestandardowy KB. Data wersji. Odśwież rytm.
2. Generator kandydatów. Indeks aliasów, osadzanie lub hybryda. Przypomnienie wzmianki o celu @ K.
3. Ujednoznaczniający. Wcześniejszy + kontekst, oparty na osadzaniu, generatywny lub podpowiadany przez LLM.
4. Strategia NIL. Próg najwyższego wyniku, klasyfikatora lub wyraźnego kandydata NIL.
5. Ocena. Wspomnij o przywołaniu @ 30, najwyższej dokładności, wykrywaniu NIL F1 na zestawie trzymanym.

Odrzuć jakikolwiek potok EL bez linii bazowej przypominającej wzmiankę (nie możesz ocenić ujednoznaczniania, nie wiedząc, że kandydat na gen pojawił się na właściwym poziomie). Odrzuć dowolny potok używający EL podpowiadanego przez LLM bez ograniczonego wyjścia do prawidłowych identyfikatorów KB. Systemy flag, w których stronniczość popularności wpływa na podmioty mniejszościowe (np. konflikty nazw) bez dostrajania domeny.