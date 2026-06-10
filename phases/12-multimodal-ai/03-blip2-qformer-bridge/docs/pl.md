# Od CLIP do BLIP-2 — Q-Former jako mostek modalny

> CLIP wyrównuje obraz i tekst, ale nie może generować podpisów, odpowiadać na pytania ani prowadzić rozmowy. Projekt BLIP-2 (Salesforce, 2023) rozwiązał ten problem za pomocą małego mostu, który można wytrenować: 32 możliwe do nauczenia wektory zapytań obsługują zamrożone funkcje ViT poprzez wzajemne uwagi, a następnie trafiają bezpośrednio do strumienia wejściowego zamrożonego LLM. Parametry 188M mostka łączyły 11B LLM z ViT-g/14. Każdy VLM oparty na adapterach do roku 2026 — MiniGPT-4, InstructBLIP i kuzyni LLaVA — będzie potomkiem. W tej lekcji zapoznajemy się z architekturą Q-Formera, wyjaśniamy jego dwuetapowe szkolenie i budujemy wersję zabawkową, która wprowadza tokeny wizualne do dekodera zamrożonego tekstu.

**Typ:** Kompilacja
**Języki:** Python (stdlib, cross-attention + demonstracja zapytań do nauki)
**Wymagania:** Faza 12 · 02 (CLIP), Faza 7 (Transformatory)
**Czas:** ~180 minut

## Cele nauczania

- Wyjaśnij, dlaczego możliwe do wyszkolenia wąskie gardło między zamrożonym koderem wizyjnym a zamrożonym LLM przewyższa kompleksowe dostrajanie kosztów i stabilności.
- Zaimplementuj blok wzajemnej uwagi, w którym ustalony zestaw możliwych do nauczenia się zapytań dotyczy zewnętrznych funkcji obrazu.
- Przejdź przez dwuetapowe uczenie wstępne BLIP-2: reprezentacja (ITC + ITM + ITG), a następnie generacja (utrata LM z zablokowanym dekoderem).
- Porównaj Q-Former z prostszym projektorem MLP używanym w LLaVA i argumentuj, kiedy każdy wybór wygrywa.

## Problem

Masz zamrożony ViT, który produkuje 256 tokenów łatek o przyciemnieniu 1408 na obraz. Masz zamrożony LLM 7B, który oczekuje osadzania tokenów o wartości dim 4096. Oczywisty most — warstwa liniowa od 1408 do 4096 — działa, ale wprowadzenie wszystkich 256 tokenów łatek do kontekstu LLM kosztuje 256 dodatkowych tokenów na obraz. W ramach partii 32 obrazów, czyli 8192 tokenów wykorzystanych wyłącznie przez modalność wizualną.

Pytanie BLIP-2: czy możesz skompresować reprezentację obrazu składającą się z 256 tokenów do znacznie mniejszej liczby tokenów (powiedzmy 32), zachowując jednocześnie wystarczającą ilość informacji, aby LLM mógł napisać podpis, odpowiedzieć na pytania i uzasadnić obraz? Czy można trenować ten most bez dotykania zamarzniętych szkieletów, utrzymując koszty szkolenia na poziomie parametrów mostu?

Odpowiedź: Q-Former. 32 możliwe do nauczenia wektory „zapytań”, które łączą się z tokenami łatek ViT, tworząc 32-tokenowe wizualne podsumowanie wykorzystywane przez LLM. Łącznie 188M parametrów. Przeszkolony w zakresie kontrastowych, dopasowujących i generatywnych celów, zanim jeszcze dotkniesz LLM.

## Koncepcja

### Zapytania, których można się nauczyć

Podstawowa sztuczka Q-Formera: zamiast pozwalać, aby tokeny tekstowe LLM zajmowały się poprawkami obrazów, wprowadź nowy zestaw 32 możliwych do nauczenia się wektorów zapytań `Q` i pozwól *im* zająć się poprawkami obrazów. Zapytania są parametrami modelu — są uczone podczas uczenia i dla każdego obrazu używane są te same 32 zapytania.

Po wzajemnej uwagi każde zapytanie zawiera skompresowane podsumowanie obrazu — „opisz główny obiekt”, „opisz tło”, „policz obiekty” itp. Zapytania nie specjalizują się dosłownie w etykietach semantycznych; uczą się dowolnego kodowania, które zmniejsza straty na dalszym etapie.

### Architektura

Q-Former to mały transformator (12 warstw, ~100M parametrów) z dwiema ścieżkami:

1. Ścieżka zapytania: 32 wektory zapytań przepływają przez samouważność (między sobą), następnie przez krzyżową uwagę przez zamrożone tokeny łatki ViT, a następnie FFN.
2. Ścieżka tekstowa: koder tekstu podobny do BERT dzieli wagę samouwagi i FFN ze ścieżką zapytania. Uwaga krzyżowa jest wyłączona dla ścieżki tekstowej.

W czasie treningu obie ścieżki biegną. Zapytania i tekst oddziałują na siebie poprzez wspólną samouważność, co oznacza, że ​​zapytania mogą uzależniać tekst od zadań, które tego potrzebują (ITM, ITG). W momencie wnioskowania dla przekazania VLM przepływają tylko zapytania, dając 32 tokeny wizualne.

### Szkolenie dwuetapowe

Wstępne szkolenie BLIP-2 odbywa się w dwóch etapach:

Etap 1: nauka reprezentacji (bez LLM). Trzy straty:
- ITC (kontrastowy obraz i tekst): kontrast w stylu CLIP pomiędzy zbiorczymi tokenami zapytań i tekstowym tokenem CLS.
- ITM (dopasowanie obrazu i tekstu): klasyfikator binarny — czy ta para obraz-tekst pasuje? Wydobywany na twardo-ujemnie.
- ITG (generowanie tekstu oparte na obrazie): przyczynowy nagłówek LM na tekście, uwarunkowany zapytaniami. Wymusza na zapytaniach kodowanie treści generowanej przez tekst.

Tylko pociągi Q-Former. ViT jest zamrożony. Brak zaangażowania LLM.

Etap 2: uczenie się generatywne. Dołącz zamrożony LLM (OPT-2.7B lub Flan-T5-XL itp.). Wyświetlaj 32 wyniki zapytań na przyciemnieniu osadzającym LLM za pomocą małej warstwy liniowej. Dołącz je do podpowiedzi tekstowej. Trenuj tylko projekcję liniową i Q-Former na utracie LM w połączonej sekwencji zachęty + obrazu + podpisu.

Po etapie 2 projekcja Q-Former+ jest pełnym adapterem wizualnym. Podsumowując: obraz → ViT → Q-Former → projekt liniowy → dodany do tekstu → zamrożony LLM emituje dane wyjściowe.

### Ekonomia parametrów

BLIP-2 z ViT-g/14 (1,1B, zamrożone) + OPT-6.7B (6,7B, zamrożone) + Q-Former (188M, przeszkolony) = łącznie 8B, 188M przeszkolonych. Sam Q-Former ma ~2,4% parametrów pełnego stosu. Koszt szkolenia odzwierciedla to: dni na kilku A100 w porównaniu z tygodniami w przypadku kompleksowego szkolenia.

Jakość: BLIP-2 dorównuje lub pokonuje Flamingo-80B w zakresie VQA z zerowym strzałem, a jednocześnie jest 50 razy mniejszy. Most działa.

### InstructBLIP i Q-Former obsługujący instrukcje

InstructBLIP (2023) rozszerza Q-Former o dodatkowe dane wejściowe: sam tekst instrukcji. W momencie wzajemnej uwagi zapytania mają teraz dostęp zarówno do poprawek obrazu, jak i do instrukcji. Zapytania mogą specjalizować się w poszczególnych instrukcjach („policz samochody”, „opisz nastrój”), zamiast uczyć się jednego, ustalonego podsumowania. Korzyści z benchmarków w przypadku wstrzymanych zadań.

### MiniGPT-4 i rozwiązanie oparte wyłącznie na projektorze

MiniGPT-4 zachował Q-Former, ale trenował tylko wyjściową projekcję liniową, zamrażając wszystko inne. Tanie, ale koszt to jakość — zapytania dotyczyły BLIP-2, a nie Twojego. Dobry do szybkiej iteracji, a nie najlepszej architektury.

### Dlaczego LLaVA stała się prostsza

LLaVA (2023, lekcja 12.05) zastąpiła Q-Former zwykłym 2-warstwowym systemem MLP, który wyświetla każdy token łatki ViT w przestrzeni LLM — 576 tokenów na obraz w siatce 24x24, wszystkie podawane do LLM. Gorsza kompresja, ale umożliwia LLM obsługę surowych poprawek. W tamtym czasie było to kontrowersyjne; pod koniec 2023 r. był dominujący, ponieważ dane z instrukcji wizualnych (LLaVA-Instruct-150k) wykazały, że MLP można wyszkolić, aby zachował wystarczający sygnał. Kompromis: kontekst LLaVA zapełnia się szybciej, ale skaluje się naturalnie do wielu obrazów i wideo.

Do 2026 r. podział obszarów: Q-Former przetrwa tam, gdzie liczy się symboliczny budżet (długie wideo, wiele obrazów); Projektor MLP dominuje tam, gdzie priorytetem jest surowa jakość na token.

### Bramka uwagi: Flaming, przodek

Flaming (lekcja 12.04) był starszy niż BLIP-2 i stosował ten sam pomysł wzajemnej uwagi, ale w każdej zamrożonej warstwie LLM, a nie jako pojedynczy most. BLIP-2 pokazał, że możesz kompresować tylko do warstwy wejściowej i nadal działać. Gemini i Idefics łączą oba elementy: przeplatane tokeny wejściowe oraz opcjonalną bramkowaną uwagę krzyżową dla kilku strzałów w kontekście.

### Potomkowie roku 2026

- Q-Former: BLIP-2, InstructBLIP, MiniGPT-4 i większość modeli z językiem wideo ze względu na niewielki budżet.
- Resampler perceivera: wariant Flamingo (lekcja 12.04); Rodzina Idefików, Orzeł, OmniMAE.
- Projektor MLP: LLaVA, LLaVA-NeXT, LLaVA-OneVision, Cambrian-1.
- Pula uwagi: VILA, PaliGemma.

Wszystkie cztery są ważne. Decydującym pytaniem jest, czy jesteś ograniczony budżetem na token, czy jakością na token.

## Użyj tego

`code/main.py` tworzy bibliotekę stdlib w stylu Q-Former:

1. Symuluj 256 żetonów poprawek obrazu (wymiar 128).
2. Utwórz instancję 32 zapytań, których można się nauczyć (wymiar 128).
3. Uruchom analizę krzyżową skalowanego produktu punktowego (Q z zapytań, K/V z poprawek).
4. Projektuj do LLM-dim (512) poprzez warstwę liniową.
5. Wyprowadź 32 żetony wizualne gotowe do użycia w LLM.

Cała matematyka w czystym Pythonie (zagnieżdżone pętle na wektorach). Zabawka, ale o prawidłowym kształcie. Drukowana jest macierz wagi uwagi, dzięki czemu można zobaczyć, z których poprawek zostało pobrane każde zapytanie.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-modality-bridge-picker.md`. Biorąc pod uwagę docelową konfigurację VLM (liczba tokenów kodera wizyjnego, budżet kontekstu LLM, ograniczenia wdrożeniowe, cel jakościowy), zaleca się resampler Q-Former vs MLP vs Perceiver z krótkim uzasadnieniem i szacunkową liczbą parametrów dla każdego mostu.

## Ćwiczenia

1. Zaimplementuj blok krzyżowej uwagi w PyTorch. Sprawdź, czy przy 32 zapytaniach i 256 kluczach/wartościach macierz wagi uwagi wynosi 32 x 256, a każdy wiersz sumuje się do 1 po softmax.

2. W etapie 1 BLIP-2 Q-Former zanotował jednocześnie trzy straty: ITC, ITM, ITG. Zapisz podpis forward dla każdego z nich w pseudokodzie. Który wymaga, aby ścieżka kodera tekstu była aktywna?

3. Porównaj liczbę parametrów: Q-Former (12 warstw, 768 ukrytych) vs 2-warstwowy projektor MLP (1408 → 4096, dwie warstwy). W jakiej skali LLM koszt 188M Q-Former zwraca się w postaci efektywności szkolenia?

4. Przeczytaj sekcję 3.2 artykułu BLIP-2 (arXiv:2301.12597) na temat inicjalizacji Q-Former. Wyjaśnij, dlaczego inicjowanie z bazy BERT (nie losowe) przyspiesza zbieżność.

5. W przypadku 10-minutowego wideo przy 1 kl./s próbkowanego do 60 klatek oblicz koszt tokena na klatkę przy (Q-Former → 32 tokeny/ramkę) w porównaniu z (projektor MLP → 576 tokenów/ramkę). Które pasuje do okna kontekstowego LLM o pojemności 128 tys. tokenów?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Były Q | „Zapytanie o transformator” | Mały transformator z 32 możliwymi do nauczenia się wektorami zapytań, które obsługują zamrożone funkcje ViT |
| Pytania, których można się nauczyć | „Miękki monit o wizję” | Stały zestaw parametrów służących jako strona zapytania w ramach wzajemnej uwagi; wiedza na temat modelu, wspólna dla wszystkich danych wejściowych |
| Uwaga krzyżowa | „Q stąd, K/V stamtąd” | Uwaga, jeśli zapytanie, klucz i wartość pochodzą z różnych źródeł; jak zapytania pobierają z poprawek ViT |
| ITC | „Kontrast obrazu i tekstu” | Strata w stylu CLIP zastosowana do zapytań zbiorczych Q-Former w porównaniu z tekstem CLS |
| ITM | „Dopasowanie obrazu do tekstu” | Klasyfikator binarny na parach wydobywanych metodą twardo-ujemną; zmusza zapytania do rozróżniania drobnych niedopasowań |
| ITG | „Generowanie tekstu w oparciu o obraz” | Przyczynowa utrata LM, gdy tekst jest generowany na podstawie zapytań; wymusza na zapytaniach kodowanie treści dających się zdekodować |
| Dwuetapowy trening wstępny | „Reprezentacja następnie generatywna” | Etap 1 szkoli Q-Formera samodzielnie (ITC/ITM/ITG); Etap 2 dołącza zamrożony LLM i trenuje tylko projekcję + Q-Former |
| Zamrożony kręgosłup | „Nie dostrajaj” | Koder wizyjny i wagi LLM są stałe; tylko pociągi mostowe |
| Głowica projekcyjna | „Przyciemnienie liniowe do LLM” | Ostateczna warstwa liniowa mapująca dane wyjściowe Q-Former na wymiar osadzania LLM |
| Resampler perceivera | „Wersja Flaminga” | Podobne wzajemna uwaga, której można się nauczyć, używana przez Flamingo w każdej warstwie, a nie jako pojedynczy most |

## Dalsze czytanie

- [Li i in. — BLIP-2 (arXiv:2301.12597)](https://arxiv.org/abs/2301.12597) — artykuł podstawowy.
- [Li i in. — BLIP (arXiv:2201.12086)](https://arxiv.org/abs/2201.12086) — poprzednik z trio ITC/ITM/ITG.
- [Li i in. — ALBEF (arXiv:2107.07651)](https://arxiv.org/abs/2107.07651) — „align before bezpiecznik” — koncepcyjny przodek szkolenia etapu 1.
- [Dai i in. — InstructBLIP (arXiv:2305.06500)](https://arxiv.org/abs/2305.06500) — Q-Former obsługujący instrukcje.
- [Zhu i in. — MiniGPT-4 (arXiv:2304.10592)](https://arxiv.org/abs/2304.10592) — podejście wyłącznie z projektorem.
- [Jaegle i in. — Perceiver IO (arXiv:2107.14795)](https://arxiv.org/abs/2107.14795) — ogólna architektura dla wzajemnej uwagi, której można się nauczyć.