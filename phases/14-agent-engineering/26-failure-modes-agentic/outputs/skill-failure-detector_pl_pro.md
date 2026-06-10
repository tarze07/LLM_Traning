---

name: failure-detector
description: Generowanie detektorów trybów awarii dla śladów agentów zintegrowanych z bazą śladów, służących do oznaczania pięciu typowych trybów awarii oraz specyficznych dla domeny sygnatur błędów.
version: 1.0.0
phase: 14
lesson: 26
tags: [failure-modes, masft, detection, observability]

---

Mając zdefiniowaną domenę produktu oraz dostęp do bazy śladów (traces), stwórz detektory trybów awarii agentów.

Zakres wdrożenia:

1. Detektory dla każdego z trybów awarii: `hallucinated_action`, `scope_creep`, `cascading_errors`, `context_loss`, `tool_misuse`, `success_hallucination`.
2. Detektory specyficzne dla domeny biznesowej (np. „utworzono Pull Request bez powiązanego issue” w narzędziu programistycznym lub „wysłano e-mail do > 5 odbiorców bez zatwierdzenia” w module marketingowym).
3. Moduł tagujący (tagger) uruchamiający wszystkie detektory dla każdego śladu i agregujący statystyki.
4. Alerty progowe: jeśli >=5% dzisiejszych śladów zostanie oznaczonych etykietą trybu awarii, wyślij powiadomienie (np. PagerDuty) lub utwórz zgłoszenie w systemie typu Jira.
5. Magazyn próbek: dla każdego oznaczonego śladu zapisuj dane wejściowe, wyjściowe oraz migawki stanu środowiska do analizy dla operatorów systemu.

Kryteria odrzucenia (Hard Rejects):

- Projektowanie detektorów wymagających wywołania modelu LLM dla każdego śladu na produkcji. Używaj detektorów opartych na regułach i wzorcach; sędziego LLM rezerwuj wyłącznie do asynchronicznej analizy próbek.
- Analizowanie wyłącznie jawnych błędów wykonania (wyjątków). Większość błędów jakościowych generuje poprawny format JSON lub tekst. Wymagana jest weryfikacja zawartości merytorycznej oraz stanu środowiska.
- Zapisywanie próbek z błędami bez wcześniejszego usuwania danych osobowych (PII). Próbki awarii często zawierają wrażliwe informacje i muszą być zanonimizowane przed zapisem.

Zasady odmowy (Refusal Rules):

- Jeśli użytkownik żąda „przechowywania wszystkich śladów bezterminowo”, odmów ze względu na koszty i wymogi RODO/compliance. Wprowadź próbkowanie na podstawie przypisanych tagów oraz retencję danych.
- Jeśli produkt nie posiada zdefiniowanej linii bazowej (baseline) reprezentującej poprawny stan aplikacji, odrzuć żądanie konfiguracji alertów o dryfie. Analiza dryfu wymaga punktu odniesienia.
- Jeśli detektory nie są wersjonowane w systemie kontroli wersji, odmów wdrożenia. Zmiany w logice detekcji mogą bez zapowiedzi zaburzyć sygnał alarmowy.

Dane wyjściowe: Pliki `detectors.py`, `tagger.py`, `alerts.py`, `retention.py`, `README.md` wyjaśniające progi alarmowe, reguły retencji danych oraz ścieżki eskalacji alertów. Zakończ sekcją „Co przeczytać dalej”, odsyłającą do lekcji 24 (Platformy obserwowalności) lub lekcji 27 (Prompt injection) w kontekście odporności na ataki i celowe manipulacje.
