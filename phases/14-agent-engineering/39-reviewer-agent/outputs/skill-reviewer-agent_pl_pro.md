---

name: reviewer-agent
description: Wdróż agenta-recenzenta wyposażonego w pięciowymiarową rubrykę ocen. Agent analizuje artefakty wykonawcy (buildera) i generuje ustrukturyzowany raport z recenzji, ułatwiając zespołowi manualny audyt na bazie gotowych wniosków.
version: 1.0.0
phase: 14
lesson: 39
tags: [reviewer, rubric, role-separation, second-loop, review-report]

---

Zakładając, że agent-wykonawca (builder) generuje już artefakty w środowisku roboczym, wdróż agenta-recenzenta, który je przeanalizuje i sporządzi ustrukturyzowany raport.

Wymagane elementy:

1. Plik `agents/reviewer.md` zawierający prompt systemowy dla recenzenta: zdefiniowany dostęp wyłącznie do odczytu, pięciowymiarowa rubryka ocen oraz wymóg wskazywania ścieżki do źródłowego artefaktu dla każdej oceny cząstkowej.
2. Skrypt `tools/reviewer.py` ładujący dane wejściowe `ReviewerInputs` ze środowiska roboczego i uruchamiający ocenianie LLM dla każdego z wymiarów.
3. Plik `outputs/review/<task_id>.json` stanowiący oficjalną ścieżkę zapisu raportu z recenzji.
4. Dokument `docs/reviewer-rubric.md` określający pięć wymiarów oceny, pytania pomocnicze oraz opisy kryteriów punktacji (dla ocen 0, 1, 2).
5. Krok w potoku CI dodający raport z recenzji jako komentarz w pull request (PR) po każdym zakończeniu prac przez wykonawcę.

Bezwzględne odrzucenia (Twarde kryteria):

- Nadanie recenzentowi uprawnień do edycji kodu lub zmian (diff). Podział ról między wykonawcę a recenzenta jest kluczem do sukcesu; jego zatarcie niweczy niezawodność weryfikacji.
- Kryteria oceny bez jednoznacznych definicji punktowych. Skala „od 0 do 2” bez precyzyjnych opisów staje się oceną czysto subiektywną.
- Raporty z recenzji pozbawione bezpośrednich odwołań i cytatów. Każda wystawiona ocena musi wskazywać na konkretny plik lub wpis w logach.
- Współdzielenie promptu systemowego wykonawcy. Użycie tego samego modelu LLM jest dopuszczalne, ale prompt musi być całkowicie odrębny.

Zasady odmowy współpracy (Refusal rules):

- Jeśli wykonawca nie dostarczy raportu weryfikacji, odmów uruchomienia recenzenta. Zanim przejdziesz do oceny semantycznej, kod musi pomyślnie przejść testy akceptacyjne.
- Jeśli projekt zawiera mniej niż trzy ukończone zadania, odmów uznania rubryki za w pełni skalibrowaną. Zapisz pierwsze raporty jako początkowy zestaw kalibracyjny.
- Jeśli stopień pewności recenzenta spadnie poniżej minimalnego progu, odmów wydania oceny i przekaż niepewny wymiar do weryfikacji przez człowieka.

Struktura plików:

```
<repo>/
├── agents/reviewer.md
├── tools/reviewer.py
├── outputs/review/
│   └── <task_id>.json
├── docs/reviewer-rubric.md
└── .github/workflows/review.yml
```

Na koniec dodaj sekcję „Co przeczytać dalej”, wskazującą na:

- Lekcję 40 dotyczącą pakowania przekazania prac (handoff package), łączącego weryfikację z recenzją.
- Lekcję 41 dotyczącą testowania w praktyce pełnego procesu separacji wykonawcy od recenzenta.
- Lekcję 05 (Samoudoskonalanie i KRYTYK) stanowiącą podstawę dla mechanizmów samooceny agenta, które ta lekcja rozwija.
