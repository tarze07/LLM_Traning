---

name: gated-bridge-diagnostic
description: Zidentyfikuj elementy architektury typu Flamingo w otwartej konfiguracji VLM i zdiagnozuj problemy z działaniem mechanizmu bramkowania.
version: 1.0.0
phase: 12
lesson: 04
tags: [flamingo, idefics, openflamingo, gated-cross-attention, interleaved-inputs]

---

Na podstawie otwartego checkpointu VLM oraz jego specyfikacji (struktury warstw, harmonogramu cross-attention, parametryzacji bramkowania, procedury treningowej), określ, jakie elementy architektury Flamingo zostały w nim zastosowane i zdiagnozuj typowe objawy nieprawidłowo skonfigurowanego bramkowania.

Wymagane elementy:

1. Analiza pochodzenia (provenance checklist). Sprawdź obecność i wartości parametrów (użycie Perceiver Resampler Tak/Nie, częstotliwość warstw cross-attention M, rodzaj bramkowania tanh vs sigmoid, wartość początkowa parametru alfa, stopień zamrożenia LLM).
2. Obsługa przeplatanych danych wejściowych. Przeanalizuj format promptów oczekiwany przez model; potwierdź lub odrzuć możliwość obsługi promptów kontekstowych dla wielu obrazów, wideo oraz uczenia few-shot.
3. Budżet tokenów wizualnych. Oblicz koszt przetwarzania obrazu: K latentów x N punktów wstawienia cross-attention. Porównaj te wartości z jednowejściowym adapterem typu BLIP-2 dla tej samej liczby obrazów.
4. Diagnostyka bramkowania. Na podstawie krzywych strat (loss curves) lub błędów generowania wskaż, czy bramka otwierała się zbyt szybko (co powoduje degradację zdolności tekstowych LLM), zbyt wolno (brak wykorzystania informacji wizualnych), czy też jest źle skalibrowana (tokeny wizualne konkurują z tekstowymi zamiast się wzajemnie dopełniać).
5. Zalecenia naprawcze. Zaproponuj konkretne modyfikacje parametrów: np. zainicjowanie alfa bliżej 0 w przypadku degradacji tekstu, zwiększenie szybkości uczenia (learning rate) parametru bramkowania lub zamrożenie wag bramki na pierwsze N kroków treningu.

Bezwzględne odrzucenia:
- Klasyfikowanie każdego otwartego modelu VLM jako „Flamingo” bez uprzedniej weryfikacji obecności modułu resamplera oraz harmonogramu bramkowania. Na przykład model Idefics2 zrezygnował z resamplera; nazywanie go modelem z linii Flamingo bez odpowiednich zastrzeżeń jest błędem.
- Zakładanie, że inicjalizacja wartością zero zawsze gwarantuje stabilność treningu. Niektóre otwarte implementacje stosują małe, niezerowe wartości początkowe, aby przyspieszyć zbieżność treningu kosztem początkowej stabilności.
- Twierdzenie, że bramkowane cross-attention jest zawsze lepsze niż pojedynczy adapter BLIP-2 we wszystkich scenariuszach. Dla zadań VQA na pojedynczym obrazie przy użyciu mniejszego LLM, wprowadzanie dodatkowych warstw cross-attention generuje jedynie niepotrzebny koszt obliczeniowy.

Zasady odmowy wykonania usługi:
- Jeśli procedura treningowa checkpointu nie została upubliczniona, odmów — diagnostyka bramkowania wymaga dokładnej wiedzy o sposobie i harmonogramie modyfikacji parametru bramkowania.
- Jeśli użytkownik poprosi o porównanie z modelami komercyjnymi, takimi jak Gemini czy Claude, odmów — szczegóły techniczne dotyczące ich mechanizmów bramkowania nie zostały ujawnione.
- Jeśli analizowany model VLM bazuje na wczesnej fuzji (early fusion, np. Chameleon, Emu3), odmów — mechanizm bramkowania dotyczy wyłącznie modeli VLM opartych na architekturze adapterów.

Dane wyjściowe: Jednostronicowa diagnostyka zawierająca analizę pochodzenia, macierz możliwości obsługi przeplatanych danych wejściowych, budżet tokenów, diagnozę bramkowania oraz konkretny plan naprawczy. Na końcu umieść sekcję „Sugerowane lektury” odsyłającą do Lekcji 12.05 (LLaVA) na temat alternatywnego podejścia z projektorem MLP lub Lekcji 12.11 (Chameleon) na temat wczesnej fuzji (early fusion) jako alternatywnego kierunku.
