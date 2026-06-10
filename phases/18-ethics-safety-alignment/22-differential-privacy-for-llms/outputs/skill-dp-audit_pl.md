---

name: dp-audit
description: Przeprowadź inspekcję roszczenia dotyczącego różnicowej prywatności dla wdrożenia modelu językowego.
version: 1.0.0
phase: 18
lesson: 22
tags: [differential-privacy, dp-sgd, lora, mia, pmixed]

---

Biorąc pod uwagę roszczenie dotyczące prywatności w przypadku wdrożenia modelu językowego, sprawdź to roszczenie.

Wyprodukuj:

1. (ε, δ) wartości. Jakie ε i δ zostały użyte? Który księgowy je obliczył (Księgowy Moments, Rényi DP, PKB)? ε bez księgowego nie ma sensu.
2. Cel DP. Czy gwarancja DP obejmuje cały model czy adaptery (LoRA)? W przypadku LoRA zapamiętywanie modelu podstawowego nie jest objęte gwarancją.
3. Protokół MIA. Czy wnioskowanie o członkostwie testowano na kanarkach (Duan 2024), czy na ekstrakcji (Carlini 2021, Nasr 2025)? Per Kowalczyk i in. 2025, oba mierzą różne rzeczy.
4. Kontrola narażenia na zaufanie. Czy wdrożenie udostępnia wyniki zaufania? Jeśli tak, obowiązuje atak Odwrócenie DP poprzez informację zwrotną LLM; wymagane jest dodatkowe obcięcie/kwantyzacja.
5. Porównanie mechanizmów alternatywnych. Czy wzięto pod uwagę dane PMixED lub DP-syntetyczne? Te alternatywy mogą zapewnić lepszą użyteczność w przypadku określonych modeli zagrożeń.

Twarde odrzucenia:
- Każde roszczenie DP bez pary ε, δ i księgowego.
- Wszelkie roszczenia DP oparte wyłącznie na MIA dla kanarków.
- Każde wdrożenie ujawniające wskaźniki zaufania bez rozwiązania problemu cofnięcia DP.

Zasady odmowy:
- Jeśli użytkownik zapyta „czy epsilon=8 jest wystarczająco bezpieczny”, odrzuć odpowiedź numeryczną; bezpieczeństwo zależy od modelu zagrożenia i dystrybucji danych, które dają najwięcej możliwości wyodrębnienia.
- Jeśli użytkownik poprosi o zalecane ε dla wdrożenia LLM, odrzuć uniwersalny cel liczbowy; wymagają modelu zagrożeń, wrażliwości danych, ograniczeń użyteczności i szczegółów księgowych przed omówieniem potencjalnych zakresów.

Wynik: jednostronicowy audyt wypełniający pięć sekcji, wskazujący brakującego księgowego lub ocenę MSWiA oraz wymieniający środki zaradcze o największej wartości. Cytuj Abadi i in. 2016 (DP-SGD) oraz Kowalczyk i in. 2025 raz na każdą.