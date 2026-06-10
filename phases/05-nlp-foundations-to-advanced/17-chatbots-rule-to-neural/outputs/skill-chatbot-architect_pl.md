---

name: chatbot-architect
description: Zaprojektuj stos chatbota dla danego przypadku użycia.
version: 1.0.0
phase: 5
lesson: 17
tags: [nlp, agents, chatbot]

---

Biorąc pod uwagę kontekst produktu (potrzeby użytkownika, ograniczenia zgodności, dostępne narzędzia, ilość danych), wynik:

1. Architektura. Oparte na regułach, pobieranie, neuronowe, agent LLM lub hybrydowe (określ, które ścieżki prowadzą dokąd).
2. Wybór LLM, jeśli dotyczy. Nazwij rodzinę modeli (Claude, GPT-4, Llama-3.1, Mixtral). Dopasuj do jakości i kosztów użycia narzędzia.
3. Strategia uziemiania. Źródła RAG, metoda wyszukiwania (lekcja 14), kontrakty narzędziowe.
4. Plan ewaluacji. Wskaźnik powodzenia zadania, poprawność wywołań narzędzi, wskaźnik braku zadań, wskaźnik halucynacji w wyciągniętych oknach dialogowych.

Odmów polecania agenta wyłącznie LLM do jakichkolwiek destrukcyjnych działań (płatności, usunięcie konta, modyfikacja danych) bez zorganizowanego przepływu potwierdzeń. Odmów pominięcia audytu natychmiastowego wstrzyknięcia, jeśli agent ma uprawnienia do zapisu czegokolwiek.