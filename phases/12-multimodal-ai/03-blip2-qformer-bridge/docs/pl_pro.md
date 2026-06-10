# Od CLIP do BLIP-2 — Q-Former jako mostek modalny

> CLIP skutecznie dopasowuje obrazy i teksty, ale nie potrafi generować opisów, odpowiadać na pytania ani prowadzić konwersacji. Projekt BLIP-2 (Salesforce, 2023) rozwiązał ten problem za pomocą niewielkiego, trenowalnego adaptera: 32 trenowalne wektory zapytań (queries) przetwarzają reprezentacje z zamrożonego encodera ViT za pomocą mechanizmu cross-attention, a następnie trafiają bezpośrednio do warstwy wejściowej zamrożonego modelu LLM. Ten mostek o rozmiarze 188M parametrów połączył LLM o rozmiarze 11B z ViT-g/14. Praktycznie każdy VLM oparty na adapterach powstały do 2026 roku — w tym MiniGPT-4, InstructBLIP czy modele z rodziny LLaVA — jest jego bezpośrednim następcą. W tej lekcji zapoznamy się z architekturą Q-Formera, wyjaśnimy jego dwuetapowe uczenie wstępne (pretraining) i zbudujemy uproszczoną wersję, która wprowadza tokeny wizualne do dekodera zamrożonego modelu tekstowego.

**Typ:** Projekt / Implementacja
**Języki:** Python (biblioteka standardowa, cross-attention + demonstracja trenowalnych zapytań)
**Wymagania:** Faza 12 · Lekcja 02 (CLIP), Faza 7 (Transformatory)
**Czas:** ~180 minut

## Cele nauczania

- Wyjaśnij, dlaczego trenowalne wąskie gardło (bottleneck) pomiędzy zamrożonym encoderem wizyjnym a zamrożonym LLM jest lepszym rozwiązaniem pod kątem kosztów i stabilności niż pełne dostrajanie (full fine-tuning).
- Zaimplementuj blok cross-attention, w którym ustalony zestaw trenowalnych zapytań przetwarza zewnętrzne cechy obrazu.
- Przejdź przez dwuetapowe uczenie wstępne BLIP-2: etap reprezentacji (ITC + ITM + ITG), a następnie etap generatywny (strata LM z zamrożonym dekoderem).
- Porównaj Q-Former z prostszym projektorem MLP stosowanym w LLaVA i wskaż sytuacje, w których każdy z tych wyborów sprawdza się lepiej.

## Problem

Masz zamrożony model ViT, który generuje 256 tokenów patchy o wymiarze (dim) 1408 na jeden obraz. Masz także zamrożony LLM 7B, który oczekuje wejściowych embeddingów tokenów o wymiarze 4096. Najprostszy mostek — warstwa liniowa mapująca z 1408 do 4096 — działa, ale przekazanie wszystkich 256 tokenów patchy do kontekstu LLM zużywa 256 dodatkowych tokenów na każdy obraz. Przy wielkości paczki (batch size) równej 32 daje to 8192 tokenów zużytych wyłącznie na samą modalność wizualną.

Pytanie postawione w BLIP-2 brzmi: czy można skompresować reprezentację obrazu z 256 tokenów do znacznie mniejszej liczby (np. 32), zachowując przy tym wystarczająco dużo informacji, by LLM mógł wygenerować opis, odpowiadać na pytania i wnioskować na podstawie obrazu? Czy da się wytrenować ten mostek bez modyfikowania zamrożonych modeli bazowych, utrzymując koszty treningu na poziomie liczby parametrów samego adaptera?

Rozwiązaniem jest Q-Former: 32 trenowalne wektory „zapytań” (queries), które łączą się z tokenami patchy ViT, tworząc 32-tokenowe wizualne podsumowanie dla LLM. Całość ma zaledwie 188M parametrów i jest trenowana za pomocą celów kontrastowych, dopasowujących oraz generatywnych jeszcze przed podłączeniem LLM.

## Koncepcja

### Trenowalne zapytania (Learnable Queries)

Główna idea Q-Formera polega na tym, że zamiast pozwalać tokenom tekstowym LLM na bezpośrednie przetwarzanie patchy obrazu, wprowadzamy nowy zestaw 32 trenowalnych wektorów zapytań `Q` i to *im* powierzamy to zadanie. Zapytania te są parametrami modelu — są optymalizowane podczas treningu i dla każdego obrazu używa się tych samych 32 zapytań początkowych.

Po przejściu przez mechanizm cross-attention każde zapytanie zawiera skompresowane podsumowanie cech obrazu — np. „opisz główny obiekt”, „opisz tło”, „policz obiekty” itp. Zapytania nie specjalizują się dosłownie w konkretnych etykietach semantycznych; uczą się dowolnego kodowania, które najlepiej minimalizuje stratę w zadaniach wyjściowych.

### Architektura

Q-Former to niewielki transformator (12 warstw, ~100M parametrów) składający się z dwóch ścieżek:

1. Ścieżka zapytań (Query): 32 wektory zapytań przechodzą przez mechanizm self-attention (wzajemna uwaga między zapytaniami), następnie przez cross-attention z zamrożonymi tokenami patchy z ViT, a na końcu przez sieć FFN.
2. Ścieżka tekstowa: encoder tekstu (podobny do BERT) współdzieli wagi self-attention oraz FFN ze ścieżką zapytań. W przypadku ścieżki tekstowej mechanizm cross-attention z cechami obrazu jest wyłączony.

Podczas treningu aktywne są obie ścieżki. Zapytania i tekst oddziałują na siebie poprzez wspólną warstwę self-attention, dzięki czemu zapytania mogą dostosowywać się do tekstu w zadaniach, które tego wymagają (ITM, ITG). Przy wnioskowaniu (inference) w pełnym modelu VLM uruchamiana jest tylko ścieżka zapytań, dając w efekcie 32 tokeny wizualne.

### Szkolenie dwuetapowe

Uczenie wstępne BLIP-2 składa się z dwóch etapów:

Etap 1: Nauka reprezentacji (bez udziału LLM). Optymalizowane są trzy funkcje straty:
- ITC (Image-Text Contrastive loss): strata kontrastowa w stylu CLIP pomiędzy zagregowanymi tokenami zapytań a tokenem tekstowym CLS.
- ITM (Image-Text Matching loss): klasyfikator binarny oceniający, czy dana para obraz-tekst jest dopasowana (stosuje się tu hard-negative mining).
- ITG (Image-grounded Text Generation loss): przyczynowa (causal) strata językowa LM na tekście warunkowanym zapytaniami. Wymusza to na zapytaniach kodowanie informacji niezbędnych do wygenerowania tekstu.

W tym etapie trenowany jest wyłącznie Q-Former. ViT pozostaje zamrożony. Model LLM nie jest używany.

Etap 2: Nauka generatywna. Podłączamy zamrożony LLM (np. OPT-2.7B, Flan-T5-XL itp.). Mapujemy 32 wyjściowe wektory zapytań na wymiarowość embeddingów LLM za pomocą małej warstwy liniowej. Dołączamy je do promptu tekstowego. Trenujemy tylko projekcję liniową i Q-Former na zadaniu modelowania języka (LM loss) dla połączonej sekwencji prompt + obraz + opis.

Po zakończeniu Etapu 2 duet Q-Former + projekcja działa jako kompletny adapter wizualny. Proces wygląda następująco: obraz → ViT → Q-Former → projekcja liniowa → dołączenie do tekstu → zamrożony LLM generujący odpowiedź.

### Ekonomia parametrów

BLIP-2 z ViT-g/14 (1.1B parametrów, zamrożony) + OPT-6.7B (6.7B parametrów, zamrożony) + Q-Former (188M parametrów, trenowany) = łącznie 8B parametrów, z czego trenujemy tylko 188M. Sam Q-Former stanowi zaledwie ~2,4% parametrów całego stosu. Odzwierciedla to koszt treningu: dni na kilku kartach A100 w porównaniu do tygodni przy pełnym dostrajaniu.

Pod kątem jakości: BLIP-2 osiąga wyniki porównywalne lub lepsze niż Flamingo-80B w zadaniach zero-shot VQA, będąc od niego 50 razy mniejszym. Ten mostek po prostu działa.

### InstructBLIP i Q-Former uwzględniający instrukcje

InstructBLIP (2023) rozszerza Q-Formera o dodatkowe dane wejściowe: sam tekst instrukcji. W warstwie self-attention zapytania mają teraz dostęp zarówno do patchy obrazu, jak i do treści instrukcji. Dzięki temu zapytania mogą dostosować się do konkretnego polecenia („policz samochody”, „opisz nastrój”), zamiast generować jedno, uniwersalne podsumowanie. Przekłada się to na lepsze wyniki w benchmarkach na nowych zadaniach.

### MiniGPT-4 i podejście oparte wyłącznie na projektorze

MiniGPT-4 wykorzystywał Q-Formera, ale trenował wyłącznie wyjściową projekcję liniową, zamrażając całą resztę. Było to tanie w realizacji, ale cierpiała na tym jakość — zapytania były zoptymalizowane pod kątem BLIP-2, a nie pod Twój docelowy model. To dobre rozwiązanie do szybkiej iteracji, ale nie jest to optymalna architektura.

### Dlaczego LLaVA postawiła na prostotę

LLaVA (2023, Lekcja 12.05) zastąpiła Q-Formera zwykłym, 2-warstwowym modułem MLP, który mapuje każdy token patchy ViT bezpośrednio do przestrzeni LLM — co daje 576 tokenów na obraz przy siatce 24x24 podawanych wprost do LLM. Oznacza to brak kompresji, ale pozwala LLM na przetwarzanie surowych patchy. Początkowo budziło to kontrowersje, lecz pod koniec 2023 roku podejście to zdominowało architekturę, ponieważ dane instruktażowe (LLaVA-Instruct-150k) wykazały, że MLP można skutecznie wyuczyć tak, aby zachować pełny sygnał. Kompromis: kontekst LLaVA zapełnia się szybciej, ale model naturalnie skaluje się do wielu obrazów i wideo.

Do 2026 roku podział ról się ustabilizował: Q-Former sprawdza się tam, gdzie kluczowy jest budżet tokenów (długie wideo, wiele obrazów), natomiast projektor MLP dominuje w zadaniach, gdzie priorytetem jest najwyższa jakość na token.

### Bramkowana uwaga (Gated Attention): Flamingo jako protoplasta

Flamingo (Lekcja 12.04) jest projektem starszym niż BLIP-2 i wykorzystywał ten sam pomysł uczenia zapytań poprzez cross-attention, ale robił to wewnątrz każdej zamrożonej warstwy LLM, a nie jako pojedynczy mostek na wejściu. BLIP-2 udowodnił, że kompresję można wykonać wyłącznie na poziomie warstwy wejściowej i wciąż uzyskiwać świetne wyniki. Modele takie jak Gemini czy Idefics łączą oba podejścia: przeplatane tokeny wejściowe oraz opcjonalną bramkowaną uwagę krzyżową (gated cross-attention) dla uczenia few-shot w kontekście.

### Następcy i warianty w roku 2026

- Q-Former: BLIP-2, InstructBLIP, MiniGPT-4 oraz większość modeli wideo-językowych (ze względu na ograniczenia budżetu tokenów).
- Perceiver Resampler: wariant z Flamingo (Lekcja 12.04); używany w rodzinie Idefics, Eagle, OmniMAE.
- Projektor MLP: LLaVA, LLaVA-NeXT, LLaVA-OneVision, Cambrian-1.
- Attention Pooling: VILA, PaliGemma.

Wszystkie cztery podejścia są istotne. Decydującym kryterium wyboru jest to, czy ogranicza Cię budżet tokenów, czy zależy Ci na maksymalnej jakości każdego tokena.

## Użycie praktyczne

Skrypt `code/main.py` tworzy uproszczoną implementację Q-Formera w czystym Pythonie:

1. Symuluje 256 tokenów patchy obrazu (o wymiarze 128).
2. Tworzy zestaw 32 trenowalnych zapytań (o wymiarze 128).
3. Wykonuje operację scaled dot-product cross-attention (Q z zapytań, K/V z patchy).
4. Mapuje wynik na wymiar LLM (512) za pomocą warstwy liniowej.
5. Zwraca 32 tokeny wizualne przygotowane do podania do LLM.

Cała matematyka została zaimplementowana w czystym Pythonie (zagnieżdżone pętle na wektorach) w celach demonstracyjnych. Skrypt wypisuje macierz wag uwagi, co pozwala zaobserwować, z których patchy dane zapytanie pobierało informacje.

## Zadanie zaliczeniowe

W ramach tej lekcji należy stworzyć dokument `outputs/skill-modality-bridge-picker_pro.md`. Na podstawie podanej specyfikacji VLM (liczba tokenów encodera, budżet kontekstu LLM, ograniczenia wdrożeniowe, cel jakościowy), zarekomenduj wybór pomiędzy Q-Former, MLP a Perceiver Resampler, dołączając zwięzłe uzasadnienie oraz szacunkową liczbę parametrów dla każdego mostka.

## Ćwiczenia

1. Zaimplementuj blok cross-attention w PyTorch. Upewnij się, że przy 32 zapytaniach i 256 kluczach/wartościach macierz wag uwagi ma wymiar 32 x 256, a każdy wiersz sumuje się do 1 po zastosowaniu funkcji softmax.

2. W 1. etapie BLIP-2 Q-Former optymalizuje jednocześnie trzy funkcje straty: ITC, ITM oraz ITG. Zapisz sygnaturę metody forward dla każdej z nich w pseudokodzie. Która z nich wymaga aktywnej ścieżki encodera tekstu?

3. Porównaj liczbę parametrów: Q-Former (12 warstw, wymiar ukryty 768) vs 2-warstwowy projektor MLP (1408 → 4096, dwie warstwy). Przy jakiej skali modelu LLM koszt 188M parametrów Q-Formera zwraca się dzięki wyższej efektywności uczenia?

4. Przeczytaj sekcję 3.2 artykułu BLIP-2 (arXiv:2301.12597) na temat inicjalizacji Q-Formera. Wyjaśnij, dlaczego inicjalizacja wagami modelu BERT-base (zamiast losowej) przyspiesza zbieżność procesu uczenia.

5. Dla 10-minutowego wideo próbkowanego z częstotliwością 1 kl./s (łącznie 600 klatek), oblicz koszt tokenów na klatkę przy użyciu: (Q-Former → 32 tokeny/klatkę) vs (projektor MLP → 576 tokenów/klatkę). Które z tych rozwiązań zmieści się w oknie kontekstowym LLM o rozmiarze 128k tokenów?

## Słownik pojęć

| Termin | Potoczne określenie | Co to dokładnie oznacza |
|------|----------------|--------------------------------------|
| Q-Former | „Query Transformer” | Mały transformator z 32 trenowalnymi wektorami zapytań przetwarzającymi cechy z zamrożonego ViT. |
| Trenowalne zapytania | „Wizualny soft-prompt” | Stały zestaw parametrów służący jako zapytania (Q) w mechanizmie cross-attention; reprezentuje wiedzę zakodowaną w modelu, wspólną dla wszystkich danych wejściowych. |
| Cross-attention | „Q stąd, K/V stamtąd” | Mechanizm uwagi, w którym zapytania (Q) oraz klucze/wartości (K/V) pochodzą z różnych źródeł; w tym przypadku zapytania pobierają informacje z patchy ViT. |
| ITC | „Image-Text Contrastive” | Strata kontrastowa w stylu CLIP aplikowana do zagregowanych zapytań Q-Formera i tokena tekstowego CLS. |
| ITM | „Image-Text Matching” | Klasyfikator binarny oceniający dopasowanie par obraz-tekst na przykładach trudnych negatywnych (hard negatives); zmusza zapytania do wyłapywania drobnych różnic. |
| ITG | „Image-grounded Text Generation” | Przyczynowa (causal) strata językowa LM przy generowaniu tekstu na podstawie zapytań; wymusza na zapytaniach kodowanie cech łatwych do zdekodowania przez LLM. |
| Trening dwuetapowy | „Reprezentacja, potem generacja” | Etap 1 trenuje sam Q-Former (ITC/ITM/ITG); Etap 2 dołącza zamrożony LLM i optymalizuje wyłącznie projekcję oraz Q-Former. |
| Zamrożony model bazowy (backbone) | „Frozen backbone” | Stałe wagi encodera wizyjnego i LLM; trenowany jest wyłącznie adapter (mostek). |
| Głowica projekcyjna | „MLP / projekcja do LLM” | Warstwa liniowa (lub MLP) mapująca wyjście Q-Formera na wymiar embeddingów LLM. |
| Perceiver resampler | „Wersja z Flamingo” | Podobny mechanizm cross-attention z trenowalnymi zapytaniami, stosowany przez model Flamingo wewnątrz każdej warstwy, a nie jako pojedynczy mostek wejściowy. |

## Dalsze czytanie

- [Li et al. — BLIP-2 (arXiv:2301.12597)](https://arxiv.org/abs/2301.12597) — kluczowa publikacja źródłowa.
- [Li et al. — BLIP (arXiv:2201.12086)](https://arxiv.org/abs/2201.12086) — poprzednik wprowadzający trio strat ITC/ITM/ITG.
- [Li et al. — ALBEF (arXiv:2107.07651)](https://arxiv.org/abs/2107.07651) — „align before fuse” — koncepcyjny fundament dla treningu 1. etapu.
- [Dai et al. — InstructBLIP (arXiv:2305.06500)](https://arxiv.org/abs/2305.06500) — wersja Q-Formera uwzględniająca instrukcje tekstowe.
- [Zhu et al. — MiniGPT-4 (arXiv:2304.10592)](https://arxiv.org/abs/2304.10592) — uproszczone podejście z samym projektorem.
- [Jaegle et al. — Perceiver IO (arXiv:2107.14795)](https://arxiv.org/abs/2107.14795) — ogólna architektura uczenia zapytań przez cross-attention.
