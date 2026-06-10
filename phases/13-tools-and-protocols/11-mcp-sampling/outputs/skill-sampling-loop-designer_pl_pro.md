---

name: sampling-loop-designer
description: Zaprojektuj pętlę agentyczną hostowaną na serwerze z użyciem próbkowania MCP, określając preferencje modeli, rate limity oraz reguły bezpieczeństwa.
version: 1.0.0
phase: 13
lesson: 11
tags: [mcp, sampling, agent-loop, model-preferences]

---

Na podstawie zdefiniowanego algorytmu serwera wymagającego wnioskowania LLM (analiza, podsumowywanie, planowanie, selekcja) zaprojektuj architekturę pętli agentycznej opartej na mechanizmie próbkowania MCP.

Wygeneruj:

1. Struktura pętli konwersacji. Wypisz i ponumeruj poszczególne rundy próbkowania, określ strukturę promptów oraz oczekiwany format danych wyjściowych.
2. Konfiguracja `modelPreferences` dla każdej rundy. Przypisz wagi dla kosztu, szybkości i inteligencji (suma wag = 1.0) dla każdego etapu. Przykładowo: etap wstępnej selekcji plików powinien kłaść nacisk na niskie koszty, natomiast etap syntezy i podsumowania wymaga najwyższej inteligencji.
3. Limity częstotliwości zapytań (Rate limits). Zdefiniuj maksymalną liczbę żądań próbkowania przypadających na jedno wywołanie narzędzia (`max_samples_per_tool`) wraz z uzasadnieniem biznesowym.
4. Punkty weryfikacji (Security Hooks). Wskaż momenty, w których klient powinien poprosić użytkownika o akceptację żądania próbkowania, oraz zdefiniuj zachowanie systemu po odrzuceniu zapytania.
5. Integracja z SEP-1577. Określ, czy w pętli próbkowania zostaną użyte narzędzia pomocnicze. Jeśli tak, wskaż ryzyko związane z eksperymentalnym statusem specyfikacji oraz przygotuj listę planowanych narzędzi.

Kryteria odrzucenia (Twarde reguły):
- Zaprojektowanie pętli bez zdefiniowania limitu częstotliwości zapytań (ryzyko zapętlenia i kradzieży zasobów).
- Ustawienie parametru `includeContext: "allServers"` (wyciek danych między sesjami różnych serwerów).
- Scenariusz, w którym serwer żąda wygenerowania treści, a następnie przekazuje ją jako dane wejściowe do innego narzędzia bez weryfikacji i zatwierdzenia przez człowieka (podatność typu Confused Deputy).

Zasady odmowy usługi:
- Jeśli serwer posiada bezpośredni dostęp do kluczy LLM, zapytaj użytkownika, czy próbkowanie jest niezbędne (bezpośrednie zapytania do API mogą uprościć architekturę).
- Jeśli zapytanie dotyczy pojedynczego, jednorazowego wywołania narzędzia, odmów projektowania pętli (próbkowanie służy do realizacji procesów wieloetapowych).
- Jeśli użytkownik zażąda ukrycia zapytań próbkowania przed użytkownikiem końcowym na czacie, kategorycznie odmów (zakaz ukrytego próbkowania / covert sampling).

Format wyjściowy: Jednostronicowy projekt architektury zawierający etapy pętli, wagi preferencji modeli dla każdej rundy, konfigurację limitów zapytań oraz listę kontrolną bezpieczeństwa. Na końcu dodaj informację o ryzyku migracji związanym z eksperymentalnym statusem SEP-1577 (wywoływanie narzędzi w próbkowaniu).
