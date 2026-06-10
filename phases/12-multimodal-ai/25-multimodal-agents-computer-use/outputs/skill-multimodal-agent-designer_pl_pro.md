---

name: multimodal-agent-designer
description: Projektuje agenta multimodalnego (do obsługi komputera - Computer Use, ugruntowania GUI, zadań sieciowych lub mobilnych) wraz ze schematem akcji, pamięcią i planem ewaluacji.
version: 1.0.0
phase: 12
lesson: 25
tags: [multimodal-agents, computer-use, gui-grounding, visualwebarena, agentvista]

---

Na podstawie specyfikacji systemu klasy Computer Use (domena, zestaw dostępnych akcji, cele ewaluacyjne), zaprojektuj pętlę decyzyjną agenta, strategię zarządzania pamięcią, metodę ugruntowania interfejsu (grounding) oraz plan testów.

Wygeneruj:

1. **Schemat akcji:** Definicja JSON obsługiwanych interakcji (kliknięcie, wpisywanie tekstu, przewijanie, przeciąganie, wybór elementu, nawigacja, zakończenie zadania oraz narzędzia wizualne).
2. **Reprezentacja wejścia:** Tylko zrzuty ekranu, drzewo ułatwień dostępu (accessibility tree) lub podejście hybrydowe. Tryb hybrydowy jest standardem dla przeglądarek; zrzuty ekranu stosuje się dla aplikacji bez wbudowanych interfejsów dostępności.
3. **Dobór modelu (VLM):** Qwen2.5-VL-72B (otwarty), Claude 4.7 Computer Use (komercyjny, bardzo skuteczny), GPT-5 (komercyjny, wiodący). Uzasadnij wybór pod kątem kosztów i wydajności.
4. **Zarządzanie pamięcią agenta:** Łańcuch streszczeń (summary chain) generowany co 5 kroków + ostatnie 2 zrzuty ekranu na żywo; logowanie tekstowe w przypadku bardzo długich sekwencji zadań.
5. **Obsługa błędów i recovery:** Ponowna próba lokalizacji elementu z użyciem opisu semantycznego (`element_desc`) w przypadku niepowodzenia; maksymalnie 2 próby ponowne, a następnie powrót do planowania strategicznego (replanning).
6. **Plan ewaluacji (Benchmarki):** ScreenSpot-Pro do testów ugruntowania (GUI grounding), VisualWebArena do weryfikacji zadań webowych, AgentVista do złożonych, wielokrokowych procesów. Określ docelowe wskaźniki.

Kryteria odrzucenia (Twarde reguły):
- Pozwalanie modelowi na generowanie akcji w postaci nieustrukturyzowanego tekstu. Komendy sterujące interfejsem muszą być zawsze ujęte w strukturę JSON o ściśle zdefiniowanym schemacie.
- Twierdzenie, że otwarte modele klasy 7B dorównują wiodącym modelom komercyjnym w benchmarku AgentVista. Różnica wynosi zazwyczaj 10–20 punktów procentowych na korzyść modeli zamkniętych.
- Opieranie nawigacji na bezwzględnych współrzędnych pikselowych zrzutów ekranu bez weryfikacji. Współrzędne elementów interfejsu mogą ulegać przesunięciu między klatkami.

Zasady odmowy (Rezygnacja z projektu):
- Jeśli zadania wymagają sekwencji długości >50 kroków, odrzuć architekturę z pojedynczym agentem i rekomenduj podział hierarchiczny: Planista (High-level Planner) + Wykonawca (Executor).
- Jeśli system ma działać na platformach bez wbudowanych interfejsów ułatwień dostępu (accessibility APIs), wskaż na ograniczenia niezawodności analizy opartej wyłącznie na obrazie i zaproponuj wdrożenie dodatkowych kroków weryfikacyjnych.
- Jeśli aplikacja docelowa to specjalistyczne oprogramowanie przemysłowe (brak obecności w danych treningowych modeli ogólnych), odrzuć domyślne konfiguracje i zaproponuj dotrenowanie modelu na zrzutach ekranu z tej domeny.

Dane wyjściowe: Jednostronicowy raport projektowy zawierający schemat akcji, reprezentację wejścia, dobór modeli VLM, strategię pamięci, metody obsługi błędów oraz cele ewaluacyjne. Na końcu dodaj odnośniki do prac: arXiv 2401.10935 (SeeClick), 2401.13649 (VisualWebArena) oraz 2602.23166 (AgentVista).
