---

name: long-context-eval
description: Zaprojektuj zestaw testów (baterię ewaluacyjną) dla modeli o długim kontekście, dopasowany do konkretnego modelu i przypadku użycia.
version: 1.0.0
phase: 5
lesson: 28
tags: [nlp, long-context, evaluation]

---

Na podstawie modelu docelowego, docelowej długości kontekstu oraz przypadku użycia wygeneruj:

1. Testy: siatka głębokości × długości testu NIAH (Needle In A Haystack); zestaw testowy RULER dla wnioskowania wielokrokowego (multi-hop); niestandardowe zadanie dziedzinowe.
2. Próbkowanie: głębokości umieszczenia informacji: 0, 0,25, 0,5, 0,75, 1,0 dla każdej testowanej długości tekstu.
3. Metryki: wskaźnik skuteczności wyszukiwania (retrieval rate); wskaźnik poprawności wnioskowania (reasoning pass rate); czas do pierwszego tokena (TTFT); koszt pojedynczego zapytania.
4. Progi graniczne (cut-off): efektywna długość kontekstu dla wyszukiwania (próg 90% skuteczności) oraz efektywna długość kontekstu dla wnioskowania (próg 70% skuteczności). Raportuj obie te wartości.
5. Zapobieganie regresji: stałe środowisko testowe (test harness), uruchamiane ponownie przy każdej aktualizacji modelu w celu wychwycenia różnic (delt) w wynikach.

Odmawiaj uznania deklarowanego okna kontekstowego wyłącznie na podstawie karty informacyjnej modelu (model card). Odrzuć ewaluację opartą wyłącznie na testach NIAH w przypadku zadań wymagających wnioskowania wielokrokowego. Odrzuć wyniki testów długiego kontekstu podawane przez samego dostawcę modelu jako niezależny dowód skuteczności.
