---

name: a2a-agent-spec
description: Utwórz kartę agenta i schemat umiejętności dla agenta, którego można wezwać za pośrednictwem A2A.
version: 1.0.0
phase: 13
lesson: 18
tags: [a2a, agent-card, task-lifecycle, delegation]

---

Biorąc pod uwagę możliwości agenta i przewidywanych współpracowników, przygotuj jego Kartę Agenta A2A i definicje umiejętności.

Wyprodukuj:

1. Karta Agenta. `name`, `description`, `url`, `version`, `schemaVersion`, `capabilities` (streaming, powiadomienia push), `skills[]`.
2. Lista umiejętności. Każdy z `id`, `name`, `description`, `inputModes`, `outputModes`. Użyj opcji „Użyj, gdy X. Nie używaj dla Y”. wzór w opisach.
3. Plan zadań i stanów. Dla każdej umiejętności oczekiwane przejścia stanu i ścieżki wymagane do wejścia.
4. Plan podpisania. Czy podpisać kartę za pośrednictwem AP2 (zalecane dla agentów, z którymi można kontaktować się z zewnątrz).
5. Transport. JSON-RPC przez HTTP (domyślnie) lub gRPC. Uwaga: kompatybilność wsteczna z wersją 1.0.

Twarde odrzucenia:
- Dowolna karta agenta bez stałego adresu URL. Przerywa odkrywanie.
- Dowolna umiejętność bez zadeklarowanych trybów wejścia i wyjścia. Osoby dzwoniące nie mogą uzasadniać zgodności.
- Dowolny agent, z którym można się kontaktować z zewnątrz, bez planu podpisywania AP2. Wektor podszywania się.

Zasady odmowy:
- Jeśli przypadek użycia agenta to wywołanie pojedynczego narzędzia, odmów stosowania rusztowania A2A; polecam MCP.
- Jeśli agent ujawnia elementy wewnętrzne, nie powinien (ślady wywołań narzędzi, łańcuch myślowy) odmawiać i narzucać nieprzezroczystości.
- Jeśli agent potrzebuje A2A do płatności (przypadek użycia AP2), potwierdź wersję rozszerzenia AP2 i zaznacz, że AP2 jest oddzielony od podstawowego A2A.

Dane wyjściowe: jednostronicowy plik JSON karty agenta, schemat umiejętności dla każdej operacji, plan przejścia stanu, opcje podpisywania i transportu. Zakończ z minimalną gwarancją zgodności wstecznej v1.0, którą obiecuje agent.