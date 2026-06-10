---

name: resolution-budget-planner
description: Dobierz strategię przetwarzania obrazów (skalowanie do kwadratu, AnyRes, M-RoPE lub NaFlex) dla obciążeń VLM o mieszanych proporcjach i wygeneruj plan budżetu tokenów dla poszczególnych zadań.
version: 1.0.0
phase: 12
lesson: 06
tags: [vlm, patch-n-pack, naflex, anyres, m-rope, token-budget]

---

Na podstawie profilu obciążenia (opisu obrazów przetwarzanych przez model VLM, takich jak dokumenty OCR, wykresy, zrzuty ekranu interfejsu użytkownika, zdjęcia naturalne, klatki wideo) oraz zadanego limitu tokenów na zapytanie, dobierz odpowiednią strategię rozdzielczości dla każdej klasy obrazów i wygeneruj gotową konfigurację wdrożeniową.

Wymagane elementy:

1. Strategia dla każdej klasy obrazów. Dla każdej zdefiniowanej klasy (OCR, wykres, interfejs użytkownika, zdjęcie, klatka wideo) wybierz jedną ze strategii: {square-resize, AnyRes, M-RoPE, NaFlex}. Uzasadnij wybór jednym zdaniem, biorąc pod uwagę wrażliwość danego zadania na rozdzielczość obrazu.
2. Budżet tokenów na obraz. Określ parametry min_pixels i max_pixels (w stylu Qwen2.5-VL) oraz oczekiwaną długość sekwencji dla wybranej strategii. Wyraźnie oznacz sytuacje, w których pojedynczy obraz zużywa ponad 40% dostępnego okna kontekstowego LLM.
3. Plan pakowania paczek (batch packing). W przypadku grupowania zapytań (batching) określ sposób przetwarzania: użycie `cu_seqlens` (wersja FlashAttention varlen), gęstej maski blokowo-diagonalnej, czy wnioskowanie dla pojedynczego obrazu bez pakowania (non-batched). Podaj szacowaną oszczędność operacji FLOP dzięki FlashAttention varlen w scenariuszach, gdzie proporcje obrazów w paczce różnią się ponad dwukrotnie.
4. Rekomendacja encodera. Na przykład: SigLIP 2 NaFlex dla obciążeń mieszanych; natywny Qwen2.5-VL dla agentów interfejsu użytkownika; CLIP-336 + AnyRes dla wdrożeń z zamrożonym encoderem; podstawowy ViT o rozdzielczości 224x224 dla systemów przetwarzających wyłącznie typowe zdjęcia naturalne.
5. Analiza ryzyka (alarmy). Wskaż liczbę tokenów na obraz w wybranej konfiguracji, prognozowany wpływ na opóźnienie (latency) przy założeniu szybkości generowania pre-fill na poziomie 30 tokenów/sekundę, procent zajętości okna kontekstowego oraz szacowany spadek dokładności w benchmarkach OCR w przypadku powrotu do skalowania obrazów do kwadratu.

Bezwzględne odrzucenia:
- Sugerowanie skalowania obrazów do kwadratu (square-resize) w zadaniach OCR lub analizie wykresów bez podania konkretnych spadków w benchmarkach, na jakie naraża się użytkownik.
- Proponowanie konfiguracji generującej więcej tokenów niż wynosi fizyczne okno kontekstowe modelu LLM. Budżet tokenów musi zawsze mieścić się w zadeklarowanym oknie kontekstowym.
- Traktowanie AnyRes jako rozwiązania uniwersalnego. Narzut wynikający z kafelkowania w AnyRes może zapełnić cały kontekst LLM zanim zakończy się proces kodowania pojedynczego obrazu.

Zasady odmowy wykonania usługi:
- Jeśli budżet tokenów zadeklarowany przez użytkownika wynosi mniej niż 256 tokenów na obraz, odmów planowania dla zadań innych niż zadania semantyczne na typowych zdjęciach naturalnych — przy tak niskim limicie żadna metoda agregacji nie pozwoli na zachowanie poprawnej dokładności OCR.
- Jeśli użytkownik oczekuje predykcji gęstej (dense prediction, np. segmentacja, estymacja głębokości) przy braku tokenów rejestrów ViT (register tokens) w encoderze, odmów i zalecaj użycie modeli DINOv2 lub SigLIP 2 z aktywnymi rejestrami.
- Jeśli rozmiar okna kontekstowego LLM wynosi poniżej 8k tokenów, a przetwarzane dane obejmują dokumenty tekstowe lub zrzuty ekranów, odmów i rekomenduj zwiększenie okna kontekstowego lub zastosowanie potoku (pipeline) z wydzielonym krokiem OCR na początku.

Dane wyjściowe: Jednostronicowy plan budżetu tokenów zawierający tabelę strategii dla poszczególnych klas, plan pakowania paczek (batch packing), rekomendację encodera oraz analizę ryzyka (alarmy). Na końcu umieść odnośnik do odpowiedniej publikacji naukowej na arXiv: 2307.06304 (NaViT), 2502.14786 (SigLIP 2 / NaFlex) lub 2502.13923 (Qwen2.5-VL).
