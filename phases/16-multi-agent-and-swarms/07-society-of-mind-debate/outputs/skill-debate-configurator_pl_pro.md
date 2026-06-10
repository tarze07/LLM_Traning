---

name: debate-configurator
description: Skonfiguruj debatę wieloagentową dla danego zadania, szacując przyrost jakości oraz koszty tokenów przed uruchomieniem systemu.
version: 1.0.0
phase: 16
lesson: 07
tags: [multi-agent, debate, society-of-mind, consensus]

---

Na podstawie pytania lub zadania utwórz konfigurację debaty gotową do wdrożenia w dowolnym środowisku agentowym (np. LangGraph, AutoGen, pętla niestandardowa).

Wygeneruj:

1. **Ocena dopasowania zadania.** Czy to zadanie kwalifikuje się do optymalizacji poprzez konsensus? Debata przynosi korzyści przy zadaniach logicznych, analizie faktów oraz dekompozycji; nie sprawdza się w procesach z natury deterministycznych (np. arytmetyka, kompilacja kodu) ani w czystej generacji treści (np. twórcze pisanie).
2. **Liczba agentów.** 3, 4 lub 5. Domyślnie 3; 4+ tylko wtedy, gdy budżet projektu pozwala na zwiększone koszty w celu uzyskania szerszego wachlarza opinii.
3. **Liczba rund.** 2 lub 3. Domyślnie 3; rzadko więcej. Odwołaj się do plateau opisanego przez Du i in.
4. **Heterogeniczność.** Ten sam model bazowy dla wszystkich uczestników (prostsze, tańsze rozwiązanie o wyższym ryzyku skorelowanych błędów) lub modele z różnych rodzin (np. Llama + Claude + GPT; zapewnia dekorelację błędów, ale jest droższe i wymaga warstwy routingu).
5. **Przypisanie ról.** Symetryczne (wszyscy agenci mają identyczne role) vs rola oponenta (jeden agent jest instruowany, aby kwestionować zdanie większości). Rola oponenta to proste i tanie zabezpieczenie przed kaskadowym potakiwaniem (konformizmem).
6. **Metoda agregacji.** Głosowanie większościowe (dla odpowiedzi dyskretnych), średnia ważona (dla wyników liczbowych) lub synteza dokonywana przez sędziego LLM (dla odpowiedzi otwartych).
7. **Szacowanie kosztów.** N agentów × R rund × mediana tokenów na turę. Podaj szacunkowy koszt w dolarach na podstawie aktualnych cenników dostawców API.

Twarde kryteria odrzucenia:

- Odrzuć konfiguracje zakładające więcej niż 5 agentów lub więcej niż 3 rundy bez bardzo silnego uzasadnienia biznesowego.
- Odrzuć projekty oparte wyłącznie na debacie symetrycznej dla zadań obarczonych wysokim ryzykiem konformizmu (potakiwania).
- Odrzuć stosowanie debaty w zadaniach, które posiadają deterministyczny weryfikator (np. kompilacja kodu, uruchamianie testów jednostkowych, precyzyjne obliczenia) — w takich przypadkach należy bezpośrednio wywołać weryfikator.

Zasady obsługi przypadków szczególnych:

- Jeśli zadanie polega na prostym wyszukiwaniu pojedynczego faktu, odrzuć debatę i zarekomenduj pojedynczego agenta z dostępem do narzędzia wyszukiwania (RAG).
- Jeśli zadanie ma charakter czysto kreatywny (np. napisanie wiersza), odrzuć debatę — proces ten ma tendencję do sprowadzania wyników do przeciętnej.
- Jeśli użytkownik nie określił budżetu tokenowego/finansowego, odrzuć projekt i poproś o jego zdefiniowanie. Debata generuje koszty od 5 do 15 razy wyższe niż pojedyncze wywołanie agenta.

Wynik: jednostronicowy raport konfiguracji. Rozpocznij od oceny dopasowania zadania, a zakończ szacunkowym wyliczeniem kosztów całkowitych.
