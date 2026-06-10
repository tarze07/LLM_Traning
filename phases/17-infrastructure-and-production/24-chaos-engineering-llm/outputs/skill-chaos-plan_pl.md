---

name: chaos-plan
description: Zaprojektuj plan inżynierii chaosu LLM — sprawdź wymagania wstępne, zbuduj cztery samoloty, wybierz narzędzie, zacznij od trzech bezpiecznych eksperymentów, wprowadź bramy samolotu bezpieczeństwa.
version: 1.0.0
phase: 17
lesson: 24
tags: [chaos-engineering, litmuschaos, chaosmesh, harness, llm-chaos, game-day]

---

Biorąc pod uwagę stos (Kubernetes / maszyny wirtualne / zarządzane), dojrzałość SLI/SLO, jakość obserwowalności i dojrzałość zespołu na wezwanie, tworzą plan chaosu.

Wyprodukuj:

1. Kontrola warunków wstępnych. Sprawdź, czy zdefiniowano SLI/SLO, podłączono obserwowalność, zautomatyzowane wycofywanie zmian, strukturę elementów Runbook, rotację na żądanie. Jeżeli któregokolwiek brakuje, odmów wprowadzenia chaosu produkcyjnego.
2. Cztery samoloty. Nazwij narzędzia dla każdej płaszczyzny (kontrola, cel, bezpieczeństwo, obserwowalność). Wskaż fazę 17 · 13, aby uzyskać obserwowalność.
3. Trzy wstępne eksperymenty. Zacznij od zabicia kapsuły. Następnie dostawca 429. Następnie przeciążenie pamięci. Każdy z limitem promienia wybuchu, czasem trwania i kryterium sukcesu.
4. Bramki zabezpieczające. Szybkość spalania (>2x oczekiwana), promień wybuchu (< 30% of fleet), trace-ID tagging, suppression windows.
5. Cadence. Weekly small canary. Monthly game day (cross-team). Quarterly resilience audit.
6. Tooling. LitmusChaos (OSS, CNCF graduated), Chaos Mesh (OSS, CNCF sandbox), Harness Chaos (commercial AI-assisted), AWS FIS / Azure Chaos Studio (managed cloud-native).

Hard rejects:
- Running chaos in production without the five prerequisites. Refuse — will become real incident.
- Experiments without blast-radius caps. Refuse.
- Experiments without trace-ID tagging. Refuse — impossible to dedupe alerts.

Refusal rules:
- If team has never run one successful experiment in staging, refuse production chaos until one is green in staging.
- If incident volume is already high (>2/tydzień), dodatkowy chaos w postaci śmieci — najpierw ustabilizuj się.
- Jeśli zespół nie ma SLO, wymagaj SLO przed jakimkolwiek eksperymentem.

Wynik: jednostronicowy plan ze sprawdzeniem wymagań wstępnych, narzędzia czteropłaszczyznowe, trzy wstępne eksperymenty, bramki zabezpieczające, rytm. Zakończ kwartalnym zobowiązaniem do aktualizacji mapy zależności.