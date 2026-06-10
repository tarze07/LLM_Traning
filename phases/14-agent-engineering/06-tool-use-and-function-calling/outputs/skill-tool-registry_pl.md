---

name: tool-registry
description: Zbuduj katalog i rejestr narzędzi produkcyjnych z walidacją schematu JSON, równoległą dystrybucją i obserwowalnością.
version: 1.0.0
phase: 14
lesson: 06
tags: [function-calling, tools, schema, validation, bfcl, parallel-tools]

---

Biorąc pod uwagę domenę zadań, utwórz katalog narzędzi, z których agent może niezawodnie korzystać we wszystkich osiach BFCL V4 (agent, wieloobrotowy, żywy, nieżywy, halucynacja).

Wyprodukuj:

1. Definicje narzędzi. Dla każdego narzędzia: `name` (snake_case), `description` (mówi modelowi, kiedy go używać, a kiedy NIE), dane wejściowe schematu JSON z wpisanymi właściwościami, wymagane pola, wyliczenia, jeśli ma to zastosowanie, minimum/maksimum dla liczb, limit czasu dla każdego narzędzia, zasady piaskownicy dla każdego narzędzia (powierzchnia fs, sieć, limit pamięci).
2. Kontrola jakości opisu. Przeprowadź każdy opis przez pytanie „czy to informuje model, kiedy wybrać to narzędzie, a nie inne?” Jeśli dwa narzędzia mają pokrywające się opisy, odrzuć je i napisz od nowa.
3. Plan wysyłki równoległej. Dla każdego realistycznego zadania określ, które wywołania narzędzi są niezależne (mogą być zrównoleglone), a które muszą być sekwencyjne. Wyemituj oczekiwany wykres wysyłki.
4. Polityka walidacji. Sprawdzanie wyliczeń, reguły wymuszania typu (np. „zaakceptuj int-jako ciąg, odrzuć zmiennoprzecinkowy jako ciąg”), wymuszanie wymaganego pola. Każda awaria zwraca uporządkowany ciąg obserwacji, nigdy nie wywołuje pętli.
5. Obserwowalność. Każde narzędzie emituje zakres OpenTelemetry GenAI `tool_call` z atrybutami `gen_ai.tool.name`, `gen_ai.tool.call.id`, `gen_ai.tool.call.arguments`, `gen_ai.tool.call.result` (odniesienie, a nie wbudowane, gdy wymaga tego polityka dotycząca treści).

Twarde odrzucenia:

- Ogólne narzędzie Shell/command-exec. Odmów i podziel się na konkretne czasowniki (`git_status`, `fs_read`, `npm_test`).
- Brakujące wyliczenia, gdy parametr ma zamknięty zbiór wartości. Walidacja wyliczeniowa to najtańszy sposób na wyłapanie dryfu.
- Ten sam opis dla dwóch różnych narzędzi. Modelka nie potrafi rzetelnie wybierać pomiędzy nimi.
- `description`, który tylko nazywa narzędzie („Dodaje dwie liczby”). Podaj KIEDY, aby wybrać to zamiast alternatyw.
- Brak limitu czasu. Każde wywołanie narzędzia musi mieć górny pułap.

Zasady odmowy:

- Jeśli lista narzędzi przekracza 30 narzędzi dla pojedynczego agenta, odmów i zalecaj delegację subagentów (Lekcja 17).
- Jeśli jakiekolwiek narzędzie wykona destrukcyjną akcję bez bramki potwierdzenia, odmów i wskaż Lekcję 09 (uprawnienia, piaskownica).
- Jeśli zadaniem jest korzystanie z komputera (kliknij, napisz, zrzut ekranu), odmów i wskaż Lekcję 21 — czyli osobny kształt narzędzia z działaniami opartymi na wizji.

Dane wyjściowe: katalog narzędzi JSON gotowy do wklejenia do wywołań Anthropic/OpenAI/Gemini SDK, diagram wysyłkowy, dokument zasad walidacji i mini-ewaluacja w stylu BFCL, którą rejestr powinien przejść.

Zakończ wskaźnikiem „co dalej czytać”: Lekcja 09 (sandboxing), Lekcja 23 (rozpiętość OTel GenAI) lub Lekcja 30 (oparta na eval).