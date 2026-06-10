---

name: ecosystem-blueprint
description: Zaprojektuj kompletną specyfikację techniczną (blueprint) dla ekosystemu Fazy 13 na podstawie wymagań biznesowych, określając narzędzia, architekturę bezpieczeństwa, model telemetrii oraz strukturę pakowania.
version: 1.0.0
phase: 13
lesson: 22
tags: [mcp, capstone, ecosystem, architecture, a2a, otel]

---

Na podstawie wymagań funkcjonalnych systemu (badania, synteza, automatyzacja procesów lub dowolny zaawansowany przepływ pracy oparty na agentach) opracuj kompletną architekturę techniczną ekosystemu.

Wygeneruj następujące sekcje:

1. Pojęcia bazowe (primitives) MCP. Zdefiniuj wymagane narzędzia, zasoby, prompty i zadania. Określ interfejsy graficzne `ui://` oraz zadania asynchroniczne.
2. Architektura bezpieczeństwa. Struktura zakresów OAuth 2.1, macierz RBAC na bramie sieciowej, manifest przypiętych skrótów (hash pinning) oraz egzekwowanie reguły dwóch.
3. Współpraca A2A. Wskaż obszary integracji z subagentami za pośrednictwem A2A i zdefiniuj ich karty agentów (Agent Cards).
4. Telemetria. Hierarchia zakresów w standardzie OTel GenAI wraz z wyborem eksportera i systemu docelowego (backendu).
5. Pakowanie i wdrożenie. Projekty plików AGENTS.md, SKILL.md oraz struktura wdrożeniowa (np. Docker Compose, Kubernetes).
6. Powiązanie z lekcjami Fazy 13. Przypisanie poszczególnych decyzji projektowych do lekcji źródłowych.

Kategoryczne odrzucenia:
- Dowolna architektura łamiąca regułę dwóch (jednoczesne przetwarzanie niezaufanych danych wejściowych, operowanie na wrażliwych danych i wywoływanie akcji o wysokim priorytecie w jednej turze).
- Dowolna architektura pozbawiona propagacji kontekstu śledzenia (tracing propagation) pomiędzy granicami MCP i A2A.
- Dowolna architektura bez zdefiniowania co najmniej jednego zapasowego dostawcy LLM (fallback).

Reguły odmowy:
- Jeśli wymagania biznesowe mogą być efektywnie zrealizowane za pomocą pojedynczego, bezpośredniego wywołania LLM, odrzuć potrzebę budowy zaawansowanego ekosystemu.
- Jeśli zespół nie dysponuje inżynierami SRE odpowiedzialnymi za utrzymanie bramy, zarekomenduj wybór bramy zarządzanej (np. Cloudflare MCP Ports, Portkey).
- Jeśli architektura obejmuje procesy płatnicze, wskaż, że rozszerzenie AP2 niesie ryzyko zmian specyfikacji (drift) i zalecaj odseparowanie procedury podpisywania.

Format wyjściowy: Jednostronicowy plan wdrożenia zawierający specyfikację pojęć bazowych MCP, model bezpieczeństwa, schemat integracji A2A, plan telemetrii, strukturę pakowania oraz mapę lekcji źródłowych. Na końcu wskaż w jednym zdaniu najpoważniejsze ryzyko operacyjne związane z wdrożeniem tej architektury.
