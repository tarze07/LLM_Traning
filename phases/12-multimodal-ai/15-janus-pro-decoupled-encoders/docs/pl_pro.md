# Janus-Pro: Rozdzielone enkodery w zunifikowanych modelach multimodalnych

> W zunifikowanych modelach multimodalnych występuje nieuniknione napięcie projektowe. Zrozumienie obrazu wymaga cech semantycznych – reprezentacji (embeddings) z modeli takich jak SigLIP czy DINOv2, bogatych w informacje pojęciowe. Z kolei generowanie wymaga tokenów ułatwiających rekonstrukcję – tokenów VQ, które można precyzynie zdekodować z powrotem do postaci pikseli. Tych dwóch celów nie da się pogodzić w ramach jednego enkodera. Twórcy modeli Janus (DeepSeek, październik 2024) i Janus-Pro (DeepSeek, styczeń 2025) uznali, że rozwiązaniem jest rezygnacja z kompromisów i rozdzielenie obu enkoderów. Główny korpus transformatora jest współdzielony między zadaniami, ale proces rozumienia opiera się na koderze SigLIP, a proces generowania – na tokenizerze VQ. W wersji 7B Janus-Pro przewyższa model DALL-E 3 w teście GenEval i dorównuje modelowi LLaVA w teście MMMU. Z tej lekcji dowiesz się, dlaczego podejście z dwoma enkoderami sprawdza się tam, gdzie jeden wspólny koder zawodzi.

**Typ:** Kompilacja
**Języki:** Python (biblioteka standardowa, routing z dwoma enkoderami + współdzielony sygnał)
**Wymagania wstępne:** Faza 12 · 13 (Transfusion), Faza 12 · 14 (Show-o)
**Czas:** ~120 minut

## Cele kształcenia

- Wyjaśnienie, dlaczego pojedynczy współdzielony enkoder obniża jakość rozumienia lub generowania obrazu.
- Opis routingu w Janus-Pro: wykorzystanie reprezentacji SigLIP na wejściu do zadań rozumienia oraz tokenów VQ (na wejściu i wyjściu) do zadań generowania.
- Przeanalizowanie skalowania miksu danych treningowych, które zdecydowało o sukcesie Janus-Pro w porównaniu z pierwszą wersją Janus.
- Porównanie architektur: rozdzielonej (Janus-Pro), zintegrowanej ciągłej (Transfusion) oraz zintegrowanej dyskretnej (Show-o).

## Problem

Zunifikowane modele współdzielą ten sam rdzeń (korpus) transformatora do zadań rozumienia i generowania obrazu. Wcześniejsze podejścia (takie jak Chameleon, Show-o czy Transfusion) wykorzystywały jeden wspólny tokenizer wizualny do obu tych celów. Taki tokenizer stanowi jednak kompromis:

- **Optymalizacja pod kątem rekonstrukcji (generowanie):** model typu VQ-VAE dobrze odwzorowuje szczegóły pikseli, ale tworzy tokeny o niskiej spójności semantycznej.
- **Optymalizacja pod kątem semantyki (rozumienie):** reprezentacje (embeddings) SigLIP grupują obrazy przedstawiające kota blisko powiązanych z nim tokenów tekstowych, ale nie pozwalają na poprawną rekonstrukcję pikseli.

Modele Show-o i Transfusion płacą za to pogorszeniem jakości w jednym z tych obszarów. Twórcy Janus-Pro zadali sobie pytanie: po co ograniczać się do jednego tokenizera, skoro oba zadania mają zupełnie inne wymagania?

## Koncepcja

### Rozdzielone kodowanie wizualne (Decoupled Visual Encoding)

Architektura Janus-Pro wykorzystuje dwa osobne enkodery:

- **Ścieżka rozumienia (understanding path):** Obraz wejściowy → SigLIP-SO400m → 2-warstwowy MLP → korpus transformatora.
- **Ścieżka generowania (generation path):** Obraz wejściowy (w przypadku warunkowania obrazem) → Tokenizer VQ → ID tokenów → korpus transformatora.
- **Wyjście generowania:** Tokeny obrazu wygenerowane przez transformator → Dekoder VQ → Piksele.

Korpus transformatora pozostaje wspólny. Wszystkie elementy wejściowe i wyjściowe zależą od realizowanego zadania.

Tryb pracy jest określany na podstawie formatu promptu: znacznik `<understand>` kieruje dane przez koder SigLIP, natomiast `<generate>` uruchamia ścieżkę VQ. Alternatywnie routing może wynikać bezpośrednio z rodzaju zadania.

### Dlaczego to działa

Ścieżka rozumienia korzysta z reprezentacji SigLIP, które w procesie wstępnego trenowania (w stylu CLIP) zostały zoptymalizowane pod kątem podobieństwa semantycznego. Wyniki modelu w testach percepcji są wyższe niż w przypadku Show-o czy Transfusion, ponieważ cechy wejściowe są lepiej dopasowane do tego zadania.

Z kolei w ścieżce generowania model uczy się na tokenach VQ, które zostały zoptymalizowane pod kątem rekonstrukcji obrazu. Jakość generowanych obrazów przewyższa Show-o, ponieważ kody VQ pozwalają na dokładne odtworzenie pikseli.

Wspólny rdzeń transformatora przetwarza dwa różne rozkłady danych wejściowych (SigLIP oraz VQ) i uczy się obsługiwać oba. Założenie jest proste: przy odpowiedniej ilości danych i parametrów, sieć bez problemu radzi sobie z przełączaniem między tymi reprezentacjami.

### Skalowanie danych — Janus vs Janus-Pro

Pierwsza wersja modelu Janus (arXiv 2410.13848) wprowadziła koncepcję rozdzielonych enkoderów, ale na mniejszą skalę (model 1,3B parametrów, ograniczony zbiór danych). Wersja Janus-Pro (arXiv 2501.17811) została znacznie skalowana:

- Model o rozmiarze 7B parametrów (w porównaniu do 1,3B).
- 90 mln par obraz-tekst w Etapie 1 (dopasowanie/alignment) w porównaniu do 72 mln.
- 72 mln próbek w Etapie 2 (trening zunifikowany) w porównaniu do 26 mln.
- Dodanie 200 tys. próbek instrukcji generowania obrazu (instruction tuning) w Etapie 3.

Efekt: Janus-Pro-7B dorównuje modelowi LLaVA w benchmarku MMMU (60,3 vs ~58) i pokonuje DALL-E 3 w teście GenEval (0,80 vs 0,67). Powstał jeden otwartoźródłowy model, który radzi sobie świetnie zarówno w zadaniach rozumienia, jak i generowania.

### JanusFlow — wariant z dopasowaniem przepływu (Rectified Flow)

JanusFlow (arXiv 2411.07975) zastępuje dyskretną ścieżkę generowania VQ ciągłą metodą opartą na dopasowaniu przepływu (Rectified Flow). Architektura łączy SigLIP do rozumienia obrazu oraz Rectified Flow do jego generowania. Pozwala to na dalsze przesunięcie granicy jakości generowanego obrazu. Sama architektura wciąż bazuje na rozdzielonych enkoderach i współdzielonym korpusie.

### Rola współdzielonego korpusu

Współdzielony transformator przetwarza zunifikowane sekwencje pochodzące z dwóch różnych rozkładów danych. Jego zadania to:

- **W zadaniach rozumienia:** przyjmowanie reprezentacji SigLIP + tokenów tekstowych → generowanie tekstu w sposób autoregresyjny.
- **W zadaniach generowania:** przyjmowanie tokenów tekstowych + (opcjonalnie tokenów obrazu VQ) → generowanie tokenów obrazu VQ w sposób autoregresyjny.

Korpus nie posiada wag specyficznych dla poszczególnych modalności w swoich blokach. Jest to standardowy transformator tekstowy (zbliżony do modeli Qwen czy Llama) wzbogacony o dwa adaptery wejściowe.

Co ważne, dzięki temu rdzeń Janus-Pro można zainicjować z poziomu wstępnie wytrenowanego modelu LLM. W przypadku Janus-Pro bazowano na modelu DeepSeek-MoE-7B. Ma to kluczowe znaczenie: model językowy wnosi zaawansowane zdolności rozumowania, które trudno wypracować w modelach szkolonych od zera jako w pełni zintegrowane systemy multimodalne.

### Porównanie z InternVL-U

InternVL-U (lekcja 12.10) to nowsza konstrukcja z 2026 roku. Łączy ona w sobie:

- Natywne multimodalne trenowanie wstępne (szkielet InternVL3).
- Zastosowanie rozdzielonych enkoderów (wejście SigLIP, wyjście VQ + głowice dyfuzyjne).
- Zunifikowane środowisko do rozumienia, generowania oraz edycji obrazu.

InternVL-U rozwija założenia architektoniczne Janus-Pro w bardziej rozbudowany system. Koncepcja rozdzielonych enkoderów staje się obecnie standardem w zunifikowanych modelach na dużą skalę.

### Ograniczenia

Stosowanie rozdzielonych enkoderów zwiększa stopień skomplikowania architektury. Wymaga to trenowania dwóch osobnym tokenizerów, utrzymywania dwóch ścieżek wejściowych oraz radzenia sobie z dwoma zestawami potencjalnych błędów. Jeśli Twój produkt nie potrzebuje funkcji generowania obrazów, wybór Janus-Pro będzie nadmiarowy – lepiej sprawdzi się czysty model do rozumienia obrazu z rodziny LLaVA.

Z kolei w projektach skupionych wyłącznie na generowaniu, Janus-Pro ma zbyt szeroki wachlarz możliwości – w takim scenariuszu lepiej sięgnąć po dedykowane modele generatywne, takie jak Stable Diffusion 3 czy Flux.

Jednak dla systemów wymagających obu tych funkcji jednocześnie, Janus-Pro stanowi obecnie referencyjną architekturę open-source.

## Zastosowanie w kodzie

Plik `code/main.py` zawiera symulację routingu w Janus-Pro:

- Dwa makiety enkoderów: koder typu SigLIP (generujący 256-wymiarowe wektory semantyczne) oraz koder typu VQ (generujący tokeny w postaci liczb całkowitych).
- Router promptów, który wybiera odpowiedni koder na podstawie znacznika zadania.
- Współdzielony korpus (mock), przetwarzający sekwencje tokenów bez względu na to, który koder je wygenerował.
- Przejście od Etapu 1 (dopasowanie) do Etapu 3 (instruction tuning) przy użyciu ważonego harmonogramu próbek.

Skrypt wypisuje na ekranie ścieżki przepływu dla 3 przykładów: analizy jakości obrazu, generowania obrazu z tekstu (T2I) oraz edycji obrazu.

## Rezultat

Do tej lekcji dołączono dokument `outputs/skill-decoupled-encoder-picker.md`. Ułatwia on wybór między modelami Janus-Pro, JanusFlow a InternVL-U dla systemów wymagających najwyższej jakości jednoczesnego generowania i rozumienia obrazu, oferując konkretne wskazówki dotyczące skali danych.

## Ćwiczenia

1. Janus-Pro-7B pokonuje DALL-E 3 w teście GenEval. Wyjaśnij, dlaczego model otwartoźródłowy o rozmiarze 7B jest w stanie dorównać wiodącym zamkniętym modelom komercyjnym w generowaniu obrazu, podczas gdy w zadaniach rozumienia wciąż ustępuje największym z nich.
2. Zaimplementuj funkcję routera: na podstawie tekstu promptu zaklasyfikuj zadanie jako `understand` lub `generate`. W jaki sposób obsłużysz niejednoznaczne polecenia, takie jak „opisz, a następnie naszkicuj”?
3. JanusFlow zastępuje ścieżkę VQ metodą Rectified Flow (dopasowaniem przepływu). Co w takim przypadku generuje korpus transformatora i jak zmienia się funkcja straty?
4. Zaproponuj czwarte zadanie, które mogłoby być realizowane przez architekturę Janus-Pro po dodaniu kolejnego rozdzielonego enkodera. Przykłady: segmentacja obrazu (w stylu DINO), estymacja głębi (w stylu MiDaS).
5. Przeczytaj sekcję 4.2 pracy o Janus-Pro poświęconą skalowaniu danych. Który etap przygotowania danych ma największy wpływ na poprawę jakości generowania obrazu z tekstu (T2I) w porównaniu do pierwszej wersji Janus?

## Kluczowe pojęcia

| Termin | Potoczne określenie | Co to dokładnie oznacza |
| :--- | :--- | :--- |
| **Rozdzielone kodowanie (Decoupled encoding)** | „Dwa enkodery wizualne” | Zastosowanie osobnego enkodera lub tokenizera dla każdego z kierunków: semantycznego (do zadań rozumienia) oraz rekonstrukcyjnego (do generowania). |
| **Współdzielony korpus (Shared body)** | „Jeden transformator” | Pojedynczy rdzeń transformatora przetwarzający dane wyjściowe z dowolnego enkodera, bez dedykowanych wag dla poszczególnych modalności w blokach. |
| **SigLIP do rozumienia** | „Cechy semantyczne” | Model wizyjny z rodziny CLIP, dostarczający bogatych reprezentacji pojęciowych, ale nie pozwalający na poprawną rekonstrukcję obrazu. |
| **VQ do generowania** | „Kody rekonstrukcyjne” | Tokeny kwantyzacji wektorowej (Vector Quantized), które pozwalają na dokładne odtworzenie pikseli przez dekoder. |
| **JanusFlow** | „Wariant z dopasowaniem przepływu” | Odmiana Janus-Pro wykorzystująca ciągłą głowicę generującą opartą na Rectified Flow zamiast tokenów VQ. |
| **Znacznik routingu (Routing token)** | „Znacznik zadania” | Specjalny token w prompcie (`<understand>` / `<generate>`), decydujący o wyborze odpowiedniego enkodera wejściowego. |

## Literatura uzupełniająca

- [Wu i in. — Janus (arXiv:2410.13848)](https://arxiv.org/abs/2410.13848)
- [Chen i in. — Janus-Pro (arXiv:2501.17811)](https://arxiv.org/abs/2501.17811)
- [Ma i in. — JanusFlow (arXiv:2411.07975)](https://arxiv.org/abs/2411.07975)
- [InternVL-U (arXiv:2603.09877)](https://arxiv.org/abs/2603.09877)
- [Dong i in. — DreamLLM (arXiv:2309.11499)](https://arxiv.org/abs/2309.11499)
