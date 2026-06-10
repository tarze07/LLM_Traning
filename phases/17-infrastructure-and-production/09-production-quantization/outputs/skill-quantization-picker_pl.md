---

name: quantization-picker
description: Wybierz format kwantyzacji na rok 2026, biorąc pod uwagę sprzęt, silnik, obciążenie pracą i tolerancję jakości, a następnie przygotuj plan kalibracji i walidacji.
version: 1.0.0
phase: 17
lesson: 09
tags: [quantization, awq, gptq, gguf, fp8, nvfp4, calibration]

---

Biorąc pod uwagę sprzęt (CPU / H100 / H200 / B200 / GB200, z liczbą), silnik (llama.cpp / vLLM / TRT-LLM / SGLang), model (rozmiar + typ zadania — rutynowy czat / rozumowanie / kod / multi-LoRA) i tolerancję jakości (może pochłonąć spadek punktu N w HumanEval / MATH / MMLU), wybierz format kwantyzacji i przygotuj plan walidacji.

Wyprodukuj:

1. Zalecenia dotyczące formatu. Jeden z: GGUF Q4_K_M, GGUF Q5_K_M, GPTQ-Int4 + Marlin, AWQ-Int4 + Marlin, FP8, NVFP4 + FP8 KV lub kombinacja stosowa. Uzasadnij drzewem decyzyjnym: CPU → GGUF; rozumowanie → 8PR; multi-LoRA na vLLM → GPTQ; rutynowy czat GPU → AWQ; Zatwierdzone przez Blackwell → NVFP4.
2. Budżet pamięci. Wagi raportów + pamięć podręczna KV (przy zgłaszanej współbieżności × kontekst) + aktywacje. Upewnij się, że pasuje do docelowego procesora graficznego lub podaj wymagania dotyczące wielu procesorów graficznych.
3. Plan kalibracji. Źródło zbioru danych (dopasowane do domeny dla AWQ/GPTQ; w ostateczności ogólny C4/WikiText). Liczba próbek (500-2000 dla domeny). Zestaw walidacyjny (10% pobrane z puli kalibracyjnej).
4. Plan walidacji. Zestaw eval dopasowany do zadania: HumanEval dla kodu, MATH/MMLU dla rozumowania, MT-Bench dla chatu. Linia bazowa BF16 vs. skwantowana. Wysyłka w przypadku spadku ≤ tolerancji jakości.
5. Decyzja o pamięci podręcznej KV. Oddzielone od kwantyzacji wagi. Polecaj KV 8PR do uzasadnienia; BF16 KV, jeśli dokładność uwagi jest marginalna; INT8 KV dopiero po walidacji.
6. Ścieżka wycofania. Przechowuj odważniki BF16/FP8 na dysku; flagę, aby przełączyć się z powrotem w przypadku pogorszenia jakości produkcji.

Twarde odrzucenia:
- Zalecanie wag NVFP4 w przypadku obciążeń wymagających dużego wnioskowania bez sprawdzania poprawności zestawu ewaluacyjnego.
- Kalibracja na ogólnych danych internetowych dla modeli domen. Zawsze używaj w domenie.
- Zapomnienie o pamięci podręcznej KV w budżecie HBM. Zawsze wyszczególniaj.
- Podawanie liczb przepustowości bez nazywania jąder (Marlin-AWQ w porównaniu ze zwykłym AWQ wynosi 10x).

Zasady odmowy:
- Jeśli obciążenie pracą jest z natury marginalne pod względem jakości (otwarte generowanie kreatywności, rozumowanie na podstawie przypadków skrajnych), odrzuć agresywne INT4. Pozostań FP8 lub BF16.
- Jeśli silnikiem jest llama.cpp, odrzuć format inny niż GGUF. Dopasowany format do silnika to stawki stołowe.
- Jeśli użytkownik nie może przeprowadzić oceny 1000 próbek, odmów. Brak ślepej kwantyzacji w produkcji.

Wynik: jednostronicowy wybór kwantyzacji zawierający listę wybranego formatu, budżetu HBM, planu kalibracji, planu walidacji, decyzji o pamięci podręcznej KV i ścieżki wycofania. Zakończ akapitem „Co dalej mierzyć” wymieniając jedną z wartości delta zestawu eval, ciśnienie pamięci podręcznej KV przy szczytowej współbieżności lub przepustowość przy rzeczywistym rozmiarze partii w zależności od kluczowego ryzyka.