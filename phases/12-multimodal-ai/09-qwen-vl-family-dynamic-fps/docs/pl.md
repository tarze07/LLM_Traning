# Rodzina Qwen-VL i wideo z dynamicznym FPS

> Rodzina Qwen-VL — Qwen-VL (2023), Qwen2-VL (2024), Qwen2.5-VL (2025), Qwen3-VL (2025) — to najbardziej wpływowa linia modeli otwartego języka wizyjnego w 2026 r. Każde pokolenie dokonało jednego decydującego założenia architektonicznego, które reszta otwartego ekosystemu skopiowała w ciągu dwunastu miesięcy: natywna rozdzielczość dynamiczna za pośrednictwem M-RoPE, próbkowanie dynamiczne FPS w czasie bezwzględnym wyrównanie, uwaga okna w ViT i ustrukturyzowane formaty wyjściowe agenta. Dzięki Qwen3-VL przepis się ustabilizował: koder 2D-RoPE-ViT z wejściami o natywnych proporcjach obrazu, projektor MLP do dużej bazy językowej Qwen3 oraz etapy szkoleniowe, które kładły nacisk na OCR, uziemienie i zachowanie agenta jako cele najwyższej klasy. W tej lekcji rodzina jest czytana chronologicznie, dzięki czemu zrozumiesz, dlaczego każde pokrętło jest tam, gdzie jest.

**Typ:** Ucz się
**Języki:** Python (stdlib, koder M-RoPE + próbnik dynamiki FPS)
**Wymagania wstępne:** Faza 12 · 06 (patch-n'-pack)
**Czas:** ~120 minut

## Cele nauczania

- Oblicz obroty M-RoPE w trzech osiach (czas, wysokość, szerokość) i wyjaśnij, dlaczego potrzebne są wszystkie trzy.
- Wybierz strategię próbkowania dynamicznego FPS dla filmu i uzasadnij różnicę między liczbą tokenów na sekundę a dokładnością wykrywania zdarzeń.
- Wymień w kolejności cztery ulepszenia pokoleniowe Qwen-VL i określ, co każde z nich umożliwia.
— Podłącz format wyjściowy agenta JSON w stylu Qwen2.5-VL i przeanalizuj wywołania narzędzi strukturalnych z odpowiedzi VLM.

## Problem

Qwen-VL został dostarczony w sierpniu 2023 r. jako bezpośrednia odpowiedź na LLaVA-1.5 i BLIP-2. Luka, na którą celował zespół Qwen, była trojaka: rozdzielczość, wideo i ustrukturyzowane wyjście.

Rozdzielczość: LLaVA-1.5 działała w rozdzielczości 336x336. Dobry do zdjęć, bezużyteczny do faktury w języku chińskim lub gęstego zrzutu ekranu arkusza kalkulacyjnego. Pierwszą innowacją Qwen-VL była rozdzielczość 448x448 i uziemiona ramka ograniczająca, dzięki czemu model mógł wskazywać rzeczy.

Wideo: Video-LLaMA ułożyła w stos kodery poklatkowe i przekazała je do LLM. Działało to w przypadku krótkich klipów, a nie wielominutowych filmów, w których sygnałem jest oś czasowa. Zespół Qwen potrzebował jednego kodera, który rozumiałby czas.

Ustrukturyzowane dane wyjściowe: tekst w dowolnej formie emitowany przez LLaVA. Agent potrzebuje formatu JSON. Qwen-VL przeszkolony w zakresie jawnych formatów wyjściowych JSON, w tym współrzędnych ramki ograniczającej w postaci tekstu.

Każda generacja Qwen-VL rozszerza jedną z tych trzech osi.

## Koncepcja

### Qwen-VL (sierpień 2023 r.)

Pierwsza generacja: OpenCLIP ViT-bigG/14 jako enkoder (2,5B parametrów), Q-Former kompatybilny z LLama (1-krokowy z 256 zapytaniami), baza Qwen-7B. Wkład:

- Rozdzielczość 448x448 (wtedy SOTA dla otwartego VLM).
- Uziemienie: trenowane na parach obraz-tekst z jawnym wyjściem współrzędnych-tokenów. „Kot jest w <box>(112, 204), (280, 344)</box>”.
- Wielojęzyczne szkolenie chińskie i angielskie od samego początku.

Punkty odniesienia w tamtym czasie: konkurencyjny z GPT-4V w języku angielskim, dominujący w języku chińskim. Nadzór nad uziemieniem był prawdziwym nagłówkiem.

### Qwen2-VL (wrzesień 2024 r.) — M-RoPE i rozdzielczość natywna

Qwen2-VL zastąpił stos o stałej rozdzielczości + Q-Former natywnym koderem ViT o dynamicznej rozdzielczości. Kluczowe zmiany:

- Natywna rozdzielczość dynamiczna. ViT akceptuje dowolne HxW podzielne przez 28 (łata 14 z 2x scalaniem przestrzennym). Obraz o rozdzielczości 1120x672 (40x24 połączone obszary) tworzy 960 tokenów wizualnych. Bez zmiany rozmiaru, bez kafelkowania i bez miniatur.
- Lina M (Lina Multimodalna). Każdy żeton zawiera pozycję 3D (t, h, w) zamiast 1D. Dla obrazów t=0, dla wideo t = indeks_klatki. RoPE obraca wektory zapytań/kluczy o częstotliwość na oś. Brak tabeli osadzania pozycyjnego.
- Projektor MLP. Upuść Q-Formera; użyj 2-warstwowego MLP na połączonych żetonach łatek.
- Wideo z dynamicznym FPS. Wideo jest domyślnie próbkowane z częstotliwością 1-2 kl./s, ale model akceptuje dowolną liczbę klatek.

Wynik: Qwen2-VL-7B dorównał GPT-4o w kilku multimodalnych testach porównawczych i pobił go w DocVQA (94,5 vs 88,4). Decydującym posunięciem była zmiana architektury.

### Qwen2.5-VL (luty 2025) — dynamiczny FPS + czas bezwzględny

Największą zmianą w Qwen2.5-VL było wideo. Dynamiczny FPS to nie tylko „próbkowanie większej liczby klatek, jeśli zajdzie taka potrzeba”. W artykule sformalizowano:

- Żetony czasu bezwzględnego. Zamiast indeksów pozycyjnych (ramka 0, 1, 2...) użyj rzeczywistych znaczników czasu. „O 0:04 kot skacze.” Model widzi tokeny `<time>0.04</time>` przeplatane tokenami ramki.
- Dynamiczny FPS. Próbka przy 1 kl./s w przypadku powolnego materiału, 4+ kl./s w przypadku akcji. Użytkownik lub trener wybiera; M-RoPE dostosowuje się.
- Uwaga okienna w ViT. Uwaga przestrzenna jest okienkowa (lokalna w blokach) w celu zapewnienia przepustowości; globalna uwaga co kilka warstw.
- Jawny format wyjściowy JSON. Przeszkolony w zakresie danych wywołań narzędzi: „{„narzędzie”: „kliknięcie”, „współrzędne”: [380, 220]}”. Gotowy do pracy z agentem od razu po wyjęciu z pudełka.
- Skalowanie MRoPE-v2. Pozycje skalują się z maksymalnym rozmiarem wejściowym, więc 10-minutowy film nie wykracza poza zakres częstotliwości.

Testy porównawcze: Qwen2.5-VL-72B pokonuje GPT-4o w większości testów porównawczych wideo, dorównuje Gemini 2.0 w dokumentach i ustawia otwarty model SOTA dla uziemienia GUI (ScreenSpot: dokładność 84% w porównaniu z 38% dla GPT-4o).

### Qwen3-VL (listopad 2025)

Qwen3-VL to stopniowa aktualizacja, która raczej konsoliduje niż odkrywa na nowo: większy szkielet LLM (Qwen3-72B), rozszerzone dane szkoleniowe, ulepszony OCR, silniejsze rozumowanie poprzez „tryb myślenia” Qwen3. Pobyty ViT i M-RoPE. W artykule skupiono się na ulepszeniach danych i szkoleń w architekturze.

Wniosek na wynos: do 2025 roku architektura Qwen-VL ustabilizowała się. Dodatkowe generacje skalują obliczenia i dane, a nie rozwiązania pierwotne.

### M-RoPE matematycznie

Klasyczna RoPE obraca zapytanie `q` o wymiar `d` według pozycji `m` przy użyciu sparowanych współrzędnych:

```
q_rot[2i]   = q[2i]   * cos(m * theta_i) - q[2i+1] * sin(m * theta_i)
q_rot[2i+1] = q[2i]   * sin(m * theta_i) + q[2i+1] * cos(m * theta_i)
theta_i     = 10000^(-2i/d)
```

M-RoPE dzieli ukryty cień na trzy pasma. Powiedz `d = 96`. Przypisz 32 przyciemnienia do tymczasowego, 32 do wysokości i 32 do szerokości. Każde pasmo obraca się według własnego położenia osi. Łatka w (t=5, h=10, w=20) otrzymuje rotacje `R_t(5)`, `R_h(10)`, `R_w(20)` zastosowane do swoich trzech pasm.

Tokeny tekstowe używają `t = text_index, h = 0, w = 0` (lub znormalizowanego wyboru), zachowując kompatybilność. Klatki wideo wykorzystują `t = frame_time, h = row, w = col`. Pojedyncze obrazy używają `t = 0`.

Korzyść: kodowanie z jedną pozycją obsługuje tekst, obraz i wideo bez rozgałęziania kodu lub różnych tabel pozycji.

### Logika próbkowania dynamicznego FPS

Biorąc pod uwagę czas trwania filmu `T` sekund i budżet tokenów docelowych `B`:

1. Oblicz maksymalną liczbę klatek na sekundę, na jaką Cię stać: `fps_max = B / (T * tokens_per_frame)`.
2. Wybierz docelowy FPS z `{1, 2, 4, 8}`, który spełnia `fps <= fps_max`.
3. Jeśli ruch jest duży (heurystyka przepływu optycznego lub wyraźne żądanie użytkownika), wybierz wyższą liczbę klatek na sekundę. Jeśli ruch jest niski, wybierz niższy.
4. Próbkuj równomiernie w wybranym FPS; wstaw tokeny `<time>t</time>` pomiędzy ramkami.

Qwen2.5-VL pośrednio ćwiczy tę logikę; przy wnioskowaniu użytkownik kontroluje poprzez parametr `fps`. 60-sekundowa sekwencja akcji przy 4 FPS z 81 tokenami na klatkę = 19440 tokenów, którymi można zarządzać w kontekście 32 tys.

### Ustrukturyzowane dane wyjściowe agenta

Szkolenie agentów Qwen2.5-VL jest wyraźnie ukierunkowane na wywołania narzędzi strukturalnych:

```
{
  "tool": "mouse_click",
  "coords": [1024, 512],
  "button": "left",
  "modifier": null
}
```

Analiza jest deterministyczna: JSON.parse na wyjściu modelu. Porównaj z swobodną formą „kliknij na (1024, 512)”, która wymagała obsługi wyrażeń regularnych i niejednoznaczności. Ta zmiana spowodowała, że ​​wyniki Qwen2.5-VL w ScreenSpot wzrosły z 55% do 84%.

## Użyj tego

`code/main.py` implementuje:

- Obliczanie pozycji M-RoPE dla upakowanej sekwencji łączącej tekst, fragmenty obrazów i klatki wideo.
- Próbnik dynamicznej liczby klatek na sekundę: podany (czas trwania, budżet, poziom_ruchu), wybierz liczbę klatek na sekundę i wyemituj znaczniki czasu klatek.
- Zabawkowy parser wyjściowy JSON Qwen2.5-VL, który obsługuje odpowiedzi na wywołania narzędzi z polami współrzędnych.

Uruchom go, a poczujesz różnicę, zamieniając stałą liczbę klatek na sekundę na dynamiczną liczbę klatek na sekundę w 5-minutowym filmie.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-qwen-vl-pipeline-designer.md`. Biorąc pod uwagę zadanie wideo (monitorowanie, agent, rozpoznawanie akcji, dostępność), emituje konfigurację Qwen2.5-VL (budżet ramki, strategia FPS, flaga uwagi okna, tryb wyjściowy agenta) i szacunkowe opóźnienie. Użyj tej opcji za każdym razem, gdy wdrażasz model rodziny Qwen-VL dla produktu wideo.

## Ćwiczenia

1. Oblicz obroty M-RoPE dla fragmentu w (t=3, h=5, w=7) z ukrytymi 48 (16 na pasmo, podstawa theta 10000). Pokaż kąty obrotu dla pierwszych trzech par w każdym paśmie.

2. Ile klatek tworzy 10-minutowe nagranie z kamery bezpieczeństwa przy 1 kl./s? Ile tokenów ogółem przy rozdzielczości 384 i 3x puli? Czy domyślny kontekst 32 KB Qwen2.5-VL sobie z tym radzi?

3. Wybierz FPS dla 30-sekundowego rajdu tenisowego, 30-sekundowego pokazu przepisu lub 30-sekundowego nagrania agenta interfejsu użytkownika. Uzasadnij każdy za pomocą logiki dynamicznego FPS.

4. Qwen2.5-VL całkowicie porzuca Q-Former. Dlaczego prosty MLP działa w 2025 r., a nie w 2023 r.? (Wskazówka: skala danych i jakość kodera.)

5. Przeanalizuj trzy wyjścia wywołań narzędzi Qwen2.5-VL JSON w słowniki Pythona. Co zawodzi w przypadku zniekształconego JSON i jaką strategię odzyskiwania zaleca książka kucharska Qwen?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|--------------------------------------|
| Lina M | „Lina multimodalna” | Osadzanie pozycji obrotowej 3D z pasmami czasowymi, wysokościowymi i szerokościowymi w ukrytym przyciemnieniu |
| Dynamiczny FPS | „Inteligentne pobieranie próbek” | Częstotliwość próbkowania klatek wybrana dla filmu na podstawie ruchu, czasu trwania i budżetu tokenów |
| Absolutny znacznik czasu | „Token znacznika czasu” | `<time>t</time>` przeplatane w sekwencji, tak aby model widział rzeczywiste sekundy, a nie indeks klatek |
| Uwaga okna | „Lokalna uwaga” | Przestrzenna samouważność ograniczona do małych okien ze względu na szybkość; uwaga globalna dodawana okresowo |
| Dane wyjściowe agenta strukturalnego | „Tryb JSON” | Nadzór nad danymi szkoleniowymi, ucząc VLM emitowania parsowalnego JSON ze współrzędnymi i nazwami narzędzi |
| min_piksele / maks._piksele | „Granice rozdzielczości” | Na żądanie Qwen2.5-VL kontroluje całkowitą liczbę pikseli, a tym samym liczbę tokenów |
| Uziemienie | „Wskaż to” | Wyprowadzanie współrzędnych obwiedni jako tokenów tekstowych; używany od Qwen-VL v1 |

## Dalsze czytanie

- [Bai i in. — Qwen-VL (arXiv:2308.12966)](https://arxiv.org/abs/2308.12966)
- [Wang i in. — Qwen2-VL (arXiv:2409.12191)](https://arxiv.org/abs/2409.12191)
— [Zespół Qwen — raport techniczny Qwen2.5-VL (arXiv:2502.13923)](https://arxiv.org/abs/2502.13923)
- [Zespół Qwen — Qwen3-VL (arXiv:2511.21631)](https://arxiv.org/abs/2511.21631)
- [Zhu i in. — InternVL3 (arXiv:2504.10479)](https://arxiv.org/abs/2504.10479)