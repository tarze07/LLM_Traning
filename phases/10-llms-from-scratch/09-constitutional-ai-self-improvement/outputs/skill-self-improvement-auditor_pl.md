---

name: self-improvement-auditor
description: Przeprowadź audyt proponowanego procesu samodoskonalenia lub konstytucyjnego rurociągu sztucznej inteligencji, zanim zacznie on działać na dużą skalę.
version: 1.0.0
phase: 10
lesson: 9
tags: [alignment, cai, grpo, rlhf, self-improvement, reward-hacking]

---

Biorąc pod uwagę proponowany proces szkoleniowy, który zakłada wykorzystanie konstytucyjnej sztucznej inteligencji, RLAIF, GRPO lub dowolnej formy samodzielnie wygenerowanych danych dotyczących preferencji, przeprowadź audyt obejmujący:

1. Zasada nagrody. Podaj dokładny weryfikator (regex, sympy, zestaw testów, sędzia LLM). Klasyfikuj jako deterministyczne, stochastyczne-LLM lub hybrydowe. Odrzuć każdą pętlę „samodoskonalenia”, która nie ma zewnętrznego uziemienia — model nie może pobierać sygnału znikąd.
2. Statystyki grupowe. W przypadku potoków GRPO potwierdź wielkość grupy, sposób obliczania korzyści (wynik Z vs ranga względna) i co się stanie, gdy standardowe wynagrodzenie grupy spadnie do zera. Rurociąg musi pomijać lub zmniejszać grupy o zerowej wariancji, a nie dzielić przez epsilon i udawać, że sygnał jest prawdziwy.
3. Budżet KL. Liczbowy limit skumulowanego KL(polityka || odwołanie) w trakcie przebiegu. Rurociąg musi się zatrzymać, zresetować lub przełączyć na cieplejsze źródło odniesienia po uderzeniu w korek. Nieograniczony KL to nieograniczony dryf.
4. Podłoga różnorodności. Zmierzona dolna granica standardu nagrody dla grupy, wariancji długości odpowiedzi lub entropii w n-gramach, w zależności od tego, co dopuszcza zadanie. Jeśli podłoga zostanie przekroczona przez N kolejnych rund, rurociąg musi zawierać świeże dane ludzkie lub szerszą, szybką dystrybucję.
5. Limit danych ludzkich. Minimalna część miksu szkoleniowego, która musi pozostać autorstwa człowieka, zazwyczaj 5–10%. Rurociągi przeznaczone wyłącznie do samodestylacji zapadają się po 3-5 rundach. Nazwij to wyraźnie.
6. Watchdog powodujący załamanie trybu. Automatyczne sprawdzanie flagi: standard nagrody w rundach, unikalna liczba n-gramów w przypadku wstrzymanych podpowiedzi, rozkład długości, współczynnik odmów. Każde z tych przekroczeń progu powoduje zatrzymanie treningu.
7. Dryf konstytucyjny. W przypadku potoków CAI wymagaj wersjonowanego pliku konstytucji, dziennika zmian i „zestawu testów regresji konstytucyjnej” — podpowiedzi, których oczekiwane zachowanie nie może zmieniać się podczas edycji.

Odmówić zatwierdzenia rurociągów, które:
- twierdzenie „zero danych ludzkich” bez zewnętrznego weryfikatora (reguły, narzędzia, środowiska).
- używaj PRM bez sondy hakerskiej z nagrodą za proces (czy model zapisuje kroki, które wyglądają dobrze, bez zaawansowanego dowodu?).
- przeprowadzić więcej niż 5 rund dostrajania próby odrzucenia bez ustalonego punktu odniesienia dotyczącego różnorodności.
- udostępnij model referencyjny w polisie (brak referencji oznacza brak KL, oznacza brak kotwicy).
- ocena u sędziego LLM według tego samego modelu, co polityka (zanieczyszczenie sędziego).

Wynik: jednostronicowy audyt z informacją o pozytywnym/negatywnym wyniku dla każdej bramki, zmierzoną lub ustaloną wartością oraz dokładnym krokiem w potoku, który generuje każdy sygnał. Jeśli którakolwiek bramka zawiedzie, wypisz minimalną realną zmianę, która sprawi, że przejdzie.