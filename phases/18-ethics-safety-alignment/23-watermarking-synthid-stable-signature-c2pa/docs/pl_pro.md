# Znak wodny — SynthID, stabilny podpis, C2PA

> Struktura trzech technologii z 2026 roku służących do oznaczania pochodzenia treści generowanych przez sztuczną inteligencję. SynthID (Google DeepMind) – znak wodny dla obrazów wprowadzony na rynek w sierpniu 2023 r., dla tekstu i wideo w maju 2024 r. (Gemini + Veo), tekstowa wersja open-source w październiku 2024 r. w ramach Responsible GenAI Toolkit oraz zunifikowany detektor multimediów w listopadzie 2025 r. wraz z Gemini 3 Pro. Tekstowy znak wodny niezauważalnie modyfikuje prawdopodobieństwo próbkowania kolejnego tokenu; znaki wodne w obrazach i wideo są odporne na kompresję, kadrowanie, filtry oraz zmiany liczby klatek na sekundę. Stable Signature (Fernandez et al., ICCV 2023, arXiv:2303.15435) – dostraja dekoder ukrytej dyfuzji (latent diffusion), tak aby każdy wygenerowany element zawierał stałą wiadomość; wygenerowane obrazy przycięte nawet do 10% zawartości są wykrywane ze skutecznością >90% przy FPR < 1e-6. Publikacja „Stable Signature is Unstable” (arXiv:2405.07145, maj 2024 r.) wykazuje jednak, że dostrajanie (fine-tuning) usuwa znak wodny przy jednoczesnym zachowaniu jakości. C2PA to standard metadanych podpisanych kryptograficznie, pozwalający na wykrycie manipulacji (C2PA 2.2 Explainer, 2025). Znak wodny i C2PA wzajemnie się uzupełniają: metadane można usunąć, ale oferują one bogatsze informacje o pochodzeniu; znaki wodne przetrwają transkodowanie, lecz przenoszą mniej danych.

**Typ:** Kompilacja
**Języki:** Python (biblioteka standardowa, osadzanie znaku wodnego w tokenach + wykrywanie)
**Wymagania wstępne:** Faza 10 · 04 (próbkowanie), Faza 01 · 09 (teoria informacji)
**Czas:** ~75 minut

## Cele nauczania

- Opisać znak wodny na poziomie tokenów (tekstowy SynthID) oraz mechanizm umożliwiający jego wykrywanie.
- Wyjaśnić działanie technologii Stable Signature oraz opisać atak polegający na usuwaniu znaku wodnego z 2024 roku, który ją złamał.
- Określić rolę standardu C2PA i wyjaśnić, dlaczego stanowi on dopełnienie znaków wodnych.
- Opisać kluczowe ograniczenia: zależność sygnału od konkretnego modelu, odporność na parafrazowanie oraz ataki zachowujące znaczenie (arXiv:2508.20228).

## Problem

W latach 2023–2024 deepfake'i oraz treści generowane przez sztuczną inteligencję na masową skalę przeniknęły do sfery politycznej i konsumenckiej. Znaki wodne stanowią proponowane techniczne rozwiązanie problemu pochodzenia treści: oznaczają wygenerowane dane w momencie ich tworzenia, umożliwiając ich późniejsze wykrycie. Dowody z 2025 roku pokazują, że żaden znak wodny nie jest bezwzględnie odporny na próby jego usunięcia, jednak w połączeniu z metadanymi C2PA rozwiązanie to zapewnia użyteczną historię pochodzenia.

## Koncepcje

### Tekstowy znak wodny (styl SynthID)

Mechanizm opisany przez Kirchenbauera i in. (2023) oraz wdrożony przez Google:

1. Na każdym etapie dekodowania na podstawie poprzednich K tokenów generowany jest pseudolosowy podział słownika na zbiór „zielony” i „czerwony”.
2. Próbkowanie jest modyfikowane na korzyść zbioru zielonego poprzez dodanie wartości δ do zielonych logitów.
3. Wygenerowany tekst zawiera więcej zielonych tokenów, niż wynikałoby to z przypadku.

Wykrywanie: dla każdego prefiksu powtarza się procedurę podziału, zlicza zielone tokeny w wygenerowanym tekście i oblicza statystykę Z (Z-score). Wartość Z jest znacząco większa od zera dla tekstu ze znakiem wodnym i bliska zeru dla tekstu napisanego przez człowieka.

Właściwości:
- Niezauważalny dla czytelnika (wartość δ jest na tyle mała, że utrata jakości tekstu jest minimalna).
- Wykrywalny przy dostępie do funkcji podziału słownika.
- Nieodporny na parafrazowanie – przepisanie tekstu niszczy sygnał.

Tekstowa wersja SynthID została udostępniona jako open-source w październiku 2024 roku w ramach zestawu narzędzi Google Responsible GenAI Toolkit.

### Stable Signature (obrazy)

Fernandez i in. (ICCV 2023). Metoda polega na dostrojeniu dekodera ukrytej dyfuzji w taki sposób, aby każdy wygenerowany obraz zawierał stałą sygnaturę binarną osadzoną w przestrzeni ukrytej (latent space). Sygnatura jest odczytywana z przestrzeni ukrytej za pomocą dekodera neuronowego. Obrazy przycięte nawet do 10% oryginalnej zawartości były wykrywane ze skutecznością >90% przy współczynniku fałszywych alarmów (FPR) < 1e-6.

W maju 2024 roku w pracy „Stable Signature is Unstable” (arXiv:2405.07145) wykazano, że dostrojenie (fine-tuning) dekodera usuwa znak wodny przy jednoczesnym zachowaniu jakości obrazu. Ponieważ dostrajanie po generacji jest tanie, odporność znaku wodnego na modyfikacje modelu okazuje się ograniczona.

### Zunifikowany detektor SynthID (listopad 2025)

Wprowadzony wraz z Gemini 3 Pro: detektor multimediów, który w ramach jednego API potrafi odczytywać sygnały SynthID z tekstu, obrazu, dźwięku i wideo. Ujednolica on cały stos technologii oznaczania pochodzenia od Google.

### C2PA

Coalition for Content Provenance and Authenticity (Koalicja na rzecz Pochodzenia i Autentyczności Treści). Jest to standard kryptograficznie podpisanych metadanych, który pozwala na łatwe wykrycie manipulacji (por. C2PA 2.2 Explainer, 2025). Manifest C2PA rejestruje deklaracje dotyczące pochodzenia (twórca, czas, dokonane przekształcenia) podpisane kluczem prywatnym autora lub systemu.

Uzupełnienie znaku wodnego:
- Metadane można łatwo usunąć; znaki wodne są trudniejsze do usunięcia.
- Metadane są bogate w informacje (pełny łańcuch pochodzenia); znaki wodne przenoszą jedynie pojedyncze bity danych.
- Działanie C2PA zależy od wsparcia ze strony platform i aplikacji; znaki wodne są osadzane bezpośrednio w treści.

Google integruje oba te rozwiązania w swojej wyszukiwarce, reklamach oraz funkcji „Informacje o tym obrazie”.

### Ograniczenia

- **Zależność od modelu.** Znaki wodne SynthID są generowane wyłącznie przez modele obsługujące tę technologię. Treści z modeli bez wsparcia dla SynthID nie są oznaczane, więc brak sygnału nie stanowi dowodu na to, że tekst lub obraz pochodzi od człowieka.
- **Parafrazowanie.** Tekstowe znaki wodne nie są odporne na parafrazowanie zachowujące sens wypowiedzi.
- **Ataki transformacyjne.** W publikacji arXiv:2508.20228 (2025) przedstawiono ataki zachowujące znaczenie, które skutecznie niszczą zarówno tekstowe, jak i wiele graficznych znaków wodnych.
- **Usuwanie przez dostrajanie.** W przypadku Stable Signature wykazano, że dostrojenie modelu po jego wygenerowaniu usuwa osadzony znak wodny.

### Artykuł 50 Aktu o sztucznej inteligencji UE (AI Act)

Wymóg przejrzystości dotyczący oznaczania treści generowanych przez sztuczną inteligencję (pierwszy projekt kodeksu postępowania powstał w grudniu 2025 r., drugi w marcu 2026 r., a ostateczna wersja spodziewana jest w czerwcu 2026 r. zgodnie ze [stroną statusu Komisji Europejskiej](https://digital-strategy.ec.europa.eu/en/policies/code-practice-ai-generated-content)). Według stanu na kwiecień 2026 r. kodeks pozostaje w fazie roboczej, a harmonogram prac może ulec zmianie. Jest to warstwa regulacyjna wymagająca wdrożenia odpowiednich rozwiązań technicznych. Treści typu deepfake muszą być wyraźnie oznaczone.

### Miejsce w strukturze Fazy 18

Lekcje 22–23 dotyczą danych wyjściowych z modeli (ochrona prywatności, oznaczenia pochodzenia). Lekcja 27 skupia się na zarządzaniu danymi treningowymi. Lekcja 24 opisuje ramy prawne i regulacyjne wymagające wdrożenia tych zabezpieczeń technicznych.

## Zastosowanie

Skrypt `code/main.py` tworzy uproszczony (zabawkowy) mechanizm tekstowego znaku wodnego. Tokeny są reprezentowane przez liczby całkowite z zakresu 0..N-1. Próbkowanie ze znakiem wodnym faworyzuje zbiór zielony, wyznaczony na podstawie funkcji haszującej. Detektor oblicza wartość statystyki Z (Z-score) dla zielonych tokenów. Możesz przetestować wykrywanie na wygenerowanych tekstach o długości 1000 tokenów, sprawdzić, jak parafraza niszczy sygnał, oraz zmierzyć współczynnik fałszywych alarmów (false positives) dla tekstów napisanych przez człowieka.

## Efekt końcowy

W ramach tej lekcji powstanie dokument `outputs/skill-provenance-audit.md`. Przeprowadza on audyt wdrożenia treści z deklaracją pochodzenia, weryfikując: mechanizm znaku wodnego (jeśli istnieje), kryptograficzny łańcuch podpisu C2PA (jeśli istnieje), odporność obu rozwiązań na modyfikacje oraz zakres wspieranych modalności.

## Ćwiczenia

1. Uruchom skrypt `code/main.py`. Porównaj wartości statystyki Z dla wygenerowanego tekstu ze znakiem wodnym o długości 1000 tokenów oraz tekstu napisanego przez człowieka. Określ odsetek wyników fałszywie dodatnich (FPR) przy poziomie ufności 95%.

2. Przeprowadź atak polegający na parafrazowaniu, zastępując 30% tokenów synonimami. Ponownie zmierz wartość Z.

3. Przeczytaj sekcję 6 pracy Kirchenbauera i in. (2023) dotyczącą odporności. Dlaczego tekstowe znaki wodne nie są odporne na parafrazowanie, podczas gdy graficzne znaki wodne potrafią przetrwać kadrowanie obrazu?

4. Zaprojektuj system wdrażający tekstowy znak wodny SynthID oraz metadane C2PA. Opisz łańcuch pochodzenia widoczny dla końcowego użytkownika. Zidentyfikuj po jednym scenariuszu awarii (mode of failure) dla każdego z komponentów.

5. Wyniki pracy „Stable Signature is Unstable” z 2024 roku pokazują, że dostrojenie modelu usuwa znak wodny z obrazu. Zaprojektuj mechanizm kontroli wdrożenia, który ograniczy ten atak – na przykład poprzez wymóg podpisywania dopracowanych (fine-tuned) wag modelu.

## Słownik pojęć

| Termin | Potoczne określenie | Co to dokładnie oznacza |
|------|-----------------|--------------------------------------|
| SynthID | „Znak wodny od Google” | Wielomodalny system oznaczania pochodzenia treści; obsługuje tekst, obrazy, dźwięk i wideo |
| Tokenowy znak wodny | „W stylu Kirchenbauera” | Tekstowy znak wodny modyfikujący prawdopodobieństwo próbkowania, wykrywany na podstawie statystyki Z (Z-score) zielonych tokenów |
| Stable Signature | „Znak wodny dla obrazów” | Znak wodny wbudowany w dostrojony dekoder; zaprezentowany na ICCV 2023 |
| C2PA | „Standard metadanych” | Kryptograficznie podpisane metadane poświadczające pochodzenie i historię modyfikacji treści |
| Odporność na parafrazowanie | „Czy zmiana słów to psuje” | Zdolność tekstowego znaku wodnego do przetrwania modyfikacji tekstu; obecnie mocno ograniczona |
| Usuwanie przez dostrajanie | „Atak na znak wodny” | Metoda usunięcia znaku wodnego z obrazu poprzez lekkie dostrojenie (fine-tuning) dekodera |
| Detektor wielomodalny | „Zunifikowany SynthID” | Wprowadzony w listopadzie 2025 r. wspólny interfejs API do detekcji znaków we wszystkich modalnościach |

## Literatura uzupełniająca

- [Kirchenbauer et al. – A Watermark for Large Language Models (ICML 2023, arXiv:2301.10226)](https://arxiv.org/abs/2301.10226) – podstawy teoretyczne znaków wodnych na poziomie tokenów.
- [Fernandez et al. – Stable Signature (ICCV 2023, arXiv:2303.15435)](https://arxiv.org/abs/2303.15435) – publikacja opisująca znak wodny dla obrazów.
- [„Stable Signature is Unstable” (arXiv:2405.07145)](https://arxiv.org/abs/2405.07145) – opis ataku usuwającego znak wodny.
- [Google DeepMind – SynthID](https://deepmind.google/models/synthid/) – strona domowa wielomodalnego systemu znaków wodnych.
- [C2PA 2.2 Explainer (2025)](https://c2pa.org/specifications/specifications/2.2/explainer/Explainer.html) – przewodnik po specyfikacji standardu metadanych.
