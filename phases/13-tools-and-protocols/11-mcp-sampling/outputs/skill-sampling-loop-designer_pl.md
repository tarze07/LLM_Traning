---

name: sampling-loop-designer
description: Zaprojektuj pętlę agenta hostowaną na serwerze, korzystając z próbkowania MCP z odpowiednimi preferencjami modelu, limitami szybkości i potwierdzeniami bezpieczeństwa.
version: 1.0.0
phase: 13
lesson: 11
tags: [mcp, sampling, agent-loop, model-preferences]

---

Biorąc pod uwagę algorytm po stronie serwera, który wymaga rozumowania LLM (badania, podsumowanie, planowanie, selekcja), zaprojektuj implementację opartą na próbkowaniu MCP.

Wyprodukuj:

1. Struktura pętli. Ponumeruj każdą rundę próbkowania, podaj kształt podpowiedzi i oczekiwany typ wyniku.
2. `modelPreferences` na rundę. Koszt wagi/szybkość/inteligencja (suma 1,0) na rundę. Runda „wyboru plików” zmniejsza koszt; runda „syntetyzowania” rozwija inteligencję.
3. Limit stawki. Ustaw `max_samples_per_tool` na wywołanie; uzasadnij liczbę.
4. Haki zabezpieczające. Określ, gdzie klient powinien wyświetlić okno dialogowe z potwierdzeniem i co robi ścieżka odmowy.
5. Włączenie SEP-1577. Zdecyduj, czy użyć narzędzi w ramach próbkowania; jeśli tak, oznacz ryzyko dryfu i podaj listę narzędzi.

Twarde odrzucenia:
- Dowolna pętla bez limitu szybkości. Bomby pętlowe i ryzyko kradzieży zasobów.
- Dowolna pętla ustawiająca `includeContext: "allServers"`. Wyciek między serwerami.
- Dowolna pętla, w której serwer prosi klienta o wygenerowanie treści, która jest następnie przekazywana jako dane wejściowe narzędzia bez potwierdzenia przez użytkownika. Zdezorientowany zastępca wektora.

Zasady odmowy:
- Jeśli serwer ma własne poświadczenia LLM, zapytaj, czy rzeczywiście potrzebne jest pobieranie próbek; połączenia bezpośrednie mogą być prostsze.
- Jeśli przypadek użycia to pojedyncze, jednorazowe wywołanie narzędzia, odmów projektowania pętli próbkowania; pobieranie próbek służy rozumowaniu wielorundowemu.
- Jeśli użytkownik poprosi o pętlę próbkowania, która ukrywa jego zamiary przed użytkownikiem końcowym, kategorycznie odmów (ukryte pobieranie próbek).

Wynik: jednostronicowy projekt z krokami pętli, preferencjami modelu na rundę, limitem szybkości i listą kontrolną bezpieczeństwa. Zakończ notatką oznaczającą ryzyko dryfu SEP-1577 (pobieranie próbek) istotne dla projektu.