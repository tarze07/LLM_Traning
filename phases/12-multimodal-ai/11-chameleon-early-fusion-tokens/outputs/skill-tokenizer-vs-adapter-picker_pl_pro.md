---

name: tokenizer-vs-adapter-picker
description: Dobierz architekturę dla modelu VLM: wczesną fuzję w stylu Chameleon (tokenizer i wspólny słownik) lub późną fuzję w stylu LLaVA (adapter na zamrożonym LLM).
version: 1.0.0
phase: 12
lesson: 11
tags: [chameleon, early-fusion, vq-vae, late-fusion, adapter]

---

Na podstawie specyfikacji produktu (samo rozumienie obrazów vs rozumienie + generowanie obrazów), docelowej jakości wizualnej (media społecznościowe / publikacje naukowe / druk / transmisja wideo) oraz budżetu (trening + wnioskowanie), zarekomenduj wybór pomiędzy architekturą wczesnej fuzji (rodzina Chameleon) a późnej fuzji (rodzina LLaVA), dołączając szczegółowy opis sugerowanej struktury modelu.

Wymagane elementy:

1. Rekomendacja (werdykt). Wybór: wczesna fuzja (Chameleon / Emu3 / AnyGPT) lub późna fuzja (LLaVA / BLIP-2 / Qwen-VL).
2. Dobór tokenizatora (dla wczesnej fuzji). Wybór spośród: VQ-VAE (Chameleon), MAGVIT-v2, IBQ lub SBER-MoVQGAN wraz z podaniem maksymalnej jakości rekonstrukcji (PSNR).
3. Plan stabilizacji treningu. Metody: QK-Norm, strategiczne rozmieszczenie dropoutu oraz pozycjonowanie LayerNorm w celu stabilizacji wczesnej fuzji w dużej skali.
4. Szacunek kosztów. Liczba roboczych godzin GPU na trening oraz opóźnienia wnioskowania (latency) na jeden obraz w porównaniu do alternatywnej metody późnej fuzji.
5. Poprzeczka jakości generowania (quality bar). Szacowany zakres wartości PSNR/FID; określenie, czy wymagana jakość jest osiągalna przy użyciu dyskretnych tokenów, czy wymaga przejścia na generowanie ciągłe (w stylu Transfusion).
6. Ścieżka migracji. Plan przejścia z architektury późnej fuzji na wczesną fuzję w sytuacji, gdy rozwój produktu wymusi konieczność generowania obrazów przez model.

Bezwzględne odrzucenia:
- Rekomendowanie wczesnej fuzji w stylu Chameleon dla systemów, które wymagają wyłącznie rozumienia obrazów. Późna fuzja (late fusion) jest prostsza, tańsza i oferuje wyższy pułap jakościowy w zadaniach czystej analizy.
- Sugerowanie użycia tokenizatora VQ-VAE z książką kodową K < 4096 do komercyjnego generowania obrazów (książka kodowa jest zbyt mała, co powoduje powstawanie widocznych artefaktów).
- Twierdzenie, że wnioskowanie we wczesnej fuzji jest bezkosztowe. Dekodowanie VQ-VAE dodaje około 50–200 ms do czasu generowania każdego obrazu, co często przekracza czas generowania odpowiedzi tekstowej przez LLM.

Zasady odmowy wykonania usługi:
- Jeśli użytkownik oczekuje generowania obrazów o fotorealistycznej jakości (FID < 15, jakość do druku), odrzuć tokeny dyskretne i rekomenduj modele oparte na podejściu ciągłym (np. Transfusion, Stable Diffusion 3, MMDiT - Lekcja 12.13).
- Jeśli specyfikacja produktu wyklucza potrzebę generowania obrazów przez model, odrzuć wczesną fuzję — stopień skomplikowania tej architektury jest w tym przypadku nieuzasadniony.
- Jeśli użytkownik planuje wykorzystać gotowe, zamrożone wagi modeli Llama lub Qwen LLM, odmów rekomendowania wczesnej fuzji — podejście to wymaga treningu modelu od podstaw.

Dane wyjściowe: Jednostronicowa rekomendacja zawierająca werdykt, wybór tokenizatora, listą kontrolną stabilności, kosztorys, ograniczenia jakościowe oraz ścieżkę migracji. Na końcu umieść odnośniki do publikacji arXiv: 2405.09818 (Chameleon) oraz 2408.11039 (Transfusion).
