# MIO i multimodalne modele strumieniowe typu „any-to-any”

> Model GPT-4o oferuje funkcjonalność, której większość modeli open-source nie potrafi odtworzyć: agenta, który słyszy głos, analizuje obraz i odpowiada w czasie rzeczywistym. Odpowiedzią otwartego ekosystemu pod koniec 2024 roku stał się model MIO (Wang i in., wrzesień 2024). MIO tokenizuje tekst, obraz, mowę oraz muzykę, trenuje jeden transformator przyczynowy (causal transformer) na przeplatanych sekwencjach danych i pozwala na generowanie dowolnej modalności wyjściowej na podstawie dowolnej wejściowej (any-to-any). AnyGPT (Zhan i in., luty 2024) stanowił dowód słuszności koncepcji (Proof of Concept); MIO to jej wyskalowanie; z kolei Unified-IO 2 (Allen AI, grudzień 2023) to pokrewny projekt skupiony na zadaniach wizyjnych i robotycznych. W tej lekcji omówiono architekturę „any-to-any” – cztery tokenizatory, jeden wspólny transformator oraz dekodowanie dostosowane do transmisji strumieniowej.

**Typ:** Podstawy
**Języki:** Python (biblioteka standardowa, czteromodalny alokator tokenów + pętla dekodowania strumieniowego)
**Wymagania wstępne:** Faza 12 · 11 (Chameleon), Faza 6 (Mowa i dźwięk)
**Czas:** ~120 minut

## Cele kształcenia

- Zaprojektowanie wspólnego słownika (vocabulary) zawierającego tokeny tekstu, obrazu, mowy i muzyki bez nakładania się ich zakresów (bez kolizji).
- Porównanie modeli SEED-Tokenizer (dla obrazów) oraz SpeechTokenizer z kwantyzacją RVQ (dla mowy) pod kątem kompromisów między kompresją a jakością rekonstrukcji.
- Wyjaśnienie czteroetapowego programu treningowego (curriculum learning), który kształtuje możliwości generatywne modelu.
- Zestawienie trzech otwartoźródłowych architektur „any-to-any” i ich głównych kompromisów: MIO, AnyGPT oraz Unified-IO 2.

## Problem

Projektowanie zunifikowanych modeli multimodalnych jest stosunkowo proste, lecz ich skalowanie i wdrożenie produkcyjne stanowią ogromne wyzwanie. Większość systemów „any-to-any” przed rokiem 2024 opierała się na kaskadach modeli: model wizyjny → reprezentacja tekstowa → model mowy → dźwięk. Każde takie przejście powoduje utratę informacji, zwiększa opóźnienia (latency) i komplikuje proces uczenia. Prezentacja GPT-4o pokazała zalety jednego, spójnego modelu z czasem reakcji poniżej sekundy; społeczność open-source potrzebowała wielu miesięcy na zbliżenie się do tego wyniku.

Wyzwania inżynieryjne obejmują:

- Konieczność stworzenia wydajnych tokenizerów dla każdej z modalności, które kompresują dane bez istotnych strat (umożliwiając rekonstrukcję) i generują tokeny w tempie akceptowalnym dla transformatora.
- Zaprojektowanie jednego spójnego słownika mieszczącego tokeny tekstu (32k+), obrazu (16k+), mowy (4k+) i muzyki (8k+), co daje łącznie co najmniej 60 tysięcy wpisów.
- Zbiory treningowe muszą pokrywać wszystkie możliwe pary wejście-wyjście (tekst → obraz, obraz → mowa, mowa → obraz itd.), aby model potrafił generalizować połączenia między nimi.
- Proces wnioskowania (inference) musi przesyłać strumieniowo tokeny wyjściowe na tyle szybko, aby utrzymać tempo naturalnej rozmowy (czas do pierwszego bajtu audio – TTFAB – poniżej 500 ms).

## Koncepcja

### Cztery tokenizatory dla czterech modalności

Zestaw tokenizerów w modelu MIO:

- **Tekst:** standardowy BPE, słownik o rozmiarze ok. 32 000 tokenów.
- **Obraz:** SEED-Tokenizer (2023) – skwantowany model VAE z dyskretnym słownikiem zawierającym 4096 wpisów (generuje 32x32 tokeny na obraz).
- **Mowa:** SpeechTokenizer z kwantyzacją RVQ (Residual Vector Quantization, 2023) – koduje sygnał audio 16 kHz za pomocą 8 hierarchicznych książek kodowych (codebooks); pierwszy poziom odpowiada za treść semantyczną, a kolejne kodują prozodię i cechy mówcy.
- **Muzyka:** analogiczny tokenizer oparty na RVQ (rodzina modeli MusicGen / Encodec od Meta) z 4–8 książkami kodowymi.

Każda z modalności generuje tokeny w postaci liczb całkowitych, którym przypisywane są rozłączne zakresy identyfikatorów we wspólnym słowniku:

```
text:   0..31999
image:  32000..36095  (4096 image tokens)
speech: 36096..40191  (4096 speech base tokens, plus residual layers)
music:  40192..48383  (8192 music tokens)
sep:    48384..48390  (<image>, <speech>, <music>, </...>, etc.)
```

Łącznie: słownik o rozmiarze ok. 48 tysięcy tokenów. Warstwy osadzania (embedding) i rzutowania wyjściowego obsługują całą tę przestrzeń.

### Dekodowanie strumieniowe

Generowanie mowy opiera się na kwantyzacji RVQ. Transformator przewiduje tokeny mowy z warstwy bazowej (warstwa 0), a dekodowane równolegle warstwy resztkowe uzupełniają brakujące szczegóły. Każdy token warstwy 0 odpowiada za ok. 50 ms dźwięku o częstotliwości próbkowania 16 kHz.

Model strumieniowania wygląda następująco:

1. Użytkownik mówi do mikrofonu, a tokenizer audio na bieżąco generuje tokeny mowy (co 50 ms).
2. Model MIO natychmiast przetwarza te tokeny (szybkie przetwarzanie promptu / prefill + przyrostowe przejścia w przód / incremental forward pass).
3. Tokeny wyjściowe są wysyłane strumieniowo zaraz po wygenerowaniu; równoległy dekoder mowy przekształca je na fale dźwiękowe z opóźnieniem ok. 50–150 ms.
4. Czas do pierwszego bajtu dźwięku (TTFAB): ok. 300–500 ms (w dokumentacji MIO), co zbliża model do wyników GPT-4o (~250 ms).

Modele takie jak Mini-Omni (arXiv:2408.16725), GLM-4-Voice (arXiv:2412.02612) oraz Moshi (arXiv:2410.00037) to pokrewne, zorientowane na mowę projekty LLM. Warto zauważyć, że Moshi osiąga opóźnienie rzędu 160 ms w obie strony (round-trip) na pojedynczej karcie GPU.

### Czteroetapowy proces uczenia

Schemat treningowy MIO składa się z czterech kroków:

1. **Etap 1 – Dopasowanie (Alignment):** Uczenie na wielkich zbiorach par modalności (tekst-obraz, tekst-mowa, tekst-muzyka). Każda para korzysta ze swojego segmentu we wspólnym słowniku, co pozwala na zestrojenie reprezentacji przestrzeni wejściowej.
2. **Etap 2 – Dane przeplatane (Interleaved):** Trenowanie na dokumentach zawierających przeplatane treści multimodalne (np. artykuły z ilustracjami, podcasty z transkrypcjami). Kształtuje to zdolność rozumienia kontekstu międzymodalnego.
3. **Etap 3 – Wzmocnienie mowy (Speech enhancement):** Dofazowanie treningu za pomocą dodatkowych danych audio w celu podniesienia jakości mowy, bez utraty zdolności tekstowych.
4. **Etap 4 – SFT (Strojenie instrukcyjne):** Dopasowywanie modelu do instrukcji w różnych modalnościach (np. VQA, opisywanie obrazów, narracja, bezpośredni dialog głosowy).

Pominięcie któregokolwiek z tych kroków upośledza konkretne funkcje: brak Etapu 2 uniemożliwia łączenie kontekstów międzymodalnych, a brak Etapu 3 skutkuje niską jakością generowanego głosu.

### Łańcuch myśli wizualnej (Visual Chain of Thought)

MIO wprowadza mechanizm wizualnego łańcucha myśli: model generuje pośrednie tokeny obrazu jako krok w procesie wnioskowania. Na przykład przy pytaniu „Czy kot wspina się na drzewo?” model:

1. Generuje tokeny `<image>` przedstawiające scenę (na podstawie obrazu wejściowego lub szkicu).
2. Generuje tekst analizujący ten szkic.
3. Zwraca ostateczną odpowiedź.

Taki wyrenderowany obraz pośredni służy jako wizualny „brudnopis” (scratchpad). Testy benchmarkowe wykazują poprawę wyników w zadaniach wymagających rozumowania przestrzennego. Koncepcja ta jest bezpośrednim odpowiednikiem tekstowego łańcucha myśli (Chain of Thought).

### Podobne rozwiązania „any-to-any”

- **AnyGPT** (arXiv:2402.12226): Obsługuje 4 modalności (tekst, obraz, mowa, muzyka) i opiera się na zbliżonej koncepcji.
- **Unified-IO 2** (arXiv:2312.17172): Dodaje dodatkowo współrzędne detekcji, głębię oraz wektory normalne powierzchni. Oferuje szerszy wachlarz zadań, ale przy mniejszej skali modelu.
- **NExT-GPT** (arXiv:2309.05519): Wykorzystuje LLM jako kontroler oraz dedykowane dekodery dyfuzyjne dla poszczególnych modalności. Nie jest to architektura oparta na jednym wspólnym modelu.
- **CoDi** (arXiv:2305.11846): Komponowalny model dyfuzyjny realizujący zadania „any-to-any” poprzez współdzieloną przestrzeń ukrytą (latent space).

MIO reprezentuje najbardziej ortodoksyjne podejście typu „any-to-any” oparte wyłącznie na tokenach. AnyGPT jest jego bezpośrednim przodkiem koncepcyjnym.

### Budżet opóźnień (Latency Budget)

W systemach konwersacyjnych w czasie rzeczywistym liczy się opóźnienie każdego pojedynczego elementu:

- Droga od mikrofonu do tokenów audio: ~50 ms.
- Przetwarzanie wejścia / prefill (tokeny audio + historia konwersacji): ~100 ms dla modelu 8B.
- Generowanie pierwszego tokenu wyjściowego: ~50 ms.
- Działanie dekodera RVQ + synteza mowy: ~100–150 ms.

Łączny czas do pierwszego bajtu dźwięku (TTFAB) to minimum ok. 300 ms. Dla porównania, GPT-4o osiąga ok. 250 ms, a Moshi ok. 160 ms. Modele MIO i AnyGPT w testach publicznych mieszczą się w przedziale 400–600 ms.

### Dlaczego podejście „any-to-any” jest trudne

Otwarte modele „any-to-any” wciąż ustępują komercyjnym rozwiązaniom zamkniętym w dwóch głównych obszarach:

- **Jakość mowy:** Tokenizacja za pomocą RVQ wprowadza straty; generowany głos wciąż brzmi dość nienaturalnie (robotycznie) w porównaniu do rozwiązań takich jak ElevenLabs.
- **Rozumowanie międzymodalne:** Zadania takie jak „zaśpiewaj o tym, co widzisz na obrazku” wciąż stanowią ogromną trudność w porównaniu do standardowych zadań wizyjnych.

Są to wciąż otwarte zagadnienia badawcze. Model Qwen3-Omni (lekcja 12.20) to jedna z najbardziej zaawansowanych otwartych prób w tym kierunku.

## Zastosowanie w kodzie

Plik `code/main.py` realizuje następujące zadania:

- Definiuje alokację zakresów wspólnego słownika dla czterech modalności i wypisuje ją.
- Przepuszcza listę wejść multimodalnych (tekst, obraz, klip audio, muzyka) przez router tokenizera.
- Symuluje proces strumieniowego dekodowania w celu uzyskania odpowiedzi głosowej (Text-to-Speech) wraz z szacowaniem opóźnienia.
- Oblicza oczekiwany czas do pierwszego bajtu audio (TTFAB), biorąc pod uwagę opóźnienia enkodera, przetwarzania promptu (prefill) oraz dekodowania.

## Rezultat

Do tej lekcji dołączono dokument `outputs/skill-any-to-any-pipeline-auditor.md`. Na podstawie specyfikacji produktu konwersacyjnego (modalności wejścia/wyjścia, docelowe opóźnienie) weryfikuje on wybory projektowe z rodziny MIO i analizuje dopuszczalny budżet opóźnień.

## Ćwiczenia

1. Twój produkt przyjmuje głos użytkownika i również odpowiada głosem. Jaki jest docelowy budżet na opóźnienie typu end-to-end? Wymień wszystkie komponenty, które generują opóźnienie.
2. Tokenizer RVQ SpeechTokenizer wykorzystuje 8 książek kodowych. Wyjaśnij, dlaczego konieczne jest dekodowanie równoległe (a nie sekwencyjne) kolejnych poziomów resztkowych i jakie oszczędności w opóźnieniu to przynosi.
3. Twój słownik obejmuje 32 tys. tokenów tekstowych, 4 tys. obrazkowych i 4 tys. głosowych. Chcesz dodać 8 tys. tokenów muzycznych i ok. 10 separatorów. Jaki będzie koszt pamięciowy samej macierzy osadzeń (embedding matrix) przy wymiarze ukrytym (hidden dimension) równym 4096?
4. Mechanizm wizualnego łańcucha myśli generuje obraz pośredni. W jakiego typu pytaniach przynosi to korzyść, a w jakich generowanie dodatkowych tokenów będzie jedynie stratą czasu?
5. Przeczytaj publikację o modelu Moshi (arXiv:2410.00037). Opisz technikę „wewnętrznego monologu” (inner monologue) i porównaj ją z wizualnym łańcuchem myśli w MIO.

## Kluczowe pojęcia

| Termin | Potoczne określenie | Co to dokładnie oznacza |
| :--- | :--- | :--- |
| **Any-to-Any** | „Multimodalne wejście i wyjście” | Pojedynczy model potrafiący przetwarzać i generować tekst, obrazy, mowę oraz muzykę w dowolnej konfiguracji. |
| **RVQ (Residual Vector Quantization)** | „Kwantyzacja resztkowa” | Tokenizacja audio z użyciem wielu książek kodowych układających się hierarchicznie; warstwa bazowa koduje treść semantyczną, a kolejne uzupełniają prozodię i barwę. |
| **SEED-Tokenizer** | „Kody obrazu” | Dyskretny tokenizer obrazu ze słownikiem o rozmiarze 4096 wpisów, wykorzystywany m.in. w MIO. |
| **Wizualny łańcuch myśli (Visual CoT)** | „Wizualny brudnopis” | Model generuje pomocniczy obraz w procesie wnioskowania przed sformułowaniem ostatecznej odpowiedzi tekstowej. |
| **TTFAB (Time to First Audio Byte)** | „Czas do pierwszego dźwięku” | Opóźnienie mierzone od zakończenia wypowiedzi użytkownika do rozpoczęcia odtwarzania odpowiedzi audio; dla płynnej konwersacji powinno wynosić <500 ms. |
| **Czteroetapowy program nauczania** | „Schemat treningowy” | Uporządkowany proces uczenia modelu: Dopasowanie → Dane przeplatane → Wzmocnienie mowy → Strojenie instrukcyjne (SFT). |

## Literatura uzupełniająca

- [Wang i in. — MIO (arXiv:2409.17692)](https://arxiv.org/abs/2409.17692)
- [Zhan i in. — AnyGPT (arXiv:2402.12226)](https://arxiv.org/abs/2402.12226)
- [Lu i in. — Unified-IO 2 (arXiv:2312.17172)](https://arxiv.org/abs/2312.17172)
- [Wu i in. — NExT-GPT (arXiv:2309.05519)](https://arxiv.org/abs/2309.05519)
- [Tang i in. — CoDi (arXiv:2305.11846)](https://arxiv.org/abs/2305.11846)
