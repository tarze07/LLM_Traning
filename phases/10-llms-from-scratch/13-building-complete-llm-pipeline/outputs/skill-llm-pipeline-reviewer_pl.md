---

name: llm-pipeline-reviewer
description: Przejrzyj kompleksowy manifest programu szkolenia LLM przed wielomilionowym uruchomieniem.
version: 1.0.0
phase: 10
lesson: 13
tags: [pipeline, training, manifest, eval-gate, cost, rollback]

---

Biorąc pod uwagę proponowany manifest potoku szkolenia (YAML lub JSON opisujący tokenizator, dane, szkolenie wstępne, SFT, wyrównanie, ocenę, kwantyzację i etapy udostępniania), przygotuj przegląd obejmujący:

1. Wykres etapowy. Upewnij się, że każdy etap ma wpisane wejścia i wyjścia. Wywołaj brakujące zależności, stan niejawny lub dowolny etap, który zużywa sam katalog zamiast nazwanego skrótu artefaktu.
2. Łańcuch mieszający. Sprawdź, czy Output_hash etapu N jest równy jednemu z input_hash każdego dalszego etapu. Jakakolwiek niezgodność oznacza, że ​​manifest jest niespójny i potok nie może zostać uruchomiony.
3. Bramka ewaluacyjna. Każda metryka na liście bramek musi być liczbowa, mieć operator, próg i źródło pomiaru. Odrzuć każdą bramkę, która jest subiektywna („wygląda dobrze”), nieograniczona (bez progu) lub zmierzona na podstawie danych treningowych.
4. Strażnik regresji. Podstawowe testy porównawcze nowego modelu (MMLU, MATH, HumanEval+, GPQA lub odpowiednik specyficzny dla domeny) muszą mieć dołączone liczby bazowe. Przebieg bez linii bazowych to przebieg bez wykrycia regresji.
5. Budżet KL. Etapy dostosowania (RLHF, DPO, CAI, GRPO) muszą zadeklarować skumulowany limit KL w stosunku do odniesienia. Nieograniczony KL to dryf nieograniczony.
6. Kontrola zanieczyszczenia. Fragmenty danych szkoleniowych i zestawy ewaluacyjne muszą mieć udokumentowaną kontrolę nakładania się (dokładne dopasowanie lub 13 gramów). Wymagany próg przejścia: budżet <0.1%.
7. Cost estimate. Pre-run estimate for each stage plus a total, compared against the budget gate. If estimate >, potok odmawia uruchomienia.
8. Plan wycofania. Dla każdego etapu nazwane działania w przypadku niepowodzenia: ponowne uruchomienie, powrót do poprzedniego artefaktu, sprawdzenie danych wejściowych i ponowne uruchomienie w dół. Drogie etapy (przedtreningowe) muszą mieć strategię ciepłego punktu kontrolnego.
9. Sklep z artefaktami. Punkty kontrolne, zbiory danych, tokenizatory, raporty ewaluacyjne muszą być adresowane pod względem treści (SHA-256). Artefakty związane z nazwą pliku („latest.pt”) są zdecydowanie odrzucane.
10. Obserwowalność. Każdy etap musi emitować dzienniki strukturalne z identyfikatorem śledzenia, nazwą etapu, skrótem wejściowym, skrótem wyjściowym, zegarem ściennym i kosztem. Brakujące identyfikatory śledzenia oznaczają, że przebiegu nie można debugować po fakcie.

Sygnały ostrzegawcze wstrzymujące recenzję:
- w bramce brakuje źródła pomiaru (bramka na metryce bez obliczeń etapowych)
- etap dzielący punkt kontrolny z etapem późniejszym (bez rozdzielania obaw)
- etap osiowania bez modelu referencyjnego (bez kotwy dla KL)
- ocena LLM jako sędzia, w której sędzią jest ta sama rodzina modelowa co polisa (zanieczyszczenie)
- kosztorys przekraczający budżet o ponad 20%
- plan wycofania składający się wyłącznie z „ponownego uruchomienia od zera”

Wynik: dwustronicowa recenzja z PASS/HOLD na każdą bramkę, dokładne pole manifestu lub brakujące pole, które wygenerowało każdy werdykt, oraz minimalna zmiana wymagana do zamiany HOLD na PASS.