---

name: quantization-picker
description: Wybierz format kwantyzacji na rok 2026, biorąc pod uwagę sprzęt, silnik, obciążenie pracą i tolerancję jakości, a następnie przygotuj plan kalibracji i walidacji.
version: 1.0.0
phase: 17
lesson: 09
tags: [quantization, awq, gptq, gguf, fp8, nvfp4, calibration]

---

Na podstawie parametrów sprzętowych (CPU / H100 / H200 / B200 / GB200 wraz z ich liczbą), silnika (llama.cpp / vLLM / TRT-LLM / SGLang), modelu (rozmiar + typ zadania – np. zwykły czat, wnioskowanie logiczne, programowanie, środowiska multi-LoRA) oraz tolerancji na spadek jakości (dopuszczalny spadek o N punktów procentowych w testach HumanEval / MATH / MMLU), wybierz optymalny format kwantyzacji i opracuj plan walidacji.

Wygeneruj:

1. Rekomendacja formatu. Wybierz jeden z formatów: GGUF Q4_K_M, GGUF Q5_K_M, GPTQ-Int4 + Marlin, AWQ-Int4 + Marlin, FP8, NVFP4 + FP8 KV lub kombinację stosową. Decyzję uzasadnij ścieżką decyzyjną: CPU → GGUF; zadania logiczne (reasoning) → FP8; multi-LoRA na vLLM → GPTQ; typowy czat na GPU → AWQ; zweryfikowana architektura Blackwell → NVFP4.
2. Budżet pamięci. Przedstaw wyliczenia pamięci dla wag modelu + pamięci podręcznej KV (przy zadanej współbieżności × długość kontekstu) + aktywacji. Upewnij się, że model mieści się w pamięci docelowego GPU, lub określ wymagania dotyczące konfiguracji wielokartowej (multi-GPU).
3. Plan kalibracji. Określ źródło zbioru danych kalibracyjnych (dopasowane dziedzinowo dla metod AWQ/GPTQ; w ostateczności ogólne zbiory C4/WikiText). Liczba próbek (od 500 do 2000 próbek dziedzinowych). Zbiór walidacyjny (10% wydzielone z puli kalibracyjnej).
4. Plan walidacji. Dobierz zbiór testowy (eval set) odpowiadający charakterowi zadania: HumanEval dla kodu, MATH/MMLU dla wnioskowania logicznego, MT-Bench dla czatu. Porównaj wyniki linii bazowej w precyzji BF16 z modelem skwantowanym. Zezwól na wdrożenie produkcyjne tylko wtedy, gdy spadek jakości mieści się w zdefiniowanej tolerancji.
5. Decyzja dotycząca pamięci podręcznej KV. Pamięć KV należy traktować niezależnie od kwantyzacji wag. Dla wnioskowania logicznego rekomenduj format FP8 KV; wybierz BF16 KV, jeśli stabilność mechanizmu uwagi jest krytyczna; format INT8 KV dopuść do użycia wyłącznie po pełnej walidacji.
6. Strategia wycofania zmian (Rollback path). Przechowuj oryginalne wagi w formacie BF16/FP8 na dysku; przygotuj flagę konfiguracyjną umożliwiającą szybkie przywrócenie poprzedniej wersji w razie wykrycia degradacji modelu na produkcji.

Kategoryczne odrzucenia:
- Zalecanie wag NVFP4 w przypadku zadań wymagających zaawansowanego wnioskowania bez wcześniejszego przeprowadzenia walidacji na zbiorze testowym.
- Kalibracja modeli dziedzinowych na ogólnych tekstach z internetu. Zawsze stosuj dane z domeny docelowej.
- Ignorowanie zapotrzebowania na pamięć podręczną KV w budżecie HBM. Zawsze wyszczególniaj tę pozycję.
- Podawanie wskaźników przepustowości bez określenia wersji kerneli (np. wydajność Marlin-AWQ vs standardowe AWQ może różnić się 10-krotnie).

Zasady odmowy wdrożenia (odrzucenie rekomendacji):
- Jeśli obciążenie dotyczy obszarów o krytycznym znaczeniu dla jakości (np. generowanie twórcze, analiza rzadkich przypadków skrajnych w logice), odrzuć agresywne formaty INT4. Pozostań przy precyzji FP8 lub BF16.
- Jeśli silnikiem serwującym jest llama.cpp, odrzuć formaty inne niż GGUF. Format modelu musi być dostosowany do używanego silnika.
- Jeśli użytkownik nie ma możliwości przeprowadzenia ewaluacji na próbie składającej się z co najmniej 1000 zapytań, odrzuć wdrożenie. Nie wdrażaj kwantyzacji produkcyjnie bez weryfikacji.

Wynik: jednostronicowy dokument wyboru kwantyzacji zawierający: wybrany format, budżet HBM, plan kalibracji, plan walidacji, decyzję dotyczącą pamięci podręcznej KV oraz plan wycofania zmian. Zakończ sekcją „Co dalej mierzyć”, wskazującą na analizę różnic (delta) w wynikach zbiorów testowych, obciążenie pamięci KV przy szczytowej współbieżności lub przepustowość dla rzeczywistych rozmiarów wsadu (batch size) – w zależności od kluczowego ryzyka.
