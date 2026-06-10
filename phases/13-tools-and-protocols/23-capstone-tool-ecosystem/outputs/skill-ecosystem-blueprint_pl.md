---

name: ecosystem-blueprint
description: Stworzenie pełnej architektury ekosystemu fazy 13, biorąc pod uwagę zapotrzebowanie na produkt; nazwij prymitywy, stan zabezpieczeń, telemetrię i opakowanie.
version: 1.0.0
phase: 13
lesson: 22
tags: [mcp, capstone, ecosystem, architecture, a2a, otel]

---

Biorąc pod uwagę potrzeby produktu (badania, podsumowania, automatyzacja, dowolny przepływ pracy oparty na agentach), utwórz pełną architekturę.

Wyprodukuj:

1. Elementy podstawowe MCP. Jakie narzędzia, zasoby, podpowiedzi i zadania są potrzebne. Jakieś aplikacje `ui://`? Jakieś zadania asynchroniczne?
2. Postawa bezpieczeństwa. Zestaw zakresu OAuth 2.1, macierz RBAC bramy, przypięty manifest skrótu, audyt Reguły Dwóch.
3. Współpraca A2A. Zidentyfikuj wszelkie połączenia podrzędnych agentów. Zdefiniuj ich karty agentów.
4. Telemetria. Hierarchia zakresu Otel GenAI. Wybór eksportera i zaplecza.
5. Opakowanie. AGENTS.md, SKILL.md i powierzchnia wdrożenia (Docker Compose, K8s).
6. Mapowanie do lekcji fazy 13. Z której lekcji wynika każdy wybór projektu.

Twarde odrzucenia:
- Dowolna architektura, która łączy niezaufane dane wejściowe, wrażliwe dane i wynikające z nich działania w jednej turze (Zasada dwóch).
- Dowolna architektura bez propagacji śladów pomiędzy przeskokami MCP i A2A.
- Dowolna architektura bez co najmniej jednego dostawcy zastępczego w warstwie LLM.

Zasady odmowy:
- Jeśli zapotrzebowanie na produkt lepiej zaspokoi bezpośrednie wezwanie LLM, odmów budowania całego ekosystemu.
- Jeśli zespołowi brakuje oprogramowania SRE dla bramy, zarekomenduj zarządzaną bramę (portale Cloudflare MCP, Portkey).
- Jeśli architektura obejmuje płatności, oznacz AP2 jako rozszerzenie A2A z ryzykiem dryfu i zaleć osobne podpisanie.

Wynik: jednostronicowy plan zawierający elementy podstawowe, stan zabezpieczeń, przeskoki A2A, plan telemetrii, opakowanie i mapę lekcji. Zakończ jednym zdaniem identyfikującym najtrudniejsze ryzyko operacyjne związane z wdrożeniem.