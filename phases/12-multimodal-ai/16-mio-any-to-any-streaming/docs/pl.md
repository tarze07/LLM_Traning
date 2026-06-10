# MIO i multimodalne modele przesyłania strumieniowego typu „każdy do dowolnego”.

> GPT-4o zawiera produkt, którego nie jest w stanie odtworzyć większość otwartych modeli: agenta, który słyszy głos, widzi obraz i odpowiada w czasie rzeczywistym. Odpowiedzią w zakresie otwartego ekosystemu do końca 2024 r. będzie MIO (Wang i in., wrzesień 2024 r.). MIO tokenizuje tekst, obraz, mowę i muzykę, szkoli jeden transformator przyczynowy na przeplatanych sekwencjach i generuje dowolną modalność do dowolnej modalności. AnyGPT (Zhan i in., luty 2024) był dowodem słuszności koncepcji; MIO to skalowanie; Unified-IO 2 (Allen AI, grudzień 2023) to kuzyn z wizją i podstawą działania. W tej lekcji przedstawiono wzorzec „każdy do dowolnego” — cztery tokenizatory, jeden transformator i dekodowanie przyjazne dla przesyłania strumieniowego.

**Typ:** Ucz się
**Języki:** Python (stdlib, czteromodalny alokator tokenów + pętla dekodowania strumieniowego)
**Wymagania wstępne:** Faza 12 · 11 (Kameleon), Faza 6 (Mowa i dźwięk)
**Czas:** ~120 minut

## Cele nauczania

- Zaprojektuj wspólne słownictwo, które będzie zawierać tokeny tekstu, obrazu, mowy i muzyki bez kolizji.
- Porównaj SEED-Tokenizer (obrazy) i SpeechTokenizer resztkowe VQ (mowa) w zakresie kompromisów w zakresie kompresji i rekonstrukcji.
- Wyjaśnij czteroetapowy program nauczania, który kształtuje każde pokolenie.
- Wymień trzy otwarte receptury typu „każdy z każdym” i ich główne kompromisy: MIO, AnyGPT, Unified-IO 2.

## Problem

Łatwo jest stworzyć ujednolicony model multimodalny, ale trudno go zbudować na dużą skalę. Większość systemów „każdy z każdym” do 2024 r. została uruchomiona: model wizji → reprezentacja tekstu → model mowy → dźwięk. Każdy przeskok powoduje utratę informacji, zwiększenie opóźnienia i komplikowanie uczenia. Film demonstracyjny GPT-4o pokazał alternatywę dla jednego modelu z czasem reakcji poniżej sekundy; systemy otwarte przeciągane miesiącami.

Wyzwania inżynieryjne:

- Tokenizatory muszą istnieć dla każdej modalności, kompresować bezstratnie w stopniu wystarczającym do rekonstrukcji i produkować tokeny z szybkością, jaką może zużyć transformator.
- Pojedyncze słownictwo musi przydzielać miejsce na tekst (32 tys.+), obraz (16 tys.+), mowę (4k+), muzykę (8k+). Minimum czterdzieści tysięcy wpisów.
- Dane szkoleniowe muszą obejmować każdą parę wejście-wyjście (tekst → obraz, obraz → mowa, mowa → obraz itp.) lub model musi się ułożyć.
— Wnioskowanie musi przesyłać strumieniowo tokeny wyjściowe wystarczająco szybko, aby zapewnić opóźnienie konwersacji (czas do pierwszego bajtu audio < 500 ms).

## Koncepcja

### Cztery tokenizatory dla czterech modalności

Stos tokenizera MIO:

- Tekst: standardowy BPE, słownictwo ~32000.
- Obraz: SEED-Tokenizer (2023) — skwantowany VAE z dyskretnym słownikiem, 4096 wpisów, 32x32 tokeny na obraz.
- Speech: SpeechTokenizer pozostałości-VQ (2023) — koduje przebieg 16 kHz w 8 hierarchicznych słownikach; pierwszy poziom to prosta treść, późniejsze poziomy dodają prozodię i tożsamość mówiącego.
- Muzyka: podobne resztkowe VQ (rodzina MusicGen / Encodec firmy Meta), 4-8 książek kodowych.

Każda modalność generuje tokeny całkowite. Tokeny otrzymują rozłączne zakresy identyfikatorów we wspólnym słownictwie:

```
text:   0..31999
image:  32000..36095  (4096 image tokens)
speech: 36096..40191  (4096 speech base tokens, plus residual layers)
music:  40192..48383  (8192 music tokens)
sep:    48384..48390  (<image>, <speech>, <music>, </...>, etc.)
```

Razem: ~48 tys. słownictwa. Osadzanie danych wejściowych i projekcja wyników obejmują to wszystko.

### Dekodowanie strumieniowe

Generowanie mowy wykorzystuje resztkowe VQ. Transformator przewiduje żetony mowy bazowej (warstwa 0); dekodowany równolegle kwantyzator resztkowy przewiduje kolejne warstwy. Każdy token warstwy 0 to około 50 ms dźwięku przy 16 kHz.

Wzór przesyłania strumieniowego:

1. Użytkownik mówi do mikrofonu; Tokenizator audio w czasie rzeczywistym emituje tokeny mowy co 50 ms.
2. MIO zużywa tokeny w momencie ich otrzymania (wstępne wypełnienie monitu + przyrostowe przesyłanie dalej).
3. Tokeny wyjściowe są wysyłane w miarę wygenerowania; równoległy dekoder mowy konwertuje je na próbki audio z opóźnieniem ~ 50-150 ms.
4. Czas do pierwszego bajtu audio: ~300-500ms w dokumencie MIO, zbliżony do ~250ms w GPT-4o.

Mini-Omni (arXiv:2408.16725), GLM-4-Voice (arXiv:2412.02612) i Moshi (arXiv:2410.00037) to uzupełniające się projekty LLM do strumieniowego przesyłania mowy. W szczególności Moshi osiąga 160 ms w obie strony na jednym procesorze graficznym.

### Program czteroetapowy

Program szkolenia MIO:

1. Etap 1 — wyrównanie. Wielkoskalowe korpusy par modalności: tekst-obraz, tekst-mowa, tekst-muzyka. Każda para używa własnego segmentu słownictwa symbolicznego. Trenuje wspólne słownictwo.
2. Etap 2 – przeplatany. Dokumenty przeplatane multimodalnie (blogi ze zdjęciami i filmami, podcasty z transkrypcjami itp.). Trenuje kontekst międzymodalny.
3. Etap 3 — wzmocnienie mowy. Dodatkowe dane audio poprawiające jakość mowy bez utraty możliwości tekstowych.
4. Etap 4 – SFT. Dopasowanie instrukcji do różnych modalności: VQA, napisy, narracja, dialog mowy na mowę.

Pominięcie etapu pogarsza określone możliwości: pomiń etap 2, a model traci kontekst międzymodalny; pomiń etap 3 i mowa jest słaba.

### Łańcuch myśli wizualnej

MIO wprowadza łańcuch myślenia wizualnego: model emituje pośrednie tokeny obrazu jako krok rozumowania. Na przykład „Czy kot wspina się na drzewo?” model:

1. Emituje `<image>` tokeny renderujące scenę (z obrazu wejściowego lub szkicu).
2. Emituje tekst analizując szkic.
3. Wydaje ostateczną odpowiedź.

Wyrenderowany obraz pośredni służy jako notatnik. Testy porównawcze usprawniają zadania związane z rozumowaniem przestrzennym. Pomysł odzwierciedla łańcuch myślowy dotyczący rozumowania tekstu.

### Konkurenci w trybie „każdy z każdym”.

- AnyGPT (arXiv:2402.12226): 4 modalności (tekst, obraz, mowa, muzyka), podobny projekt.
- Unified-IO 2 (arXiv:2312.17172): dodaje wyniki działań wizyjnych, głębokość i normalne. Większa różnorodność zadań, mniejsza skala.
- NExT-GPT (arXiv:2309.05519): LLM + dekodery dyfuzyjne specyficzne dla modalności. Nie jest to podejście oparte na jednym modelu.
- CoDi (arXiv:2305.11846): dyfuzja komponowalna; „każdy-do-każdego” poprzez współdzielone utajone.

MIO jest najbliższy czystemu tokenowi typu „any-to-any”. AnyGPT jest jego koncepcyjnym przodkiem.

### Budżet opóźnień

W przypadku produktu konwersacyjnego opóźnienie każdego komponentu ma znaczenie:

- Mikrofon do tokenów audio: ~ 50 ms.
- Wstępne wypełnienie (tokeny audio + historia): ~100 ms w modelu 8B.
- Pierwszy token wyjściowy: ~50ms.
- Równoległy dekoder resztkowego VQ + mowy: ~100-150 ms.

Całkowity czas do pierwszego bajtu audio: minimum ~300 ms. GPT-4o twierdzi ~250ms. Moshi twierdzi, że 160 ms. MIO/AnyGPT mieszczą się w zakresie 400–600 ms w publicznych testach porównawczych.

### Dlaczego relacja „każdy z każdym” jest trudna

Nawet w 2026 r. modele otwarte „każdy z każdym” będą podążać za modelami zamkniętymi na dwóch osiach:

- Jakość mowy. Tokenizator pozostałości VQ jest stratny; mowa konwersacyjna brzmi jak robot w porównaniu z głosami klasy ElevenLabs.
- Rozumowanie intermodalne. Poproszenie modelki o „śpiewanie o tym, co widzisz” nadal kończy się niepowodzeniem niż zadania polegające na czystym widzeniu.

Są to otwarte problemy badawcze. Qwen3-Omni (lekcja 12.20) to najbardziej zaawansowana próba otwarta w 2025 roku.

## Użyj tego

`code/main.py`:

- Definiuje alokację słownika czterech modalności i drukuje ją.
- Kieruje listę multimodalnych wejść (tekst, obraz, klip audio, muzyka) przez router tokenizera.
— Symuluje dekodowanie strumieniowe w celu uzyskania odpowiedzi zamiany tekstu na mowę ze zliczaniem opóźnień.
- Oblicza oczekiwany czas do pierwszego bajtu audio, biorąc pod uwagę opóźnienia kodera, wstępnego wypełnienia i dekodera.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-any-to-any-pipeline-auditor.md`. Biorąc pod uwagę specyfikację produktu konwersacyjnego (modalności wejścia, modalności wyjścia, docelowe opóźnienie), sprawdza wybory projektowe rodziny MIO i oblicza budżet opóźnień.

## Ćwiczenia

1. Twój produkt akceptuje wprowadzanie mowy i zwraca mowę. Jaki jest docelowy budżet dotyczący kompleksowych opóźnień? Wymień elementy, które spędzają czas.

2. Rezydualny VQ SpeechTokenizer wykorzystuje 8 książek kodowych. Zaproponuj, dlaczego konieczne jest dekodowanie równoległe poziomów resztkowych (a nie sekwencyjne) i jakie przynosi to oszczędności w zakresie opóźnień.

3. Twoje słownictwo obejmuje 32 tys. tekstu, 4 tys. obrazu i 4 tys. mowy. Dodaj muzykę 8k i ~10 separatorów. Jaki jest koszt parametru macierzy osadzania przy ukrytym przyciemnieniu 4096?

4. Łańcuch myśli wizualnej emituje obraz pośredni. Jakiego rodzaju pytania są korzystne? Jakie rodzaje bolą dodatkowe żetony?

5. Przeczytaj Moshi (arXiv:2410.00037). Opisz technikę „monologu wewnętrznego” i porównaj z łańcuchem myśli wizualnej MIO.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|--------------------------------------|
| Każdy z każdym | „Wejście/wyjście multimodalne” | Pojedynczy model, który akceptuje i emituje tekst, obraz, mowę i muzykę w dowolnym kierunku |
| Resztkowe VQ | „Stos tokenizatora mowy” | Tokenizacja z wieloma książkami kodowymi, w której każda warstwa dodaje informacje; warstwa podstawowa to treść, kolejne warstwy to prozodia |
| Tokenizer SEED | „Kody obrazu” | Dyskretny tokenizator obrazu ze słownikiem na 4096 wpisów używany przez MIO |
| Łańcuch myśli wizualnej | „Wizualny notatnik” | Model generuje obraz pośredni jako krok rozumowania przed ostateczną odpowiedzią |
| Czas do pierwszego bajtu audio | „TTFAB” | Opóźnienie od głosu użytkownika do pierwszego wyjścia audio; <500ms dla wrażenia konwersacyjnego |
| Program czteroetapowy | „Przepis na trening” | Wyrównanie -> przeplatane -> wzmocniona mowa -> SFT, w tej kolejności |

## Dalsze czytanie

- [Wang i in. — MIO (arXiv:2409.17692)](https://arxiv.org/abs/2409.17692)
- [Zhan i in. — AnyGPT (arXiv:2402.12226)](https://arxiv.org/abs/2402.12226)
- [Lu i in. — Unified-IO 2 (arXiv:2312.17172)](https://arxiv.org/abs/2312.17172)
- [Wu i in. — NExT-GPT (arXiv:2309.05519)](https://arxiv.org/abs/2309.05519)
- [Tang i in. — CoDi (arXiv:2305.11846)](https://arxiv.org/abs/2305.11846)