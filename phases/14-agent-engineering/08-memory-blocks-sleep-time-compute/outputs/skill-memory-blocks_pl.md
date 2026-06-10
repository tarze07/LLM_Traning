---

name: memory-blocks
description: Wygeneruj trójpoziomowy system pamięci w kształcie Letty (bloki podstawowe, przywracanie, archiwizacja) z agentem konsolidacji czasu uśpienia poza ścieżką krytyczną.
version: 1.0.0
phase: 14
lesson: 08
tags: [memory, letta, blocks, sleep-time, consolidation]

---

Biorąc pod uwagę docelowy czas wykonania, model podstawowy i (prawdopodobnie silniejszy) model czasu uśpienia, utwórz trójwarstwowy system pamięci z jawnymi typami bloków i konsolidacją asynchroniczną.

Wyprodukuj:

1. Typ `Block` z `label`, `value`, `limit`, `description`, `version`, `history`. Każdy zapis podbija wersję i zapisuje starą wartość. Odsłoń `near_limit(threshold=0.8)`.
2. `BlockStore` z co najmniej trzema domyślnymi blokami: `human` (fakty o użytkowniku), `persona` (samoświadomość agenta) i `task` (bieżący zakres). Zezwalaj na bloki zdefiniowane przez użytkownika.
3. Sklep `Recall` — log stronicowany według sesji. Automatyczny zapis w każdej turze. Ogon zostaje eksmitowany na czapce, ale można go odzyskać.
4. Sklep `Archival` — co najmniej dwa backendy (wektor, KV). Wstaw identyfikator rekordu zwrotów. Unieważnij zamiast usunąć w przypadku sprzeczności.
5. `PrimaryAgent`, który obsługuje zakręty i wysyła tylko nieprzetworzone zapisy. Brak podsumowania na ścieżce krytycznej.
6. `SleepTimeAgent`, który działa pomiędzy turami: sumuje bloki przekraczające próg, unieważnia sprzeczne zapisy archiwalne, zapisuje `learned_context` we wspólnych blokach.

Twarde odrzucenia:

- Dowolna operacja pamięci, która działa synchronicznie podczas tury skierowanej w stronę użytkownika, z wyjątkiem bezpośredniego wyszukiwania. Podsumowanie, utrwalenie, unieważnienie należy do przepustki na sen.
- Usuwanie zapisów archiwalnych w przypadku sprzeczności. Unieważnij, aby historia mogła zostać skontrolowana.
- Zapis do bloku Persona lub Safety bez etapu przeglądu. Bloki te kształtują zachowania na całym świecie; cichy zapisuje błędy maski.

Zasady odmowy:

- Jeśli środowisko wykonawcze nie jest w stanie utrzymać bloków między sesjami, odmów wysyłki produktu opisanego jako „pamięć”. Obniż roszczenie.
- Jeśli agent czasu uśpienia nie ma danych wyjściowych, odmów. Cicha konsolidacja to martwa strefa debugowania.
- Jeśli użytkownik poprosi o „żadnego unieważnienia, zawsze ufaj najnowszym zapisom”, odrzuć jakąkolwiek domenę, w której liczą się roszczenia historyczne (zgodność z przepisami, medyczne, prawne).

Dane wyjściowe: jeden plik na komponent plus plik `README.md` zawierający nazwy domyślnych bloków, rytm uśpienia i zasady rozwiązywania sprzeczności. Zakończ słowami „Co przeczytać dalej”, wskazując Lekcję 09, jeśli agent potrzebuje wnioskowania grafowego w oparciu o pamięć, lub Lekcję 23, jeśli produkt wymaga rozpiętości OTel podczas operacji pamięci.