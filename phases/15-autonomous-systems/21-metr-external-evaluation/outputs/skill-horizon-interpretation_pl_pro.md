---

name: horizon-interpretation
description: Dokonaj krytycznego przeglądu deklaracji dostawców dotyczących horyzontu czasowego modeli i przygotuj analizę rozbieżności między wynikami benchmarków a rzeczywistością wdrożeniową.
version: 1.0.0
phase: 15
lesson: 21
tags: [metr, time-horizon, hcast, re-bench, eval-vs-deploy, external-evaluation]

---

Na podstawie opublikowanych przez dostawcę deklaracji dotyczących horyzontu czasowego (np. „nasz model wykonuje zadania trwające 14 godzin z zachowaniem 50% niezawodności”) przygotuj analizę luk. Powinna ona ilościowo określić różnice między wynikami testów a rzeczywistym wdrożeniem oraz wskazać ewentualne słabości metodologiczne.

Przygotuj:

1. **Audyt metodologiczny.** Zidentyfikuj wykorzystany zestaw zadań (HCAST, RE-Bench, SWAA lub baza własna). Upewnij się, że ujawniono parametry dopasowania logistycznego (np. nachylenie krzywej, wielkość próby, przedział ufności). Horyzont czasowy zadeklarowany bez opisu metodologii należy traktować jako zwykły slogan marketingowy.
2. **Spójność rozkładu zadań.** Porównaj strukturę zadań testowych z rzeczywistym profilem pracy w środowisku produkcyjnym użytkownika. Jeśli rozkłady te znacząco się różnią (np. dostawca testuje model na zadaniach SWE, a wdrożenie dotyczy obsługi klienta), wyniki benchmarków nie mają przełożenia na rzeczywistość.
3. **Luka ewaluacyjna (eval-to-deploy gap).** Przyjmij margines błędu rzędu 10–40% między horyzontem testowym a rzeczywistym. Powołaj się na badanie Anthropic z 2024 roku nad fałszowaniem dopasowania (alignment faking) oraz Międzynarodowy Raport Bezpieczeństwa AI z 2026 roku opisujący optymalizację pod testy (gaming of evaluations). Rzeczywista luka zależy od protokołu testowego – jest wyższa w przypadku zadań nieustrukturyzowanych.
4. **Niedopasowanie narzędziowe.** W testach benchmarkowych model korzysta z idealnie sformatowanych, sprawdzonych narzędzi. W środowisku produkcyjnym integracje są znacznie bardziej chaotyczne. Oszacuj dodatkowe obniżenie wskaźnika niezawodności o 5–30%.
5. **Nadzór ludzki w pętli (HITL).** Benchmarki zazwyczaj nie zakładają obecności człowieka w pętli decyzyjnej. Wdrożenia produkcyjne z aktywnym udziałem HITL wykazują wyższą niezawodność, ale ograniczają stopień autonomii agenta. Skoryguj odpowiednio interpretację horyzontu czasowego.

Kryteria bezwzględnego odrzucenia (Hard rejects):
- Deklarowanie horyzontu czasowego bez podania metodologii źródłowej oraz wielkości próby.
- Założenie, że horyzont uzyskany w benchmarkach bezpośrednio przekłada się na niezawodność wdrożenia produkcyjnego.
- Powoływanie się na wyniki testów z roku 2025 lub wcześniejszych jako na dane aktualne (czas podwojenia wynosi ok. 7 miesięcy, przez co starsze dane szybko tracą aktualność).
- Interpretowanie horyzontu na poziomie 50% jako gwarancji poprawnego działania w większości przypadków (50% niezawodności to poziom losowy, jak rzut monetą).

Zasady odmowy zatwierdzenia:
- Jeśli dostawca odmawia ujawnienia metodologii, zablokuj proces i zażądaj publikacji źródłowej lub oficjalnej dokumentacji.
- Jeśli struktura zadań w testach benchmarkowych nie pokrywa się z profilem środowiska produkcyjnego, odrzuć wniosek i zażądaj przeprowadzenia testów wewnętrznych.
- Jeśli dostawca podaje horyzont czasowy bez analizy podatności na manipulacje ewaluacyjne (gaming) w swoim procesie testowym, odmów przyjęcia tych wskaźników jako wiarygodnej prognozy.

Format raportu z analizy horyzontu:

Raport musi zawierać:
- **Metodologia źródłowa** (wykorzystany zestaw testowy, metoda dopasowania krzywej, wielkość próby, przedział ufności)
- **Spójność rozkładu zadań** (porównanie profilu testowego i produkcyjnego wraz z procentowym stopniem pokrycia)
- **Szacunek luki ewaluacyjnej** (niska/średnia/wysoka wraz z uzasadnieniem)
- **Szacunek luki narzędziowej** (niska/średnia/wysoka)
- **Model nadzoru (HITL)** (porównanie w pełni autonomicznego podejścia testowego z produkcyjnym schematem HITL)
- **Skorygowany horyzont wdrożeniowy** (horyzont czasowy po uwzględnieniu luki ewaluacyjnej i narzędziowej)
- **Status gotowości** (produkcja / środowisko przejściowe / badania)
