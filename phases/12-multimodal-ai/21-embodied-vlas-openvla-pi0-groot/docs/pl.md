# Wbudowane VLA: RT-2, OpenVLA, π0, GR00T

> Modelka po raz pierwszy przeczytała przepis ze strony internetowej i wykonała go w robocie kuchennym za pomocą robota kuchennego RT-2 (Google DeepMind, lipiec 2023 r.). W ramach projektu RT-2 dyskretyzowano działania w postaci tokenów tekstowych, dostrojono VLM na podstawie danych internetowych oraz danych dotyczących działań robotów i udowodniono, że wiedza o języku wizyjnym na skalę sieciową jest transferowana do sterowania robotycznego. OpenVLA (czerwiec 2024) dostarczyło otwartą wersję referencyjną 7B. Seria π0 firmy Physical Intelligence (2024–2025) dodała ekspertów w zakresie działań dopasowujących przepływ. NVIDIA GR00T N1 (marzec 2025 r.) zapewniła sterowanie dwoma systemami (System 1 / System 2) dla robotów humanoidalnych na dużą skalę. Prymityw VLA — wizja, język i działanie, pojedynczy model, który widzi, czyta i działa — jest pomostem pomiędzy modelami rozumienia tej fazy a systemami autonomicznymi w fazie 15.

**Typ:** Ucz się
**Języki:** Python (stdlib, tokenizer akcji + szkielet wnioskowania VLA)
**Wymagania wstępne:** Faza 12 · 05 (LLaVA), Faza 15 (Systemy autonomiczne, odniesienie)
**Czas:** ~180 minut

## Cele nauczania

- Opisać tokenizację akcji: dyskretne kodowanie binarne (RT-2), wydajne tokeny akcji FAST, ciągłe akcje dopasowujące przepływ (π0).
- Wyjaśnij, dlaczego wspólne dostrajanie danych w sieci i robotach pozwala zachować transfer wiedzy ogólnej do nowatorskich zadań.
- Porównaj OpenVLA (otwarty 7B Lama+VLM), π0 (dopasowanie przepływu) i GR00T N1 (dwa systemy) w tym samym zadaniu robota.
- Nazwij zbiór danych Open X-Embodiment i jego rolę jako korpusu szkoleniowego RT-X.

## Problem

Robot wykonujący prace domowe na podstawie instrukcji w języku naturalnym jest celem badań od lat 70. XX wieku. Odpowiedź na lata 20. XX w.: model wizji, języka i działania (VLA). Ta sama architektura VLM używana w VQA, ale dane wyjściowe to działania (momenty obrotowe stawów, pozycje efektorów końcowych, polecenia dyskretne) zamiast tekstu.

Wyzwania specyficzne dla VLA:

1. Przestrzenie działania są ciągłe (kąty połączeń, siły) i wielowymiarowe (ramię 7-DOF + chwytak 3-DOF = 10 przyciemnień przy 30 Hz).
2. Dane szkoleniowe dotyczące konkretnych robotów są rzadkie. Otwarte X-Embodiment ma trajektorie ~1M; obraz tekstowy w Internecie to 5B+.
3. Częstotliwość kontroli ma znaczenie. Pętla kontrolna 30 Hz oznacza budżet 33 ms na akcję.
4. Bezpieczeństwo. Niewłaściwe działanie powoduje uszkodzenie sprzętu, ludzi lub mienia.

## Koncepcja

### Tokenizacja akcji (RT-2)

Sztuczka RT-2: przedstaw każdy wspólny cel jako skwantowany żeton tekstowy. Dyskretyzuj znormalizowany zakres [-1, 1] na 256 przedziałów, mapuj każdy przedział na identyfikator słownictwa. Akcja 10-DOF staje się 10 żetonami na każdym etapie kontroli.

Wspólne dostrojenie PaLM-X VLM w mieszaninie:

- Pary obraz-tekst w sieci Web (napisy, VQA).
- Pokazy robotów, akcja w formie żetonów.

Model widzi „podnieś czerwoną kostkę” (język) → obraz (wizja) → 10-żetonową sekwencję akcji (dyskretne wspólne cele). Wstępne uczenie w sieci pozwala zachować transfer wiedzy ogólnej: RT-2 może podążać za „przesuwaniem się w stronę szybko poruszającego się obiektu”, nawet jeśli w danych treningowych nie ma słowa „szybko poruszający się”.

Wnioskowanie przy 3-5 Hz w artykule RT-2, ograniczone przez dekodowanie autoregresyjne VLM.

### OpenVLA — otwarte odniesienie 7B

OpenVLA (Kim i in., czerwiec 2024) jest odpowiednikiem RT-2 z otwartą wagą. Szkielet 7B Lama, podwójny koder wizyjny DINOv2 + SigLIP, tokenizacja akcji w 256 pojemnikach.

Szkolenie w Open X-Embodiment (970 tys. trajektorii w 22 robotach). Dostarczane ze wsparciem dostrajania LoRA w celu dostosowania do nowych robotów.

Wniosek: 4-5 Hz na A100 z kwantyzacją. Wystarczająco szybki do powolnej manipulacji, a nie do kontroli wysokich częstotliwości.

### FAST tokenizer — szybsze dekodowanie akcji

Pertsch i in. (2024) wykazali, że tokenizacja dyskretnych binów jest nieefektywna — większość działań skupia się w małym obszarze przestrzeni bin. FAST (Frequency-Domain Action Sequence Tokenizer) kompresuje sekwencje akcji poprzez DCT i kwantyzuje współczynniki.

30-etapowa trajektoria akcji to ~10 żetonów FAST zamiast 300 żetonów z dyskretnymi pojemnikami. Wnioskowanie przyspiesza 3-5 razy bez utraty jakości.

### π0 i akcje dopasowujące przepływ

π0 inteligencji fizycznej (Black et al., październik 2024 r.) zastępuje dyskretne żetony akcji ekspertem akcji dopasowującym przepływ:

- Mały transformator akcji odczytuje ukryte stany VLM i generuje ciągłą 50-krokową sekwencję działania poprzez wyprostowany przepływ.
- Głowa akcji trenuje ze stratą dopasowania przepływu; Trening wstępny VLM pozostaje niezmieniony.
- Wnioskowanie: pełna sekwencja akcji emitowana w ~5 krokach odszumiania, efektywnie sterowanie 50 Hz.

Twierdzenie π0: pokonuje OpenVLA i Octo w szerokim zakresie zadań manipulacyjnych. Formuła o ciągłym działaniu zachowuje gładkość, którą niszczy dyskretyzacja.

π0.5 i π0-FAST to aktualizacje przyrostowe. π0-FAST łączy tokenizację FAST z dopasowaniem przepływu.

### GR00T N1 — podwójny system dla humanoidów

NVIDIA GR00T N1 (marzec 2025) została stworzona dla robotów humanoidalnych (>30 DOF, całe ciało):

- System 2: duża scena czytania VLM + instrukcja, tworząca cele cząstkowe wysokiego poziomu przy ~1 Hz.
- System 1: mały transformator z głowicą czynną wytwarzający wspólne polecenia niskiego poziomu 50-100 Hz uwarunkowane celami cząstkowymi.

Podział ten odpowiada szybkiemu i powolnemu myśleniu Kahnemana: System 2 planuje, System 1 działa. Korzyści: powolne planowanie na poziomie VLM nie blokuje szybkiej kontroli; System 1 pozostaje mały ze względu na opóźnienia.

GR00T N1.7 (koniec 2025 r.) poprawia skalowanie danych. GR00T dostraja się, korzystając z danych symulacyjnych i rzeczywistych z Omniverse.

### Otwórz wersję X

Dane treningowe. W ramach projektu RT-X (październik 2023 r.) zebrano 22 zbiory danych obejmujące 1 milion trajektorii w 22 robotach. Open X-Embodiment to korpus, którego wszyscy używają:

- ALOHA / Bridge V2 / Droid / RT-2 Kuchnia / Stolik językowy.
- Każda próbka: (stan robota, widoki z kamery, instrukcja, sekwencja działań).
- Higiena treningu: ujednolicenie przestrzeni akcji, normalizacja zakresów stawów, zmiana rozmiaru kamer.

Pociąg OpenVLA i π0 w Open X-Embodiment. Luka w domenie w stosunku do konkretnego robota jest wypełniana przez dostrajanie LoRA na 100-1000 demonstracjach specyficznych dla zadań.

### Wspólne dostrajanie zamiast korzystania tylko z robota

Współdostrajanie łączy dane internetowe VQA z trajektoriami robotów. Proporcje mają znaczenie: za dużo VQA i model zapomina o działaniach; za dużo danych robota i model traci wiedzę ogólną.

Stosunek RT-2: ~1:1. OpenVLA: ~0,5:1 z sieci do robota. π0: podobne. Dokładny współczynnik to hiperparametr, który należy dostroić według rozmiaru zestawu danych.

Szkolenie wyłącznie na robotach tworzy modele specyficzne dla zadania, które nie spełniają instrukcji spoza dystrybucji. Dostrajanie to różnica pomiędzy „podnieś czerwoną kostkę (w wersji demonstracyjnej)” a „podnieś trzeci co do wielkości obiekt od lewej (nowe sformułowanie)”.

### Limity bezpieczeństwa i działania

Każda produkcyjna VLA jest dostarczana z:

- Twarde ograniczenia połączeń (nie można dokręcić powyżej specyfikacji).
- Ograniczenia prędkości (miękkie obcinanie).
- Ograniczenia obszaru roboczego (efektor końcowy nie może opuścić stołu).
- Zatwierdzanie nowatorskich zadań przez człowieka w pętli.

Znajdują się one poza VLA jako kontrole warstwy kontrolnej. Dane wyjściowe VLA są sugestią, a nie poleceniem.

## Użyj tego

`code/main.py`:

- Implementuje tokenizację i detokenizację akcji 256-bin.
- Szkicuje SZYBKI tokenizator oparty na kwantyzacji DCT +.
- Porównuje liczbę tokenów na krok akcji (dyskretny pojemnik, SZYBKI, przepływ ciągły).
- Drukuje podsumowanie rodowodu RT-2 → OpenVLA → π0 → GR00T.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-vla-action-format-picker.md`. Biorąc pod uwagę zadanie robota (manipulacja, nawigacja, humanoidalne całe ciało), wybiera pomiędzy dyskretnym pojemnikiem + RT-2, FAST + OpenVLA, dopasowywaniem przepływu + π0 lub systemem podwójnym + GR00T.

## Ćwiczenia

1. Ramię 10-DOF przy częstotliwości sterowania 30 Hz. Tokenizacja dyskretna przy 256 pojemnikach emituje ile tokenów na sekundę? Czy 7B VLM może dotrzymać kroku?

2. SZYBKA tokenizacja kompresuje 30-stopniowe trajektorie do ~10 tokenów. Co traci użytkownik, jeśli na trajektorii występuje ruch o wysokiej częstotliwości (np. bębnienie)?

3. Głowica dopasowująca przepływ π0 odszumia w ~5 krokach. Porównaj przepustowość z dekodowaniem autoregresyjnym OpenVLA przy 4-5 Hz.

4. System 1/System 2 GR00T rozdzielił mapy na Kahnemana. Zaproponuj inny podział (System 3?), który mógłby pomóc w chodzeniu dwunożnym.

5. Przeczytaj sekcję 4 Open X-Embodiment na temat sprawdzania zbioru danych. Wymień trzy zasady sprawdzania, które zapobiegają wyciekom domeny.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|--------------------------------------|
| VLA | „Wizja-język-działanie” | Model pobierający obraz + instrukcję i wyprowadzający polecenia akcji |
| Tokenizacja akcji | „Dyskretne pojemniki” | Kwantyzuj ciągłe wspólne cele w 256 pojemnikach na dim, każdy z identyfikatorem słownictwa |
| SZYBKI tokenizer | „Żetony akcji częstotliwości” | DCT + kwantyzacja w celu skompresowania 30-stopniowych trajektorii do ~10 tokenów |
| Współdostrojenie | „Połącz sieć + robot” | Trenuj w Internecie dane VQA wraz z demonstracjami robotów, aby zachować ogólną wiedzę |
| Głowica dopasowująca się do przepływu | „wyjście ciągłe π0” | Mały transformator generujący 50-stopniową sekwencję działania poprzez wyprostowany przepływ |
| System 1 / System 2 | „Sterowanie dwusystemowe” | Duży VLM planuje powoli, mały szef działa szybko; Wzór GR00T |
| Otwórz wykonanie X | „Zbiór danych RT-X” | Zbiór danych obejmujący różne roboty o trajektorii 1M; korpus szkoleniowy |

## Dalsze czytanie

- [Brohan i in. — RT-2 (arXiv:2307.15818)](https://arxiv.org/abs/2307.15818)
- [Kim i in. — OpenVLA (arXiv:2406.09246)](https://arxiv.org/abs/2406.09246)
- [Black i in. — π0 (arXiv:2410.24164)](https://arxiv.org/abs/2410.24164)
- [NVIDIA — GR00T N1 (arXiv:2503.14734)](https://arxiv.org/abs/2503.14734)
– [Open X-Embodiment Collab — RT-X (arXiv:2310.08864)](https://arxiv.org/abs/2310.08864)