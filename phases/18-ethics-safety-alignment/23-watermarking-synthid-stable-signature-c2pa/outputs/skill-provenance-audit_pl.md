---

name: provenance-audit
description: Przeprowadź audyt łańcucha pochodzenia wdrożenia treści w zakresie znaków wodnych i metadanych C2PA.
version: 1.0.0
phase: 18
lesson: 23
tags: [watermarking, synthid, stable-signature, c2pa, provenance]

---

Biorąc pod uwagę wdrożenie treści z oświadczeniem o pochodzeniu, przeprowadź audyt łańcucha pochodzenia.

Wyprodukuj:

1. Inwentarz znaku wodnego. Wymień każdą modalność (tekst, obraz, dźwięk, wideo) i znak wodny zastosowany w każdej z nich. Brak znaku wodnego = brak ścieżki wykrywania.
2. Solidność znaku wodnego. Dla każdego znaku wodnego nazwij klasę przeciwnika, którą przetrwa (kompresja, kadrowanie, parafraza, dostrajanie). Ograniczenia flagi zgodnie z Kirchenbauer 2023, sekcja 6 (parafraza) i „Stabilny podpis jest niestabilny” 2024 (doprecyzowanie).
3. Zasięg C2PA. Czy załączono metadane C2PA? Czy łańcuch podpisujący pochodzi z zaufanej tożsamości? Metadane można usunąć; obecność nie jest wystarczająca.
4. Detektor crossmodalny. Czy istnieje ujednolicony detektor dla różnych modalności (SynthID 2025), czy tylko dla konkretnej modalności?
5. Dostosowanie regulacyjne. Czy wdrożenie spełnia wymogi w zakresie przejrzystości określone w art. 50 ustawy UE o sztucznej inteligencji (obowiązujące od sierpnia 2026 r.)? Czy jest zgodny z Kodeksem Przejrzystości (wersja ostateczna z czerwca 2026 r.)?

Twarde odrzucenia:
- Wszelkie roszczenia dotyczące „znaku wodnego” bez nazwanego mechanizmu i detektora.
- Wszelkie twierdzenia dotyczące „autentyczności” oparte wyłącznie na braku znaku wodnego (model bez znaku wodnego ≠ autentyczny).
– Wszelkie roszczenia dotyczące pochodzenia obrazu bez oceny ataku polegającego na usunięciu Fernandez 2024.

Zasady odmowy:
- Jeśli użytkownik zapyta „czy to wykryje całą zawartość AI”, odrzuci twierdzenie binarne; znak wodny zależy od modelu.
- Jeśli użytkownik prosi o rozwiązanie o uniwersalnym pochodzeniu, odmów i wskaż podejście oparte na znaku wodnym + C2PA.

Wynik: jednostronicowy audyt wypełniający pięć sekcji, wskazujący luki w solidności poszczególnych modalności i wymieniający pojedynczą dodatkową kontrolę o najwyższej wartości. Przytocz po jednym SynthID (Google DeepMind), Stable Signature (Fernandez et al. 2023) i C2PA.