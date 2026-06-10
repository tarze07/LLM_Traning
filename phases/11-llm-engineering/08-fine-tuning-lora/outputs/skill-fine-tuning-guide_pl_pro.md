---

name: skill-fine-tuning-guide
description: Drzewo decyzyjne określające, kiedy i jak przeprowadzić dostrajanie (fine-tuning) LLM przy użyciu metod LoRA i QLoRA.
version: 1.0.0
phase: 11
lesson: 8
tags: [fine-tuning, lora, qlora, peft, llm-engineering]

---

# Strategia wyboru metod optymalizacji modeli

Przed przystąpieniem do dostrajania (fine-tuning) sprawdź alternatywne rozwiązania w podanej kolejności:

```
1. Inżynieria promptów (minuty, $0)
2. Przykłady few-shot w prompcie (minuty, $0)
3. Potok RAG do wyszukiwania wiedzy (dni, $10-100/miesiąc)
4. Dostrajanie LoRA/QLoRA (dni, $5-50 za eksperyment)
5. Pełne dostrajanie (tygodnie, $100-10 000 za uruchomienie)
```

Do kolejnego kroku przechodź tylko wtedy, gdy poprzedni okazał się mierzalnie niewystarczający dla osiągnięcia celu.

## Kiedy dostrajać model

- Model musi zachować bardzo spójny styl wypowiedzi lub sztywny format wyjściowy (np. JSON), którego nie da się uzyskać instrukcjami w prompcie.
- Wdrażasz destylację wiedzy z dużego modelu do małego (np. przeniesienie jakości GPT-4 na poziom lokalnego modelu 8B).
- Opóźnienia (latency) są krytyczne, a przykłady few-shot zajmują zbyt wiele cennych tokenów w oknie kontekstowym.
- Model musi stabilnie i bezbłędnie realizować skomplikowany, wieloetapowy proces wnioskowania.
- Dysponujesz zbiorem ponad 1000 wysokiej jakości przykładów par wejście-wyjście.

## Kiedy NIE dostrajać modelu

- Model poprawnie realizuje zadanie przy użyciu odpowiednio sformułowanego promptu.
- Model musi posiadać aktualną wiedzę o faktach (w tym celu wdróż potok RAG).
- Dysponujesz zbiorem mniejszym niż 500 przykładów (ryzyko przeuczenia / overfittingu).
- Specyfika zadania lub dane źródłowe często się zmieniają (proces ponownego treningu i wdrożenia jest kosztowny).
- Wymagana jest pełna wyjaśnialność decyzji (dostrojony model to struktura czarnej skrzynki).

## Wybór metody w zależności od VRAM

| Wolna pamięć GPU (VRAM) | Model 7B/8B | Model 13B | Model 70B |
|---------|----------|----------|-----------|
| 16 GB (np. Tesla T4) | QLoRA | Niewykonalne | Niewykonalne |
| 24 GB (np. RTX 3090/4090) | QLoRA lub LoRA | QLoRA | Niewykonalne |
| 40 GB (np. A100 40GB) | LoRA lub Pełne SFT | QLoRA lub LoRA | QLoRA |
| 80 GB (np. A100/H100 80GB) | Pełne SFT | LoRA lub Pełne SFT | QLoRA lub LoRA |

## Lista kontrolna konfiguracji LoRA

1. Rozpocznij eksperyment od bezpiecznych wartości domyślnych: `r = 16`, `alpha = 32`.
2. Jako pierwsze moduły docelowe wybierz `q_proj` i `v_proj` (wariant minimalny).
3. Zastosuj współczynnik uczenia (learning rate): `2e-4` dla QLoRA, `5e-5` dla LoRA w precyzji FP16.
4. Ustaw wartość dropoutu `lora_dropout = 0.05`.
5. Trenuj model w zakresie 1–3 epok (dłuższy trening grozi przeuczeniem).
6. Wykonuj ewaluację kontrolną co 100 kroków (steps) na wyodrębnionym zbiorze walidacyjnym (eval set).
7. Zapisuj punkty kontrolne (checkpoints) i wybierz ten, który uzyskał najniższą wartość straty walidacyjnej (validation loss).

## Typowe błędy

- Trenowanie przez zbyt wiele epok (overfitting następuje zazwyczaj po 2–3 epokach przy małych zbiorach danych).
- Stosowanie zbyt niskiego współczynnika uczenia, typowego dla pełnego SFT (LoRA wymaga wyższych wartości LR).
- Pomijanie konfiguracji tokenu dopełnienia (`pad token`), co wywołuje błędy typu `NaN loss` (szczególnie w modelach z rodziny Llama).
- Brak zamrożenia wag modelu bazowego (niweczy to cały sens stosowania techniki LoRA).
- Przeprowadzanie ewaluacji wyłącznie na zbiorze treningowym (zawsze wydziel 10–20% danych na zbiór walidacyjny).
- Pominięcie etapu inżynierii promptów (dostrajanie modelu do rozwiązania problemu, który można załatwić modyfikacją instrukcji).

## Ewaluacja i weryfikacja jakości

Po zakończeniu treningu porównaj odpowiedzi dla min. 200 przykładów testowych:
1. Model bazowy z optymalnym promptem (punkt odniesienia / baseline).
2. Model bazowy z załadowanym adapterem LoRA (dostrojony model).
3. Model komercyjny (np. GPT-4 lub Claude) z tym samym promptem (górna granica możliwości / ceiling).

Jeśli model LoRA nie osiąga mierzalnie lepszych wyników niż punkt odniesienia (baseline), oznacza to błędy w zbiorze danych lub błędną konfigurację hiperparametrów – dalsze wydłużanie treningu nie rozwiąże tego problemu.

## Zarządzanie adapterami

- Przechowuj adaptery jako osobne pliki (10–100 MB) w celu dynamicznego serwowania wielu zadań z jednego modelu bazowego.
- Scal adapter z wagami bazowymi (hard merge) na potrzeby wdrożenia do jednego, dedykowanego zadania.
- Przechowuj pliki adapterów w Hugging Face Hub (łatwe wersjonowanie i współdzielenie).
- Przed wdrożeniem produkcyjnym upewnij się, czy odpowiedzi po scaleniu wag są identyczne z odpowiedziami modelu przed scaleniem.
- Wykorzystaj techniki TIES-Merging lub DARE w przypadku fuzji kilku adapterów w jeden model.

## Debugowanie procesu szkolenia

**Jeśli strata (loss) nie maleje:**
1. Sprawdź współczynnik uczenia (learning rate) – prawdopodobnie jest zbyt niski (dla LoRA zalecane ok. `2e-4`).
2. Upewnij się, czy warstwy LoRA poprawnie otrzymują gradienty i czy parametr `requires_grad = True` dla wag A i B.
3. Zweryfikuj, czy wagi modelu bazowego zostały poprawnie zamrożone.
4. Sprawdź poprawność formatowania danych (szablon promptu i tokenizer muszą być w pełni zgodne z modelem bazowym).

**Jeśli strata maleje, ale jakość odpowiedzi w ewaluacji jest niska:**
1. Niska jakość danych szkoleniowych (zasada garbage in, garbage out).
2. Przeuczenie modelu (overfitting) – skróć czas treningu, zwiększ wartość `lora_dropout` lub dodaj więcej zróżnicowanych danych.
3. Błędnie dobrane moduły docelowe – dodaj warstwy MLP dla zadań wymagających złożonej logiki.
4. Zbyt niska ranga adaptera – przetestuj wartości `r = 32` lub `r = 64`.
