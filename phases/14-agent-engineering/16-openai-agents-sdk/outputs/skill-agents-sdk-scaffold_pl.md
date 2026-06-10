---

name: agents-sdk-scaffold
description: Stwórz szkielet aplikacji OpenAI Agents SDK z agentem selekcji, przekazywaniem, barierami wejściowymi/wyjściowymi/narzędziowymi, magazynem sesji i procesorem śledzenia.
version: 1.0.0
phase: 14
lesson: 16
tags: [openai, agents-sdk, handoffs, guardrails, tracing, session]

---

Mając domenę produktu i listę wyspecjalizowanych agentów, zbuduj aplikację OpenAI Agents SDK.

Wyprodukuj:

1. `Agent` na specjalistę plus jeden agent `triage`, który ma tylko przełączenia (bez narzędzi domenowych).
2. Narzędzie `FunctionTool` dla każdej domeny z wpisanym schematem wejściowym, przejrzystym opisem (informuje model, kiedy go używać) i piaskownicą wykonawczą.
3. `Handoff` od segregacji do każdego specjalisty. Sprawdź, czy nazwy narzędzi są zgodne z konwencją `transfer_to_<agent>`.
4. `InputGuardrail` dla informacji umożliwiających identyfikację, polityka, zakres. Domyślnie tryb równoległy, chyba że poręcz LLM jest duża w porównaniu z modelem głównym — wówczas użyj blokowania.
5. `OutputGuardrail` dla długości, PII, polisy. Zawsze blokuje na wyjściu dla wyjść krytycznych dla bezpieczeństwa.
6. Poręcze ochronne dla poszczególnych narzędzi w narzędziach funkcyjnych, które dotykają sieci lub systemu plików.
7. Sklep `Session` (domyślnie SQLite; Redis dla prod).
8. Okablowanie `add_trace_processor` obejmuje backend wraz z interfejsem śledzenia OpenAI.

Twarde odrzucenia:

- Agenci segregujący za pomocą narzędzi domeny. Tylko przekazywanie segregacji; mieszanie osłabia decyzję routera.
- Poręcze ochronne mutujące wejście/wyjście. Poręcze zatwierdzają lub odrzucają – nie przepisują.
- Ciche pętle przełączania. Wymagaj licznika przeskoków (domyślnie maksymalnie 3).

Zasady odmowy:

- Jeśli użytkownik chce „żadnych poręczy, po prostu działać szybko”, odrzuć jakikolwiek produkt, który trafia do płacących użytkowników lub umożliwia identyfikację.
- Jeśli produkt ma tylko 2 specjalistów, zasugeruj routing przez `Agents` z bezpośrednim klasyfikatorem (lekcja 12) zamiast selekcji i przekazywania — mniejszy koszt tokena.
- Jeśli śledzenie jest wyłączone w prodzie, odmów wysyłki. Awarie wieloetapowe są niemożliwe do debugowania i nie pozostawiają śladów.

Dane wyjściowe: `agents.py`, `tools.py`, `guardrails.py`, `app.py`, `README.md` z uzasadnieniem agenta segregacji, trybami poręczy, procesorem śledzenia i zapleczem sesji. Zakończ słowami „co dalej czytać”, wskazując Lekcję 23 (OTel GenAI), Lekcję 24 (backendy obserwowalności) lub Lekcję 17 dotyczącą tłumaczenia pakietu SDK Claude Agent.