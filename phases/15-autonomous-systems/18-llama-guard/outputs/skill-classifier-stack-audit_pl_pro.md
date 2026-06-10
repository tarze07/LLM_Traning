---

name: classifier-stack-audit
description: Przeprowadź audyt stosu klasyfikatorów wejścia/wyjścia we wdrożeniu (model, taksonomia, szyny wejściowe, szyny wyjściowe, szyny dialogowe) oraz zidentyfikuj podatności na ataki typu adversarial (kontradyktoryjne).
version: 1.0.0
phase: 15
lesson: 18
tags: [llama-guard, nemo-guardrails, input-rails, output-rails, colang, adversarial-attacks]

---

Na podstawie stosu klasyfikatorów wdrożenia (wersja Llama Guard, konfiguracja NeMo Guardrails, niestandardowe klasyfikatory, kroki normalizacji) przeprowadź weryfikację pod kątem standardów z 2026 roku i wskaż obszary ataku, przed którymi dany stos nie zapewnia ochrony.

Przygotuj:

1. **Wykaz modeli.** Wymień wdrożone klasyfikatory, określając ich warianty (np. Llama Guard 3 8B / 1B-INT4 vs Llama Guard 4 multimodalny S1–S14), wersję frameworku NeMo Guardrails oraz wszelkie niestandardowe klasyfikatory. Jeśli system przyjmuje obrazy na wejściu, upewnij się, że klasyfikator obsługuje multimodalność.
2. **Mapowanie taksonomii.** Przyporządkuj zdefiniowane kategorie biznesowe do taksonomii klasyfikatora. Każda kluczowa dla operatora kategoria musi mieć swój odpowiednik w klasyfikatorze; obszary niepowiązane pozostają bez ochrony.
3. **Pokrycie szyn (rails).** Upewnij się, że szyny wejściowe (input rails) uruchamiają się przed przetworzeniem zapytania przez model bazowy, a szyny wyjściowe (output rails) przed wysłaniem odpowiedzi do użytkownika. Szyny dialogowe (np. Colang w NeMo) powinny kontrolować przebieg całej rozmowy; klasyfikatory analizujące pojedyncze wypowiedzi (single-turn) nie są w stanie wykryć ataków wieloturowych (multi-turn).
4. **Normalizacja tekstu.** Zweryfikuj, czy dane wejściowe przed przekazaniem do klasyfikacji są normalizowane za pomocą algorytmu NFKC, sprawdzane pod kątem homoglifów oraz oczyszczane ze znaków o zerowej szerokości i selektorów wariantów (variation selectors). Analiza surowego tekstu bez normalizacji naraża system na 100% skuteczność ataku (ASR) metodą emoji smuggling (Huang i in., 2025).
5. **Odporność na typy ataków.** Dla każdej udokumentowanej metody ataku (emoji smuggling, homoglify, przekierowanie kontekstowe, parafraza semantyczna) określ zastosowany mechanizm obronny. Zabezpieczenia oparte wyłącznie na klasyfikatorach są niewystarczające do zaliczenia audytu; niezbędna jest wielowarstwowość obejmująca Konstytucję (Lekcja 17) oraz warstwę uruchomieniową (Lekcje 10, 13, 14).

Kryteria bezwzględnego odrzucenia (Hard rejects):
- Stosowanie klasyfikatorów wyłącznie tekstowych dla systemów przyjmujących wejścia multimodalne.
- Brak etapu normalizacji i oczyszczania tekstu wejściowego.
- Wdrożenie wyłącznie szyn wejściowych (brak szyn wyjściowych dla odpowiedzi w kategoriach wrażliwych).
- Traktowanie klasyfikatora jako jedynego elementu systemu bezpieczeństwa.
- Deklarowanie wskaźników ASR, których operator nie jest w stanie weryfikować i powtórzyć w rzeczywistych warunkach.

Zasady odmowy zatwierdzenia:
- Jeśli zadeklarowane przez użytkownika kategorie nie pasują do taksonomii klasyfikatora, zablokuj proces i zażądaj najpierw poprawnego mapowania (kategorie niezmapowane pozostają bez ochrony).
- Jeśli we wdrożeniu powołano się na wskaźniki ASR dla Llama Guard 3 przy jednoczesnym przyjmowaniu danych multimodalnych, odrzuć projekt i zażądaj zastosowania Llama Guard 4 lub innego klasyfikatora multimodalnego.
- Jeśli użytkownik uznaje warstwę klasyfikatora za w pełni wystarczającą w scenariuszach wysokiego ryzyka, zablokuj zatwierdzenie. Zgodnie z Artykułem 14 unijnego aktu o sztucznej inteligencji (Lekcja 15) wymagany jest nadrzędny nadzór człowieka (human oversight).

Format raportu z audytu:

Raport z audytu klasyfikatorów must zawierać:
- **Wykaz modeli** (nazwa, wersja, obsługiwane modalności)
- **Mapowanie taksonomii** (kategoria zdefiniowana przez operatora → kategoria w klasyfikatorze)
- **Pokrycie szyn** (szyny wejściowe/wyjściowe/dialogowe; moment uruchomienia przed/po wywołaniu modelu)
- **Weryfikacja normalizacji** (normalizacja NFKC: tak/nie, obsługa homoglifów: tak/nie, filtr znaków o zerowej szerokości: tak/nie)
- **Odporność na typy ataków** (metoda ataku → zastosowana obrona)
- **Kompletność warstw zabezpieczeń** (obecność klasyfikatora + reguł systemowych + mechanizmów czasu wykonania – wymagane są wszystkie trzy)
- **Status gotowości** (produkcja / środowisko przejściowe / badania)
