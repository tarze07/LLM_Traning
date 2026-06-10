---

name: onevision-budget-planner
description: Alokuj ujednolicone budżety tokenów wizualnych w stylu LLaVA-OneVision dla scenariuszy obejmujących jeden obraz, wiele obrazów i wideo w celu uzyskania docelowego asortymentu produktów.
version: 1.0.0
phase: 12
lesson: 08
tags: [llava-onevision, token-budget, curriculum, multi-image, video]

---

Biorąc pod uwagę oczekiwany rozkład zadań produktu — procent żądań obejmujących jeden obraz, wiele obrazów i wideo — oraz budżet na symbole wizualne na próbkę, wyemituj plan alokacji według scenariusza i program szkoleniowy.

Wyprodukuj:

1. Konfiguracja według scenariusza. Pojedynczy obraz: liczba płytek AnyRes + miniatura + współczynnik łączenia; wiele obrazów: łączenie obrazów na próbkę + na obraz; wideo: liczba klatek + łączenie na klatkę.
2. Symboliczne saldo budżetu. Suma tokenów każdego scenariusza powinna mieścić się w granicach ±30% budżetu docelowego; oznacz dowolny scenariusz, który spada poniżej 70% wartości docelowej (niedostatecznie tokenizowane) lub powyżej 130% (ryzyko kontekstu).
3. Plan nauczania. Trzy etapy (SI → OV → TT) z wagami danych. Na etapie TT użyj zestawu produktów użytkownika.
4. Oczekiwane nowe umiejętności. Biorąc pod uwagę asortyment produktów użytkownika, należy przewidzieć, które nowe możliwości w stylu LLaVA-OneVision prawdopodobnie się pojawią (wiele kamer, zestaw znaków, agent zrzutów ekranu lub warianty specyficzne dla produktu).
5. Pole treningowe z danymi. Przybliżona liczba tokenów/obrazów/ramek wymagana na etap, biorąc pod uwagę podstawowy LLM 7B, powołując się na skalę danych OneVision-1.5.

Twarde odrzucenia:
- Proponowanie zleceń scenicznych, które stawiają wideo lub wieloobrazy przed pojedynczym obrazem. OneVision pokazuje, że traci to 2-4 MMMU.
- Przydzielanie całego budżetu na wideo, gdy produkt składa się w 80% z pojedynczego obrazu. Marnotrawstwo, a nie równowaga.
- Zakładając, że AnyRes-16 (siatka 4x4) mieści się w budżecie tokenów 4 tys. bez agresywnego łączenia. Tak nie jest.

Zasady odmowy:
- Jeśli budżet tokena na próbkę jest niższy niż 1024, odrzuć przypadki użycia wielu obrazów lub wideo — poniżej tego progu scenariusze się załamują.
- Jeśli użytkownik chce mieć ponad 5 klatek wideo w pełnej rozdzielczości 729 tokenów, odmów; zalecamy 3x łączenie lub mniej klatek.
- Jeśli w dystrybucji produktów całkowicie pominięty jest pojedynczy obraz, odmów i zamiast tego poleć M-RoPE typu Qwen2.5-VL — program OneVision zakłada, że ​​podstawą percepcji będzie pojedynczy obraz.

Dane wyjściowe: jednostronicowy plan z konfiguracją tokenów dla poszczególnych scenariuszy, wagami etapów programu nauczania, przewidywaniami pojawiających się umiejętności i szacunkową skalą danych. Zakończ wskaźnikami do arXiv 2408.03326 (OneVision) i arXiv 2509.23661 (OneVision-1.5 w pełni otwarty).