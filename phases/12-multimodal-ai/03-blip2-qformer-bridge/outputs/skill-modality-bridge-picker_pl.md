---

name: modality-bridge-picker
description: Poleć Q-Former vs projektor MLP vs resampler Perceiver dla konfiguracji VLM, biorąc pod uwagę budżet tokenów, docelową jakość i obliczenia szkoleniowe.
version: 1.0.0
phase: 12
lesson: 03
tags: [blip2, qformer, vlm, modality-bridge, architecture]

---

Biorąc pod uwagę liczbę tokenów kodera wizyjnego na obraz, budżet kontekstowy LLM, docelową liczbę obrazów na monit i budżet obliczeniowy szkolenia, zarekomenduj, którego mostu modalnego użyć i uzasadnij liczbą parametrów i ekonomią tokenów.

Wyprodukuj:

1. Audyt budżetu tokenowego. Zgłaszaj surowe tokeny na obraz z kodera wizyjnego, tokeny na obraz po każdej opcji mostu oraz część kontekstu LLM zużytego przy zadeklarowanej liczbie obrazów na monit.
2. Porównanie mostów. Dla każdego z Q-Former (32 tokeny, ~188M parametrów), projektora MLP (wszystkie poprawki, ~20M parametrów) i narzędzia do resamplingu Perceiver (K ​​zapytań do nauczenia się za pośrednictwem N-warstwowej uwagi krzyżowej, zmienne), podaj parametry, proxy jakości i pole do popisu kosztów szkolenia.
3. Zalecenie. Pojedynczy najlepszy wybór dla określonych ograniczeń, z uzasadnieniem w jednym wierszu. Oznacz, gdy ograniczenia są sprzeczne (wysoka jakość + napięty budżet tokenów + niskie obliczenia szkoleniowe).
4. Dwuetapowy ślad treningowy. Jeśli wybrano Q-Former, opisz straty ITC + ITM + ITG dla etapu 1 i utratę LM dla etapu 2. Dla każdego z nich nazwij reprezentatywny zbiór danych (COCO, LAION, Visual Genome).
5. Lista kontrolna ablacji. Pięć eksperymentów, które wywołujący powinien przeprowadzić przed zablokowaniem mostu (liczba zapytań, dwuetapowe i jednoetapowe, głębokość projektora, harmonogram zamrożenia, dostrojenie podzbioru).

Twarde odrzucenia:
- Wszelkie zalecenia ignorujące budżet tokena. „Użyj MLP” z 576 tokenami na obraz kończy się niepowodzeniem przy 10 obrazach w kontekście 4K.
- Twierdzenie, że Q-Former ściśle dominuje w MLP. W przypadku zadań wysokiej jakości obejmujących jeden obraz i nieograniczonym kontekstem wygrywa MLP.
- Traktowanie resamplera Perceiver jako odpowiednika Q-Former. Flamingo stosuje to na każdej warstwie LLM; BLIP-2 stosuje go raz.

Zasady odmowy:
- Jeśli rozmówca poprosi o mostek obsługujący wideo, nie określając, ile klatek i z jaką szybkością klatek, odmów — mosty wideo różnią się od mostów obsługujących pojedynczy obraz specyfikacją, a nie tylko skalą.
- Jeśli LLM w zakresie jest szkolony od podstaw za pomocą wieży wizyjnej (wczesna fuzja, w stylu kameleona), odrzuć — Lekcja 12.11 omawia ten przypadek osobno.
- Jeśli nie podano kosztów szkolenia, odmów i zapytaj, czy rozmówcę stać na drugi etap BLIP-2 (~kilkaset godzin A100), czy tylko na szkolenie z użyciem projektora.

Dane wyjściowe: jednostronicowe zalecenie dotyczące mostu zawierające matematykę tokenów, liczbę parametrów, zalecaną architekturę, zarys szkolenia i listę kontrolną ablacji. Zakończ akapitem „co przeczytać dalej” wskazującym na lekcję 12.04 (Flamingo) dotyczącą przechodzenia między uwagami w każdym miejscu, lekcję 12.05 (LLaVA) dotyczącą wyłącznie MLP lub lekcję 12.07 (ablacje) dotyczącą kompromisu między danymi a architekturą.