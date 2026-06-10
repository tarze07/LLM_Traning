---

name: agents-sdk-scaffold
description: Stwórz szkielet aplikacji OpenAI Agents SDK z agentem selekcji (triage), przekazywaniem zadań (handoffs), barierami ochronnymi (guardrails) wejściowymi/wyjściowymi/narzędziowymi, magazynem sesji i procesorem śledzenia.
version: 1.0.0
phase: 14
lesson: 16
tags: [openai, agents-sdk, handoffs, guardrails, tracing, session]

---

Na podstawie domeny produktu i listy wyspecjalizowanych agentów zbuduj aplikację korzystającą z OpenAI Agents SDK.

Wyprodukuj:

1. Jednego agenta typu `Agent` dla każdego specjalisty oraz jednego agenta typu `triage`, który odpowiada wyłącznie za przekazywanie zadań (nie posiada narzędzi domenowych).
2. Narzędzie `FunctionTool` dla każdej domeny z określonym schematem danych wejściowych, jasnym opisem (wskazującym modelowi, kiedy należy go użyć) oraz izolowanym środowiskiem uruchomieniowym (piaskownicą).
3. Przekazanie zadań (`Handoff`) od agenta selekcji (triage) do każdego specjalisty. Upewnij się, że nazwy narzędzi są zgodne z konwencją `transfer_to_<agent>`.
4. `InputGuardrail` sprawdzający dane osobowe (PII), zgodność z politykami oraz zakres tematyczny. Domyślnie użyj trybu równoległego, chyba że model filtrujący LLM (guardrail) jest duży w porównaniu z głównym modelem – w takim przypadku zastosuj tryb blokujący.
5. `OutputGuardrail` weryfikujący długość, obecność danych osobowych (PII) oraz zgodność z politykami. Dla odpowiedzi kluczowych z punktu widzenia bezpieczeństwa zawsze stosuj tryb blokujący.
6. Bariery ochronne (guardrails) dedykowane dla konkretnych narzędzi funkcyjnych, które wchodzą w interakcję z siecią lub systemem plików.
7. Magazyn sesji (`Session` store) – domyślnie SQLite, a dla środowiska produkcyjnego Redis.
8. Skonfigurowanie `add_trace_processor` łączące backend z interfejsem śledzenia (tracing) OpenAI.

Kategoryczne odrzucenia (Twarde kryteria):

- Wyposażanie agentów selekcji (triage) w narzędzia domenowe. Agent triage powinien służyć wyłącznie do przekazywania zadań; łączenie tych funkcji pogarsza decyzje routingu.
- Bariery ochronne (guardrails) modyfikujące dane wejściowe lub wyjściowe. Poręcze powinny jedynie zatwierdzać lub odrzucać żądania, a nie modyfikować ich treść.
- Nieskończone lub ciche pętle przekazywania zadań. Wymagaj licznika przekazań (domyślnie maksymalnie 3).

Zasady odmowy wykonania usługi (Refusal rules):

- Jeśli użytkownik żąda „braku barier ochronnych dla szybszego działania”, odmów realizacji dla jakiegokolwiek produktu trafiającego do klientów końcowych lub przetwarzającego dane osobowe.
- Jeśli produkt ma tylko dwóch specjalistów, zasugeruj routing za pomocą prostego klasyfikatora bezpośredniego (Lekcja 12) zamiast pełnego agenta selekcji i przekazywania (triage & handoff) – pozwala to obniżyć zużycie tokenów.
- Jeśli śledzenie (tracing) jest wyłączone na produkcji, odmów wdrożenia. Wieloetapowe awarie są niemożliwe do zdiagnozowania bez logów śledzenia.

Pliki wynikowe: `agents.py`, `tools.py`, `guardrails.py`, `app.py`, `README.md` z uzasadnieniem wyboru agenta selekcji (triage), opisanymi trybami barier ochronnych (guardrails), procesorem śledzenia oraz backendem sesji. Zakończ sekcją „Dalsza lektura”, wskazując na Lekcję 23 (OTel GenAI), Lekcję 24 (backendy obserwowalności) lub Lekcję 17 (dotyczącą Claude Agent SDK).
