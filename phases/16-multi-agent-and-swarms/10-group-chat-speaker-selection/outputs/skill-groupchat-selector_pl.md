---

name: groupchat-selector
description: Skonfiguruj selektor GroupChat w stylu AutoGen/AG2 dla zadania, nadając nazwę wariantowi selektora, terminacji i regułom zapobiegania gorącym głośnikom.
version: 1.0.0
phase: 16
lesson: 10
tags: [multi-agent, groupchat, autogen, ag2, speaker-selection]

---

Mając zadanie i listę agentów, utwórz konfigurację GroupChat: wybór selektora, dane wejściowe selektora, zasady zakończenia i poręcze.

Wyprodukuj:

1. **Wariant selektora.** Metoda okrężna (tani, uczciwy, ślepy na kontekst), wybór LLM (świadomy kontekstu, drogi) lub niestandardowy (LLM + powrót oparty na regułach).
2. **Wejścia selektora.** Jeśli wybrano LLM: N ostatnich wiadomości, specjalizacje agentów, liczba tur. Jeśli niestandardowe: wyraźne zasady.
3. **Zasady zakończenia.** Maksymalna liczba rund, żeton ZAKOŃCZENIA, weryfikator osiągniętego celu lub kombinacja.
4. **Ograniczenie przegrzania głośników.** Limit obrotów dla poszczególnych agentów, wynik zrównoważenia głośników na wejściu selektora, wymuszona rotacja po K kolejnych tur.
5. **Ograniczenie rozdęcia kontekstu.** Plan projekcji (określone widoki na rolę), punkty kontrolne podsumowania, limit kontekstu na agenta.
6. **Obserwowalność.** Dane wejściowe selektora dziennika, wybór selektora, opóźnienie agenta na turę.

Twarde odrzucenia:

- Dowolna konfiguracja wybrana przez LLM bez rejestrowania wejścia/wyjścia selektora. Debugowanie staje się niemożliwe.
- Konfiguracje bez limitu max_rounds.
- Czaty symetryczne (bez specjalizacji) dotyczące zadań związanych z rozumowaniem — zamiast tego użyj debaty (lekcja 07).

Zasady odmowy:

- Jeśli zadanie ma znaną strukturę DAG, odrzuć GroupChat i poleć statyczny wykres LangGraph ze względu na determinizm.
- Jeśli zadanie wymaga ścisłych ścieżek audytu, odmów GroupChat; polecam LangGraph ze wskaźnikiem kontrolnym.
- Jeśli liczba agentów jest większa niż 5-6, odrzuć płaski GroupChat i zaleć grupy zagnieżdżone lub wzór hierarchiczny.

Wynik: jednostronicowy opis konfiguracji GroupChat. Zamknij kosztorysem (wybór LLM wiąże się z jednym wywołaniem selektora na turę).