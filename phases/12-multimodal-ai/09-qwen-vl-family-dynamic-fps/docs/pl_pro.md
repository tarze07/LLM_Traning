# Rodzina Qwen-VL i wideo z dynamicznym FPS

> Rodzina modeli Qwen-VL — Qwen-VL (2023), Qwen2-VL (2024), Qwen2.5-VL (2025) oraz Qwen3-VL (2025) — to jedna z najbardziej wpływowych linii otwartoźródłowych modeli VLM. Każda kolejna generacja wprowadzała kluczowe rozwiązania architektoniczne, które były następnie adaptowane przez resztę ekosystemu w ciągu kolejnych miesięcy: natywna rozdzielczość dynamiczna dzięki M-RoPE, dynamiczne próbkowanie klatek wideo (dynamic FPS) powiązane z czasem rzeczywistym, mechanizm window attention w ViT oraz ustrukturyzowane dane wyjściowe agenta. W modelu Qwen3-VL ta recepta została ostatecznie dopracowana: koder 2D-RoPE-ViT przetwarzający obrazy w ich natywnych proporcjach, projektor MLP łączący go z modelem językowym Qwen3 oraz procedury treningowe kładące nacisk na zadania OCR, lokalizowanie obiektów (grounding) i zachowania agentowe jako priorytet. W tej lekcji prześledzimy chronologiczny rozwój rodziny Qwen-VL, co pozwoli zrozumieć motywacje stojące za każdą decyzją projektową.

**Typ:** Teoria / Zrozumienie
**Języki:** Python (biblioteka standardowa, koder M-RoPE + dynamiczny próbnik FPS)
**Wymagania wstępne:** Faza 12 · Lekcja 06 (pakowanie patchy - patch-n'-pack)
**Czas:** ~120 minut

## Cele nauczania

- Oblicz rotacje M-RoPE w trzech osiach (czas, wysokość, szerokość) i wyjaśnij konieczność stosowania każdej z nich.
- Dobierz strategię próbkowania dynamicznego FPS dla wideo i uzasadnij kompromis pomiędzy liczbą tokenów na sekundę a dokładnością wykrywania zdarzeń.
- Przedstaw w kolejności chronologicznej cztery generacje ulepszeń w rodzinie Qwen-VL i określ ich kluczowe możliwości.
- Zaimplementuj parser ustrukturyzowanych odpowiedzi JSON w stylu agenta Qwen2.5-VL w celu przetwarzania wywołań narzędzi (tool calls).

## Problem

Model Qwen-VL został wydany w sierpniu 2023 roku jako bezpośrednia odpowiedź na LLaVA-1.5 i BLIP-2. Zespół Qwen zidentyfikował trzy główne obszary wymagające poprawy w istniejących modelach VLM: rozdzielczość, wideo oraz ustrukturyzowane wyjście.

Rozdzielczość: LLaVA-1.5 przetwarzała obrazy w rozdzielczości 336x336. Było to wystarczające dla typowych zdjęć naturalnych, lecz bezużyteczne przy analizie chińskich faktur czy szczegółowych zrzutów ekranu tabel. Pierwszą innowacją Qwen-VL była obsługa rozdzielczości 448x448 oraz zdolność do wskazywania i lokalizowania obiektów za pomocą współrzędnych ramek otaczających (bounding boxes).

Wideo: Wczesne modele wideo, takie jak Video-LLaMA, po prostu składały embeddingi klatek sekwencyjnie i przekazywały je do LLM. Sprawdzało się to dla kilkusekundowych klipów, ale zawodziło przy dłuższych nagraniach, gdzie kluczem jest zależność czasowa. Zespół Qwen potrzebował encodera, który natywnie rozumie wymiar czasu.

Ustrukturyzowane dane wyjściowe: Wczesne modele VLM generowały odpowiedzi w formacie swobodnego tekstu. Dla agentów produkcyjnych niezbędny jest jednak czytelny format typu JSON. Qwen-VL od początku był trenowany do generowania ustrukturyzowanych obiektów JSON, w tym współrzędnych obiektów zapisanych w tekście.

Każda kolejna generacja Qwen-VL rozwijała te trzy kluczowe kierunki.

## Koncepcja

### Qwen-VL (sierpień 2023)

Pierwsza generacja: OpenCLIP ViT-bigG/14 jako encoder (2.5B parametrów), jednokrokowy adapter Q-Former z 256 zapytaniami (kompatybilny z LLaMA) oraz model bazowy Qwen-7B. Główne atuty:

- Rozdzielczość 448x448 (wówczas najwyższa wśród otwartych modeli VLM).
- Lokalizacja obiektów (grounding): trening na parach obraz-tekst z generowaniem współrzędnych jako tokenów tekstowych: „Kot znajduje się w <box>(112, 204), (280, 344)</box>”.
- Pełna dwujęzyczność (angielski i chiński) od samego początku.

W tamtym okresie model rywalizował z GPT-4V w zadaniach anglojęzycznych i dominował w testach chińskojęzycznych. Zdolność lokalizacji przestrzennej była jego kluczowym wyróżnikiem.

### Qwen2-VL (wrzesień 2024): M-RoPE i rozdzielczość natywna

W wersji Qwen2-VL zrezygnowano ze stałej rozdzielczości i Q-Formera na rzecz natywnego encodera ViT obsługującego rozdzielczość dynamiczną. Kluczowe zmiany:

- Natywna rozdzielczość dynamiczna. ViT przetwarza obrazy o dowolnych wymiarach HxW podzielnych przez 28 (rozmiar patcha 14 z agregacją przestrzenną 2x). Obraz o rozmiarze 1120x672 (siatka 40x24 po agregacji) generuje 960 tokenów wizualnych bez potrzeby skalowania, kafelkowania czy miniatur.
- M-RoPE (Multimodalne RoPE). Każdy token otrzymuje pozycję trójwymiarową (t, h, w) zamiast jednowymiarowej. Dla obrazów t=0, dla wideo t odpowiada indeksowi klatki. Mechanizm RoPE modyfikuje wektory zapytań i kluczy (Q/K) z częstotliwością przypisaną do danej osi. Eliminuje to tradycyjne tabele osadzeń pozycyjnych.
- Projektor MLP. Usunięto Q-Former na rzecz 2-warstwowej sieci MLP przetwarzającej zagregowane tokeny patchy.
- Wideo z dynamicznym FPS. Nagrania są domyślnie próbkowane z częstotliwością 1-2 klatek na sekundę (FPS), lecz model akceptuje dowolną liczbę klatek.

Wynik: Model Qwen2-VL-7B wyrównał wyniki z GPT-4o w wielu benchmarkach multimodalnych i pokonał go w zadaniu DocVQA (94,5% vs 88,4%). Decydujące znaczenie miała zmiana architektury.

### Qwen2.5-VL (luty 2025): dynamiczny FPS i czas bezwzględny

Najważniejsze innowacje w Qwen2.5-VL dotyczyły przetwarzania wideo. Koncepcja dynamicznego FPS została sformalizowana w następujący sposób:

- Tokeny czasu bezwzględnego. Zamiast operować na indeksach klatek (klatka 0, 1, 2...), model wykorzystuje rzeczywiste znaczniki czasu, np.: „O 0:04 kot skacze”. Model widzi tokeny `<time>0.04</time>` przeplatane z tokenami klatek wideo.
- Dynamiczny FPS. Próbkowanie z częstotliwością 1 FPS dla scen o wolnym tempie zmian i 4+ FPS dla scen dynamicznych. Parametr ten jest w pełni konfigurowalny przez użytkownika przy wnioskowaniu, a mechanizm M-RoPE dostosowuje się do niego.
- Window attention w ViT. Warstwy uwagi przestrzennej są okienkowane (ograniczone do lokalnych bloków) w celu optymalizacji przepustowości; uwaga globalna jest stosowana tylko co kilka warstw.
- Ustrukturyzowane dane wyjściowe JSON. Model przeszkolono do generowania bezpośrednich wywołań narzędzi w formacie: `{"tool": "mouse_click", "coords": [380, 220]}`. Dzięki temu jest gotowy do wdrożeń agentowych od zaraz.
- Skalowanie M-RoPE-v2. Współrzędne pozycyjne są skalowane proporcjonalnie do maksymalnego rozmiaru wejścia, dzięki czemu 10-minutowe wideo nie wykracza poza zakres częstotliwości roboczych.

Benchmarki: Qwen2.5-VL-72B pokonał model GPT-4o w większości zadań wideo, zrównał się z Gemini 2.0 w analizie dokumentów i ustanowił nowy rekord w zadaniach GUI (ScreenSpot: dokładność 84% w porównaniu do 38% dla GPT-4o).

### Qwen3-VL (listopad 2025)

Wersja Qwen3-VL to ewolucyjna aktualizacja konsolidująca dotychczasowe osiągnięcia: zastosowano silniejszy model bazowy (Qwen3-72B), rozszerzono dane treningowe, ulepszono OCR oraz zaimplementowano „tryb myślenia” (thinking mode) z Qwen3. Struktura ViT oraz M-RoPE pozostały bez zmian. Publikacja skupia się głównie na optymalizacji danych i procedur uczenia, co potwierdza, że do 2025 roku architektura Qwen-VL uległa pełnej stabilizacji.

### Matematyka M-RoPE

Klasyczny mechanizm RoPE modyfikuje zapytanie `q` o wymiarze `d` na pozycji `m` przy użyciu par współrzędnych:

```
q_rot[2i]   = q[2i]   * cos(m * theta_i) - q[2i+1] * sin(m * theta_i)
q_rot[2i+1] = q[2i]   * sin(m * theta_i) + q[2i+1] * cos(m * theta_i)
theta_i     = 10000^(-2i/d)
```

M-RoPE dzieli wymiar ukryty (hidden dim) na trzy pasma. Załóżmy, że `d = 96`. Przypisujemy po 32 wymiary dla osi czasu, wysokości oraz szerokości. Każde pasmo jest modyfikowane zgodnie z pozycją na danej osi. Patch o współrzędnych (t=5, h=10, w=20) otrzymuje rotacje `R_t(5)`, `R_h(10)` oraz `R_w(20)` zaaplikowane odpowiednio do swoich trzech pasm.

Tokeny tekstowe przyjmują wartości `t = text_index, h = 0, w = 0`, co zachowuje pełną kompatybilność. Klatki wideo wykorzystują `t = frame_time, h = wiersz, w = kolumna`. Pojedyncze obrazy statyczne przyjmują `t = 0`.

Atut: jedno uniwersalne kodowanie pozycyjne obsługuje tekst, obrazy i wideo bez konieczności tworzenia osobnych tabel czy rozgałęzień kodu.

### Algorytm próbkowania dynamicznego FPS

Dla wideo o czasie trwania `T` sekund oraz docelowego budżetu tokenów `B`:

1. Oblicz maksymalną dopuszczalną częstotliwość klatek: `fps_max = B / (T * tokens_per_frame)`.
2. Dobierz docelowy FPS ze zbioru `{1, 2, 4, 8}`, spełniający warunek `fps <= fps_max`.
3. Jeśli scena charakteryzuje się dynamicznym ruchem (analiza optical flow lub żądanie użytkownika), wybierz wyższy FPS. W przeciwnym razie wybierz niższy.
4. Próbkuj klatki równomiernie z wybranym FPS; wstaw tokeny `<time>t</time>` pomiędzy klatkami.

Qwen2.5-VL uczy się tego zachowania w sposób niejawny; przy wnioskowaniu użytkownik steruje tym zachowaniem bezpośrednio za pomocą parametru `fps`. Przykładowo, 60 sekund dynamicznego wideo przy 4 FPS i 81 tokenach na klatkę daje 19440 tokenów, co bez problemu mieści się w oknie kontekstowym 32k.

### Ustrukturyzowane wyjście JSON agenta

Dostrajanie agentowe w Qwen2.5-VL jest wyraźnie zorientowane na generowanie ustrukturyzowanych wywołań narzędzi:

```
{
  "tool": "mouse_click",
  "coords": [1024, 512],
  "button": "left",
  "modifier": null
}
```

Dzięki temu parser po stronie kodu aplikacyjnego może wykonać standardowe `JSON.parse` na odpowiedzi modelu. Eliminuje to konieczność pisania skomplikowanych i podatnych na błędy wyrażeń regularnych (regex) dla analizy swobodnego tekstu typu „kliknij w punkt (1024, 512)”. Ta jedna zmiana podniosła skuteczność modelu w benchmarku ScreenSpot z 55% do 84%.

## Użycie praktyczne

Skrypt `code/main.py` zawiera:

- Obliczanie współrzędnych M-RoPE dla spakowanej sekwencji łączącej tekst, patche obrazów i klatki wideo.
- Próbnik dynamicznego FPS: na podstawie czasu trwania, budżetu i dynamiki ruchu dobiera optymalny FPS i generuje znaczniki czasu.
- Uproszczony parser JSON obsługujący wywołania narzędzi ze współrzędnymi w stylu Qwen2.5-VL.

Uruchomienie skryptu pozwala zobaczyć korzyści z zastosowania dynamicznego FPS nad sztywnym próbkowaniem przy długich nagraniach.

## Zadanie zaliczeniowe

W ramach tej lekcji należy stworzyć dokument `outputs/skill-qwen-vl-pipeline-designer_pro.md`. Na podstawie specyfikacji zadania wideo (np. monitoring, automatyzacja GUI, rozpoznawanie akcji), wygeneruj optymalną konfigurację parametrów Qwen2.5-VL (budżet klatek, strategia FPS, parametry window attention, tryb wyjściowy agenta) oraz oszacuj spodziewane opóźnienia. Korzystaj z tej umiejętności przy każdym wdrażaniu modeli z rodziny Qwen-VL do przetwarzania wideo.

## Ćwiczenia

1. Oblicz rotacje M-RoPE dla patcha o współrzędnych (t=3, h=5, w=7) przy wymiarze ukrytym równym 48 (16 wymiarów na pasmo, podstawa theta = 10000). Podaj kąty obrotu dla pierwszych trzech par w każdym z pasm.

2. Ile klatek wygeneruje 10-minutowe nagranie z monitoringu próbkowane z częstotliwością 1 FPS? Ile łącznie tokenów wygeneruje ten plik przy rozdzielczości 384x384 i poolingu 3x3? Czy domyślne okno kontekstowe Qwen2.5-VL o rozmiarze 32k tokenów obsłuży to zadanie?

3. Dobierz optymalny FPS dla: 30-sekundowego skrótu meczu tenisowego, 30-sekundowego nagrania przepisu kulinarnego oraz 30-sekundowej sesji pracy agenta na interfejsie użytkownika. Uzasadnij każdy wybór za pomocą logiki dynamicznego FPS.

4. Model Qwen2.5-VL całkowicie zrezygnował z Q-Formera. Wyjaśnij, dlaczego prosty projektor MLP okazał się lepszym rozwiązaniem w roku 2025 niż w 2023. (Wskazówka: weź pod uwagę wolumen danych treningowych oraz jakość encodera wizyjnego).

5. Zaimplementuj funkcję parsującą trzy wyjściowe JSON-y z wywołaniami narzędzi Qwen2.5-VL na słowniki Pythona. Jak należy obsłużyć błędy składniowe JSON i jaką strategię naprawczą rekomenduje dokumentacja techniczna Qwen?

## Słownik pojęć

| Termin | Potoczne określenie | Co to dokładnie oznacza |
|------|-----------------|--------------------------------------|
| M-RoPE | „Wielomodalne RoPE” | Kodowanie pozycyjne 3D dzielące wymiar ukryty na osobne pasma dla czasu, wysokości i szerokości. |
| Dynamiczny FPS | „Smart sampling” | Dobór częstotliwości próbkowania klatek wideo na podstawie dynamiki ruchu, czasu trwania oraz budżetu tokenów. |
| Absolutny znacznik czasu | „Token czasu” | Znacznik `<time>t</time>` przeplatany z klatkami wideo, informujący model o rzeczywistym czasie nagrania w sekundach. |
| Window attention | „Uwaga lokalna” | Ograniczenie zasięgu self-attention w koderze do małych okien lokalnych w celu optymalizacji wydajności obliczeniowej. |
| Dane wyjściowe agenta | „Tryb agentowy JSON” | Strategia treningu wymuszająca na modelu generowanie precyzyjnych i parsujących się struktur JSON reprezentujących akcje agenta. |
| min_pixels / max_pixels | „Zakres rozdzielczości” | Parametry w Qwen2.5-VL kontrolujące minimalną i maksymalną liczbę pikseli obrazu, a tym samym liczbę generowanych tokenów. |
| Lokalizacja (Grounding) | „Wskazywanie obiektów” | Zadanie polegające na generowaniu współrzędnych ramek otaczających (bounding boxes) jako wyjściowych tokenów tekstowych. |

## Dalsze czytanie

- [Bai et al. — Qwen-VL (arXiv:2308.12966)](https://arxiv.org/abs/2308.12966)
- [Wang et al. — Qwen2-VL (arXiv:2409.12191)](https://arxiv.org/abs/2409.12191)
- [Qwen Team — Qwen2.5-VL Technical Report (arXiv:2502.13923)](https://arxiv.org/abs/2502.13923)
- [Qwen Team — Qwen3-VL (arXiv:2511.21631)](https://arxiv.org/abs/2511.21631)
- [Zhu et al. — InternVL3 (arXiv:2504.10479)](https://arxiv.org/abs/2504.10479)
