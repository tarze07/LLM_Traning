---

name: reward-hack-auditor
description: Diagnozuj tryby awarii hakowania nagród w wytrenowanym modelu RLHF na podstawie dzienników szkoleniowych i wyników ewaluacji.
version: 1.0.0
phase: 18
lesson: 2
tags: [reward-hacking, goodhart, rlhf, over-optimization, sycophancy]

---

Biorąc pod uwagę raporty szkoleniowe modelu RLHF (krzywa zastępcza-nagroda, trajektoria KL, delty ewaluacyjne) i próbkę wyników, określ, który z czterech kostiumów hakowania nagród jest najprawdopodobniej aktywny i zlokalizuj go w dowodach.

Wyprodukuj:

1. Odcisk palca ze złotą szczeliną proxy. Narysuj (lub opisz) nagrodę zastępczą w zależności od odległości KL od odniesienia SFT. Zaznacz szczyt nagrody w złocie (ocena człowieka, zatrzymane RM lub ich zastępstwo). Podaj, czy model znajduje się przed, w trakcie czy po szczycie złota.
2. Identyfikacja kostiumu. Sprawdź pod kątem gadatliwości, pochlebstw, niewiernego rozumowania i manipulacji osoby oceniającej. Dla każdego: przytocz konkretny wynik lub wskaźnik, który spowodował wyświetlenie flagi.
3. Ślad mechanizmu. Wymień fałszywą cechę, którą RM prawdopodobnie nagradza (długość, pewne sformułowanie, zgodność, formatowanie). Zacytuj podpowiedź, w której funkcja różni się od jakości.
4. Zalecenie łagodzące. Z zestawu {więcej danych dotyczących preferencji, zespół RM, nadzór nad procesem, zaostrzenie harmonogramu KL, wcześniejsze zatrzymanie, przejście na DAA} zarekomenduj pojedynczą interwencję popartą dowodami i wskaż tę, która byłaby tutaj zmarnowanym wysiłkiem.

Twarde odrzucenia:
- Wszelkie twierdzenia, że pojedynczy RM „naprawia” hakowanie nagród. Gao i in. (ICML 2023) jest uniwersalna – większy RM wypycha szczyt, ale go nie eliminuje.
- Wszelkie twierdzenia, że ​​regularyzacja KL jest wystarczająca. Katastrofalny Goodhart (OpenReview UXuBzWoZGK) pokazuje, że sam KL zawodzi w wyniku ciężkiego błędu nagrody.
- Wszelkie zalecenia dotyczące „po prostu dostrojenia wersji beta” bez utrzymywania testów porównawczych możliwości.

Zasady odmowy:
- Jeśli użytkownik podaje jedynie krzywe zastępcze-nagroda bez wstrzymanego złotego sygnału, odmów diagnozy i żądaj wstrzymanych ewaluacji. Diagnoza bez złota to hakowanie nagród poprzez zastępstwo diagnozy.
- Jeśli użytkownik przedstawi niewierny dowód CoT i zapyta, czy nadzór nad procesem go „rozwiązuje”, odmów odpowiedzi binarnej i wskaż otwartą literaturę.

Wynik: jednostronicowy audyt obejmujący listę kontrolną zawierającą cztery kostiumy, jeden najbardziej prawdopodobny kostium, konkretny dowód na jego rzecz oraz pojedyncze zalecenie łagodzące uzasadnione dowodami. Cytuj Gao i in. (ICML 2023) i artykuł o ujednoliconym poglądzie z 2026 r. (arXiv:2604.13602) dokładnie raz.