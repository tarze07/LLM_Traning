---

name: resolution-budget-planner
description: Wybierz pomiędzy kwadratową zmianą rozmiaru, AnyRes, M-RoPE i NaFlex, aby uzyskać obciążenie VLM o mieszanych proporcjach i wyemituj plan budżetu tokenów dla poszczególnych zadań.
version: 1.0.0
phase: 12
lesson: 06
tags: [vlm, patch-n-pack, naflex, anyres, m-rope, token-budget]

---

Biorąc pod uwagę obciążenie pracą — opis obrazów, które VLM zobaczy (dokumenty OCR, wykresy, zrzuty ekranu interfejsu użytkownika, zdjęcia naturalne, klatki wideo) i całkowity budżet tokenów na żądanie — wybierz jedną strategię rozdzielczości na klasę obrazu i utwórz uruchamialną konfigurację.

Wyprodukuj:

1. Strategia według klasy obrazu. Dla każdej zadeklarowanej klasy (OCR, wykres, interfejs użytkownika, zdjęcie, klatka wideo) wybierz jedną z {square-resize, AnyRes, M-RoPE, NaFlex}. Uzasadnij jednym zdaniem, podając czułość rozdzielczości zadania.
2. Budżet tokenowy na obraz. Uwzględnij min_pixels, max_pixels (styl Qwen2.5-VL) i oczekiwaną długość sekwencji w wybranej strategii. Oznacz, jeśli jakikolwiek pojedynczy obraz przekracza 40% kontekstu LLM.
3. Plan pakowania partii. Jeśli żądania są grupowane, określ, czy chcesz używać `cu_seqlens` (FlashAttn varlen), gęstej maski o przekątnej blokowej, czy niewsadowego wnioskowania o pojedynczym obrazie. Zwróć uwagę na oszczędności FLOP varlena, gdy współczynniki proporcji wsadu różnią się > 2x.
4. Zalecenie dotyczące enkodera. SigLIP 2 NaFlex do obciążeń mieszanych; Natywny Qwen2.5-VL dla interfejsów użytkownika agentów; CLIP-336 + AnyRes do wdrożeń z zamrożonym koderem; surowy ViT przy 224 dla ścieżek zawierających wyłącznie zdjęcia.
5. Alarmy stanu awaryjnego. Tokeny na obraz w wybranej konfiguracji; koszt opóźnienia przy wstępnym wypełnieniu 30 tok/s; procent wypełnienia kontekstem; oczekiwana delta dokładności w porównaniu do kwadratowej zmiany rozmiaru w typowych testach OCR.

Twarde odrzucenia:
- Zalecanie zmiany rozmiaru kwadratu dla zadań OCR lub wykresów bez podawania numeru testu porównawczego, który użytkownik utraci.
- Zaproponowanie strategii, która produkuje więcej tokenów, niż pozwala na to kontekst LLM. Zawsze budżetuj w oparciu o zadeklarowane okno kontekstowe.
- Traktowanie AnyRes jako uniwersalnej odpowiedzi — jego multiplikatywny narzut kafelkowy może przekroczyć kontekst LLM, zanim jeden obraz zakończy kodowanie.

Zasady odmowy:
- Jeśli zadeklarowany przez użytkownika budżet na tokeny jest niższy niż 256 tokenów na obraz, odmów wykonania czegokolwiek innego niż zadanie semantyczne obejmujące wyłącznie zdjęcia — żadna ilość łączenia nie odzyska dokładności OCR przy tym budżecie.
- Jeśli użytkownik chce wyjść o gęstej predykcji (segmentacja, głębokość) bez tokenów rejestrów ViT w koderze, odmów i wskaż DINOv2 / SigLIP 2 z włączonymi rejestrami.
- Jeśli kontekst LLM użytkownika wynosi < 8 tys., a obciążenie obejmuje dokumenty lub zrzuty ekranu, odmów i zalecaj większy kontekst lub potok oparty najpierw na OCR.

Dane wyjściowe: jednostronicowy plan budżetu z tabelą strategii dla poszczególnych klas, plan pakowania wsadowego, zalecenia dotyczące kodera i lista alarmów. Zakończ odpowiednim dokumentem arXiv w celu kontynuacji — 2307.06304 dla NaViT, 2502.14786 dla SigLIP 2 / NaFlex, 2502.13923 dla Qwen2.5-VL.