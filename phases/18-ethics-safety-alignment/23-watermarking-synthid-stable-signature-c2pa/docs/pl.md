# Znak wodny — SynthID, stabilny podpis, C2PA

> Struktura trzech technologii 2026 Pochodzenie treści generowanych przez sztuczną inteligencję. SynthID (Google DeepMind) — znak wodny obrazu wprowadzony na rynek w sierpniu 2023 r., tekst+wideo w maju 2024 r. (Gemini + Veo), tekst typu open source w październiku 2024 r. za pośrednictwem zestawu narzędzi Responsible GenAI Toolkit, ujednolicony detektor multimediów w listopadzie 2025 r. wraz z Gemini 3 Pro. Tekstowy znak wodny niezauważalnie dostosowuje prawdopodobieństwo próbkowania następnego tokenu; znaki wodne obrazów/wideo przetrwają kompresję, kadrowanie, filtry i zmiany liczby klatek na sekundę. Stable Signature (Fernandez et al., ICCV 2023, arXiv:2303.15435) — dostraja dekoder dyfuzji ukrytej, tak aby każde wyjście zawierało stałą wiadomość; przycięte (10% zawartości) wygenerowane obrazy wykryto >90% przy FPR<1e-6. Kontynuacja „Stabilny podpis jest niestabilny” (arXiv:2405.07145, maj 2024) — dostrajanie usuwa znak wodny przy jednoczesnym zachowaniu jakości. C2PA — standard metadanych podpisanych kryptograficznie i umożliwiający uwidocznienie manipulacji (C2PA 2.2 Wyjaśnienie 2025). Znak wodny i C2PA uzupełniają się: metadane można usunąć, ale mają bogatsze pochodzenie; znaki wodne zachowują się po transkodowaniu, ale niosą ze sobą mniej informacji.

**Typ:** Kompilacja
**Języki:** Python (stdlib, osadzanie znaku wodnego tokena + wykrywanie)
**Wymagania wstępne:** Faza 10 · 04 (próbkowanie), Faza 01 · 09 (teoria informacji)
**Czas:** ~75 minut

## Cele nauczania

- Opisać znak wodny na poziomie tokena (styl tekstu SynthID) i mechanizm, dzięki któremu jest on wykrywalny.
- Opisz stabilny podpis i atak usuwania w 2024 r., który go złamał.
- Określ rolę C2PA i dlaczego stanowi ona uzupełnienie znaku wodnego.
- Opisać kluczowe ograniczenia: sygnał specyficzny dla modelu, odporność na parafrazę i ataki zachowujące znaczenie (arXiv:2508.20228).

## Problem

W latach 2023–2024 deepfake i treści generowane przez sztuczną inteligencję wkroczyły na dużą skalę do kontekstu politycznego i konsumenckiego. Znak wodny to proponowany techniczny sygnał pochodzenia: oznaczaj pokolenia w momencie tworzenia, wykrywaj je później. Dowody z 2025 r.: żaden znak wodny nie jest bezwarunkowo solidny, ale w połączeniu z metadanymi C2PA kombinacja zapewnia użyteczną historię pochodzenia.

## Koncepcja

### Tekstowy znak wodny (styl tekstu SynthID)

Kirchenbauer i in. Mechanizm 2023, wyprodukowany przez Google:

1. Na każdym etapie dekodowania mieszaj poprzednie K tokenów, aby uzyskać pseudolosowy podział słownictwa na zestawy „zielone” i „czerwone”.
2. Przesuń próbkowanie w stronę zbioru zielonego, dodając δ do zielonych logitów.
3. Generacja zawiera więcej zielonych żetonów, niż wytworzyłby przypadek.

Wykrywanie: powtórz każdy prefiks, zlicz zielone żetony w generacji, oblicz wynik Z. Wartość Z wynosi >0 dla tekstu ze znakiem wodnym, ~0 dla tekstu ludzkiego.

Właściwości:
- Niedostrzegalne dla czytelników (δ jest na tyle małe, że utrata jakości jest niewielka).
- Wykrywalne dzięki dostępowi do funkcji podziału słownika.
- Nieodporny na parafrazę - przepisanie tekstu niszczy sygnał.

Tekst SynthID zostanie udostępniony jako open source w październiku 2024 r. za pośrednictwem zestawu narzędzi Google Responsible GenAI.

### Stabilny podpis (obrazek)

Fernandez i in. ICCV 2023. Dostosuj dekoder dyfuzji ukrytej, tak aby każdy wygenerowany obraz zawierał stałą wiadomość binarną osadzoną w reprezentacji ukrytej. Wykrycie jest dekodowane na podstawie danych ukrytych za pomocą dekodera neuronowego. Przycięte (do 10% zawartości) obrazy wykryto >90% przy FPR<1e-6.

Maj 2024 r. „Stabilny podpis jest niestabilny” (arXiv:2405.07145): dostrojenie dekodera usuwa znak wodny, zachowując jednocześnie jakość obrazu. Kontrowersyjne dostrajanie po generacji jest tanie; odporność kontradyktoryjności znaku wodnego jest ograniczona.

### Zunifikowany detektor SynthID (listopad 2025)

Oprócz Gemini 3 Pro: detektor multimediów, który odczytuje sygnały SynthID z tekstu, obrazu, dźwięku i wideo w jednym API. Ujednolica stos pochodzenia Google.

### C2PA

Koalicja na rzecz pochodzenia i autentyczności treści. Standard metadanych z podpisem kryptograficznym umożliwiającym identyfikację manipulacji. Wyjaśnienie C2PA 2.2 (2025). Manifest C2PA rejestruje roszczenia dotyczące pochodzenia (kto stworzył, kiedy, jakie transformacje) podpisane kluczem twórcy.

Uzupełnienie znaku wodnego:
- Metadane można usunąć; znaki wodne nie mogą (łatwo).
- Metadane są bogate (pełny łańcuch pochodzenia); znaki wodne niosą ze sobą bity.
- C2PA zależy od przyjęcia platformy; znaki wodne osadzają się automatycznie.

Google integruje zarówno wyszukiwarkę, reklamy, jak i „Informacje o tym obrazie”.

### Ograniczenia

- **Specyficzne dla modelu.** Generacje znaków wodnych SynthID z modeli obsługujących SynthID. Generacja z modelu bez SynthID nie jest oznaczona znakiem wodnym, więc brak sygnału SynthID nie jest dowodem autentyczności.
- **Parafraza.** Tekstowe znaki wodne nie przetrwają parafrazy zachowującej znaczenie.
- **Ataki transformacyjne.** arXiv:2508.20228 (2025) przedstawia ataki zachowujące znaczenie, które niszczą zarówno tekstowe znaki wodne, jak i wiele graficznych znaków wodnych.
- **Dokładne usuwanie.** W przypadku komunikatu „Stabilny podpis jest niestabilny” dostrajanie po generacji usuwa osadzone znaki wodne.

### Ustawa UE o sztucznej inteligencji art. 50

Kodeks przejrzystości dotyczący oznaczania treści generowanych przez sztuczną inteligencję (pierwszy projekt w grudniu 2025 r., drugi projekt w marcu 2026 r., oczekiwany koniec w czerwcu 2026 r. zgodnie z [stroną statusu Komisji Europejskiej](https://digital-strategy.ec.europa.eu/en/policies/code-practice-ai-generated-content)). Kodeks pozostaje w wersji roboczej od kwietnia 2026 r., a harmonogram może ulec zmianie. Warstwa regulacyjna wymagająca warstwy technicznej. Deepfakes muszą być oznaczone.

### Gdzie to pasuje do fazy 18

Lekcje 22-23 dotyczą tego, co emituje model (dane prywatne, sygnał pochodzenia). Lekcja 27 dotyczy zarządzania danymi szkoleniowymi. Lekcja 24 to ramy regulacyjne wymagające zastosowania tych środków technicznych.

## Użyj tego

`code/main.py` tworzy zabawkowy znak wodny z tekstem. Tokeny są liczbami całkowitymi 0..N-1; próbkowanie ze znakiem wodnym odchyla się w stronę zielonego zestawu zdefiniowanego hashem. Detektor oblicza wartość Z-score zielonego znacznika. Możesz obserwować wykrywanie przy pokoleniach 1000 tokenów, oglądać, jak parafraza niszczy sygnał i mierzyć odsetek wyników fałszywie dodatnich w tekście ludzkim.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-provenance-audit.md`. Biorąc pod uwagę wdrożenie treści z oświadczeniem o pochodzeniu, przeprowadza audyt: mechanizmu znaku wodnego (jeśli istnieje), łańcucha podpisywania C2PA (jeśli istnieje), odporności kontradyktoryjnej każdego z nich oraz zasięgu poszczególnych modalności.

## Ćwiczenia

1. Uruchom `code/main.py`. Raportuj wyniki Z dla generacji 1000 tokenów ze znakiem wodnym w porównaniu z tekstem napisanym przez człowieka. Zidentyfikuj odsetek wyników fałszywie dodatnich przy progu ufności 95%.

2. Zastosuj atak parafrazowy, który zastąpi 30% tokenów synonimami. Zmierz ponownie wartość Z.

3. Przeczytaj Kirchenbauer i in. 2023 Sekcja 6 dotycząca solidności. Dlaczego tekstowe znaki wodne nie działają w przypadku parafrazy, ale graficzne znaki wodne przetrwają przycięcie?

4. Zaprojektuj wdrożenie wykorzystujące tekst SynthID + metadane C2PA. Opisz łańcuch pochodzenia, jaki widzi konsument. Zidentyfikuj jeden tryb awarii każdego komponentu.

5. Wynik „Stabilny podpis jest niestabilny” z 2024 r. pokazuje, że dostrajanie usuwa znak wodny obrazu. Zaprojektuj kontrolę wdrożenia, która ograniczy ten atak — na przykład wymagaj podpisanych wydań dopracowanych punktów kontrolnych.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|--------------------------------------|
| SynthID | „Znak wodny Google” | Sygnał pochodzenia międzymodalnego; tekst, obraz, dźwięk, wideo |
| Tokenowy znak wodny | „W stylu Kirchenbauera” | Tekstowy znak wodny z próbkowaniem stronniczym wykrywalny za pomocą zielonego tokena Z-score |
| Stabilny podpis | „znak wodny obrazu” | Znak wodny dostrojonego dekodera; ICCV 2023 |
| C2PA | „standard metadanych” | Podpisane kryptograficznie metadane potwierdzające pochodzenie |
| Parafraza solidności | „czy przeformułowanie to psuje” | Tekstowa właściwość znaku wodnego; obecnie ograniczona |
| Dostosuj usuwanie | „kontradyktoryjny znak wodny” | Atak, który usuwa znak wodny obrazu poprzez dostrajanie dekodera |
| Detektor crossmodalny | „ujednolicony SynthID” | Listopad 2025 r. Ujednolicony interfejs API dla różnych modalności |

## Dalsze czytanie

- [Kirchenbauer i in. — Znak wodny dla modeli wielkojęzycznych (ICML 2023, arXiv:2301.10226)](https://arxiv.org/abs/2301.10226) — mechanizm token-watermark
- [Fernandez i in. — Stabilny podpis (ICCV 2023, arXiv:2303.15435)](https://arxiv.org/abs/2303.15435) — papier ze znakiem wodnym
- [„Stabilny podpis jest niestabilny” (arXiv:2405.07145)](https://arxiv.org/abs/2405.07145) — atak usuwania
- [Google DeepMind — SynthID](https://deepmind.google/models/synthid/) — międzymodalny znak wodny
- [C2PA 2.2 Wyjaśnienie (2025)](https://c2pa.org/specifications/specifications/2.2/explainer/Explainer.html) — standard metadanych