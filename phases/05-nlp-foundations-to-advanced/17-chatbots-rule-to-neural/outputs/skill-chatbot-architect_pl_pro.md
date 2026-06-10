---
name: chatbot-architect
description: Zaprojektuj architekturę chatbota dla wybranego scenariusza użycia.
version: 1.0.0
phase: 5
lesson: 17
tags: [nlp, agents, chatbot]
---

Na podstawie kontekstu produktowego (potrzeby użytkownika, ograniczenia prawne/zgodności, dostępne narzędzia, wolumen danych) wygeneruj:

1. Architektura: Regułowa, oparta na wyszukiwaniu, neuronowa, agent LLM lub hybrydowa (ze wskazaniem ścieżek obsługi).
2. Wybór LLM (jeśli dotyczy): Wskaż rodzinę modeli (Claude, GPT, Llama, Mixtral) dopasowaną do wymagań jakościowych (tool-use) oraz budżetu.
3. Strategia osadzania kontekstowego (Grounding): Źródła danych dla RAG, metoda wyszukiwania (patrz lekcja 14) oraz interfejsy narzędzi.
4. Plan ewaluacji: Wskaźnik sukcesu zadań (task success rate), poprawność wywołań narzędzi, odsetek zboczenia z tematu (off-task rate), poziom halucynacji na wydzielonym zbiorze dialogów testowych.

Nigdy nie rekomenduj agenta opartego wyłącznie na modelu LLM do wykonywania operacji krytycznych (płatności, usuwanie konta, modyfikacja danych) bez wdrożenia ustrukturyzowanego procesu potwierdzeń. Bezwzględnie wymagaj audytu bezpieczeństwa pod kątem podatności na Prompt Injection (wstrzykiwanie instrukcji), jeśli agent posiada uprawnienia do zapisu.
