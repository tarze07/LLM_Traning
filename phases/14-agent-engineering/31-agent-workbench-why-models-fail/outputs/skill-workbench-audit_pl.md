---

name: workbench-audit
description: Przeprowadź inspekcję repozytorium dla siedmiu powierzchni stołu roboczego agenta i zgłoś brakujące, częściowe lub sprawne elementy przed rozpoczęciem jakiejkolwiek pracy agenta.
version: 1.0.0
phase: 14
lesson: 31
tags: [workbench, audit, reliability, agent-engineering]

---

Biorąc pod uwagę ścieżkę do repozytorium i produkt agenta, który będzie w nim działał, przeprowadź audyt siedmiu powierzchni stołu roboczego i sporządź raport gotowości.

Siedem powierzchni:

1. Instrukcje: plik główny, który agent czyta jako pierwszy (np. `AGENTS.md`), krótki, prowadzący do głębszych reguł.
2. Stan: trwały plik do odczytu maszynowego, w którym zapisywane są zadania, dotknięte pliki, blokery i następna akcja.
3. Zakres: umowa dotycząca zadania zawierająca listę dozwolonych i zabronionych plików, kryteria akceptacji, plan wycofania.
4. Sprzężenie zwrotne: moduł uruchamiający, który przechwytuje polecenie, stdout, stderr, kod wyjścia i przekazuje wynik z powrotem do pętli.
5. Weryfikacja: bramka, która przeprowadza testy, lintowanie, kontrolę typu, przebieg dymu i potwierdza kryteria akceptacji.
6. Recenzja: druga przepustka z inną rolą, budowniczy nie może oznaczać własnej pracy.
7. Przekazanie: artefakt podsumowujący, co się zmieniło, dlaczego, co pozostało i jakie jest następne najlepsze działanie.

Wyprodukuj:

- Wynik na powierzchnię: 0 braków, 1 częściowy, 2 zdrowe. Powiąż każdy wynik z plikiem lub procesem, który zaobserwowałeś.
- Trzy priorytety uporządkowane według dźwigni: która brakująca powierzchnia, jeśli zostanie dodana jako pierwsza, usuwa najwięcej trybów awarii.
- Raport w formacie `workbench_audit.json` do odczytu maszynowego oraz podsumowanie w formacie `workbench_audit.md` w formie czytelnej dla człowieka.
- Łatka startowa dla najsłabszej powierzchni: najmniejsza zmiana pliku, która przesuwa wynik z 0 na 1.

Twarde odrzucenia:

- Wyniki „zdrowe” bez ścieżki pliku lub odniesienia do procesu. Audyty bez dowodów gniją.
- Pojedyncza połączona powierzchnia „konfiguracji agenta”. Łączenie powierzchni ukrywa, która z nich się nie powiodła, gdy zadanie się nie powiedzie.
- Pomijanie weryfikacji, ponieważ testy są powolne. Jeśli weryfikacja nie odbywa się na stole warsztatowym, budowniczowie zaznaczają własną pracę domową.

Zasady odmowy:

- Jeśli w repozytorium w ogóle nie ma polecenia testowego, odrzuć wynik weryfikacji i wykaż go jako wynik blokujący.
- Jeśli repozytorium nie ma historii kontroli wersji, odrzuć wynik przekazania i wykaż go jako wynik blokujący.
- Jeśli produkt agenta działa jako root lub z nieograniczonym dostępem do plików, odrzuć ocenę zakresu do czasu zdefiniowania piaskownicy lub listy zapisu.

Struktura wyjściowa:

```
workbench-audit/
├── workbench_audit.json
├── workbench_audit.md
├── patches/
│   └── <weakest-surface>.patch
└── README.md
```

Zakończ słowami „co przeczytać dalej”, wskazując:

- Lekcja 32 dotycząca minimalnego układu repo.
- Lekcja 33, aby poznać szczegółowe instrukcje.
- Lekcja 38 dla bramki weryfikacyjnej.