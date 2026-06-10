---

name: handoff-designer
description: Zaprojektuj topologię handoffów dla systemu opartego na Swarm/Agents-SDK: zdefiniuj dostępnych agentów, możliwe przejścia sterowania oraz politykę przekazywania kontekstu.
version: 1.0.0
phase: 16
lesson: 11
tags: [multi-agent, swarm, handoff, openai-agents-sdk]

---

Na podstawie opisanego zadania (najczęściej klasyfikacji lub routingu kompetencyjnego), zaprojektuj topologię handoffów przystosowaną do wdrożenia w OpenAI Swarm lub OpenAI Agents SDK.

Opracuj:

1. **Katalog agentów.** Dla każdego agenta określ: nazwę, krótki opis celu działania, dostępne narzędzia oraz listę agentów, do których może nastąpić handoff.
2. **Funkcje handoffu.** Sygnatury funkcji narzędziowych dla każdego agenta. Każda funkcja przekazania sterowania musi zwracać obiekt docelowego agenta.
3. **Polityka przekazywania kontekstu.** Definicja kontekstu na granicach handoffu: pełna historia konwersacji, ostatnich N wiadomości lub skrócone podsumowanie (wraz z uzasadnieniem).
4. **Mechanizmy zabezpieczające (Guardrails).** Weryfikacja zapytań wejściowych (jakie prompty mogą wymusić przekazanie do agentów z wrażliwymi uprawnieniami) oraz uwierzytelnianie na poziomie handoffu (jeśli wymagane).
5. **Wykrywanie pętli.** Reguła eliminująca zapętlenia (ping-pong), np. sytuacje typu „Agent A przekazuje do B, a B natychmiast przekazuje z powrotem do A” powtórzone wielokrotnie.
6. **Procedury awaryjne (Fallback).** Wskazanie agenta domyślnego, który przejmie obsługę sesji w przypadku braku celu przekazania (np. błąd uwierzytelniania, usunięcie agenta docelowego).
7. **Strategia zarządzania stanem/pamięcią.** Określenie, czy system będzie korzystał z wbudowanych sesji w Agents SDK, pamięci kontrolowanej przez aplikację wywołującą, czy też z trybu całkowicie bezstanowego.

Kryteria wykluczające:

- Jakikolwiek projekt przekazywania sterowania bez zaimplementowanego mechanizmu wykrywania pętli.
- Funkcje handoffu przekazujące pełną historię rozmowy do specjalistów o wyższym poziomie uprawnień (ryzyko eskalacji uprawnień / wstrzyknięcia promptu).
- Projekty zakładające bezstanowość Swarm w scenariuszach wymagających pamięci wieloturowej (w takich przypadkach należy zastosować sesje z Agents SDK).

Zasady odmowy (Rejection rules):

- Jeśli zadanie wymaga równoległego przetwarzania, odrzuć Swarm i zaleć architekturę z nadzorcą (Lekcja 05).
- Jeśli zadanie wymaga w pełni deterministycznej powtarzalności lub audytowalności, odrzuć Swarm i zaleć statyczny graf LangGraph.
- Jeśli zadanie stanowi prosty proces sekwencyjny (np. research → kodowanie → recenzja), odrzuć Swarm i zaleć model sekwencyjny (np. CrewAI Sequential).

Format wyjściowy: jednostronicowy opis topologii handoffów. Na końcu umieść analizę bezpieczeństwa opisującą, jak ataki typu prompt injection mogą wywołać niepożądane przekazania sterowania oraz w jaki sposób mechanizmy zabezpieczające temu zapobiegają.
