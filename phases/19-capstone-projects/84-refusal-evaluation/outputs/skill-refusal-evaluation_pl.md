---

name: skill-refusal-evaluation
description: Dwustronne wskaźniki odmów z kalibracją i podziałem na kategorie w oznaczonym korpusie podpowiedzi
version: 1.0.0
phase: 19
lesson: 84
tags: [safety, evaluation, calibration]

---

# Ocena odmowy

Oznaczony zbiór bezpiecznych i niebezpiecznych podpowiedzi przechodzi przez jedną lub więcej zasad modelu. Wyniki są klasyfikowane jako odmowy lub odpowiedzi. Framework zwraca:

- niedostateczna odmowa: odpowiedzi na pytania oznaczone jako niebezpieczne / całkowicie niebezpieczne
- nadmierna odmowa: odrzucone podpowiedzi oznaczone jako bezpieczne/całkowicie bezpieczne
- trafność: (poprawne odmowy + prawidłowe odpowiedzi) / suma
- ECE: oczekiwany błąd kalibracji podzielony na podaną pewność
- Niedostateczna odmowa w poszczególnych kategoriach: połączona z taksonomią z lekcji 82

## Podłączanie prawdziwego modelu

Próbny LLM to wywoływalny `(prompt: str) -> str`. Zastąp go opakowaniem HTTP, które zwraca dane wyjściowe modelu i osadza znacznik zaufania (lub zmodyfikuj `parse_confidence`, aby odczytać wszystko, co ujawni Twój dostawca). Wszystko inne pozostaje takie samo.

## Artefakt

`outputs/refusal_eval_report.json` zawiera metryki poszczególnych zasad. Lekcja 87 czyta ten raport, aby ustawić progi.