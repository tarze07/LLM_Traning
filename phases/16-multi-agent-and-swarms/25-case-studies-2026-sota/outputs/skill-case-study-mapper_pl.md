---

name: case-study-mapper
description: Przypisz proponowany projekt systemu wieloagentowego do najbliższego odniesienia produkcyjnego z 2026 r. (Anthropic Research, MetaGPT/ChatDev lub OpenClaw/Moltbook). Poznaj znane kompromisy, zalecane ramy i konkretne decyzje projektowe już przetestowane w produkcji.
version: 1.0.0
phase: 16
lesson: 25
tags: [multi-agent, case-studies, production, framework-selection, reference-architectures]

---

Biorąc pod uwagę proponowany projekt systemu wieloagentowego, wybierz najbliższe kanoniczne studium przypadku z roku 2026 i dostosuj się.

Wyprodukuj:

1. **Odcisk palca projektu.** Typ zadania (badania / inżynieria / populacja / automatyzacja), liczba agentów, wymagania weryfikacji, czas trwania, odrębność ról, narażenie użytkownika na sieć.
2. **Najbliższe studium przypadku.**
   - **Badania Antropiczne** jeśli: zadanie badawcze lub polegające na pozyskiwaniu wiedzy, weryfikacja jest obowiązkowa, przebiegi wielogodzinne, agenci różnią się przede wszystkim kontekstem i zakresem (wygrywają subagenci świeżego kontekstu).
   - **MetaGPT / ChatDev** jeśli: inżynieria lub zorganizowany przepływ pracy, role są wyraźnie rozróżnialne (planista / programista / recenzent / tester), artefakty przekazania są dobrze napisane.
   - **OpenClaw / Moltbook** jeśli: skala populacji, sieć agentów skierowana do użytkowników, natychmiastowe wstrzyknięcie stanowi znaczące zagrożenie, liczy się wschodząca gospodarka.
3. **Wzorce do skopiowania.** Konkretne decyzje projektowe z wybranego studium przypadku, które mają zastosowanie: podagenci świeżego kontekstu, wdrażanie tęczy, dehalucynacja komunikacyjna, routing DAG, weryfikator niezapisywalny, bezpieczeństwo na poziomie substratu.
4. **Zalecenie dotyczące platformy.** LangGraph, CrewAI, AG2, Microsoft Agent Framework, OpenAI Agents SDK, Google ADK, Anthropic Claude Agent SDK lub niestandardowe. Domyślnie typowe ramy studium przypadku; zwróć uwagę, czy istnieje lepsze dopasowanie dla konkretnego projektu.
5. **Antywzorce z przypadku.** Rzeczy, które według przypadku referencyjnego NIE sprawdziły się. Unikaj w nowym projekcie.
6. **Prognoza kosztów.** Oczekiwany mnożnik tokena (Anthropic Research: ~15x; MetaGPT: ~5x; OpenClaw: zależy od efektów sieciowych). Oczekiwany zakres cen zegarów ściennych i dolarów.
7. **Podejście ewaluacyjne.** Który benchmark (MARBLE, SWE-bench Pro, wewnętrzny) jest istotny; jaka delta w stosunku do wartości bazowej ze studium przypadku jest uzasadniona do osiągnięcia.

Twarde odrzucenia:

- Projekty ignorujące weryfikację, gdy zadanie ma wymagania poprawności. Każde studium przypadku opłaca podatek weryfikacyjny.
- Projekty, które wymagają nowego podłoża bez uznania, że ​​natychmiastowe wstrzyknięcie jest powierzchnią ataku. Przypadek OpenClaw/Moltbook pokazuje, że jest to problem produkcyjny, a nie hipotetyczny.
- Twierdzenia „rewolucyjne”, które nie mają odniesienia do żadnego studium przypadku. Multiagent jest w produkcji od 2024 roku; nowe twierdzenia wymagają wyraźnego porównania.
- Projekty, które bez uzasadnienia pomijają przyjęcie MCP lub A2A. Obsługa protokołów to stawki tabelaryczne.

Zasady odmowy:

- Jeśli projekt nie ma jasnego rodzaju zadania, zalecamy określenie zakresu zadania przed wybraniem studium przypadku. „Multiagent do wszystkiego” nie jest projektem.
- Jeśli projekt deklaruje gotowość do produkcji, ale nie zawiera audytu trybu awaryjnego, przed mapowaniem referencyjnym zaleca się audyt w stylu MAST (lekcja 23).
- Jeśli projekt ma charakter wyłącznie eksperymentalny/badawczy, zwróć uwagę, które aspekty wymagałyby dopracowania przed przyjęciem wzorców produkcyjnych przedstawionych w studium przypadku.

Wynik: dwustronicowy brief. Zacznij od jednozdaniowego podsumowania („Najbliższe studium przypadku: MetaGPT / ChatDev. Przyjmij rozkład ról na SOP, komunikacyjną dehalucynację i ustrukturyzowane artefakty przekazania; użyj CrewAI lub niestandardowej.”), a następnie siedem sekcji powyżej. Zakończ 90-dniowym planem adaptacji: co skopiować z referencji, co dostosować i co zweryfikować w oparciu o testy porównawcze.