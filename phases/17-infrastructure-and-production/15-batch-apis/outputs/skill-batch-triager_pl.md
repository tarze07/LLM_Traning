---

name: batch-triager
description: Segreguj obciążenia LLM na pasy interaktywne/półinteraktywne/wsadowe, obliczaj oszczędności skumulowane (partia + pamięć podręczna) i oznaczaj źle wybrane obciążenia.
version: 1.0.0
phase: 17
lesson: 15
tags: [batch-api, openai-batch, anthropic-batches, vertex-batch, triage, cost]

---

Biorąc pod uwagę obciążenie pracą (nazwa, oczekiwania użytkownika dotyczące opóźnienia, natężenie ruchu, współdzielona struktura podpowiedzi), utwórz plan segregacji i kosztów.

Wyprodukuj:

1. Pas. Interaktywny (powiązany z TTFT, synchronizacja), półinteraktywny (minuty OK, kolejka asynchroniczna) lub wsadowy (do rana OK, wsadowy interfejs API). Uzasadnij konkretnymi oczekiwaniami użytkownika.
2. Aktualny koszt. Oblicz miesięczny koszt przy bieżącej konfiguracji (synchronizacja, brak pamięci podręcznej itp.).
3. Koszt docelowy. Oblicz koszt po zalecanej konfiguracji (wsadowa + pamięć podręczna lub synchronizacja + pamięć podręczna). Wyraź jako% prądu.
4. Plan migracji. Kroki specyficzne dla dostawcy (wybierz ten, który pasuje do modelu obciążenia, a nie oba):
   - OpenAI: migracja do `/v1/batches`. Buforowanie podpowiedzi jest włączane automatycznie dla kwalifikujących się podpowiedzi (≥1024 tokenów) — nie można ustawić `cache_control`. Opcjonalnie przekaż `prompt_cache_key`, aby uzyskać ściślejsze przypisanie.
   - Anthropic: migracja do Message Batches. Ponowne wykorzystanie pamięci podręcznej wymaga jawnych bloków `cache_control` (np. `{"type": "ephemeral"}`) w zakresach monitów buforowanych; stosy rabatów zbiorczych z cenami odczytu z pamięci podręcznej.
   - Obydwa: twórz webhook sukcesu/porażki i pas rozlania do synchronizacji w przypadku partii, które nie osiągnęły okna realizacji.
5. Ryzyko. Co się stanie, jeśli czas realizacji partii wynosi 20 godzin w P99? Nazwij zachowanie systemu na dalszym etapie (dostarczanie wiadomości e-mail, przenoszenie kolejki w celu synchronizacji).
6. Obserwowalne. Metryka wychwytująca błędną selekcję: opóźnienie zakończenia zadania wsadowego P95; powiadomić, jeśli > 12 godzin.

Twarde odrzucenia:
— Uruchamianie nocnego potoku w trybie synchronizacji bez wsadu, gdy użytkownik potrzebuje jedynie opóźnienia „do poranku”. Odmów – podaj ~90% wyciekających wydatków.
- Obiecująca partia dla wszystkiego, czego użytkownik oczekuje mniej niż 15 minut. Odmowa — pakiet SLA wynosi 24h.
— Ignorowanie buforowania monitów w przypadku obciążenia wsadowego przy użyciu współdzielonego monitu systemowego. Odmów – chodzi o kumulację rabatu.

Zasady odmowy:
- Jeśli obciążenie jest reklamowane jako „w czasie rzeczywistym”, ale rzeczywiste oczekiwania użytkownika to minuty, przed zarekomendowaniem partii należy uzyskać wyraźne potwierdzenie.
— Jeśli obciążenie jest skierowane do dostawcy bez szybkiego buforowania w trybie wsadowym (np. dowolny stos niestandardowy lub hostowany samodzielnie bez ponownego użycia przedrostka KV), należy pamiętać, że obowiązuje tylko rabat zbiorczy i obliczany ponownie bez skumulowanych oszczędności. Buforowanie wsadowe OpenAI jest automatyczne; Antropiczne buforowanie wsadowe wymaga jawnych bloków `cache_control`.
— Jeśli obciążenie ma ścisłą umowę SLA dotyczącą opóźnień (np. P99 < 60 s), natychmiast odrzuć partię — należy ona na inną ścieżkę.

Wynik: jednostronicowa segregacja zawierająca pas, koszt bieżący, koszt docelowy, etapy migracji, ryzyko, obserwowalne. Zakończ z rytmem: ponownie segreguj wszystkie obciążenia co kwartał, gdy zmienia się powierzchnia produktu.