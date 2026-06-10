---

name: multimodal-agent-designer
description: Zaprojektuj agenta multimodalnego (do użytku komputerowego, uziemienia GUI, sieciowego lub mobilnego) ze schematem działania, strategią dotyczącą pamięci i planem oceny testów porównawczych.
version: 1.0.0
phase: 12
lesson: 25
tags: [multimodal-agents, computer-use, gui-grounding, visualwebarena, agentvista]

---

Biorąc pod uwagę specyfikację produktu do użytku komputerowego (domena, zestaw działań, cel oceny), zaprojektuj pętlę agenta, strategię pamięci, tryb uziemienia i ocenę.

Wyprodukuj:

1. Schemat działania. Definicja JSON obsługiwanych akcji (kliknięcie, pisanie, przewijanie, przeciąganie, wybieranie, nawigacja, gotowe oraz wszelkie narzędzia wizualne).
2. Tryb wprowadzania. Tylko zrzut ekranu, drzewo dostępności lub hybryda. Hybrydowe ustawienie domyślne dla przeglądarek; zrzut ekranu - tylko dla aplikacji komputerowych bez haków dostępności.
3. Wybór modelu. Qwen2.5-VL-72B (otwarty), Claude Opus 4.7 do użytku komputerowego (zamknięty, mocny), GPT-5 (zamknięty, silniejszy). Uzasadnij wzorcem i kosztem.
4. Strategia pamięci. Łańcuch podsumowań co 5 kroków + ostatnie 2 zrzuty ekranu na żywo; log-only w przypadku bardzo długich przepływów pracy.
5. Odzyskiwanie błędów. W przypadku niepowodzenia działania należy ponownie uziemić za pomocą wskazówki semantycznej element_desc; spróbuj ponownie do 2 razy; wrócić do ponownego planowania.
6. Plan ewaluacji. ScreenSpot-Pro do uziemienia, VisualWebArena do kompleksowego działania, AgentVista do trudnych, wieloetapowych przepływów pracy. Oczekiwany poziom punktacji.

Twarde odrzucenia:
- Korzystanie z wyników akcji w postaci dowolnego tekstu. Zawsze w strukturze JSON z jawnym schematem.
- Zgłaszanie otwartych modeli 7B pasuje do granicy w AgentVista. Różnica wynosi 10-20 punktów.
- Poleganie na pamięci współrzędnych na zrzutach ekranu. Współrzędne dryfują pomiędzy zapisami.

Zasady odmowy:
- Jeśli produkt wymaga przepływów pracy obejmujących > 50 kroków, odrzuć pętlę z jednym agentem i zaleć podział hierarchiczny planista + wykonawca.
- Jeśli produkt działa na regulowanej platformie bez haczyków dotyczących ułatwień dostępu, oznacz limit niezawodności dotyczący wyłącznie zrzutów ekranu i zaproponuj dokładną weryfikację.
- Jeśli kategoria zadania znajduje się poza przeszkolonymi dystrybucjami (specjalistyczne oprogramowanie przemysłowe), odrzuć gotowe zadanie i zaproponuj dostrojenie na zrzutach ekranu domeny.

Dane wyjściowe: jednostronicowy projekt agenta ze schematem działania, trybem wprowadzania, wyborem modelu, pamięcią, odzyskiwaniem, oceną. Zakończ na arXiv 2401.10935 (SeeClick), 2401.13649 (VisualWebArena), 2602.23166 (AgentVista).