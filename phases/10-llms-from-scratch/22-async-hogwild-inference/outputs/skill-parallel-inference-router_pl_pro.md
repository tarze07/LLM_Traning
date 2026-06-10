---

name: parallel-inference-router
description: Dobierz optymalną strategię wnioskowania równoległego (głosowanie, Tree of Thought, systemy wieloagentowe, Hogwild! lub dekodowanie spekulatywne) dla danego obciążenia.
version: 1.0.0
phase: 10
lesson: 22
tags: [parallel-inference, hogwild, speculative-decoding, tree-of-thought, multi-agent, reasoning]

---

Na podstawie profilu obciążenia (budżet tokenów na zadanie, możliwości zrównoleglenia, rodzina modeli, środowisko wdrożeniowe, budżet opóźnień) zarekomenduj optymalną strategię lub kombinację technik wnioskowania równoległego.

Wygeneruj:

1. Klasyfikację zadań: długie rozumowanie (ponad 5 tys. tokenów), średnio złożony proces myślowy (1–5 tys. tokenów), krótki czat (poniżej 1 tys. tokenów) lub klasyfikacja. Podejmij decyzję na samym początku.
2. Oś zrównoleglenia: wewnątrz sekwencji (dekodowanie spekulatywne) vs na poziomie sekwencji (głosowanie, Hogwild!, systemy wieloagentowe). Dla większość obciążeń w pierwszej kolejności stosuje się zrównoleglenie wewnątrz sekwencji.
3. Rekomendację strategii. Wybierz spośród: samo dekodowanie spekulatywne (bezpieczne rozwiązanie domyślne dla każdego zadania powyżej 100 tokenów), dekodowanie spekulatywne + Hogwild! (długie wnioskowanie o strukturze podatnej na zrównoleglenie), Tree of Thought (dla problemów wymagających wyraźnego rozgałęziania i przycinania ścieżek), system wieloagentowy (dla zadań wymagających specjalizacji ról) lub konsorcjum głosujące (dla klasyfikacji o kluczowym znaczeniu).
4. Konfigurację parametrów. Dla dekodowania spekulatywnego: rodzina modeli pomocniczych (domyślnie EAGLE-3) oraz `N` (zgodnie z lekcją 15, faza 10). Dla Hogwild!: liczba wątków roboczych N (od 2 do 4, rzadko więcej), szablon promptu koordynującego, weryfikacja wdrożenia na pojedynczym węźle.
5. Szacowanie łącznego przyspieszenia. Przy połączeniu dekodowania spekulatywnego z Hogwild! oblicz skumulowane przyspieszenie (np. 3x dla dekodowania spekulatywnego * 1.5-2x dla Hogwild! = 4.5-6x).

Kategoryczne odrzucenia:
- Stosowanie Hogwild! dla obciążeń poniżej 2000 tokenów – narzut związany z koordynacją przewyższa zyski.
- Stosowanie Hogwild! na modelach niesłużących do wnioskowania (brak zdolności do koordynacji).
- Stosowanie struktur wieloagentowych do problemów bez naturalnego podziału na role.
- Stosowanie Tree of Thought bez wyraźnego zdefiniowania logiki rozgałęziania i przycinania (w przeciwnym razie strategia sprowadza się do liniowego Chain of Thought).
- Uruchamianie Hogwild! w środowisku wielowęzłowym (synchronizacja cache'u między węzłami jest zbyt wolna).

Zasady odmowy wykonania zadania:
- Jeśli obciążenie dotyczy eksperymentów badawczych, rekomenduj Hogwild! jako konfigurację eksperymentalną, a nie produkcyjną. Przyrost wydajności zależy od specyfiki zadania, a wdrożenia produkcyjne są rzadkością (stan na kwiecień 2026 r.).
- Jeśli użytkownik wymaga gwarantowanego przyspieszenia, odmów i wyjaśnij, że tylko dekodowanie spekulatywne daje silne gwarancje zachowania rozkładu prawdopodobieństwa wyników (exact distribution match). Metoda Hogwild! ma charakter empiryczny.
- Jeśli użytkownik dysponuje ograniczoną pamięcią VRAM, odrzuć konfigurację Hogwild! z N > 2 — każdy proces roboczy wymaga własnej pamięci na aktywacje, pomimo współdzielenia cache'u.

Format wyjściowy: Jednostronicowa rekomendacja zawierająca klasyfikację zadań, oś zrównoleglenia, wybraną strategię, parametry oraz skumulowane oszacowanie przyspieszenia. Zakończ sekcją „Kryteria wycofania” (rollback trigger) określającą konkretną metrykę opóźnienia lub dokładności, która uzasadniałaby rezygnację z Hogwild! na rzecz samego dekodowania spekulatywnego, jeśli to pierwsze nie przyniesie oczekiwanych rezultatów w ciągu pierwszych 100 zapytań produkcyjnych.
