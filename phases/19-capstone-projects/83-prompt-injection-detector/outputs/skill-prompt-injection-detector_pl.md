---

name: skill-prompt-injection-detector
description: Warstwowy potok detektorów, który zwraca kategorię i pewność dla każdego monitu, z mierzalną precyzją i zapamiętywaniem
version: 1.0.0
phase: 19
lesson: 83
tags: [safety, detector, prompt-injection]

---

# Szybki wykrywacz wtrysku

Detektor jest tu funkcją od podpowiedzi do werdyktu. Werdykt niesie ze sobą kategorię z taksonomii z lekcji 82 i pewność w [0, 1].

## Rurociąg

1. Normalizuj - usuń znaki o zerowej szerokości, cofnij homoglify, zdekoduj base64/hex, złóż cyfry w trybie let-speak, spróbuj rot13 z sprawdzeniem poprawności popularnych słów.
2. Zasady podciągów - igły pisane ręcznie, takie jak `ignore previous`, `from now on you are`, `decode this base64`.
3. Reguły Regex – wzorce na poziomie tokena, takie jak `\bignor\w*\s+(all|prior|previous|earlier)\b`.

Agregacja zachowuje maksymalny wynik w każdej kategorii i zwraca kategorię z największym wynikiem lub `benign`, jeśli nic się nie uruchomi.

## Dodawanie reguły

Edytuj `code/rules.py`. Reguła to słownik z `name`, `category` (jedna z sześciu kategorii taksonomii), `score` (zmiennoprzecinkowa od 0 do 1) i jedną z `substring` lub `regex`. Uruchom ponownie `main.py`, aby zobaczyć wpływ na precyzję i zapamiętywanie poszczególnych kategorii.

## Artefakt

`outputs/detector_report.json` to plik metryk dla poszczególnych kategorii. Bramka od końca do końca w lekcji 87 odczytuje ją do progu pewności.