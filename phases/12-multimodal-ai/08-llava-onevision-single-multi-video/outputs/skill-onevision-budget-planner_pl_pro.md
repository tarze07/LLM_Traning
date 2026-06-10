---

name: onevision-budget-planner
description: Zaplanuj i alokuj zunifikowane budżety tokenów wizualnych w stylu LLaVA-OneVision dla scenariuszy pojedynczego obrazu, wielu obrazów oraz wideo pod kątem docelowego profilu zadań.
version: 1.0.0
phase: 12
lesson: 08
tags: [llava-onevision, token-budget, curriculum, multi-image, video]

---

Na podstawie oczekiwanego profilu zadań produkcyjnych (procentowego udziału zapytań o pojedynczy obraz, wiele obrazów oraz wideo) oraz zadanego limitu tokenów wizualnych na przykład (sample), wygeneruj plan alokacji tokenów dla każdego scenariusza oraz harmonogram programu nauczania (curriculum plan).

Wymagane elementy:

1. Konfiguracja dla każdego scenariusza. Pojedynczy obraz: liczba kafelków AnyRes + miniatura globalna + stopień agregacji (pooling factor); wiele obrazów: liczba obrazów na przykład + stopień agregacji na obraz; wideo: liczba klatek + stopień agregacji na klatkę.
2. Zbilansowanie budżetu tokenów. Suma tokenów wygenerowanych w każdym scenariuszu powinna mieścić się w granicach ±30% docelowego budżetu; wyraźnie oznacz scenariusze zużywające poniżej 70% wartości docelowej (niedostateczne wykorzystanie budżetu) lub powyżej 130% (ryzyko przepełnienia okna kontekstowego).
3. Harmonogram programu nauczania. Plan trzech etapów treningu (SI → OV → TT) wraz z wagami proporcji danych. W etapie TT (Task Transfer) wykorzystaj specyficzny dla użytkownika profil zadań.
4. Przewidywane umiejętności wschodzące (emerging capabilities). Na podstawie profilu zadań użytkownika określ, które z zaawansowanych możliwości LLaVA-OneVision mogą się pojawić w modelu (np. wnioskowanie z wielu kamer, obsługa znaczników Set-of-Mark, agent zrzutów ekranu).
5. Zasoby danych treningowych. Szacowana liczba tokenów/obrazów/klatek wymagana na każdym etapie uczenia przy założeniu użycia modelu LLM o rozmiarze 7B, powołując się na skalę danych w zróżnicowanym modelu OneVision-1.5.

Bezwzględne odrzucenia:
- Sugerowanie etapów programu uczenia, w których dane wideo lub wiele obrazów są trenowane przed pojedynczym obrazem. Badania OneVision dowodzą, że taka zmiana kolejności skutkuje stratą rzędu 2-4 punktów w benchmarku MMMU.
- Przydzielanie całego budżetu pod kątem danych wideo, gdy wdrożenie produkcyjne zakłada 80% udział zapytań o pojedyncze obrazy.
- Zakładanie, że AnyRes-16 (siatka kafelków 4x4) zmieści się w limicie 4k tokenów bez zastosowania agresywnej agregacji (poolingu).

Zasady odmowy wykonania usługi:
- Jeśli limit tokenów na przykład (sample) wynosi mniej niż 1024, odmów obsługi scenariuszy wielu obrazów lub wideo — poniżej tego progu architektura ta staje się nieefektywna.
- Jeśli użytkownik żąda przetwarzania ponad 5 klatek wideo w pełnej rozdzielczości (729 tokenów na klatkę) bez agregacji, odmów; zalecaj zastosowanie agregacji co najmniej 3x lub zmniejszenie liczby klatek.
- Jeśli w profilu zadań całkowicie pominięto analizę pojedynczych obrazów, odmów i rekomenduj użycie modeli z natywnym M-RoPE, takich jak Qwen2.5-VL — program treningowy OneVision bezwzględnie wymaga pojedynczego obrazu jako fundamentu percepcji wizualnej.

Dane wyjściowe: Jednostronicowy plan zawierający konfigurację tokenów dla poszczególnych scenariuszy, wagi dla etapów programu nauczania, analizę spodziewanych umiejętności wschodzących oraz szacowaną skalę danych treningowych. Na końcu umieść odnośniki do publikacji arXiv: 2408.03326 (OneVision) oraz 2509.23661 (OneVision-1.5).
