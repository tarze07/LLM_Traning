# LLaVA-OneVision: pojedynczy obraz, wiele obrazów, wideo w jednym modelu

> Przed LLaVA-OneVision (Li i in., sierpień 2024 r.) świat otwartego VLM miał oddzielne linie rodowe: LLaVA-1.5 dla pojedynczych obrazów, modele wieloobrazowe, takie jak Mantis i VILA, modele wideo, takie jak Video-LLaVA i Video-LLaMA. Każdy z nich zwyciężył w swoim benchmarku, a w pozostałych poniósł porażkę. LLaVA-OneVision argumentowała, że ​​jeden program nauczania mógłby wytrenować jeden model, aby zdominował wszystkie trzy scenariusze, a pojawiające się efekty przeniesienia zadań (umiejętności związane z jednym obrazem wyeksportowane do wideo, rozumowanie wieloobrazowe wyeksportowane do pojedynczego obrazu) przewyższają sumę specjalistów. Przepis jest zwodniczo prosty: budżet wizualny, który pozostaje stały w zależności od scenariusza, a także wyraźny program nauczania, który przechodzi od jednego obrazu do OneVision (wiele obrazów) i wideo. Podczas tej lekcji zapoznajemy się z budżetem, programem nauczania i wyłaniającymi się zachowaniami.

**Typ:** Kompilacja
**Języki:** Python (stdlib, narzędzie do rozwiązywania budżetów tokenów + planer programów nauczania)
**Wymagania wstępne:** Faza 12 · 05 (LLaVA), Faza 12 · 06 (dowolna rozdzielczość)
**Czas:** ~180 minut

## Cele nauczania

- Zaprojektuj budżet tokenów wizualnych, który będzie stały dla wejść obejmujących jeden obraz, wiele obrazów i wideo.
- Zamów program szkoleniowy, który przeniesie umiejętności z pojedynczego obrazu na wideo bez katastrofalnego zapomnienia.
- Wyjaśnij, dlaczego pojedynczy model przewyższa specjalistów pod względem tej samej liczby parametrów, jeśli program nauczania jest realizowany prawidłowo.
- Wymień trzy nowe możliwości zgłoszone przez LLaVA-OneVision: rozumowanie z użyciem wielu kamer, monitowanie o ustawienie znaku, agent zrzutów ekranu z iPhone'a.

## Problem

Obraz, wiele obrazów i wideo podkreślają model w inny sposób.

Pojedynczy obraz wymaga tokenów o wysokiej rozdzielczości (AnyRes, ~2880 tokenów wizualnych), aby uchwycić OCR i drobne szczegóły. Budżet na próbkę: jeden obraz, 2880 tokenów.

Wiele obrazów wymaga kilku obrazów w umiarkowanej rozdzielczości (~ 576 tokenów każdy), więc rozumowanie dotyczące obrazów pasuje do kontekstu. Budżet na próbkę: 4-8 obrazów, po 576, 2300-4600 tokenów.

Wideo wymaga wielu klatek w niskiej rozdzielczości (~196 tokenów na klatkę po połączeniu), aby uchwycić dynamikę czasową. Budżet na próbkę: 8-32 klatki po 196 każda, 1600-6200 tokenów.

Jeśli trenujesz oddzielne modele, wybierasz jeden budżet. Jeśli szkolisz jeden model, potrzebujesz budżetu, który można rozsądnie skalować w zależności od scenariuszy, bez ujawniania kontekstu.

Przed wprowadzeniem OneVision domyślną odpowiedzią było „trenuj jeden scenariusz, ignoruj ​​pozostałe”. Wideo-LLaVA zmodernizowane do modelu obrazu z dodatkowymi etapami szkoleniowymi. LLaVA-NeXT dodała obsługę wielu obrazów z kafelkowaniem. Żaden nie poradził sobie ze wszystkimi trzema w sposób czysty.

## Koncepcja

### Budżet tokenów OneVision

LLaVA-OneVision wybiera ujednolicony budżet tokenów wizualnych wynoszący około 3000–4000 tokenów na próbkę, przydzielany w różny sposób w zależności od scenariusza:

- Pojedynczy obraz: AnyRes-9 (3x3 płytki + miniatura), każda płytka w 384 z 729 poprawkami, agresywne dwuliniowe łączenie 2x2 → 182 na płytkę. Razem: 9 * 182 + 182 = 1820 tokenów. Lub AnyRes-4 przy 729 na płytkę = 2916 + 729.
- Wiele obrazów: każdy obraz w umiarkowanej rozdzielczości (384, bez kafelkowania), 729 tokenów bez łączenia. Budżet 6 obrazów → 4374 tokenów.
- Wideo: 32 klatki w rozdzielczości 384 z agresywną pulą dwuliniową 3x3 → 81 tokenów na klatkę. Razem: 32 * 81 = 2592 tokenów.

Przydział utrzymuje mniej więcej stałą liczbę tokenów ogółem. LLM nigdy nie widzi partii, która narusza jej kontekst. Koder generuje inną geometrię w zależności od scenariusza, ale LLM zużywa ten sam budżet.

### Trzystopniowy program nauczania

Szkolenia LLaVA-OneVision odbywają się w trzech etapach:

1. Jednoobrazowy SFT (etap SI). Wszystkie dane to pojedynczy obraz i tekst. Trenuj na wejściu AnyRes o wysokiej rozdzielczości. Uczy to percepcji, OCR i szczegółowego zrozumienia. Wykorzystuje dane LLaVA-NeXT oraz dane pojedynczego obrazu specyficzne dla OneVision.
2. OneVision SFT (etap OV). Mieszaj pojedynczy obraz + wiele obrazów + wideo (jednolicie próbkowane klatki). Trenuj w oparciu o ujednolicony budżet tokenów. Uczy to model obsługi heterogenicznych kształtów partii. Bez resetowania wagi – kontynuacja od etapu SI.
3. Przekazanie zadania (etap TT). Kontynuuj z docelowym zestawem zadań, zazwyczaj cięższym w przypadku wielu obrazów lub wideo, w zależności od produktu. Opcjonalne dostosowanie do wdrożenia.

Krytyczne: kolejność programu nauczania ma znaczenie. Uczenie najpierw wideo lub wielu obrazów daje gorszą wydajność obrazu niż najpierw pojedynczy obraz, nawet przy tych samych danych. Artykuł wyraźnie to obala.

### Dlaczego program nauczania działa

Trening pojedynczego obrazu buduje bazę percepcyjną. Żetony łatek zawierają szczegółowe elementy wizualne; LLM uczy się integrować je z tekstem. Multiobraz i wideo wprowadzają wyzwania strukturalne (który obraz jest który, co wydarzyło się pierwsze), których trudno się nauczyć bez silnej podstawy percepcyjnej.

Jeśli trenujesz wszystkie scenariusze od podstaw razem, model nie dopasowuje się do percepcji (ograniczone dane pojedynczego obrazu na partię) i nadmiernie pasuje do struktury (dużo danych obejmujących wiele obrazów/wideo). Wynik: model zgodny ze wzorcami rozumowania opartymi na różnych obrazach, ale wizualnie płytki.

Porządkowanie programu nauczania zapewnia siłę percepcji od etapu SI, a następnie rozumowanie kompozycyjne/czasowe od etapu OV, bez utraty żadnego z nich.

### Pojawiające się umiejętności przekrojowe

W artykule LLaVA-OneVision opisano trzy nowe możliwości:

1. Rozumowanie wielokamerowe. Oddzielnie przeszkolony w zakresie wielu obrazów i wideo; na zakończenie poproszony o uzasadnienie sceny jazdy z użyciem wielu kamer. Model poprawnie integruje widoki, mimo że nigdy nie widział dokładnie tego formatu podczas szkolenia.
2. Monitowanie o ustawienie znaku. Użytkownik opisuje obiekty na obrazie za pomocą numerowanych znaków; model uzasadnia pytanie „co robi znak 3 w porównaniu do znaku 7”. Nie uczył się ani znaków, ani adnotacji; wyciągnąłem wnioski z połączenia uziemienia przestrzennego i odniesienia do wielu obrazów.
3. Agent zrzutów ekranu iPhone'a. Użytkownik udostępnia zrzut ekranu ekranu iPhone'a i prosi o zaplanowanie kolejnego kliknięcia. Przeszkolono w zakresie zrzutów ekranu interfejsu użytkownika, filmów przedstawiających przepływy pracy użytkowników i par wielu obrazów przed/po. Uogólnia przypadek użycia agenta.

To nie są przeszkolone zadania; wyłaniają się ze struktury kompozycyjnej programu nauczania.

### Łączenie tokenów wizualnych

Budżet tokena wymaga łączenia. OneVision wykorzystuje interpolację dwuliniową w siatce poprawek 2D: 24x24 = 576 fragmentów staje się 12x12 = 144 (2x współczynnik) lub 8x8 = 64 (3x współczynnik). Aby zachować lokalność, łączenie odbywa się w przestrzeni siatki krosowej, a nie w przestrzeni żetonów.

Wybór współczynnika łączenia na scenariusz sam w sobie jest hiperparametrem. Mniej łączenia = więcej tokenów = bogatsza reprezentacja. Więcej łączenia = mniej tokenów = więcej klatek/obrazów pasuje.

### LLaVA-OneVision-1.5

Kontynuacja z 2025 r. (LLaVA-OneVision-1.5, arXiv 2509.23661) jest „w pełni otwarta” pod względem danych szkoleniowych, wag modeli i kodu. Wyrównuje zastrzeżoną lukę w niektórych benchmarkach i demokratyzuje przepis. Ten sam program nauczania, więcej danych, lepsza baza LLM. Żadnych zmian w architekturze.

### Kontrast z Qwen2.5-VL

Qwen2.5-VL (lekcja 12.09) dokonuje różnych wyborów. Wykorzystuje M-RoPE i dynamiczny FPS zamiast stałego łączenia. Jego budżet skaluje się wraz z wkładem — 1-minutowy film zużywa więcej tokenów niż 5-sekundowy film. LLaVA-OneVision ustala budżet i skaluje łączenie. Obydwa działają; zamieniają konfigurowalność na przewidywalność.

## Użyj tego

`code/main.py` to narzędzie do planowania programów nauczania i budżetu dla VLM w stylu OneVision. Biorąc pod uwagę symboliczny budżet na próbkę i docelowy zestaw scenariuszy (powiedzmy 40% pojedynczego obrazu, 30% wielu obrazów, 30% wideo), to:

- Przydziela rozdzielczość, współczynnik łączenia i klatki według scenariusza.
- Sprawdza, czy każdy scenariusz mieści się w ramach wspólnego budżetu.
- Raportuje oczekiwaną liczbę tokenów, LLM FLOP i które scenariusze są niedostatecznie tokenizowane.
- Drukuje harmonogram szkoleń etap po etapie.

Użyj go, aby zaplanować dokładne dostrojenie OneVision lub sprawdzić, czy koszt wdrożenia VLM na żądanie jest rozsądny.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-onevision-budget-planner.md`. Biorąc pod uwagę docelowy rozkład zadań i budżet na próbkę, emituje współczynnik AnyRes, łączenie na klatkę, liczbę klatek wideo i wagi etapów programu nauczania. Używaj tego za każdym razem, gdy szkolisz lub dostrajasz VLM o ujednoliconym scenariuszu.

## Ćwiczenia

1. Twój produkt obsługuje 80% pojedynczego obrazu, 10% wielu obrazów (2-4 obrazy), 10% wideo (8-16 klatek). Zaprojektuj budżet tokena. Na co przeznaczyłbyś dodatkowy budżet zaoszczędzony dzięki rezygnowaniu z obciążania wieloma obrazami?

2. Przeczytaj sekcję 4.3 LLaVA-OneVision (możliwości wschodzące). Zaproponuj czwartą wschodzącą umiejętność, którą prawdopodobnie odblokuje program nauczania, ale w artykule tego nie podano.

3. Zmień kolejność programu nauczania — najpierw ćwicz wiele obrazów, potem pojedynczy obraz, a następnie wideo. Przewiduj, które wskaźniki referencyjne ulegają pogorszeniu i dlaczego.

4. W artykule opisano testy porównawcze wideo trenowane tylko na 8 klatkach na próbkę. Czy można to uogólnić na 30-sekundowe filmy? Co psuje się najpierw – symboliczny budżet czy temporalne rozumowanie?

5. Dwuliniowe łączenie fragmentów 24x24 do 12x12 oznacza 4-krotną redukcję na każdy wymiar. Zaimplementuj łączenie w stdlib Python i sprawdź, czy średnia z każdego bloku 2x2 odpowiada wynikowi dwuliniowemu.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|--------------------------------------|
| Scenariusz OneVision | „Pojedynczy obraz, wiele obrazów lub wideo” | Jedno z trzech danych wejściowych kształtuje ujednolicone uchwyty VLM; budżet pozostaje stały w całym |
| Budżet symboliczny | „Ile tokenów na próbkę” | Łączna liczba tokenów wizualnych, które LLM widzi na próbkę uczącą/wnioskowującą, zazwyczaj 3000–4000 |
| Program nauczania | „Zamówienie szkoleniowe” | Kolejność etapowa (pojedynczy obraz → wiele obrazów → wideo) wybrana do transferu wschodzącego |
| Łączenie dwuliniowe | „Token kurczy się” | Zastosowanie interpolacji dwuliniowej do siatki poprawek (2D) w celu zmniejszenia liczby znaczników przy jednoczesnym zachowaniu lokalizacji |
| Wschodzące umiejętności | „Nie przeszkolony, nadal działa” | Możliwość pojawiająca się podczas wnioskowania bez dopasowania danych szkoleniowych ze względu na kompozycję programu nauczania |
| AnyRes-k | „konfiguracja k-kafelków” | k podkalików o stałej rozdzielczości plus jedna miniatura, typowo k ∈ {4, 9} |
| Przeniesienie zadania | „Uogólnianie międzyscenariuszowe” | Umiejętności zdobyte na pojedynczym obrazie, które można zastosować w przypadku wideo (i odwrotnie) za pośrednictwem wspólnego szkieletu |

## Dalsze czytanie

- [Li i in. — LLaVA-OneVision (arXiv:2408.03326)](https://arxiv.org/abs/2408.03326)
- [LLaVA-OneVision-1.5: W pełni otwarte środowisko (arXiv:2509.23661)](https://arxiv.org/abs/2509.23661)
- [Lin i in. — Wideo-LLaVA (arXiv:2311.10122)](https://arxiv.org/abs/2311.10122)
- [Lin i in. — VILA (arXiv:2312.07533)](https://arxiv.org/abs/2312.07533)
- [Wang i in. — Qwen2-VL (arXiv:2409.12191)](https://arxiv.org/abs/2409.12191)