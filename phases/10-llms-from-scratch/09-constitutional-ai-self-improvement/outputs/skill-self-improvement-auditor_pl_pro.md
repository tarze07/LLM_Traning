---

name: self-improvement-auditor
description: Przeprowadź audyt proponowanego procesu samodoskonalenia (self-improvement) lub potoku Constitutional AI, przed wdrożeniem na dużą skalę.
version: 1.0.0
phase: 10
lesson: 9
tags: [alignment, cai, grpo, rlhf, self-improvement, reward-hacking]

---

Dla proponowanego procesu treningowego wykorzystującego Constitutional AI, RLAIF, GRPO lub dowolną formę syntetycznych danych preferencji, przeprowadź audyt obejmujący:

1. **Sygnał nagrody**: Określ dokładny weryfikator (np. regex, SymPy, zestaw testów jednostkowych, LLM-as-a-judge). Sklasyfikuj go jako deterministyczny, stochastyczny (oparty na LLM) lub hybrydowy. Odrzuć każdą pętlę „samodoskonalenia”, która nie ma zewnętrznego zakotwiczenia w faktach (grounding) – model nie może generować sygnału z próżni.
2. **Statystyki grupowe**: W przypadku potoków GRPO potwierdź rozmiar grupy, metodę obliczania przewagi (z-score vs ranga względna) oraz zachowanie systemu w sytuacji, gdy odchylenie standardowe nagród w grupie spadnie do zera. Potok musi pomijać lub tłumić grupy o zerowej wariancji, zamiast dzielić przez epsilon i sztucznie generować sygnał gradientu.
3. **Budżet KL**: Liczbowy limit skumulowanej dywergencji KL (polityka || model referencyjny) podczas treningu. Potok musi zatrzymać się, zresetować lub przejść na model referencyjny z cieplejszym startem (warm-start) po osiągnięciu tego limitu. Brak kontroli KL oznacza niekontrolowany dryf modelu.
4. **Minimalna różnorodność (diversity floor)**: Zmierzony dolny limit odchylenia standardowego nagród w grupie, wariancji długości odpowiedzi lub entropii n-gramów. Jeśli wartość ta spadnie poniżej progu przez $N$ kolejnych rund, potok musi zostać zasilony nowymi danymi ludzkimi lub szerszym rozkładem promptów (prompt distribution).
5. **Udział danych ludzkich**: Minimalna część mieszanki treningowej pochodząca od ludzi – zazwyczaj 5–10%. Potoki oparte wyłącznie na samodestylacji (self-distillation) ulegają degeneracji po 3–5 rundach. Należy to wyraźnie zaznaczyć.
6. **Monitor zapadania rozkładu (mode collapse watchdog)**: Automatyczne sprawdzanie wskaźników: odchylenie standardowe nagród w poszczególnych rundach, unikalna liczba n-gramów dla wydzielonych promptów (held-out prompts), rozkład długości odpowiedzi oraz współczynnik odmów. Przekroczenie dowolnego z progów powinno automatycznie zatrzymać trening.
7. **Dryf konstytucyjny (constitutional drift)**: Wupadek potoków Constitutional AI wymagaj wersjonowanego pliku konstytucji, dziennika zmian oraz „zestawu testów regresji konstytucyjnej” – zbioru promptów, których oczekiwane zachowanie nie może ulec zmianie podczas edycji zasad.

Odrzuć i nie zatwierdzaj potoków, które:
- deklarują brak konieczności użycia danych ludzkich („zero human data”) przy braku zewnętrznego weryfikatora (reguł, narzędzi, środowiska wykonawczego).
- stosują model nagrody za proces (PRM) bez zabezpieczeń przed hakowaniem nagrody procesowej (np. gdy model generuje kroki, które jedynie wyglądają poprawnie, bez faktycznego dowodu).
- przeprowadzają więcej niż 5 rund dostrajania metodą rejection sampling (próbkowania odrzucającego) bez zdefiniowanego punktu odniesienia dla różnorodności.
- pomijają model referencyjny podczas optymalizacji polityki (brak modelu referencyjnego oznacza brak obliczania dywergencji KL, co skutkuje brakiem kotwicy stabilizującej).
- wykorzystują do roli sędziego (LLM-as-a-judge) ten sam model, który jest trenowany jako polityka (ryzyko stronniczości i zanieczyszczenia ocen).

Rezultat: jednostronicowy raport z audytu zawierający status (zaliczone/niezaliczone) dla każdego kryterium, zmierzone lub założone wartości oraz wskazanie konkretnego kroku w potoku generującego dany sygnał. Jeśli dowolny warunek nie zostanie spełniony, zaproponuj minimalną niezbędną zmianę pozwalającą na zaliczenie testu.
