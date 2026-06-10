---

name: actor-runtime
description: Zbuduj środowisko wykonawcze aktora w kształcie AutoGen v0.4 ze stanem prywatnym, skrzynką odbiorczą dla aktora, IPC tylko dla komunikatów, izolacją błędów i kolejką utraconych wiadomości.
version: 1.0.0
phase: 14
lesson: 14
tags: [autogen, actor-model, messaging, fault-isolation, dead-letter]

---

Biorąc pod uwagę zadanie obejmujące wielu agentów, utwórz środowisko wykonawcze aktorów i potrzebnych aktorów agentów.

Wyprodukuj:

1. Typ `Message` z `sender`, `recipient`, `topic`, `body`, `mid`.
2. Klasa bazowa `Actor` z `receive(message, runtime)`. Stan aktora jest prywatny.
3. `Runtime` ze wspólną kolejką, `send()`, `run_until_idle()` i kolejką utraconych wiadomości. Wyjątki w procedurach obsługi trafiają do DLQ; nie propaguj.
4. Jeden pomocnik topologii: RoundRobin (stała rotacja), Selector (kolejny wybór LLM) lub transmisja niestandardowa.
5. Haki obserwowalności na wiadomość: emituj rozpiętości OTel z `gen_ai.agent.name` i `gen_ai.operation.name` na lekcji 23.

Twarde odrzucenia:

- Synchroniczne przekazywanie wiadomości, które blokuje nadawcę do czasu powrotu odbiorcy. To jest model v0.2; przerywa izolację usterek.
- Wspólny zmienny stan pomiędzy aktorami. Aktorzy czytają stan poprzez wiadomości lub wcale.
- Środowisko wykonawcze propagujące wyjątki procedury obsługi. Awarie należą do DLQ; niech inni aktorzy biegają.

Zasady odmowy:

- Jeśli w zadaniu bierze udział tylko dwóch aktorów poruszających się w tę i z powrotem, odmów aktorowi wkomponowania i zasugeruj szybki łańcuch (lekcja 12). Aktorzy generują koszty, gdy jest >= 3 aktorów lub współbieżność asynchroniczna.
- Jeśli użytkownik chce „trybu synchronicznego” w celu „łatwiejszego debugowania”, odmów. Zamiast tego zasugeruj rejestrowanie i śledzenie (lekcja 23).
- Jeśli domeną jest wyłącznie żądanie/odpowiedź z jednym specjalistą, zasugeruj routing (lekcja 12) zamiast zespołu aktorów.

Dane wyjściowe: `message.py`, `actor.py`, `runtime.py`, `teams.py`, `README.md` wyjaśniające zasady DLQ, wybór topologii i sposób okablowania zakresów OTel. Zakończ słowami „Co przeczytać dalej”, wskazując Lekcję 25 (debata wieloagentowa), jeśli aktorzy negocjują, Lekcję 23 (OTel), jeśli wymagane jest śledzenie, lub Microsoft Agent Framework, jeśli chcesz mieć przyszłościowe środowisko wykonawcze.