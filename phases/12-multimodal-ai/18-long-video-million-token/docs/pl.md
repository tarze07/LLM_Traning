# Zrozumienie długiego wideo w kontekście miliona tokenów

> Godzinny film 4K przy 24 kl./s, po poprawieniu i osadzeniu, generuje około 60 milionów tokenów. Transkrypcja 2-godzinnego odcinka podcastu kosztuje 30 000 tokenów. Pełny film fabularny Blu-ray, nawet skompresowany przy użyciu agresywnego łączenia, to setki tysięcy tokenów. Usługa Google Gemini 1.5 (marzec 2024 r.) otworzyła tę erę kontekstem zawierającym 10 milionów tokenów, zapewniając niezawodne przypominanie igły w stogu siana w ciągu godzinnych filmów. LWM (Liu i in., luty 2024) pokazał ścieżkę skalowania uwagi pierścieniowej. LongVILA i Video-XL jeszcze bardziej skalowały spożycie. VideoAgent zamienił surowy kontekst na pobieranie agenta. Każde podejście to inny kompromis w zakresie złożoności obliczeń, przypominania i inżynierii. W tej lekcji czytamy je obok siebie.

**Typ:** Kompilacja
**Języki:** Python (stdlib, symulator igły w stogu siana + router pobierania agentów)
**Wymagania wstępne:** Faza 12 · 17 (tymczasowe tokeny wideo)
**Czas:** ~180 minut

## Cele nauczania

- Oblicz całkowitą liczbę tokenów wizualnych dla długich filmów przy różnej liczbie klatek na sekundę i łączeniu.
- Wyjaśnij trzy ścieżki skalowania: kontekst brutalny (Gemini 1.5), uwaga pierścieniowa (LWM), kompresja tokena (LongVILA / Video-XL).
- Porównaj VLM wideo z surowym kontekstem i VLM z pobieraniem agenta (VideoAgent) pod względem dokładności i opóźnienia.
- Zaprojektuj test igły w stogu siana na 30-minutowy film i przypomnij sobie pomiar w określonej minucie.

## Problem

Pojedyncza klatka poprawek w rozmiarze Qwen2.5-VL w natywnej rozdzielczości 384 to ~729 tokenów. Przy łączeniu 3x3 daje to 81 tokenów na klatkę. 30-minutowy klip przy 1 FPS = 1800 klatek = 145 800 tokenów. Wykonalne do 2025 r. Otwarte VLM, szczelne. Przy 2 FPS 291 600 tokenów — pasują tylko największe konteksty.

2-godzinny film przy 1 FPS to 583 tys. tokenów. Poza większością otwartych modeli na rok 2026; wymaga Gemini 2.5 Pro lub bardziej agresywnego łączenia.

Pojawiły się trzy ścieżki skalowania.

## Koncepcja

### Ścieżka 1: Brutalny kontekst (Gemini 1.5, Claude Opus)

Rzuć sprzęt na problem. Skaluj kontekst do milionów tokenów, przetwarzaj wszystko w jednym przebiegu do przodu.

Uruchomiono Gemini 1.5 Pro z tokenami 1M; Bliźnięta 1,5 Ultra do 10M; Gemini 2.5 Pro w 2026 roku niezawodnie nagrywa wiele godzin filmów. Artykuł (arXiv:2403.05530) dokumentuje wycofanie „igły w stogu siana” na poziomie 99,7% aż do ~9,5 mln tokenów.

Inżynieria: niestandardowa implementacja uwagi z hierarchią pamięci (lokalna + globalna + rzadka) plus routing ekspercki MoE zapewniający wydajność w długim kontekście. Nieopublikowane w całości. Nie open source.

### Ścieżka 2: Uwaga pierścieniowa (LWM, LongVILA)

Uwaga pierścienia rozdziela długie sekwencje między urządzeniami w „pierścień”, w którym każde urządzenie przechowuje fragment. Uwaga w całej sekwencji odbywa się w ten sposób, że każde urządzenie wysyła swoją porcję do następnego według wzoru pierścieniowego, oblicza częściową uwagę i agreguje.

LWM (Liu i in., 2024) wytrenował w ten sposób model kontekstu z tokenem 1M. Uczenie obliczeń skaluje się liniowo w zależności od kontekstu, a nie kwadratowo — kwadratowe uderzenie w uwagę jest amortyzowane na wszystkich urządzeniach pierścienia.

LongVILA (arXiv:2408.10188) dostosował wzór do VLM. Filmy zawierające 1400 klatek przy 192 tokenach na klatkę = 268 tys. kontekstu, trenowane z uwagą pierścieniową w 8-kierunkowej równoległości.

### Ścieżka 3: Kompresja tokena (Video-XL, LongVA)

Tańszy niż brutalny kontekst: kompresuj agresywnie, zanim LLM zobaczy sekwencję.

Video-XL (arXiv:2409.14485) wykorzystuje wizualny token podsumowania: każdy klip składający się z N klatek tworzy pojedynczy token „podsumowania”, który obsługuje N. Podsumowując, LLM widzi jeden token podsumowania na klip, drastycznie zawężając kontekst.

LongVA rozszerza kontekst LLM z 200 tys. do 2M za pomocą techniki „transferu długiego kontekstu”. Trenuj na tekście o długim kontekście, przenieś na wideo o długim kontekście za pomocą współdzielonej reprezentacji.

Kompresja tokenów rezygnuje z przywoływania w określonych znacznikach czasu w celu zapewnienia skalowalności. Modelka na ogół wie, co się wydarzyło, ale czasami pomija dokładne klatki.

### Ścieżka 4: Odzyskiwanie agenta (VideoAgent)

Nie przesyłaj całego wideo do LLM. Zamiast tego traktuj wideo jako bazę danych i użyj LLM, aby wysłać do niego zapytanie.

Agent wideo (arXiv:2403.10517):

1. LLM czyta pytanie.
2. LLM prosi narzędzie do wyszukiwania odpowiednich klipów („pokaż mi segmenty z kotem”).
3. Narzędzie zwraca pasujące znaczniki czasu klipu.
4. LLM odczytuje te klipy za pośrednictwem VLM.
5. LLM tworzy odpowiedź lub zadaje pytania uzupełniające.

To jest wzorzec LLM jako agenta zastosowany do długich filmów. Tańsze wnioskowanie (zakodowane tylko odpowiednie klipy), trudniejsza inżynieria (wąskim gardłem staje się jakość wyszukiwania).

### Testy porównawcze przypominające igłę w stogu siana

Standardowy test długiego kontekstu: wstaw unikalny znacznik wizualny lub tekstowy w losowym miejscu filmu, a następnie zadaj zapytanie wymagające jego przypomnienia.

Metryka: Recall@k w zależności od długości wideo i pozycji znacznika.

Gemini 2.5 Pro osiąga ponad 99% zapamiętywania filmów trwających do 90 minut. Otwarte modele 72B (Qwen2.5-VL-72B, InternVL3-78B) uzyskują wynik ~85-90% po 30 minutach i degradują powyżej 60.

VideoAgent może dopasowywać lub pokonywać modele z surowym kontekstem w ciągu ponad 2 godzin, ponieważ pobieranie jest niezwykle trudne, jeśli narzędzie jest dobre.

### Którą ścieżkę wybrać

W przypadku 15-minutowego klipu z pogranicza dokładności: zwykle działa otwarty kontekst 72B + natywny. Wybierz Qwen2.5-VL-72B.

W przypadku treści trwających od 30 minut do 1 godziny: LongVILA lub Video-XL w wersji otwartej; Gemini 2.5 Pro dla zamkniętych. Pasek jakości ma znaczenie — granica zostaje zamknięta.

W przypadku treści trwających ponad 2 godziny: VideoAgent lub podobne wzorce wyszukiwania. Alternatywnie możesz podsumowywać w mniejszych fragmentach i podawać podsumowania hierarchiczne.

### Wzór produkcji 2026

W praktyce potoki produkcyjne długich filmów wideo są hybrydowe:

1. Uruchom dynamiczne próbkowanie FPS + agresywne łączenie całego wideo (uzyskaj globalną reprezentację o wartości 100 tys. tokenów).
2. Przejdź do 72B VLM, aby uzyskać globalne podsumowanie.
3. Jeśli użytkownik zadaje szczegółowe pytania, uruchom pobieranie agenta, używając podsumowania jako indeksu.

Łączy to brutalny kontekst dla globalnego zrozumienia i wyszukiwania lokalnych szczegółów.

## Użyj tego

`code/main.py`:

- Oblicza budżety tokenów dla filmów od 1 minuty do 3 godzin przy różnej liczbie klatek na sekundę i łączeniu.
- Symuluje bieg po igle w stogu siana: wstrzyknij znacznik w losowym znaczniku czasu, zadaj pytanie, przypomnij sobie wynik.
— Zawiera symulator routera odzyskiwania agenta, który wybiera określone klipy do przesłania do dalszego VLM.

Uruchom tabelę budżetu i poczuj lukę skali.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-long-video-strategy-planner.md`. Biorąc pod uwagę czas trwania filmu i złożoność zapytania, wybiera pomiędzy brutalnym kontekstem, kompresją i pobieraniem agentycznym i oblicza oczekiwane opóźnienie + jakość.

## Ćwiczenia

1. 45-minutowy wykład przy 1 FPS, 81 tokenów na klatkę. Łączna liczba tokenów? Pasuje do kontekstów jakich modeli?

2. Zaprojektuj test igły w stogu siana: w której minucie wstrzykujesz znacznik i jaki jest dokładny format zapytania?

3. Porównaj Qwen2.5-VL-72B w kontekście brutalnym (kontekst 80 tys.) z VideoAgent (Claude 3.5 + pobieranie) na 1-godzinnym filmie. Które wygrywa w przypadku wycofania? Które wygrywa pod względem opóźnień?

4. Koszt pamięci uwagi pierścienia skaluje się liniowo według długości sekwencji i liniowo według liczby urządzeń. Wyjaśnij, dlaczego i co się nie powiedzie, jeśli porzucisz fazę rotacji pierścienia.

5. Przeczytaj Gemini 1.5, rozdział 5 na temat igły w stogu siana. Co w artykule stwierdzono na temat wycofania na granicy tokenów 1M i 10M?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|--------------------------------------|
| Brutalny kontekst | „Tylko więcej tokenów” | Skaluj kontekst LLM do milionów tokenów; przetworzyć wszystko w jednym przebiegu |
| Uwaga pierścienia | „Równolegle w stylu LWM” | Rozproszony wzorzec uwagi, w którym każde urządzenie trzyma kawałek i obraca się |
| Kompresja tokena | „Tokeny podsumowujące” | Zmniejsz liczbę tokenów na klip za pomocą wyuczonego kompresora przed LLM |
| Igła w stogu siana | „Test NIH” | Umieść unikalny znacznik w losowym miejscu, poproś modela, aby przywołał go w czasie testu |
| Odzyskiwanie agentów | „LLM jako planista zapytań” | LLM prosi narzędzie do wyszukiwania odpowiednich klipów, czyta je za pomocą VLM, tworzy odpowiedź |
| WideoAgent | „Wzór pobierania wideo” | Kanoniczny projekt odzyskiwania agenta: pytanie -> narzędzie -> klip -> odpowiedź |

## Dalsze czytanie

– [Zespół Gemini — Gemini 1.5 (arXiv:2403.05530)](https://arxiv.org/abs/2403.05530)
- [Liu i in. — LWM / RingAttention (arXiv:2402.08268)](https://arxiv.org/abs/2402.08268)
- [Xue i in. — LongVILA (arXiv:2408.10188)](https://arxiv.org/abs/2408.10188)
- [Shu i in. — Wideo-XL (arXiv:2409.14485)](https://arxiv.org/abs/2409.14485)
- [Wang i in. — VideoAgent (arXiv:2403.10517)](https://arxiv.org/abs/2403.10517)