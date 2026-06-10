---

name: prompt-caching-planner
description: Zaprojektuj układ promptu przyjazny dla pamięci podręcznej i dobierz optymalny model buforowania dostawcy.
version: 1.0.0
phase: 11
lesson: 15
tags: [llm-engineering, caching, cost]

---

Biorąc pod uwagę strukturę promptu (system + narzędzia + przykłady few-shot + pobieranie RAG + historia + użytkownik) oraz profil użycia (częstotliwość zapytań, wymagany TTL, dostawca), wygeneruj:

1. **Układ promptu:** Uporządkowany układ sekcji ze wskazaniem granicy cache (cache breakpoint); wyjaśnij, które sekcje są stabilne, a które zmienne.
2. **Model buforowania:** Dobór i uzasadnienie wdrożenia (Anthropic `cache_control`, OpenAI automatic lub Gemini `CachedContent`) w zależności od TTL i oczekiwanego wzorca ponownego użycia.
3. **Analizę rentowności:** Obliczenie liczby wymaganych odczytów na jeden zapis w oknie TTL oraz symulacja kosztów przed i po optymalizacji (z wyliczeniami matematycznymi).
4. **Plan weryfikacji:** Konfiguracja asercji w testach CI sprawdzających, czy `cache_read_input_tokens > 0` przy drugim identycznym zapytaniu, oraz projekt podziału metryk na tokeny buforowane i niebuforowane.
5. **Ryzyka unieważnienia cache:** Wyszczególnienie trzech głównych powodów unieważniania cache w danej architekturze (np. dynamiczne daty/znaczniki czasu, zmienna kolejność narzędzi, drobne różnice znakowe w tekście) wraz z metodami zapobiegania tym problemom.

Zablokuj plany wdrożenia umieszczające zmienne dynamiczne powyżej granicy cache. Blokuj wdrożenia 1h TTL w Anthropic bez wykazania opłacalności finansowej (liczba odczytów) względem 2x wyższego kosztu zapisu.
