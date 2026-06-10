# Analiza długich materiałów wideo w kontekście miliona tokenów

> Godzinny film w rozdzielczości 4K przy 24 kl./s, po podziale na patche i przetworzeniu na tokeny, generuje około 60 milionów tokenów. Dla porównania, transkrypcja tekstowa dwugodzinnego podcastu to zaledwie 30 000 tokenów. Cały film kinowy z płyty Blu-ray, nawet po zastosowaniu agresywnego poolingu, wymaga przetworzenia setek tysięcy tokenów. Model Google Gemini 1.5 (marzec 2024) zapoczątkował nową erę dzięki oknu kontekstowemu o rozmiarze do 10 milionów tokenów, co pozwala na niezawodne odnajdywanie informacji (test „igły w stogu siana” / Needle-in-a-Haystack) w wielogodzinnych nagraniach. Projekt LWM (Liu i in., luty 2024) wskazał drogę rozwoju opartą na technologii RingAttention (uwaga pierścieniowa). Rozwiązania takie jak LongVILA czy Video-XL dodatkowo zwiększyły wydajność przetwarzania długiego kontekstu, natomiast VideoAgent zastąpił analizę całego wideo podejściem agentowym opartym na wyszukiwaniu kluczowych fragmentów. Każda z tych metod reprezentuje inny kompromis między złożonością obliczeniową, skutecznością wyszukiwania a trudnością inżynieryjną. W tej lekcji przyjrzymy się im wszystkim z bliska.

**Typ:** Teoria / Przegląd
**Języki:** Python (biblioteka standardowa, symulator testu „igły w stogu siana” + router wyszukiwania agentowego)
**Wymagania wstępne:** Faza 12 · 17 (Modele wideo-językowe: tokeny czasowe i temporal grounding)
**Czas:** ~180 minut

## Cele kształcenia

- Obliczanie łącznego zapotrzebowania na tokeny wizualne dla długich nagrań wideo przy różnych wartościach FPS i stopniach poolingu.
- Wyjaśnienie trzech głównych ścieżek skalowania: bezpośrednie skalowanie okna kontekstowego (Gemini 1.5), uwaga pierścieniowa / RingAttention (LWM) oraz kompresja tokenów (LongVILA / Video-XL).
- Porównanie modeli wideo-VLM przetwarzających pełen kontekst z podejściem opartym na wyszukiwaniu agentowym (VideoAgent) pod kątem dokładności i opóźnień.
- Zaprojektowanie testu „igły w stogu siana” dla 30-minutowego wideo i pomiar skuteczności wyszukiwania informacji w określonym punkcie czasowym.

## Problem

Pojedyncza klatka podzielona na patche w natywnej rozdzielczości 384px generuje w modelu Qwen2.5-VL ok. 729 tokenów. Zaspokojenie potrzeb modelu za pomocą poolingu 3x3 pozwala zredukować tę liczbę do 81 tokenów na klatkę. Przy częstotliwości 1 FPS, 30-minutowe nagranie (1800 klatek) generuje 145 800 tokenów. Jest to wartość obsługiwana przez zaawansowane otwarte modele VLM z przełomu 2024/2025 roku, choć na granicy ich wydajności. Zwiększenie częstotliwości do 2 FPS daje już 291 600 tokenów, co mieści się tylko w najszerszych dostępnych oknach kontekstowych.

Z kolei dwugodzinny film przy 1 FPS generuje ok. 583 000 tokenów. Przekracza to możliwości większości modeli otwartoźródłowych w 2026 roku i wymaga użycia komercyjnych modeli, takich jak Gemini 2.5 Pro, bądź zastosowania znacznie bardziej agresywnego poolingu.

W odpowiedzi na ten problem wykształciły się trzy główne ścieżki skalowania.

## Koncepcja

### Ścieżka 1: Skalowanie siłowe (Brute-force Context — Gemini 1.5, Claude Opus)

Rozwiązanie polega na bezpośrednim skalowaniu okna kontekstowego modelu do milionów tokenów przy użyciu ogromnych zasobów sprzętowych i przetwarzaniu całego materiału w jednym przejściu w przód (forward pass).

Rodzina Gemini 1.5 zadebiutowała z oknem 1M tokenów (wersja Pro) oraz do 10M tokenów (wersja Ultra). Nowszy Gemini 2.5 Pro w 2026 roku bez problemu i stabilnie analizuje wielogodzinne filmy wideo. Praca naukowa (arXiv:2403.05530) dokumentuje skuteczność wyszukiwania informacji w teście „igły w stogu siana” na poziomie 99,7% aż do objętości ~9,5 miliona tokenów.

Pod względem inżynieryjnym sukces ten opiera się na autorskiej implementacji mechanizmu atencji z hierarchicznym dostępem do pamięci (atencja lokalna, globalna oraz rzadka - sparse) połączonej z routingiem w modelach typu MoE (Mixture of Experts), co optymalizuje koszty obliczeniowe przy długim kontekście. Szczegóły te pozostają własnością firm komercyjnych i nie są dostępne jako open-source.

### Ścieżka 2: Uwaga pierścieniowa (RingAttention — LWM, LongVILA)

Mechanizm RingAttention rozdziela przetwarzanie długiej sekwencji pomiędzy poszczególne akceleratory (np. GPU) połączone w strukturę pierścienia. Każde urządzenie przechowuje i przetwarza jedynie fragment sekwencji, przesyłając swoje klucze i wartości (K, V) do kolejnego węzła w pierścieniu. Pozwala to na obliczanie częściowych macierzy atencji i ich końcową agregację.

Model LWM (Liu i in., 2024) został w ten sposób wytrenowany na kontekście o długości 1M tokenów. Koszt pamięciowy rośnie dzięki temu liniowo wraz z długością sekwencji na jedno urządzenie, a kwadratowy koszt mechanizmu atencji rozkłada się równomiernie na wszystkie akceleratory w pierścieniu.

Projekt LongVILA (arXiv:2408.10188) zaadaptował tę metodę dla modeli VLM. Umożliwiło to trenowanie modeli na wideo złożonych z 1400 klatek (co przy 192 tokenach na klatkę daje 268 tys. tokenów kontekstu) przy użyciu 8-kierunkowej równoległości RingAttention.

### Ścieżka 3: Kompresja tokenów (Video-XL, LongVA)

Podejście znacznie tańsze obliczeniowo: polega na agresywnej kompresji reprezentacji wizyjnej zanim trafi ona do właściwego modelu LLM.

Model Video-XL (arXiv:2409.14485) wprowadza pojęcie wizualnych tokenów podsumowujących: każdy podklip złożony z N klatek jest mapowany na pojedynczy token podsumowujący. W rezultacie model LLM przetwarza tylko po jednym tokenie na cały krótki segment wideo, co drastycznie redukuje długość wejściowej sekwencji.

Z kolei LongVA rozszerza efektywne okno kontekstowe modelu z 200k do 2M tokenów przy użyciu techniki transferu długiego kontekstu (long-context transfer). Model jest najpierw trenowany na bardzo długich tekstach, po czym te zdolności są przenoszone na modalność wideo za pomocą współdzielonej przestrzeni reprezentacji.

Kompresja tokenów ułatwia skalowanie, ale odbywa się kosztem precyzji czasowej (trudniej wskazać dokładne znaczniki czasu). Model dobrze rozumie ogólny sens nagrania, ale może gubić pojedyncze, drobne szczegóły.

### Ścieżka 4: Wyszukiwanie agentowe (VideoAgent)

Zamiast przesyłać całe nagranie wideo bezpośrednio do LLM, wideo jest traktowane jako baza danych, którą model odpytuje za pomocą odpowiednich narzędzi.

Schemat działania modelu VideoAgent (arXiv:2403.10517):

1. LLM zapoznaje się z pytaniem użytkownika.
2. LLM wywołuje narzędzie wyszukiwania do zlokalizowania kluczowych fragmentów nagrania (np. „znajdź segmenty, na których widać kota”).
3. Narzędzie zwraca listę pasujących przedziałów czasowych (timestampów).
4. LLM pobiera i analizuje tylko wskazane krótkie segmenty wideo za pomocą VLM.
5. LLM formułuje ostateczną odpowiedź lub realizuje kolejne kroki w pętli myślenia.

Jest to implementacja podejścia agentowego dla długich nagrań. Zaletą są znacznie niższe koszty obliczeniowe (przetwarzane są tylko wybrane klatki), a wadą skomplikowana architektura integracyjna (skuteczność całego systemu zależy od jakości modułu wyszukującego klipy).

### Benchmark „igła w stogu siana” (Needle-in-a-Haystack)

Klasyczny test oceny wydajności długiego kontekstu: w losowym miejscu nagrania wideo umieszcza się unikalny element wizualny lub tekstowy, a następnie pyta model o szczegóły z nim związane.

Miernik oceny: Recall@k w relacji do długości wideo oraz pozycji wstrzykniętego elementu.

Gemini 2.5 Pro osiąga ponad 99% skuteczności wyszukiwania w nagraniach do 90 minut. Otwarte modele o skali 72B (Qwen2.5-VL-72B, InternVL3-78B) osiągają wynik ~85-90% dla wideo o długości do 30 minut, a powyżej 60 minut ich skuteczność gwałtownie spada.

Z kolei VideoAgent potrafi dorównać lub nawet przewyższyć modele przetwarzające pełen kontekst na filmach dłuższych niż 2 godziny, pod warunkiem, że mechanizm wyszukiwania klipów działa bezbłędnie.

### Rekomendacja wyboru ścieżki

- **Dla filmów do 15 minut:** Użyj wiodących modeli otwartych o skali 72B przetwarzających natywny kontekst (np. Qwen2.5-VL-72B).
- **Dla filmów od 30 minut do 1 godziny:** Wybierz otwarte modele LongVILA lub Video-XL, ewentualnie komercyjny model Gemini 2.5 Pro, jeśli budżet i ograniczenia prywatności na to pozwalają.
- **Dla filmów powyżej 2 godzin:** Zaimplementuj architekturę VideoAgent lub podobne techniki wyszukiwania. Alternatywnie możesz podzielić wideo na krótsze segmenty i zastosować hierarchiczne streszczanie.

### Hybrydowy wzorzec produkcyjny na rok 2026

W rzeczywistych wdrożeniach produkcyjnych do analizy długiego wideo stosuje się podejście hybrydowe:

1. Przetwórz całe wideo za pomocą dynamicznego próbkowania FPS + agresywnego poolingu, aby uzyskać globalny profil wideo mieszczący się w granicach 100 tys. tokenów.
2. Przekaż te dane do modelu VLM (np. klasy 72B), aby wygenerować globalne streszczenie i spis treści.
3. Gdy użytkownik zadaje szczegółowe pytania o detale, użyj globalnego streszczenia jako indeksu do wyszukiwania agentowego (wybiórcza analiza klatek w wysokiej rozdzielczości).

Dzięki temu łączymy zalety siłowego przetwarzania kontekstu (dla zrozumienia ogólnego sensu) z precyzją wyszukiwania agentowego (dla analizy lokalnych detali).

## Zastosowanie w kodzie

Plik `code/main.py` realizuje następujące zadania:
- Oblicza zapotrzebowanie na tokeny dla nagrań wideo od 1 minuty do 3 godzin przy różnych konfiguracjach klatek (FPS) i stopniu poolingu.
- Symuluje test „igły w stogu siana”: wstrzykuje znacznik w losowym momencie wideo, formułuje zapytanie i mierzy skuteczność jego odnalezienia.
- Zawiera makiety routera wyszukiwania agentowego, który decyduje o wyborze konkretnych podklipów do przekazania do właściwego modelu VLM.

## Rezultat

Do tej lekcji dołączono dokument `outputs/skill-long-video-strategy-planner.md`. Ułatwia on wybór między bezpośrednim przetwarzaniem kontekstu, kompresją a wyszukiwaniem agentowym na podstawie długości wideo i złożoności zapytania, a także szacuje docelowe opóźnienia i jakość.

## Ćwiczenia

1. Oblicz łączną liczbę tokenów dla 45-minutowego wykładu przy próbkowaniu 1 FPS i poolingu 3x3 (81 tokenów na klatkę). W jakich znanych Ci modelach takie okno kontekstowe się zmieści?
2. Zaprojektuj własny test „igły w stogu siana”: w której minucie nagrania wstrzykniesz znacznik i jak sformułujesz zapytanie testujące?
3. Porównaj model Qwen2.5-VL-72B analizujący pełen kontekst (okno 80k) z systemem VideoAgent (np. Claude 3.5 + wyszukiwanie) na godzinnym materiale wideo. Które rozwiązanie osiągnie lepszą skuteczność wyszukiwania, a które zapewni niższe opóźnienia?
4. Koszt pamięciowy RingAttention rośnie liniowo wraz z długością sekwencji i liczbą węzłów obliczeniowych. Wyjaśnij, dlaczego tak się dzieje i co ulegnie awarii, jeśli pominiemy krok rotacji tokenów w pierścieniu.
5. Przeczytaj sekcję 5 pracy o Gemini 1.5 poświęconą testom „igły w stogu siana”. Jakie wyniki skuteczności wyszukiwania raportują autorzy na granicach okien 1M oraz 10M tokenów?

## Kluczowe pojęcia

| Termin | Potoczne określenie | Co to dokładnie oznacza |
| :--- | :--- | :--- |
| **Przetwarzanie siłowe (Brute-force context)** | „Więcej tokenów do LLM” | Bezpośrednie skalowanie okna kontekstowego LLM do milionów tokenów w celu przeanalizowania całego wideo w jednym przejściu. |
| **RingAttention** | „Równoległość pierścieniowa” | Algorytm rozproszonego obliczania atencji, w którym akceleratory GPU są połączone w pierścień i wymieniają się fragmentami sekwencji. |
| **Kompresja tokenów** | „Tokeny podsumowujące” | Zmniejszanie liczby tokenów na klatkę/klip przy użyciu specjalnej warstwy kompresującej przed podaniem danych do LLM. |
| **Igła w stogu siana (Needle-in-a-Haystack)** | „Test NIH” | Test polegający na wstrzyknięciu drobnej informacji w losowym miejscu długiego kontekstu i sprawdzeniu, czy model potrafi ją bezbłędnie odnaleźć. |
| **Wyszukiwanie agentowe** | „LLM jako planista zapytań” | Architektura, w której LLM za pomocą narzędzi wyszukuje tylko kluczowe przedziały czasowe filmu i przekazuje do VLM wyłącznie te wybrane klipy. |
| **VideoAgent** | „Podejście wyszukiwawcze” | Klasyczna implementacja wyszukiwania agentowego w wideo oparta na pętli: pytanie → wyszukiwarka klipów → analiza VLM → odpowiedź. |

## Literatura uzupełniająca

- [Zespół Gemini — Gemini 1.5 (arXiv:2403.05530)](https://arxiv.org/abs/2403.05530)
- [Liu i in. — LWM / RingAttention (arXiv:2402.08268)](https://arxiv.org/abs/2402.08268)
- [Xue i in. — LongVILA (arXiv:2408.10188)](https://arxiv.org/abs/2408.10188)
- [Shu i in. — Video-XL (arXiv:2409.14485)](https://arxiv.org/abs/2409.14485)
- [Wang i in. — VideoAgent (arXiv:2403.10517)](https://arxiv.org/abs/2403.10517)
