---

name: routing-config-designer
description: Zaprojektuj konfigurację routingu LLM, dokonując wyboru między systemami LiteLLM, OpenRouter i Portkey na podstawie profilu obciążenia i wymogów biznesowych.
version: 1.0.0
phase: 13
lesson: 20
tags: [routing, litellm, openrouter, portkey, fallback]

---

Na podstawie profilu obciążenia (wymagania dotyczące opóźnień, ograniczenia zgodności z regulacjami, wielkość zespołu deweloperskiego, budżet) wybierz i skonfiguruj bramę routingu LLM.

Wygeneruj następujące sekcje:

1. Wybór bramy. LiteLLM (Self-hosted), OpenRouter (zarządzany SaaS) lub Portkey (klasa produkcyjna z wbudowanymi filtrami). Przedstaw jednoakapitowe uzasadnienie wyboru.
2. Lista aliasów. Logiczne nazwy modeli wykorzystywane w kodzie aplikacji (np. `smart`, `fast`, `coding`, `long_context`).
3. Łańcuchy awaryjne (Failover). Uporządkowana lista konkretnych modeli przypisanych do każdego aliasu wraz z polityką ponownych prób (retries).
4. Filtry bezpieczeństwa (Guardrails). Reguły wykrywania i maskowania danych osobowych (PII), kryteria filtrowania treści wejściowych oraz reguły weryfikacji odpowiedzi wyjściowych.
5. Kontrola budżetowa. Limity wydatków przypisane do zespołów lub projektów wraz z określeniem sposobu ich weryfikacji.

Kategoryczne odrzucenia:
- Dowolna konfiguracja, która kieruje zapytania do regionów naruszających wymogi zgodności geograficznej (compliance).
- Dowolny łańcuch awaryjny (failover) ograniczający się tylko do jednego dostawcy (brak dywersyfikacji dostawców mija się z celem wdrażania routingu).
- Dowolna konfiguracja pozbawiona filtrów bezpieczeństwa (guardrails) w przypadku przetwarzania nieoczyszczonych danych bezpośrednio od użytkowników.

Reguły odmowy:
- Jeśli projekt zakłada jedynie proste testowanie pojedynczego modelu bez planów rozwoju, odrzuć potrzebę wdrażania bramy (bezpośrednia integracja z API jest w tym przypadku prostsza).
- Jeśli zespół nie dysponuje inżynierami SRE, a decyduje się na samodzielne hostowanie bramy (self-hosted), wskaż na ryzyko operacyjne.
- Jeśli użytkownik żąda użycia jednego konkretnego modelu bez alternatywnych modeli zapasowych, odrzuć konfigurację i zażądaj dodania co najmniej jednego fallbacku.

Format wyjściowy: Jednostronicowa konfiguracja routingu zawierająca wybór bramy, definicje aliasów, konfigurację łańcuchów awaryjnych, filtry bezpieczeństwa oraz plan kontroli kosztów. Na końcu wskaż kluczową metrykę, dla której należy skonfigurować alerty (np. częstotliwość przełączania na modele zapasowe - fallback rate).
