---

name: tokenizer-vs-adapter-picker
description: Wybierz pomiędzy wczesną fuzją w stylu Chameleon (tokenizer współdzielonego słownictwa) a późną fuzją w stylu LLaVA (adapter na zamrożonym LLM) dla projektu VLM.
version: 1.0.0
phase: 12
lesson: 11
tags: [chameleon, early-fusion, vq-vae, late-fusion, adapter]

---

Biorąc pod uwagę specyfikację produktu (tylko zrozumienie lub zrozumienie + generowanie), docelową jakość obrazu (post w mediach społecznościowych / czasopismo / druk / transmisja) i budżet kosztów (szkolenie + wnioskowanie), polecam rodzinę Chameleon lub rodzinę LLaVA z konkretnym zarysem architektury.

Wyprodukuj:

1. Werdykt. Rodzina wczesnej fuzji (Chameleon / Emu3 / AnyGPT) lub późnej fuzji (LLaVA / BLIP-2 / Qwen-VL).
2. Wybór tokenizatora (dla werdyktów wczesnej fuzji). VQ-VAE (Chameleon), MAGVIT-v2, IBQ lub SBER-MoVQGAN; przytocz oczekiwany pułap rekonstrukcji w PSNR.
3. Plan stabilizacji treningowej. QK-Norm, rozmieszczenie porzuceń, porządkowanie LayerNorm w celu wczesnej fuzji na dużą skalę.
4. Kosztorys. Godziny szkolenia procesora graficznego i opóźnienia wnioskowania na obraz w porównaniu z alternatywą późnej fuzji.
5. Sufit jakości generacji. Zakres PSNR/FID jakiego może oczekiwać użytkownik; czy pasek jakości produktu jest osiągalny za pomocą dyskretnych tokenów, czy też wymaga ciągłego generowania (w stylu transfuzji).
6. Ścieżka migracji. Jeśli użytkownik urośnie i późna fuzja stanie się ograniczająca (potrzebuje wyjścia obrazu), jak wygląda migracja.

Twarde odrzucenia:
- Polecanie stylu Chameleon w przypadku produktów wymagających zrozumienia. Późna fuzja jest prostsza, tańsza i wymaga wyższego pułapu dla czystego zrozumienia.
- Proponowanie VQ-VAE z K<4096 do generowania obrazu produkcyjnego. Książka kodów jest za mała, widoczne są artefakty.
- Zgłaszanie wniosków dotyczących wczesnej syntezy jest bezpłatne. Dekoder VQ dodaje 50–200 ms na wygenerowany obraz, często więcej niż czas wyjściowy LLM.

Zasady odmowy:
- Jeśli użytkownik chce wygenerować obraz o granicznej jakości (FID < 15, gotowy do druku), odrzuć dyskretne tokeny i wskaż Transfusion / Stable Diffusion 3 / MMDiT (lekcja 12.13).
- Jeśli produkt nigdy nie będzie potrzebował wydruku obrazu, odrzuć wczesną fuzję – złożoność jest nieuzasadniona.
- Jeśli użytkownik chce podłączyć istniejące ciężarki Llama / Qwen LLM, odmów wcześniejszej fuzji – wymaga to wstępnego przeszkolenia świeżego modelu.

Dane wyjściowe: jednostronicowy plan z werdyktem, wyborem tokenizatora, listą kontrolną stabilności, kosztorysem, pułapem jakości, ścieżką migracji. Zakończ arXiv 2405.09818 (Chameleon) i 2408.11039 (Transfusion) dla odczytu porównawczego.