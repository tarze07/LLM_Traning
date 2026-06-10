---

name: case-study-mapper
description: Dopasuj proponowaną architekturę systemu wieloagentowego do najbliższego produkcyjnego punktu odniesienia z 2026 r. (System badawczy Anthropic, MetaGPT/ChatDev lub OpenClaw/Moltbook). Narzędzie analizuje znane kompromisy, rekomendowane frameworki i konkretne decyzje projektowe sprawdzone w praktyce produkcyjnej.
version: 1.0.0
phase: 16
lesson: 25
tags: [multi-agent, case-studies, production, framework-selection, reference-architectures]

---

Mając do dyspozycji proponowaną architekturę systemu wieloagentowego, dopasuj ją do najbliższego kanonicznego studium przypadku z 2026 roku i dostosuj projekt na tej podstawie.

Przygotuj:

1. **Profil (charakterystyka) projektu.** Typ zadania (badawczy / inżynieryjny / populacyjny / automatyzacyjny), liczba agentów, wymagania dotyczące weryfikacji, czas trwania sesji, stopień zróżnicowania ról, interakcja użytkownika z siecią agentów (exposure to agent network).
2. **Najbliższe studium przypadku.**
   - **System badawczy Anthropic** – jeśli: zadanie ma charakter badawczy lub polega na pozyskiwaniu wiedzy, weryfikacja jest obowiązkowa, sesje trwają wiele godzin, a agenci różnią się przede wszystkim oknem kontekstowym i zakresem danych (najlepsze rezultaty dają subagenci z czystym kontekstem).
   - **MetaGPT / ChatDev** – jeśli: zadanie ma charakter inżynieryjny lub opiera się na ustrukturyzowanym przepływie pracy, role są wyraźnie rozróżnialne (np. planista / programista / recenzent / tester), a artefakty przekazywania zadań są precyzyjnie zdefiniowane.
   - **OpenClaw / Moltbook** – jeśli: system działa w skali populacyjnej, sieć agentów wchodzi w bezpośrednie interakcje z użytkownikami, ataki typu prompt injection stanowią poważne zagrożenie i kluczowe są oddolne (wschodzące) mechanizmy rynkowe.
3. **Wzorce do wdrożenia.** Konkretne decyzje projektowe z wybranego studium przypadku, które mają zastosowanie w nowym projekcie: subagenci z czystym kontekstem, wdrożenia typu rainbow, komunikacyjne zapobieganie halucynacjom, routing za pomocą grafu DAG, niezależny weryfikator (read-only verifier), zabezpieczenia na poziomie środowiska (substratu).
4. **Zalecenie dotyczące platformy.** LangGraph, CrewAI, AG2, Microsoft Agent Framework, OpenAI Agents SDK, Google ADK, Anthropic Claude Agent SDK lub rozwiązanie niestandardowe. Wskaż domyślny framework powiązany z danym studium przypadku; zaznacz, jeśli dla konkretnego projektu istnieje lepsze dopasowanie.
5. **Antywzorce projektowe.** Rozwiązania, które w analizowanym studium przypadku okazały się nieskuteczne. Unikaj ich w nowym projekcie.
6. **Prognoza kosztów.** Oczekiwany mnożnik zużycia tokenów (System badawczy Anthropic: ~15x; MetaGPT: ~5x; OpenClaw: zależnie od efektów sieciowych). Szacowany czas rzeczywisty (wall-clock time) i koszt finansowy.
7. **Podejście ewaluacyjne.** Dobór benchmarku (MARBLE, SWE-bench Pro, wewnętrzny); określenie, jaki wzrost skuteczności (delta) w stosunku do wartości bazowej z wybranego studium przypadku jest realistyczny i uzasadniony.

Bezwzględne odrzucenie projektów w przypadku:

- Pomijania weryfikacji, gdy zadanie wymaga wysokiej poprawności działania. Każde z analizowanych studiów przypadków uwzględnia narzut na weryfikację.
- Projektowania nowego środowiska (substratu) bez uwzględnienia podatności na wstrzykiwanie promptów jako realnego wektora ataku. Przypadek OpenClaw/Moltbook udowadnia, że jest to poważny problem produkcyjny, a nie czysto teoretyczny.
- Twierdzeń o „rewolucyjnych” osiągnięciach, które nie odnoszą się do żadnego znanego studium przypadku. Systemy wieloagentowe działają produkcyjnie od 2024 roku; nowe rozwiązania wymagają rzetelnego porównania.
- Pomijania implementacji standardów MCP lub A2A bez wyraźnego uzasadnienia. Obsługa tych protokołów to absolutne minimum.

Zasady weryfikacji i wstrzymania analizy:

- Jeśli cele projektu nie są sprecyzowane, zaleca się określenie zakresu zadań przed doborem studium przypadku. Tworzenie „agenta do wszystkiego” nie jest właściwym projektem.
- Jeśli projekt jest zgłaszany jako gotowy do produkcji, ale nie przeszedł analizy obsługi błędów i awarii, przed wykonaniem mapowania zaleca się przeprowadzenie audytu w standardzie MAST (lekcja 23).
- Jeśli projekt ma charakter wyłącznie eksperymentalny/badawczy, wskaż, które jego elementy wymagają dopracowania przed wdrożeniem produkcyjnych wzorców ze studium przypadku.

Format wyjściowy: Dwustronicowy brief. Rozpocznij od jednozdaniowego podsumowania (np. „Najbliższe studium przypadku: MetaGPT / ChatDev. Należy zastosować podział ról na podstawie SOP, komunikacyjne zapobieganie halucynacjom oraz ustrukturyzowane artefakty przekazywania zadań; zalecany framework to CrewAI lub rozwiązanie niestandardowe”), a następnie przedstaw siedem powyższych sekcji. Zakończ 90-dniowym planem wdrożenia: określ, które wzorce z projektu referencyjnego należy skopiować, które dostosować, a które zweryfikować w testach porównawczych.
