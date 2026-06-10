# Transformatory wizyjne i prymitywne żetony łatek

> Zanim powstanie cokolwiek multimodalnego, obraz musi stać się sekwencją żetonów, które transformator może zjeść. Artykuł ViT 2020 odpowiedział na to pytanie, oferując plamy o wymiarach 16 x 16 pikseli, projekcję liniową i osadzanie pozycji. Pięć lat później każdy model frontierowy z 2026 r. (Claude Opus 4.7 w natywnej rozdzielczości 2576 pikseli, Gemini 3.1 Pro, Qwen3.5-Omni) nadal zaczyna się w ten sposób — zmieniono koder z ViT na DINOv2 na SigLIP 2, dodano tokeny rejestrów, schemat pozycyjny stał się 2D-RoPE, ale prymityw pozostał. W tej lekcji czytamy potok tokenów łatek od początku do końca i budujemy go w stdlib Python, dzięki czemu w pozostałej części fazy 12 mamy konkretny model mentalny dla „tokenów wizualnych”.

**Typ:** Ucz się
**Języki:** Python (stdlib, tokenizer łatek + kalkulator geometrii)
**Wymagania wstępne:** Faza 7 (Transformatory), Faza 4 (Wizja komputerowa)
**Czas:** ~120 minut

## Cele nauczania

- Konwertuj obraz WxSx3 na sekwencję żetonów poprawek z prawidłowym kodowaniem pozycyjnym.
- Oblicz długość sekwencji, liczbę parametrów i wartości FLOP dla ViT o danym (rozmiar obszaru, rozdzielczość, ukryte przyciemnienie, głębokość).
- Wymień trzy ulepszenia, które umożliwiły ViT od badań w 2020 r. do produkcji w 2026 r.: samonadzorowane szkolenie wstępne (DINO / MAE), tokeny rejestracyjne i pakowanie w rozdzielczości natywnej.
- Wybierz pomiędzy łączeniem CLS, łączeniem średnich i rejestrowaniem tokenów dla kolejnego zadania.

## Problem

Transformatory działają na ciągach wektorów. Tekst jest już sekwencją (bajty lub tokeny). Obraz to dwuwymiarowa siatka pikseli z trzema kanałami kolorów, a nie sekwencja. Jeśli spłaszczysz każdy piksel, obraz RGB o wymiarach 224x224 stanie się 150 528 tokenami, a samouważność przy tej długości nie będzie początkiem (długość sekwencji kwadratowa).

Podejścia sprzed 2020 r. przykręciły ekstraktor cech CNN z przodu: ResNet tworzy mapę cech 7x7 złożoną z wektorów o 2048 przyciemnionych wektorach i przekazuje te 49 tokenów do transformatora. To działa, ale dziedziczy uprzedzenia CNN (równoważność tłumaczenia, lokalne pola recepcyjne) i traci apetyt transformatora na skalę.

Dosovitskiy i in. (2020) zadali bez ogródek pytanie: co jeśli pominiemy CNN? Podziel obraz na fragmenty o stałym rozmiarze (powiedzmy 16x16 pikseli), liniowo wyświetl każdy fragment w wektorze, dodaj osadzenie pozycyjne i wprowadź sekwencję do transformatora waniliowego. W tamtym czasie była to herezja – wizja bez zwojów. Mając wystarczającą ilość danych (JFT-300M, potem LAION), pobił ResNet w ImageNet i ciągle się poprawiał.

Do roku 2026 prymityw ViT stanie się niekwestionowanym fundamentem. Każda wieża wizyjna VLM o wadze otwartej jest jakimś potomkiem (DINOv2, SigLIP 2, CLIP, EVA, InternViT). Pytanie nie brzmi już: „czy powinniśmy używać łatek?” ale „jaki rozmiar poprawki, jaki harmonogram rozdzielczości, jaki cel wstępnego szkolenia, jakie kodowanie pozycyjne”.

## Koncepcja

### Poprawki jako tokeny

Biorąc pod uwagę obraz `x` o kształcie `(H, W, 3)` i rozmiar fragmentu `P`, wycinasz obraz w siatkę `(H/P) x (W/P)` nienakładających się na siebie fragmentów. Każda poprawka to `P x P x 3` sześcian pikseli. Spłaszcz każdą kostkę do wektora `3 P^2`. Zastosuj współdzielony rzut liniowy `W_E` kształtu `(3 P^2, D)`, aby zmapować każdą poprawkę na ukryty wymiar modelu `D`.

Dla konfiguracji kanonicznej ViT-B/16:
- Rozdzielczość 224, rozmiar łatki 16 → siatka 14x14 → 196 żetonów łatki.
- Każda poprawka ma `16 x 16 x 3 = 768` wartości pikseli, rzutowane na `D = 768`.
- Dodaj możliwy do nauczenia token `[CLS]` → długość sekwencji 197.

Projekcja poprawki jest matematycznie identyczna ze splotem 2D z kanałami wyjściowymi o rozmiarze jądra `P`, kroku `P` i `D`. Tak to faktycznie implementuje kod produkcyjny — `nn.Conv2d(3, D, kernel_size=P, stride=P)`. Kadrowanie „projekcji liniowej” ma charakter koncepcyjny; ramka jądra jest wydajna.

### Osadzenia pozycyjne

Plastry nie mają wrodzonego porządku – transformator postrzega je jako torbę. Wczesne ViT dodały możliwe do nauczenia osadzanie pozycyjne 1D (jeden wektor o 768 przyciemnieniach na pozycję, 197 z nich). Działa, ale wiąże model z rozdzielczością treningową: przy wnioskowaniu musisz interpolować tabelę pozycji, jeśli zmienisz siatkę.

Nowoczesne szkielety wizyjne wykorzystują 2D-RoPE (M-RoPE w Qwen2-VL, domyślnie w SigLIP 2) lub faktoryzowane pozycje 2D. 2D-RoPE obraca wektory zapytania i klucza w oparciu o indeks poprawki (wiersz, kolumna), dzięki czemu model wnioskuje względną pozycję 2D na podstawie kąta obrotu. Brak tabeli pozycji. Model obsługuje dowolne rozmiary siatki podczas wnioskowania.

### Token CLS, zbiorcze dane wyjściowe i tokeny rejestrów

Jaka jest reprezentacja na poziomie obrazu? Współistnieją trzy możliwości:

1. Token `[CLS]`. Dołącz możliwy do nauczenia wektor do sekwencji łatek. W końcu wszystkie bloki transformatorów stanem ukrytym tokena CLS jest reprezentacja obrazu. Odziedziczony po BERT. Używany przez oryginalny ViT, CLIP.
2. Średni basen. Uśrednij ukryte stany wyjściowe tokenów łatek. Używany przez SigLIP, DINOv2, większość nowoczesnych VLM.
3. Zarejestruj tokeny. Darcet i in. (2023) zaobserwowali, że ViT wyszkoleni bez wyraźnego tokena ujścia tworzą plamy „artefaktów” o wysokich normach, które przejmują samouwagę. Dodanie 4–16 możliwych do nauczenia się tokenów rejestrów pochłania to obciążenie i poprawia jakość gęstego przewidywania (segmentacja, głębokość). Zarówno DINOv2, jak i SigLIP 2 są dostarczane z rejestrami.

Wybór ma znaczenie w przypadku dalszych zadań. CLS jest dobry do klasyfikacji. W przypadku VLM, które dostarczają tokeny łatek do LLM, całkowicie pomijasz łączenie — każda łatka staje się tokenem wejściowym LLM. Rejestry są odrzucane przed przekazaniem (są rusztowaniem, a nie treścią).

### Trening wstępny: nadzorowany, kontrastowy, zamaskowany, samodestylowany

ViT 2020 został wstępnie przeszkolony z nadzorowaną klasyfikacją na JFT-300M. Szybko zastąpiony przez:

- CLIP (2021): kontrastowy obraz-tekst na 400 milionach par. Lekcja 12.02.
- MAE (2021, He i in.): zamaskuj 75% plam, zrekonstruuj piksele. Samodzielnie nadzorowany, pracuje na czystych obrazach.
- DINO (2021) / DINOv2 (2023): autodestylacja z uczniem-nauczycielem, bez etykiet i podpisów. DINOv2 ViT-g/14 2023 to najsilniejszy szkielet czysto wizualny i domyślny w przypadkach użycia „gęstych funkcji”.
- SigLIP / SigLIP 2 (2023, 2025): CLIP z utratą esicy i NaFlex dla natywnych proporcji. Dominująca wieża wizyjna w otwartych VLM w 2026 roku (Qwen, Idefics2, LLaVA-OneVision).

Twój wybór wstępnego uczenia określa, do czego nadaje się szkielet: CLIP/SigLIP do dopasowywania semantycznego z tekstem, DINOv2 do gęstych cech wizualnych, MAE jako punkt wyjścia do dostrajania w dalszej części.

### Prawa skalowania

Skalowanie ViT (Zhai i in. 2022) ustaliło, że jakość ViT jest zgodna z przewidywalnymi prawami dotyczącymi rozmiaru modelu, rozmiaru danych i obliczeń. Przy stałych obliczeniach:
- Większy model + więcej danych → lepsza jakość.
- Rozmiar łaty to dźwignia określająca długość sekwencji w stosunku do wierności. Łatka 14 (typowa dla DINOv2/SigLIP SO400m) daje więcej tokenów na obraz niż łatka 16; lepszy dla OCR i gęstych zadań, gorszy dla szybkości.
- Rozdzielczość to kolejna ważna dźwignia. Przejście z 224 na 384 na 512 prawie zawsze pomaga, przy koszcie kwadratowym we FLOPach.

ViT-g/14 (parametry 1B, poprawka 14, rozdzielczość 224 → 256 tokenów) i SigLIP SO400m/14 (parametry 400M, poprawka 14) to dwa wydajne kodery dla otwartych VLM na rok 2026.

### Liczba parametrów dla ViT

Pełne obliczenia znajdują się w `code/main.py`. Dla ViT-B/16 pod adresem 224:

```
patch_embed = 3 * 16 * 16 * 768 + 768  =  591k
cls + pos    = 768 + 197 * 768          =  152k
block        = 4 * 768^2 (QKVO) + 2 * 4 * 768^2 (MLP) + 2 * 2*768 (LN)
             = 12 * 768^2 + 3k          =  7.1M
12 blocks    = 85M
final LN    = 1.5k
total       ≈ 86M
```

Zaparkuj piłkę w ten sposób przed załadowaniem punktu kontrolnego. Rozmiar szkieletu określa minimalną ilość pamięci VRAM w dowolnym dalszym VLM.

### Konfiguracja produkcyjna 2026

Najbardziej otwartym koderem VLM dostępnym na rynku w 2026 r. będzie SigLIP 2 SO400m/14 w rozdzielczości natywnej (NaFlex). Posiada:
- Parametry 400M.
- Rozmiar łatki 14, domyślna rozdzielczość 384 → 729 tokenów łatki na obraz.
- Średnia pula dla zadań na poziomie obrazu; wszystkie 729 poprawek trafia do LLM dla VQA.
- 4 żetony rejestru, odrzucone przed przekazaniem LLM.
- 2D-RoPE ze skalowaniem na poziomie obrazu dla natywnych proporcji.

Każda decyzja w tej konfiguracji ma swój początek w dokumencie, który możesz przeczytać.

## Użyj tego

`code/main.py` to tokenizator poprawek i kalkulator geometrii. Zajmuje (obraz H, W, łata P, ukryte D, głębokość L) i raportuje:

- Kształt siatki i długość sekwencji po załataniu.
- Sekwencja tokenów dla syntetycznego obrazu zabawki o wymiarach 8x8 pikseli (przejście przez spłaszczenie + ścieżkę projektu).
- Liczba parametrów z podziałem na osadzoną łatę, osadzoną pozycję, bloki transformatora i głowicę.
- FLOPy na przejście do przodu przy docelowej rozdzielczości.
- Tabela porównawcza dla ViT-B/16 @ 224, ViT-L/14 @ 336, DINOv2 ViT-g/14 @ 224, SigLIP SO400m/14 @ 384.

Uruchom to. Dopasuj liczbę parametrów do opublikowanych liczb. Baw się rozmiarem i rozdzielczością łatki, aby poznać koszt liczenia tokenów.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-patch-geometry-reader.md`. Biorąc pod uwagę konfigurację ViT (rozmiar poprawki, rozdzielczość, ukryte przyciemnienie, głębokość), generuje ona liczbę tokenów, liczbę parametrów i oszacowanie pamięci VRAM z uzasadnieniami. Użyj tej umiejętności za każdym razem, gdy wybierzesz szkielet wizji dla VLM — zapobiega to niespodziankom w postaci „eksplodacji tokenów i zapełnienia kontekstu LLM”.

## Ćwiczenia

1. Oblicz długość sekwencji tokena poprawki dla Qwen2.5-VL przy natywnej rozdzielczości wejściowej 1280x720 i rozmiarze poprawki 14. Jak to się ma do reprezentacji wyłącznie CLS?

2. Ile tokenów tworzy klatka 1080p (1920x1080) w patchu 14? Ile tokenów wizualnych łącznie wynosi 30 klatek na sekundę w ciągu 5 minut wideo? Który koszt pozwala zaoszczędzić najwięcej: łączenie, próbkowanie klatek czy łączenie tokenów?

3. Zaimplementuj średnie łączenie tokenów poprawek w czystym Pythonie. Sprawdź, czy średnia pula ponad 196 tokenów wyjścia DINOv2 odpowiada temu, co zwraca `forward` modelu, gdy poprosisz o osadzenie zbiorcze.

4. Przeczytaj sekcję 3 „Rejestrów potrzebnych transformatorom wizyjnym” (arXiv:2309.16588). Opisz w dwóch zdaniach, jakie artefakty pochłaniają rejestry i dlaczego ma to znaczenie dla przewidywania gęstości w dół.

5. Zmodyfikuj `code/main.py`, aby obsługiwał patch-n'-pack: mając listę obrazów o różnych rozdzielczościach, utwórz pojedynczą spakowaną sekwencję i maskę uwagi o przekątnej blokowej. Gdy dotrzesz do tego, sprawdź lekcję 12.06.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Łatka | „Kwadrat 16x16 pikseli” | Nienakładający się obszar obrazu wejściowego o stałym rozmiarze; staje się jednym żetonem |
| Osadzanie poprawek | „Rzut liniowy” | Wspólna wyuczona macierz (lub Conv2d ze stride=P) mapująca spłaszczone piksele plamy na wektory D-dim |
| Token CLS | „Token klasy” | Dołączony wektor, którego można się nauczyć, którego ostateczny stan ukryty reprezentuje cały obraz; opcjonalne w 2026 r. |
| Zarejestruj token | „Token ujścia” | Dodatkowe tokeny, których można się nauczyć, które pochłaniają artefakty uwagi o wysokich normach, które ViT rozwijają podczas treningu wstępnego |
| Osadzanie pozycji | „Informacje o pozycji” | Wektor lub rotacja dla poszczególnych pozycji, dzięki czemu kolejność sekwencji jest świadoma; 2D-RoPE jest nowoczesnym rozwiązaniem domyślnym |
| Siatka | „Siatka poprawek” | Tablica łatek (H/P) x (W/P) 2D dla danej rozdzielczości i rozmiaru łaty |
| NaFlex | „Natywna elastyczna rozdzielczość” | Funkcja SigLIP 2: pojedynczy model obsługuje wiele współczynników proporcji i rozdzielczości bez konieczności ponownego szkolenia |
| Kręgosłup | „Wieża wizji” | Wstępnie wyszkolony koder obrazu, którego dane wyjściowe tokenów poprawek zasilają LLM w VLM |
| Łączenie | „Podsumowanie na poziomie obrazu” | Strategia przekształcania tokenów łatek w jeden wektor: CLS, średnia, pula uwagi lub oparta na rejestrach |
| Łatka 14 vs 16 | „Drobniejsza i grubsza siatka” | Poprawka 14 wytwarza więcej tokenów na obraz, lepszą wierność OCR i wolniej; łatka 16 jest klasyczną wersją domyślną |

## Dalsze czytanie

- [Dosovitskiy i in. — Obraz jest wart 16 x 16 słów (arXiv:2010.11929)](https://arxiv.org/abs/2010.11929) — oryginał ViT.
- [On i in. — Zamaskowane autoenkodery to skalowalne urządzenia uczące się ze wzrokiem (arXiv:2111.06377)](https://arxiv.org/abs/2111.06377) — MAE, samonadzorowane szkolenie wstępne.
- [Oquab i in. — DINOv2 (arXiv:2304.07193)](https://arxiv.org/abs/2304.07193) — samodestylacja na dużą skalę, bez etykiet.
- [Darcet i in. — Transformatory wizyjne potrzebują rejestrów (arXiv:2309.16588)](https://arxiv.org/abs/2309.16588) — tokeny rejestrów i analiza artefaktów.
- [Tschannen i in. — SigLIP 2 (arXiv:2502.14786)](https://arxiv.org/abs/2502.14786) — domyślna wieża wizyjna na rok 2026.
- [Zhai i in. — Skalujące transformatory wizyjne (arXiv:2106.04560)](https://arxiv.org/abs/2106.04560) — empiryczne prawa skalowania.