---

name: prompt-caching-planner
description: Zaprojektuj przyjazny dla pamięci podręcznej układ podpowiedzi i wybierz odpowiedni tryb buforowania dostawcy.
version: 1.0.0
phase: 11
lesson: 15
tags: [llm-engineering, caching, cost]

---

Biorąc pod uwagę monit (system + narzędzia + kilka zdjęć + pobieranie + historia + użytkownik) i profil użytkowania (żądania na godzinę, wymagany TTL, dostawca), wynik:

1. Układ. Zmieniono kolejność sekcji z zaznaczonym pojedynczym punktem przerwania pamięci podręcznej; wyjaśnij, które sekcje są stabilne, a które zmienne.
2. Tryb dostawcy. Anthropic cache_control, OpenAI Automatic lub Gemini CachedContent. Uzasadnij na podstawie TTL i użyj ponownie wzoru.
3. Próg rentowności. Oczekiwane odczyty na zapis w ramach TTL; koszt netto vs brak pamięci podręcznej z matematyką.
4. Plan weryfikacji. Twierdzenie CI, że cache_read_input_tokens > 0 w drugim identycznym żądaniu; podział panelu na tokeny buforowane i niebuforowane.
5. Tryby awarii. Wymień trzy najbardziej prawdopodobne przyczyny pominięcia pamięci podręcznej w tej konfiguracji (dynamiczny znacznik czasu, zmiana kolejności narzędzi, prawie zduplikowany tekst) i sposoby zapobiegania każdemu z nich.

Odmów dostarczenia planu pamięci podręcznej, który umieszcza pole dynamiczne powyżej punktu przerwania. Odmów włączenia 1h TTL bez licznika ponownego użycia, który powoduje zwrot 2x premii za zapis.