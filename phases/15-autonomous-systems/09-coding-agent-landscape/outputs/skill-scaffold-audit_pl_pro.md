---

name: coding-scaffold-audit
description: Przeprowadź audyt proponowanego szkieletu (scaffoldu) agenta kodującego (pobieranie informacji, pętla weryfikacyjna, piaskownica, dopasowanie do testów porównawczych) przed wdrożeniem go do wprowadzania zmian w kodzie produkcyjnym.
version: 1.0.0
phase: 15
lesson: 9
tags: [coding-agent, scaffolding, swe-bench, codeact, openhands]

---

Biorąc pod uwagę proponowany szkielet (scaffold) agenta kodującego (SWE-agent, OpenHands, Aider, Cline, Devin, Claude Code lub własna implementacja), oceń go w czterech wymiarach i wskaż obszary, w których wyniki testów porównawczych (benchmarków) mogą zawyżać jego rzeczywistą jakość produkcyjną.

Przygotuj:

1. **Pobieranie danych (Retrieval).** Opisz, w jaki sposób szkielet (scaffold) wybiera pliki, które agent odczytuje przed podjęciem działania. Weź pod uwagę mapę repozytorium (repository map), wyszukiwanie semantyczne (embeddings), jawną listę plików lub wywołania `grep` sterowane przez agenta. Jakość wyszukiwania informacji (retrieval) jest kluczowym, choć często niedocenianym czynnikiem determinującym niezawodność.
2. **Pętla weryfikacyjna.** Czy szkielet automatycznie uruchamia testy, analizuje ślad stosu (stack trace) i przekazuje informacje o błędach z powrotem do agenta w kolejnej iteracji? Jeśli pętla weryfikacyjna nie występuje, oznacz to jako brak – jej obecność przekłada się zazwyczaj na ponad 10-punktową bezwzględną różnicę (deltę) w wynikach zadań SWE-bench.
3. **Piaskownica (sandbox) i zakres szkód (blast radius).** Gdzie wykonywane są operacje? Lokalny system plików, kontener efemeryczny czy zarządzana maszyna wirtualna. W przypadku szkieletów typu CodeAct upewnij się, że piaskownica jest odpowiednio zabezpieczona (brak możliwości wyjścia poza środowisko izolowane, brak montowania katalogów hosta, limity czasowe). Przy szkieletach opartych na wywoływaniu narzędzi JSON (tool-calling) potwierdź, czy walidatory narzędzi skutecznie odrzucają wszelkie niepożądane efekty uboczne.
4. **Reprezentatywność benchmarku (Benchmark Alignment).** Jaki rozkład zadań w rzeczywistości odzwierciedla podany wynik (np. „80,9% w teście SWE-bench”)? Określ, jaka część benchmarku składa się z prostych zadań jednolinijkowych lub dwulinijkowych; porównaj raportowany wynik z testem SWE-bench Pro (zadania wymagające modyfikacji ponad 10 linii kodu) dla tego samego modelu. Szkielet, którego wysoki wynik wynika głównie z łatwych zadań (tzw. łatwego ogona rozkładu), nie daje miarodajnych sygnałów w warunkach produkcyjnych.

Kryteria odrzucenia (Hard Rejections):
- Dowolny szkielet pozbawiony pętli weryfikacyjnej, używany do zadań o złożoności większej niż trywialna.
- Szkielety CodeAct bez izolacji w piaskownicy (brak Dockera, brak kontenerów rootless, brak maszyn wirtualnych) mające bezpośredni dostęp do rzeczywistych repozytoriów.
- Deklaracje wyników benchmarkowych, które nie ujawniają rozkładu zadań (udział zadań prostych, wynik w wersji Pro).
- Szkielety wywołujące narzędzia, w których pojedyncze narzędzie może modyfikować dowolne ścieżki bez wcześniejszej walidacji (np. bezpośrednie udostępnienie modelowi surowego narzędzia typu `shell_exec`).

Zasady odmowy wykonania zadania (Denial Policies):
- Jeśli użytkownik nie jest w stanie podać wskaźnika sukcesu (pass rate) dla szkieletu na reprezentatywnej próbie własnych, wewnętrznych projektów, należy odmówić wykonania zadania i zażądać najpierw przeprowadzenia testów na małej próbce. Publiczne benchmarki wskazują jedynie relatywny ranking modeli, a nie ich bezwzględną jakość w konkretnym zastosowaniu.
- Jeśli proponowany szkielet miałby działać bezpośrednio na repozytorium produkcyjnym bez wcześniejszego przetestowania w środowisku stagingowym, należy odmówić wykonania zadania i zażądać wdrożenia etapu przejściowego. Agenci kodujący modyfikują pliki; agenci z błędnym mechanizmem pobierania danych modyfikują niewłaściwe pliki.
- Jeśli użytkownik planuje podjąć ostateczną decyzję o wdrożeniu wyłącznie na podstawie publicznych wyników benchmarków (bez przeprowadzenia własnej ewaluacji), należy odmówić i zażądać przedstawienia wewnętrznych danych testowych.

Format danych wyjściowych:

Przedstaw podsumowanie zawierające:
- **Wynik wyszukiwania danych (Retrieval Score)** (skala 0–5 wraz z opisem zastosowanego mechanizmu)
- **Wynik pętli weryfikacyjnej (Verifier Loop Score)** (skala 0–5 z opisem pętli zwrotnej)
- **Wynik piaskownicy (Sandbox Score)** (skala 0–5 wraz z określeniem mechanizmu izolacji)
- **Wynik reprezentatywności benchmarku (Benchmark Alignment Score)** (skala 0–5 wraz z różnicą względem wewnętrznego rozkładu zadań)
- **Rekomendacja wdrożeniowa** (wyłącznie produkcja / staging / środowisko badawcze)
- **Jednoliniowe podsumowanie ryzyka** (najbardziej prawdopodobna przyczyna pierwszej awarii na produkcji)
