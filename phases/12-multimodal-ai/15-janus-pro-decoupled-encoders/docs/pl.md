# Janus-Pro: Oddzielone enkodery dla ujednoliconych modeli multimodalnych

> Zunifikowane modele multimodalne charakteryzują się nieuniknionym napięciem. Zrozumienie wymaga cech semantycznych — wektorów wyjściowych SigLIP lub DINOv2 bogatych w informacje na poziomie koncepcji. Pokolenie chce kodów przyjaznych dla rekonstrukcji — tokenów VQ, które składają się z powrotem w wyraźne piksele. Te dwa cele nie są kompatybilne w jednym koderze. Janus (DeepSeek, październik 2024 r.) i Janus-Pro (DeepSeek, styczeń 2025 r.) twierdzą, że rozwiązaniem jest zaprzestanie prób: oddzielenie dwóch koderów. Dziel się korpusem transformatora między zadaniami, ale kieruj się zrozumieniem poprzez SigLIP i generowaniem poprzez tokenizer VQ. Na poziomie 7B Janus-Pro pokonuje DALL-E 3 na GenEval, dopasowując się do LLaVA na MMMU. W tej lekcji dowiesz się, dlaczego dwa kodery działają tam, gdzie jeden zawodzi.

**Typ:** Kompilacja
**Języki:** Python (stdlib, routing z dwoma enkoderami + sygnał współdzielony)
**Wymagania wstępne:** Faza 12 · 13 (Transfuzja), Faza 12 · 14 (Pokaz)
**Czas:** ~120 minut

## Cele nauczania

- Wyjaśnij, dlaczego pojedynczy współdzielony koder pogarsza jakość zrozumienia lub generowania.
- Opisz routing Janus-Pro: funkcje SigLIP po stronie wejściowej w celu zrozumienia, tokeny VQ zarówno na wejściu, jak i na wyjściu do generowania.
- Prześledź skalowanie miksu danych, które sprawia, że ​​Janus-Pro odniósł sukces tam, gdzie Janusowi się to nie udało.
- Porównaj architektury oddzielone (Janus-Pro), sprzężone-ciągłe (Transfusion) i sprzężone-dyskretne (Show-o).

## Problem

Ujednolicone modele mają wspólną obudowę transformatora pod względem zrozumienia i generacji. Wszystkie poprzednie próby (Chameleon, Show-o, Transfusion) wykorzystywały jeden wizualny tokenizator dla obu kierunków. Tokenizer to kompromis:

- Zoptymalizowany pod kątem rekonstrukcji (generowania): VQ-VAE przechwytuje drobnoziarniste szczegóły pikseli, ale tworzy tokeny o słabej spójności semantycznej.
- Zoptymalizowany pod kątem semantyki (zrozumienia): Osadzanie SigLIP grupuje obrazy „kota” w pobliżu tokenów „kota”, ale nie pozwala na dobrą rekonstrukcję.

Show-o i Transfusion płacą za to widocznym podatkiem od jakości w jednym kierunku. Janus-Pro pyta: po co jeden tokenizator, skoro zadania mają różne potrzeby?

## Koncepcja

### Oddzielone kodowanie wizualne

Architektura Janus-Pro oddziela dwa kodery:

- Ścieżka zrozumienia. Obraz wejściowy → SigLIP-SO400m → 2-warstwowy MLP → korpus transformatora.
- Ścieżka pokoleń. Obraz wejściowy (jeśli jest warunkowany na istniejącym obrazie) → Tokenizator VQ → Identyfikatory tokenów → Korpus transformatora.
- Generowanie wyników. Tokeny obrazu przewidywane przez transformator → dekoder VQ → piksele.

Korpus transformatora jest wspólny. Wszystko powyżej i poniżej ciała zależy od konkretnego zadania.

Dane wejściowe są rozróżniane poprzez format zachęty: znacznik `<understand>` kieruje przez SigLIP; `<generate>` prowadzi przez VQ. Lub routing jest niejawny z zadania.

### Dlaczego to działa

Zrozumienie straty pozwala uzyskać funkcje SigLIP, które podczas wstępnego uczenia w stylu CLIP dostrojono pod kątem podobieństwa semantycznego. Testy porównawcze percepcji modelu są lepsze w porównaniu z Show-o / Transfusion, ponieważ funkcje wejściowe są lepsze w przypadku tego zadania.

Strata generacji otrzymuje tokeny VQ, które tokenizator dostroił do rekonstrukcji. Jakość obrazu poprawia się w porównaniu z Show-o, ponieważ kody VQ ponownie składają się z pikseli.

Wspólny korpus transformatora widzi dwie dystrybucje wejściowe (SigLIP i VQ) i uczy się pracować z obiema. Twierdzenie: wystarczająco dużo danych + wystarczająca ilość parametrów, ciało absorbuje przełączanie.

### Skalowanie danych — Janus vs Janus-Pro

Janus (oryginał, arXiv 2410.13848) wprowadził oddzielenie, ale na małą skalę (parametry 1,3B, ograniczone dane). Janus-Pro (arXiv 2501.17811) skalowany:

- Parametry 7B (w porównaniu z 1.3B).
- 90M par obraz-tekst dla etapu 1 (wyrównanie) w porównaniu z 72M.
- 72 mln dla etapu 2 (ujednoliconego) w porównaniu z 26 mln.
— Dodano 200 tys. próbek instrukcji generowania obrazu dla etapu 3.

Wynik: Janus-Pro-7B dorównuje LLaVA na MMMU (60,3 vs ~58) i pokonuje DALL-E 3 na GenEval (0,80 vs 0,67). Jeden otwarty model, konkurencyjny po obu stronach zunifikowanego spektrum.

### JanusFlow — wariant przepływu wyprostowanego

JanusFlow (arXiv 2411.07975) zamienia ścieżkę generowania VQ na ścieżkę generowania wyprostowanego przepływu (ciągłą). Podział to SigLIP-dla-zrozumienia + wyprostowany-przepływ-dla-generowania. Sufity wysokiej jakości wznoszą się dalej. Architektura pozostaje oddzielona-koderami-współdzielonym-ciałem.

### Zadanie wspólnego ciała

Korpus transformatora przetwarza ujednoliconą sekwencję, ale z dwoma rozkładami wejściowymi. Jego zadaniem jest:

- Dla zrozumienia: korzystaj z funkcji SigLIP + tokenów tekstowych → emituj tekst autoregresywnie.
- Do generowania: zużywaj tokeny tekstowe + (opcjonalne tokeny VQ obrazu) → emituj tokeny VQ obrazu autoregresywnie.

Treść nie ma ciężarów specyficznych dla modalności na blok. Jest to transformator tekstowy, którego można spodziewać się w Qwen lub Llama, plus dwa adaptery wejściowe.

Co ciekawe, oznacza to, że ciało Janus-Pro można zainicjować z wstępnie przeszkolonego LLM. Janus-Pro inicjuje z DeepSeek-MoE-7B. Ten wybór ma znaczenie: LLM zapewnia zdolność rozumowania, której osiągnięcie nie jest możliwe w przypadku całkowicie zunifikowanych modeli.

### W porównaniu do InternVL-U

InternVL-U (lekcja 12.10) to kontynuacja z 2026 roku. Łączy w sobie:

- Natywne multimodalne szkolenie wstępne (szkielet InternVL3).
- Prowadzenie odsprzężonego enkodera (wejście SigLIP, wyjście VQ + głowice dyfuzyjne).
- Ujednolicone zrozumienie + generowanie + edycja.

InternVL-U łączy wybór architektoniczny Janus-Pro w większą strukturę. Pomysł z oddzielonym koderem jest teraz domyślny w przypadku ujednoliconych modeli na dużą skalę.

### Ograniczenia

Oddzielone enkodery zwiększają złożoność architektury. Dwa tokenizatory do wytrenowania, dwie ścieżki wejściowe do utrzymania, dwa zestawy trybów awarii. W przypadku produktów, które nie wymagają generowania, Janus-Pro jest przeprojektowany — wybierz model rozumiejący rodzinę LLaVA.

W przypadku produktów, które nie wymagają zrozumienia, Janus-Pro ma zbyt wysokie kwalifikacje — wybierz model Stable Diffusion 3 / Flux.

W przypadku produktów, które wymagają obu, Janus-Pro jest teraz referencyjną otwartą architekturą.

## Użyj tego

`code/main.py` symuluje routing Janus-Pro:

- Dwa fałszywe kodery: typu SigLIP (produkuje 256-ciemne wektory semantyczne) i typu VQ (produkuje kody całkowite).
- Router podpowiedzi, który wybiera koder na podstawie znacznika zadania.
- Wspólny korpus (zastępczy), który przetwarza sekwencje tokenów niezależnie od tego, który koder je wygenerował.
- Przejście z etapu 1 (dopasowanie) do etapu 3 (dostrojenie instrukcji) harmonogramu próbek ważonych.

Wydrukuj wytyczone ścieżki dla 3 przykładów: kontrola jakości obrazu, T2I, edycja obrazu.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-decoupled-encoder-picker.md`. Biorąc pod uwagę produkt, który wymaga ujednoliconego generowania + zrozumienia w pionierskiej jakości, wybiera Janus-Pro, JanusFlow lub InternVL-U z konkretnymi zaleceniami dotyczącymi skali danych.

## Ćwiczenia

1. Janus-Pro-7B pokonuje DALL-E 3 na GenEval. Wyjaśnij, dlaczego otwarty model 7B może dorównać pionierskiemu, zastrzeżonemu modelowi pod względem generacji, ale nie pod względem zrozumienia.

2. Zaimplementuj funkcję routera: podając tekst zachęty, sklasyfikuj jako `understand` lub `generate`. Jak sobie radzisz z niejednoznacznymi monitami, takimi jak „opisz, a następnie szkicuj”?

3. JanusFlow zastępuje ścieżkę VQ skorygowanym przepływem. Co teraz wyprowadza korpus transformatora i jakie zmiany w stratach?

4. Zaproponuj czwarte zadanie, które architektura Janus-Pro mogłaby wykonać z jeszcze jednym odsprzężonym koderem. Przykłady: segmentacja obrazu (w stylu DINO), głębokość (w stylu MiDaS).

5. Przeczytaj Janus-Pro Sekcja 4.2 na temat skalowania danych. Który etap danych najbardziej przyczynia się do wzrostu jakości T2I w porównaniu z Janusem?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|--------------------------------------|
| Oddzielone kodowanie | „Dwa kodery wizualne” | Oddzielny tokenizator lub koder dla każdego kierunku: semantyczny do zrozumienia, rekonstrukcja do generowania |
| Wspólne ciało | „Jeden transformator” | Pojedynczy transformator przetwarza sygnał wyjściowy dowolnego enkodera; brak wag specyficznych dla modalności |
| SigLIP za zrozumienie | „Cechy semantyczne” | Wieża wizyjna z rodziny CLIP zapewniająca bogate funkcje koncepcyjne, ale słabą rekonstrukcję |
| VQ dla pokolenia | „Kody rekonstrukcyjne” | Tokeny skwantowane wektorowo, które czysto dekodują z powrotem do pikseli |
| JanusFlow | „Wariant z przepływem rektyfikowanym” | Janus-Pro z głowicą generującą o ciągłym dopasowywaniu przepływu zamiast VQ |
| Znacznik routingu | „Znacznik zadania” | Znacznik podpowiedzi (`<understand>` / `<generate>`), który wybiera koder wejściowy |

## Dalsze czytanie

- [Wu i in. — Janus (arXiv:2410.13848)](https://arxiv.org/abs/2410.13848)
- [Chen i in. — Janus-Pro (arXiv:2501.17811)](https://arxiv.org/abs/2501.17811)
- [Ma i in. — JanusFlow (arXiv:2411.07975)](https://arxiv.org/abs/2411.07975)
- [InternVL-U (arXiv:2603.09877)](https://arxiv.org/abs/2603.09877)
- [Dong i in. — DreamLLM (arXiv:2309.11499)](https://arxiv.org/abs/2309.11499)