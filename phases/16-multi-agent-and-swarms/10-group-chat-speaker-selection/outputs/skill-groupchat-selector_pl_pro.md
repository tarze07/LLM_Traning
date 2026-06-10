---

name: groupchat-selector
description: Skonfiguruj selektor GroupChat w stylu AutoGen/AG2 dla wybranego zadania, określając wariant selektora, warunki zakończenia oraz reguły zapobiegające dominacji jednego rozmówcy (hot speaker).
version: 1.0.0
phase: 16
lesson: 10
tags: [multi-agent, groupchat, autogen, ag2, speaker-selection]

---

Na podstawie opisu zadania oraz listy agentów, przygotuj konfigurację dla GroupChat: wariant selektora, dane wejściowe dla selektora, reguły zakończenia i mechanizmy zabezpieczające (guardrails).

Opracuj:

1. **Wariant selektora.** Metoda cykliczna/round-robin (tania, sprawiedliwa, ignorująca kontekst), wybór przez LLM (uwzględniający kontekst, kosztowny) lub niestandardowy (wybór przez LLM + reguły rezerwowe/fallback).
2. **Dane wejściowe selektora.** Przy wyborze przez LLM: N ostatnich wiadomości, specjalizacje agentów, licznik tur. W przypadku reguł niestandardowych: precyzyjnie zdefiniowane zasady.
3. **Warunki zakończenia.** Maksymalna liczba rund, token zakończenia (np. `TERMINATE`), weryfikacja osiągnięcia celu lub kombinacja tych metod.
4. **Zapobieganie dominacji jednego rozmówcy.** Limit tur na agenta, wskaźnik zrównoważenia wypowiedzi jako metryka wejściowa dla selektora, wymuszona rotacja po K kolejnych wypowiedziach jednego agenta.
5. **Ograniczenie przepełnienia kontekstu.** Plan projekcji pamięci (filtrowanie historii per rola), generowanie podsumowań (summary checkpoints), limit rozmiaru kontekstu na agenta.
6. **Obserwowalność.** Logowanie danych wejściowych i decyzji selektora, monitorowanie opóźnień (latency) agentów na każdą turę.

Kryteria wykluczające:

- Konfiguracja wyboru przez LLM bez włączonego logowania danych wejściowych i wyjściowych selektora (uniemożliwia to debugowanie).
- Brak zdefiniowanego limitu maksymalnej liczby rund (max_rounds).
- Symetryczne czaty (agenci bez wyraźnej specjalizacji) w zadaniach wymagających rozumowania — w takich przypadkach zalecana jest topologia debaty (Lekcja 07).

Zasady odmowy (rejection rules):

- Jeśli zadanie ma z góry znaną strukturę DAG, odrzuć GroupChat i zaleć statyczny graf LangGraph w celu zapewnienia determinizmu.
- Jeśli zadanie wymaga ścisłych ścieżek audytowych, odrzuć GroupChat; zaleć LangGraph z zapisem stanu (checkpointing).
- Jeśli liczba agentów przekracza 5-6, odrzuć płaski schemat GroupChat i zaleć zagnieżdżone grupy lub wzorzec hierarchiczny.

Format wyjściowy: jednostronicowy opis konfiguracji GroupChat. Zakończ szacunkowym kosztorysem (pamiętaj, że wybór przez LLM generuje jedno zapytanie do modelu na każdą turę).
