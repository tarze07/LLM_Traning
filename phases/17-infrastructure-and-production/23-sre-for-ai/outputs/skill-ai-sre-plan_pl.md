---

name: ai-sre-plan
description: Zaprojektuj wdrożenie AI SRE dla zespołu — architektura segregacji wielu agentów, ustrukturyzowane elementy Runbook, ocena kontradyktoryjna, wąska automatyczna naprawa i postawa wykrywania predykcyjnego.
version: 1.0.0
phase: 17
lesson: 23
tags: [ai-sre, multi-agent, runbooks, auto-remediation, adversarial-eval, datadog-bits-ai, neubird, predictive]

---

Biorąc pod uwagę wielkość zespołu, liczbę incydentów, dojrzałość obserwowalności i tolerancję ryzyka, utwórz plan AI SRE.

Wyprodukuj:

1. Architektura. Multiagent: nadzorca + agent dziennika + agent metryki + agent elementu Runbook + brama ludzka. Dopasuj wyspecjalizowanych agentów do istniejących źródeł danych (Datadog, Grafana, Loki, Confluence).
2. Transformacja elementu Runbook. Przejdź od nieustrukturyzowanego Confluence do ustrukturyzowanego przeceny z sekcjami dotyczącymi symptomów/hipotez/weryfikacji/działania. Wersja w gicie.
3. Wybór produktu. Datadog Bits AI, Azure SRE Agent, NeuBird Hawkeye, Incident.io Autopilot lub DIY.
4. Zakres autoremediacji. Wąski bezpieczny zestaw (uruchom ponownie kapsułę, przywróć wdrożenie, skaluj w granicach). Jawna lista odrzuconych (topologia, kod, uprawnienia, baza danych). Polityka jako kod.
5. Ocena kontradyktoryjna. Określ bramkę umowy dwumodelowej na potrzeby automatycznej korekty. Nieporozumienia narastają.
6. Postawa predykcyjno-detekcyjna. Jeśli rozważasz (wynik MIT 89%), nazwij politykę uruchamiania — pager, drenaż wstępny, automatyczne skalowanie — w przeciwnym razie będzie to tylko pulpit nawigacyjny.

Twarde odrzucenia:
- Automatyczna naprawa bez ludzkiej bramy w przypadku szerokich zmian. Odmów — wyraźnie nazwij zestaw sejfów.
- Nieustrukturyzowane elementy Runbook jako baza wiedzy. Odmów — wymagaj uporządkowanej i wersjonowanej przeceny.
- Ramka „Ustaw i zapomnij”. Odmów — wyraźnie określ, co jest, a co nie jest autonomiczne.

Zasady odmowy:
- Jeśli liczba incydentów wynosi <10 miesięcznie, odmów pełnego wdrożenia AI SRE – koszty przewyższają korzyści. Polecaj tylko strukturalne elementy Runbook.
- Jeśli obserwowalność zespołu jest niedojrzała (nie można przeszukać logów, metryki są rzadkie), odmów — AI SRE wzmacnia błędne dane.
- Jeśli zespół zaproponuje jako pierwszą funkcję „wykrywanie predykcyjne → automatyczne naprawianie”, odmów — najpierw przeanalizuj kwestię zasad uruchamiania.

Dane wyjściowe: jednostronicowy plan z architekturą, planem elementu Runbook, wyborem produktu, zakresem automatycznej naprawy, bramą przeciwstawną, postawą predykcyjną. Zakończ 12-tygodniowym harmonogramem wdrażania: tygodnie 1–4 ustrukturyzowane elementy Runbook, 5–8 agent selekcji, 9–12 wąskie automatyczne korygowanie.