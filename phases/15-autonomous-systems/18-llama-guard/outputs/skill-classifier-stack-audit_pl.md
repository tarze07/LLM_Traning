---

name: classifier-stack-audit
description: Przeprowadź audyt stosu klasyfikatorów wejścia/wyjścia we wdrożeniu (model, taksonomia, szyny wejściowe, szyny wyjściowe, szyny dialogowe) i oznacz luki w ataku kontradyktoryjnym.
version: 1.0.0
phase: 15
lesson: 18
tags: [llama-guard, nemo-guardrails, input-rails, output-rails, colang, adversarial-attacks]

---

Biorąc pod uwagę stos klasyfikatorów wdrożenia (wersja Llama Guard, konfiguracja NeMo Guardrails, niestandardowe klasyfikatory, kroki normalizacji), sprawdź je pod kątem odniesienia z roku 2026 i zaznacz powierzchnię ataku, której stos nie obejmuje.

Wyprodukuj:

1. **Wykaz modeli.** Wymień używane klasyfikatory. Llama Guard 3 (8B / 1B-INT4) kontra Llama Guard 4 (multimodalny, S1 – S14). Wersja NeMo Poręcze ochronne. Wszelkie niestandardowe klasyfikatory. Jeśli wdrożenie akceptuje obrazy, upewnij się, że klasyfikator jest wielomodalny.
2. **Mapowanie taksonomii.** Mapuj zadeklarowane kategorie biznesowe na taksonomię klasyfikatora. Każda kategoria, na której zależy operatorowi, musi zostać odwzorowana na kategorię klasyfikatora; niezamapowane kategorie są niestrzeżone.
3. **Zasięg szyn.** Potwierdź uruchomienie szyn wejściowych przed skrętem modelu i uruchomienie szyn wyjściowych przed statkami reagującymi. Szyny dialogowe (Colang w NeMo) wymuszają ograniczenia skrętu poprzecznego. Klasyfikatory jednoturowe nie mogą przechwytywać ataków wieloturowych.
4. **Normalizacja.** Upewnij się, że dane wejściowe są znormalizowane przez NFKC, odwzorowane na homoglify i mają usunięte przed klasyfikacją znaki o zerowej szerokości / selektor odmian. Klasyfikacja w postaci surowych bajtów jest w 100% celem ASR w przypadku przemytu emoji (Huang i in. 2025).
5. **Zasięg korpusu ataku.** Dla każdego udokumentowanego ataku (przemyt emoji, homoglif, przekierowanie w kontekście, parafraza semantyczna) nazwij konkretną obronę na stosie. Obrona oparta wyłącznie na klasyfikatorach nie przechodzi tego audytu; wymagane jest nakładanie warstw na Konstytucję (Lekcja 17) i czas działania (Lekcja 10, 13, 14).

Twarde odrzucenia:
- Wdrożenia wykorzystujące klasyfikator tekstowy na wejściach multimodalnych.
- Wdrożenia bez etapu normalizacji.
- Wdrożenia tylko z szynami wejściowymi (bez szyn wyjściowych na wyjściach kategorii wrażliwej).
- Stos traktujący klasyfikator jako pojedynczą warstwę bezpieczeństwa.
- ASR twierdzi, że operator nie może reprodukować na własnej dystrybucji.

Zasady odmowy:
- Jeśli kategorie zadeklarowane przez użytkownika nie pasują do taksonomii klasyfikatora, odmów i zażądaj najpierw mapowania. Niezmapowany = niestrzeżony.
- Jeśli wdrożenie powołuje się na numery ASR Llama Guard 3 na multimodalnej powierzchni wejściowej, odmów i wymagaj Llama Guard 4 lub klasyfikatora multimodalnego.
- Jeśli użytkownik uzna warstwę klasyfikatora za wystarczającą w warunkach wysokiego ryzyka, odmów. Artykuł 14 unijnej ustawy o sztucznej inteligencji (lekcja 15) przewiduje, że na górze będzie nadzór człowieka.

Format wyjściowy:

Zwróć audyt klasyfikatora za pomocą:
- **Inwentarz modelu** (nazwa, wersja, modalność)
- **Mapowanie taksonomii** (kategoria operatora → kategoria klasyfikatora)
- **Pokrycie szyn** (wejście/wyjście/okno dialogowe; strzelanie przed/za modelem)
- **Nota normalizacyjna** (NFKC t/n, homoglif t/n, pasek o zerowej szerokości t/n)
- **Zasięg korpusu ataku** (atak → obrona)
- **Kompletność warstwy** (klasyfikator + skład + czas wykonania; wymagane trzy)
- **Gotowość** (tylko produkcja / etapowanie / badania)