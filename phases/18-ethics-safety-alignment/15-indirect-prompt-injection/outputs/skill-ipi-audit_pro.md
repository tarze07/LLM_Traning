---

name: ipi-audit
description: Audyt wdrożenia agenta pod kątem pośredniego wstrzykiwania instrukcji (indirect prompt injection) oraz zakresu kontroli przepływu informacji (IFC).
version: 1.0.0
phase: 18
lesson: 15
tags: [ipi, indirect-prompt-injection, ifc, agent-security, owasp-llm01]

---

Na podstawie opisu wdrożenia agenta przeprowadź inspekcję systemu pod kątem podatności na pośrednie wstrzykiwanie instrukcji (indirect prompt injection).

Wyprodukuj:

1. Źródła niezaufanych treści. Wypisz wszystkie źródła danych, które agent może odczytywać: dokumenty RAG, skrzynkę odbiorczą, kalendarz, wyniki działania narzędzi, zgłoszenia, recenzje produktów czy zewnętrzne interfejsy API (stron trzecich). Każde z nich stanowi potencjalny wektor ataku IPI.
2. Etykietowanie poziomów zaufania. Czy wdrożony system odróżnia treści zaufane (prompty użytkownika) od niezaufanych (pobrane dane)? Jeśli te treści zostaną połączone w jednym zapytaniu bez odpowiedniego oznaczenia, mechanizm IFC (Information Flow Control) nie będzie działać.
3. Bramkowanie akcji. Z jakich narzędzi korzysta system? Czy każde wywołanie narzędzia jest autoryzowane wyłącznie przez zaufany prompt, czy też niezaufana treść może wpłynąć na to wywołanie?
4. Ocena podatności na ataki adaptacyjne. Czy wdrożenie zostało przetestowane pod kątem ataków adaptacyjnych (metody gradientowe, RL, ludzki red-teaming) zgodnie z pracą Nasra i in. (2025)? Ocena oparta wyłącznie na statycznych atakach jest niewystarczająca.
5. Granice zaufania i ich naruszenia. Zidentyfikuj wszystkie granice zaufania (np. skrzynka odbiorcza -> wysyłanie wiadomości, dokumenty -> zewnętrzny interfejs API). Dla każdego przypadku sprawdź, czy dane działanie jest zabronione pod wpływem niezaufanych treści, czy też wymaga wyraźnego zatwierdzenia przez zaufany prompt.

Kryteria odrzucenia (Hard rejects):
- Dowolne wdrożenie agenta bez wyraźnego oznaczania poziomu zaufania dla pobieranych treści.
- Wszelkie deklaracje bezpieczeństwa oparte wyłącznie na testach z użyciem ataków statycznych.
- Wszelkie twierdzenia typu „nasze rozwiązanie jest odporne na prompt injection” bez wskazania mechanizmu IFC.

Zasady odmowy (Refusal rules):
- Jeśli użytkownik zapyta, czy filtrowanie jest wystarczającym zabezpieczeniem, udziel odpowiedzi odmownej i przytocz wnioski z pracy Nasr i in. (2025) wykazujące, że ataki adaptacyjne omijają ponad 90% zabezpieczeń opartych na filtrach.
- Jeśli użytkownik poprosi o jedno uniwersalne zabezpieczenie (tzw. silver bullet), odmów – skuteczna obrona przed IPI wymaga wdrożenia IFC, wielowarstwowej moderacji odpowiedzi oraz weryfikacji przez człowieka (human-in-the-loop) w przypadku działań o krytycznym znaczeniu.

Oczekiwany rezultat: raport z audytu zawierający analizę pięciu powyższych obszarów, wskazujący najbardziej krytyczną granicę między strefami o różnym poziomie zaufania oraz wymieniający najpilniejsze zabezpieczenie do wdrożenia. Należy jednokrotnie zacytować publikację MDPI Information 17(1):54 (2026) oraz pracę Nasr i in. (październik 2025 r.).
