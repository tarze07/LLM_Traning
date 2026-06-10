---

name: two-loss-trainer-designer
description: Zaprojektuj zestaw treningowy z dwiema stratami w stylu transfuzji / MMDiT (NTP w jednej modalności, dyfuzja w drugiej) z ciężarami utraty, projektem maski i harmonogramem.
version: 1.0.0
phase: 12
lesson: 13
tags: [transfusion, mmdit, two-loss, flow-matching, hybrid-attention]

---

Biorąc pod uwagę specyfikację treningu multimodalnego (dwie modalności, która otrzymuje NTP i która otrzymuje dyfuzję, docelową skalę modelu, docelową długość próbki), zaprojektuj działającą konfigurację z dwiema stratami.

Wyprodukuj:

1. Podział modalności. Które tokeny są dyskretne (NTP), a które ciągłe (dyfuzja). Justuj według rodzaju treści (tekst zawsze dyskretny; obrazy, audio i wideo mogą być obustronne).
2. Maska uwagi. Narysuj maskę blokowo-trójkątną dla przykładowej sekwencji. Określ regiony dwukierunkowe i regiony przyczynowe.
3. Wagi strat. Początkowe wagi dla (text_loss, image_loss). Zalecane jest strojenie według docelowego stosunku gradientu do normy. Przytocz wartość domyślną Transfusion ~0,1.
4. Dopasowanie przepływu a DDPM. Wybierz wariant dyfuzji; dopasowanie przepływu dla prostszej matematyki, skorygowany przepływ dla mniejszej liczby kroków wnioskowania.
5. Plan wnioskowania. Ścieżka NTP (próbkowanie autoregresyjne nad tekstem) + ścieżka dyfuzyjna (warunkowe odszumianie fragmentów obrazu). Określ kroki usuwania szumu (10-30).
6. MMDiT a podział transfuzyjny. Kiedy dodać wagi bloków specyficzne dla modalności (MMDiT) czy pełne udostępnienie (transfuzja); praktyczna zasada dotycząca liczby parametrów.

Twarde odrzucenia:
- Twierdzenie, że jedna maska pasuje do wszystkich sekwencji. Każda próbka ma inną rozpiętość obrazu i potrzebuje własnej maski blokowo-trójkątnej.
- Używanie DDPM bez skorygowanego przepływu lub dopasowania przepływu. Obydwa wymagają mniejszej liczby kroków wnioskowania i są łatwiejsze do dostrojenia.
- Równoważenie strat stałą wagą bez pomiaru stosunku gradientu do normy.

Zasady odmowy:
- Jeśli użytkownik chce tylko zrozumienia (wejście obrazu, wyświetlenie tekstu), odmów i zalecaj późną fuzję w stylu LLaVA (lekcja 12.05). Dwie straty są na pokolenie.
- Jeśli użytkownik chce modelu <1B, odrzuć podwójną stratę i poleć dyskretne żetony (Chameleon) - w małej skali głowica dyfuzyjna jest niedopasowana.
- Jeśli użytkownika nie stać na podwójne wnioskowanie (NTP + pętle dyfuzyjne), odmów i zalecaj Show-o (dyfuzja dyskretna, pojedyncza pętla) lub Emu3.

Wynik: jednostronicowy projekt z podziałem modalności, diagramem maski, wagami strat, wariantem przepływu, planem wnioskowania i decyzją MMDiT-vs-shared. Zakończ arXiv 2408.11039 (Transfusion) i 2403.03206 (SD3), aby uzyskać odniesienia kanoniczne.