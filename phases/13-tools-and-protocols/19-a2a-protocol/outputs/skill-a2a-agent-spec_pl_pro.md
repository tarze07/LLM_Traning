---

name: a2a-agent-spec
description: Utwórz dokument opisu agenta (Agent Card) oraz schemat umiejętności (skills) dla agenta współpracującego w standardzie A2A.
version: 1.0.0
phase: 13
lesson: 18
tags: [a2a, agent-card, task-lifecycle, delegation]

---

Na podstawie specyfikacji możliwości agenta oraz profilu współpracujących systemów opracuj dokument opisu agenta (Agent Card) w standardzie A2A wraz z definicjami jego umiejętności (skills).

Wygeneruj następujące sekcje:

1. Karta agenta (Agent Card). Pola: `name`, `description`, `url`, `version`, `schemaVersion`, `capabilities` (obsługa strumieniowania, powiadomienia push) oraz lista `skills[]`.
2. Lista umiejętności (Skills). Każda pozycja powinna zawierać pola: `id`, `name`, `description`, `inputModes`, `outputModes`. W opisach zastosuj konwencję: „Używaj, gdy X. Nie używaj dla Y”.
3. Plan zadań i stanów. Dla każdej z umiejętności zdefiniuj oczekiwane przejścia stanów oraz przebieg żądań o brakujące parametry (`input_required`).
4. Plan podpisania dokumentu. Określenie zasad wdrożenia rozszerzenia AP2 w celu podpisywania karty (zalecane dla agentów udostępnianych publicznie/zewnętrznie).
5. Protokół transportowy. JSON-RPC przez HTTP (domyślny) lub gRPC, z uwzględnieniem kompatybilności z wersją 1.0.

Kategoryczne odrzucenia:
- Dowolna karta agenta pozbawiona stałego adresu URL (uniemożliwia to autowykrywanie/discovery).
- Dowolna umiejętność bez jawnie zadeklarowanych trybów wejścia (`inputModes`) i wyjścia (`outputModes`). Bez tych informacji zlecający nie mogą zweryfikować zgodności interfejsów.
- Dowolny agent udostępniany zewnętrznie bez wdrożonego podpisywania kart za pomocą rozszerzenia AP2 (ryzyko podszywania się).

Reguły odmowy:
- Jeśli jedynym zadaniem agenta jest wywołanie pojedynczej funkcji technicznej (narzędzia), odrzuć implementację A2A i zalecaj użycie protokołu MCP.
- Jeśli agent niepotrzebnie ujawnia szczegóły wewnętrzne (np. logi wywołań narzędzi, łańcuch myśli), odrzuć projekt i nakaż zachowanie zasady nieprzezroczystości (opacity).
- Jeśli agent wymaga protokołu A2A do obsługi płatności (przypadek użycia AP2), zweryfikuj wersję rozszerzenia AP2 i wskaż, że mechanizmy AP2 są oddzielone od bazowego standardu A2A.

Format wyjściowy: Jednostronicowa struktura JSON karty agenta, schemat umiejętności dla każdej operacji, plan przejść stanów oraz konfiguracja podpisywania i transportu. Na końcu określ minimalne gwarancje kompatybilności wstecznej z wersją 1.0 deklarowane przez agenta.
