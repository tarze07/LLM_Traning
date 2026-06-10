---

name: skill-fine-tuning-guide
description: Drzewo decyzyjne dotyczące tego, kiedy i jak dostroić LLM za pomocą LoRA i QLoRA
version: 1.0.0
phase: 11
lesson: 8
tags: [fine-tuning, lora, qlora, peft, llm-engineering]

---

# Przewodnik dotyczący decyzji dotyczących dostrajania

Przed dostrojeniem wypróbuj poniższe rozwiązania w podanej kolejności:

```
1. Prompt engineering (minutes, $0)
2. Few-shot examples in prompt (minutes, $0)
3. RAG for knowledge retrieval (days, $10-100/month)
4. Fine-tuning with LoRA/QLoRA (days, $5-50 per experiment)
5. Full fine-tuning (weeks, $100-10,000 per run)
```

Do kolejnego kroku należy przejść dopiero wtedy, gdy poprzedni okazał się mierzalnie niewystarczający.

## Kiedy dostroić

- Model wymaga spójnego stylu lub formatu wyjściowego, którego nie można uzyskać za pomocą podpowiedzi
- Destylujesz większy model (jakość GPT-4 z modelu 8B)
- Opóźnienie ma znaczenie, a przykłady kilku strzałów dodają zbyt wiele tokenów
- Potrzebujesz modelu, który będzie rzetelnie podążał za złożonym wzorcem rozumowania
- Masz ponad 1000 wysokiej jakości przykładów pożądanych zachowań wejścia-wyjścia

## Kiedy NIE należy dostrajać

- Model już robi to, co chcesz, wyświetlając odpowiedni monit
- Potrzebujesz modelu, aby znać fakty (zamiast tego użyj RAG)
- Masz mniej niż 500 przykładów treningowych (prawdopodobnie przetrenowania)
- Zadania często się zmieniają (przekwalifikowanie jest kosztowne)
- Musisz sprawdzić, które dane wpłynęły na konkretny wynik (dostrajanie to czarna skrzynka)

## Wybór metody

| Karta graficzna | Model 7B | Model 13B | model 70B |
|---------|----------|----------|-----------|
| 16 GB (T4) | QLoRA | Niewykonalne | Niewykonalne |
| 24 GB (3090/4090) | QLoRA lub LoRA | QLoRA | Niewykonalne |
| 40 GB (A100) | LoRA lub Pełna | QLoRA lub LoRA | QLoRA |
| 80 GB (A100/H100) | Pełny | LoRA lub Pełna | QLoRA lub LoRA |

## Lista kontrolna konfiguracji LoRA

1. Zacznij od r=16, alfa=32 (bezpieczne ustawienie domyślne dla większości zadań)
2. Najpierw wybierz q_proj i v_proj (minimalna realna LoRA)
3. Użyj szybkości uczenia się 2e-4 dla QLoRA, 5e-5 dla LoRA fp16
4. Ustaw lora_dropout=0.05
5. Trenuj przez 1-3 epoki (większe ryzyko przeuczenia)
6. Oceniaj każde 100 kroków w wyciągniętej serii
7. Zapisuj punkty kontrolne i wybieraj najlepsze poprzez utratę ewaluacji

## Typowe błędy

- Trening dla zbyt wielu epok (nadmierne dopasowanie po epoce 2-3 na małych zbiorach danych)
- Używanie tego samego tempa uczenia się, co w przypadku pełnego dostrajania (LoRA wymaga wyższego LR)
- Zapomnienie ustawienia tokena padu (powoduje straty NaN w modelach Lamy)
- Brak zamrażania modelu podstawowego (niszczy cel LoRA)
- Ocenianie tylko na danych treningowych (zawsze trzymaj 10-20% dla eval)
- Pomijanie linii bazowej szybkiej inżynierii (dopracowanie problemu, który już rozwiązuje monitowanie)

## Weryfikacja jakości

Po szkoleniu porównaj ponad 200 przykładów:
1. Model podstawowy z najlepszym podpowiedzią (linia bazowa)
2. Model podstawowy z adapterem LoRA (Twój model dostrojony)
3. GPT-4 lub Claude z tym samym monitem (sufit)

Jeśli model LoRA nie przekracza podanej linii bazowej, dane szkoleniowe lub konfiguracja wymagają pracy, a nie dodatkowych obliczeń.

## Zarządzanie adapterami

- Trzymaj adaptery oddzielnie do obsługi wielu zadań (zamień adaptery na żądanie)
- Połącz adaptery w obciążniki podstawowe w celu wdrożenia jednego zadania
- Przechowuj adaptery w Hugging Face Hub (10-100MB, łatwe wersjonowanie i udostępnianie)
— Przed wdrożeniem przetestuj, czy wyniki scalonego modelu odpowiadają niezłączonym wynikom
- Użyj TIES-Merging lub DARE, aby połączyć wiele adapterów w jeden

## Szkolenie dotyczące debugowania

Jeśli strata nie maleje:
1. Sprawdź szybkość uczenia się (zbyt niska dla LoRA, spróbuj 2e-4)
2. Sprawdź, czy warstwy LoRA rzeczywiście odbierają gradienty
3. Upewnij się, że obciążniki modelu podstawowego zostały zamrożone
4. Sprawdź formatowanie danych (tokenizer musi pasować do oczekiwanego formatu modelu)

Jeśli strata maleje, ale jakość oceny jest zła:
1. Problem z jakością danych treningowych (śmieci wchodzące, wyrzucane śmieci)
2. Overfitting (skróć epoki, zwiększ liczbę rezygnacji, dodaj więcej danych)
3. Złe moduły docelowe (dodaj warstwy MLP dla złożonych zadań)
4. Pozycja zbyt niska (spróbuj r=32 lub r=64)