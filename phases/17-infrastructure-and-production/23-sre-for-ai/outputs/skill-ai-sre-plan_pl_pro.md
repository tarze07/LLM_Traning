---

name: ai-sre-plan
description: Zaprojektuj wdrożenie AI SRE dla zespołu – wieloagentowa architektura klasyfikacji incydentów, ustrukturyzowane procedury runbook, ewaluacja kontradyktoryjna, wąski zakres automatycznej naprawy oraz strategia predykcyjnego wykrywania awarii.
version: 1.0.0
phase: 17
lesson: 23
tags: [ai-sre, multi-agent, runbooks, auto-remediation, adversarial-eval, datadog-bits-ai, neubird, predictive]

---

Na podstawie wielkości zespołu, liczby incydentów, stopnia dojrzałości systemów obserwowalności oraz tolerancji ryzyka, przygotuj plan wdrożenia AI SRE.

Wygeneruj:

1. Architektura: Wieloagentowa (nadzorca + agent logów + agent metryk + agent runbooków + bramka ludzka). Dostosuj dziedzinowych agentów do istniejących źródeł danych (np. Datadog, Grafana, Loki, Confluence).
2. Transformacja procedur runbook: Zmigruj nieustrukturyzowane dokumenty z Confluence do sformatowanych plików Markdown o ściśle określonej strukturze (objawy, hipotezy, weryfikacja, akcja). Wprowadź wersjonowanie w systemie Git.
3. Wybór narzędzia: Datadog Bits AI, Azure SRE Agent, NeuBird Hawkeye, Incident.io Autopilot lub własne rozwiązanie (DIY).
4. Zakres automatycznej naprawy (auto-remediation): Wąski zestaw bezpiecznych operacji (np. restart podu, wycofanie wdrożenia, skalowanie w określonych limitach). Zdefiniuj jawną czarną listę operacji zabronionych (zmiany topologii, kodu, uprawnień czy bazy danych). Opisz politykę w forme kodu (Policy as Code).
5. Ewaluacja kontradyktoryjna: Określ mechanizm porozumienia dwóch modeli (two-model consensus) jako warunek automatycznej naprawy. W przypadku braku zgody wymagaj eskalacji do człowieka.
6. Predykcyjne wykrywanie awarii: Jeśli planujesz wdrożenie predykcji (odnosząc się do wyników MIT na poziomie 89%), zdefiniuj konkretną politykę reagowania (np. wysłanie alertu pagerem, prewencyjne przekierowanie ruchu, automatyczne skalowanie) – w przeciwnym razie funkcja ta stanie się jedynie dodatkowym zestawem wykresów.

Kryteria odrzucenia planu (Hard rejects):
- Automatyczna naprawa szerokiego zakresu zmian bez autoryzacji przez człowieka: Odrzuć plan – bezpieczny zestaw operacji musi być ściśle zdefiniowany.
- Wykorzystanie nieustrukturyzowanych procedur runbook jako bazy wiedzy: Odrzuć – wymagaj ustrukturyzowanych i wersjonowanych plików Markdown.
- Podejście typu "ustaw i zapomnij": Odrzuć – plan must jednoznacznie określać, które operacje są w pełni autonomiczne, a które wymagają decyzji człowieka.

Zasady odrzucenia:
- Jeśli liczba incydentów wynosi < 10 miesięcznie, odrzuć pełne wdrożenie AI SRE – koszty przewyższą potencjalne korzyści. W takim wypadku zalecaj jedynie uporządkowanie procedur runbook.
- Jeśli poziom obserwowalności systemu jest niewystarczający (brak możliwości przeszukiwania logów, rzadkie próbkowanie metryk), odrzuć plan – system AI SRE powieli i wzmocni niepoprawne dane.
- Jeśli zespół proponuje w pierwszej kolejności wdrożenie ścieżki "wykrywanie predykcyjne -> automatyczna naprawa", odrzuć plan – w pierwszej kolejności należy precyzyjnie opracować zasady i reguły reagowania.

Wynik: Jednostronicowy plan zawierający architekturę, plan konwersji procedur runbook, wybór narzędzia, zakres automatycznej naprawy, mechanizm kontradyktoryjny oraz strategię predykcyjną. Na końcu umieść 12-tygodniowy harmonogram wdrożenia: tygodnie 1–4 (strukturyzacja procedur runbook), 5–8 (wdrożenie agenta klasyfikującego), 9–12 (uruchomienie wąskiego zakresu automatycznej naprawy).
