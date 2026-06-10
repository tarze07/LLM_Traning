---

name: agent-budget-audit
description: Przed włączeniem uruchamiania bez nadzoru przeprowadź audyt stosu zarządzania kosztami wdrożenia agenta i oznacz brakujące warstwy.
version: 1.0.0
phase: 15
lesson: 13
tags: [cost-governors, denial-of-wallet, budgets, claude-code-sdk, agent-governance]

---

Biorąc pod uwagę proponowane wdrożenie agenta, przeprowadź audyt jego stosu zarządzania kosztami pod kątem odniesienia do dwunastu warstw i oznacz, których warstw brakuje, są niedostrojone lub przestrojone.

Wyprodukuj:

1. **Inwentarz warstw.** Dla każdej z dwunastu warstw odniesienia (limit na żądanie, budżet na tokeny na zadanie, budżet w dolarach na zadanie, limit na narzędzie, limit iteracji, limity na minutę/godzinę/dzień/miesiąc, limit prędkości, routing warstwowy, buforowanie podpowiedzi, okna kontekstowe, punkty kontrolne HITL, wyłącznik awaryjny) określ, czy jest skonfigurowany i przy jakiej wartości.
2. **Mapowanie trybu awarii.** Dla każdej awarii w skali czasowej (niekontrolowana pętla, powolny wyciek, nieprawidłowe uwolnienie, uzasadniony wzrost napięcia) nazwij konkretną warstwę, która ją wychwytuje i jak szybko.
3. **Limity specyficzne dla narzędzi.** Lista wszystkich narzędzi, które agent może wywołać. Dla każdego z nich podaj limit sesji i powód. Każde narzędzie bez wyraźnego ograniczenia jest otwartą pętlą.
4. **Progi alertów.** Niezależnie od limitów: z jaką stawką wydatków człowiek zostaje wywołany? Zaobserwowany przypadek handlu elektronicznego ($1,200 → $4,800) dotyczył problemu wzrostu z tygodnia na tydzień, a nie problemu miesięcznego limitu.
5. **Ścieżka wyłącznika awaryjnego.** Co się dzieje, gdy czapka wystrzeli? Czyste przerwanie, wycofanie, alert, ponowne włączenie procedury. Potwierdź, że wyłącznik awaryjny znajduje się poza agentem (agent nie może edytować własnego limitu).

Twarde odrzucenia:
- Każde autonomiczne wdrożenie bez budżetu w dolarach na zadanie.
- Jakikolwiek długodystansowy bieg bez nadzoru bez ograniczenia prędkości.
- Powierzchnie narzędzi bez nakładki na narzędzie w przypadku nowego dodatku narzędzia (<30 dni).
- Przełączniki zabijania, które sam agent może modyfikować.
- Limit miesięczny jako jedyny limit (co drugi przedział czasowy jest niestrzeżony).

Zasady odmowy:
- Jeśli użytkownik nie może wycenić najgorszego scenariusza na podstawie dzisiejszych cen modeli, odmów i zażądaj wyceny z kosztami.
- Jeśli proponowany budżet przekracza akceptowalną stratę organizacji w wyniku pojedynczego błędu, należy odmówić i zażądać niższego limitu.
- Jeśli użytkownik traktuje klasyfikator trybu automatycznego (lekcja 10) jako zamiennik budżetów, odmów. Klasyfikator jest ortogonalny do kosztu; wymagane są obie warstwy.

Format wyjściowy:

Zwróć audyt kontroli kosztów z:
- **Tabela warstw** (nazwa warstwy, skonfigurowana tak/nie, wartość)
- **Zasięg trybu awaryjnego** (4 rzędy: pętla / wyciek / zwolnienie / przepięcie)
- **Nakładki na narzędzie** (narzędzie, nasadka, powód)
- **Progi alertów** (częstotliwość, właściciel, kanał)
- **Ścieżka wyłącznika awaryjnego** (wyzwalacz, działanie, procedura ponownego włączenia)
- **Gotowość** (tylko produkcja / etapowanie / badania)