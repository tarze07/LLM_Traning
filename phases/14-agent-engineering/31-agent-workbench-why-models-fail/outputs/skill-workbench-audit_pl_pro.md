---

name: workbench-audit
description: Przeprowadź inspekcję repozytorium pod kątem siedmiu płaszczyzn środowiska pracy agenta i zgłoś brakujące, częściowe lub w pełni funkcjonalne elementy przed rozpoczęciem jakiejkolwiek pracy przez agenta.
version: 1.0.0
phase: 14
lesson: 31
tags: [workbench, audit, reliability, agent-engineering]

---

Biorąc pod uwagę ścieżkę do repozytorium oraz zadanie agenta, który będzie w nim działał, przeprowadź audyt siedmiu płaszczyzn środowiska pracy i sporządź raport gotowości.

Siedem płaszczyzn:

1. Instrukcje: plik główny, który agent czyta jako pierwszy (np. `AGENTS.md`) – zwięzły, odsyłający do szczegółowych reguł.
2. Stan: trwały plik przeznaczony do odczytu maszynowego, w którym zapisywane są zadania, zmodyfikowane pliki, blokery oraz następna akcja.
3. Zakres: umowa dotycząca zadania zawierająca listę dozwolonych i zabronionych plików, kryteria akceptacji oraz plan wycofania zmian.
4. Sprzężenie zwrotne: moduł uruchamiający, który przechwytuje polecenie, stdout, stderr, kod wyjścia i przekazuje wynik z powrotem do pętli agenta.
5. Weryfikacja: bramka automatyczna uruchamiająca testy, lintowanie, kontrolę typów, testy dymne i potwierdzająca spełnienie kryteriów akceptacji.
6. Recenzja: weryfikacja przez drugą rolę – autor kodu nie może sam zatwierdzać swojej pracy.
7. Przekazanie: artefakt podsumowujący, co się zmieniło, dlaczego, co pozostało do zrobienia i jakie są sugerowane kolejne kroki.

Wygeneruj:

- Ocenę dla każdej płaszczyzny: 0 (brak), 1 (częściowa), 2 (prawidłowa). Powiąż każdą ocenę ze zidentyfikowanym plikiem lub procesem.
- Trzy priorytety uporządkowane według wpływu: dodanie której z brakujących płaszczyzn w pierwszej kolejności wyeliminuje najwięcej typów awarii.
- Raport w formacie `workbench_audit.json` do odczytu maszynowego oraz podsumowanie w formacie `workbench_audit.md` w formie czytelnej dla człowieka.
- Łatkę startową dla najsłabszej płaszczyzny: najmniejszą zmianę w pliku, która pozwala podnieść ocenę z 0 do 1.

Bezwarunkowe odrzucenia:

- Oceny "prawidłowa" (2) bez podania ścieżki do pliku lub opisu procesu. Audyty pozbawione dowodów stają się bezużyteczne.
- Traktowanie konfiguracji agenta jako pojedynczej, połączonej płaszczyzny. Łączenie płaszczyzn ukrywa rzeczywiste przyczyny awarii podczas wykonywania zadania.
- Pomijanie weryfikacji ze względu na powolne testy. Jeśli weryfikacja nie odbywa się w ramach środowiska pracy, twórcy sami oceniają swoją pracę.

Zasady odmowy:

- Jeśli w repozytorium nie ma żadnego polecenia testowego, odrzuć ocenę weryfikacji i wskaż ją jako błąd blokujący.
- Jeśli repozytorium nie ma historii kontroli wersji, odrzuć ocenę przekazania i wskaż ją jako błąd blokujący.
- Jeśli agent działa z uprawnieniami roota lub ma nieograniczony dostęp do plików, odrzuć ocenę zakresu do momentu zdefiniowania piaskownicy lub białej listy zapisów.

Struktura wyjściowa:

```
workbench-audit/
├── workbench_audit.json
├── workbench_audit.md
├── patches/
│   └── <weakest-surface>.patch
└── README.md
```

Zakończ sekcją „Polecana lektura”, wskazując:

- Lekcję 32 dotyczącą minimalnego układu repozytorium.
- Lekcję 33 omawiającą szczegółowe instrukcje.
- Lekcję 38 opisującą bramkę weryfikacyjną.
