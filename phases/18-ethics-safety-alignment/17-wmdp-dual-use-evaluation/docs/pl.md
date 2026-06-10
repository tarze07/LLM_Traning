# Ocena możliwości WMDP i podwójnego zastosowania

> Li i in., „The WMDP Benchmark: Measuring and Reducing Malicious Use with Unlearning” (ICML 2024, arXiv:2403.03218). 4157 pytań wielokrotnego wyboru dotyczących bezpieczeństwa biologicznego (1520), cyberbezpieczeństwa (2225) i chemii (412). Pytania mieszczą się w „żółtej strefie” — wiedza przybliżona, filtrowana na podstawie przeglądu wielu ekspertów i zgodności z przepisami ITAR/EAR. Podwójny cel: zastępcza ocena możliwości podwójnego zastosowania i test porównawczy usuwania uczenia się (towarzysząca metoda RMU zmniejsza wydajność WMDP, zachowując jednocześnie ogólne możliwości). Narracja terenowa na lata 2024–2025: wczesne oceny OpenAI/Anthropic 2024 wykazały „łagodny wzrost” w stosunku do wyszukiwania w Internecie; do kwietnia 2025 r. w ramach gotowości OpenAI v2 stwierdzono, że modele „są o krok od znaczącej pomocy nowicjuszom w tworzeniu znanych zagrożeń biologicznych”. Badanie Anthropic dotyczące nabycia broni biologicznej wykazało 2,53-krotny wzrost, co jest niewystarczające, aby wykluczyć ASL-3.

**Typ:** Ucz się
**Języki:** Python (stdlib, uprząż ewaluacyjna w kształcie WMDP)
**Wymagania wstępne:** Faza 18 · 16 (oprzyrządowanie zespołu czerwonego), faza 14 (inżynieria agentów)
**Czas:** ~60 minut

## Cele nauczania

- Opisz trzy domeny WMDP, liczbę pytań i kryterium filtrowania „żółtej strefy”.
- Wyjaśnij RMU i dlaczego WMDP jest zarówno punktem odniesienia dla oceny, jak i oduczenia się.
– Proszę opisać narrację dotyczącą wzrostu gospodarczego w latach 2024–2025: „łagodny wzrost” -> „na krawędzi” -> „niewystarczający, aby wykluczyć ASL-3”.
- Odróżnij wzrost względny nowicjusza od umiejętności absolutnych eksperta.

## Problem

Możliwość podwójnego zastosowania jest problemem pomiarowym w ramach ram bezpieczeństwa każdego laboratorium (lekcja 18). Pytanie: czy model X w istotny sposób zwiększa zdolność nowicjusza do wyrządzania masowych szkód w biologii, chemii i cyberprzestrzeni? Pomiar bezpośredni (poproś modelkę, aby faktycznie wyrządził krzywdę) jest nielegalny i nieetyczny. Pomiar zastępczy wymaga punktu odniesienia, którego model nie może odmówić (aby uzyskać uczciwe liczby dotyczące możliwości), ale którego pytania same w sobie nie są szkodliwymi publikacjami.

## Koncepcja

### „Żółta strefa”

Pytania wymagające bliskiej, umożliwiającej poznanie szkodliwego procesu, niebędące receptą na bezpośrednią syntezę. „Jaki odczynnik katalizuje etap 4 [opublikowanej ścieżki]?” a nie „jak zrobić [niebezpieczny związek]?” Każde pytanie sprawdzane przez wielu ekspertów dziedzinowych; filtrowane pod kątem zgodności z przepisami dotyczącymi kontroli eksportu ITAR/EAR.

Łącznie 4157 pytań:
- Bezpieczeństwo biologiczne: 1520
- Cyberbezpieczeństwo: 2225
- Chemia: 412

Format wielokrotnego wyboru. Modelki odpowiadają, nie prosząc o jakąkolwiek pomoc; możliwości można zmierzyć bez wywoływania szkodliwych zachowań.

### RMU — błędny kierunek reprezentacji w przypadku oduczania się

Metoda oduczania towarzysza. Zastosowany do LLaMa-2-7B, obniżył wyniki WMDP do niemal losowych, zachowując jednocześnie MMLU i inne standardy ogólnych możliwości w granicach kilku punktów procentowych. Opublikowana metoda stanowi punkt odniesienia dla każdego kolejnego artykułu dotyczącego oduczania się w obszarze biochemii i cybernetyki.

### Narracja o wzroście w latach 2024–2025

Trzy fazy:

1. **2024 „łagodny wzrost”.** Wczesne oceny OpenAI i Anthropic Readness/RSP wykazały niewielką przewagę nad wyszukiwaniem internetowym w przypadku nowicjuszy próbujących wykonywać zadania związane z biologią. Ramy publiczne: modele pionierskie pomagają, ale nie bardziej niż Google.

2. **Kwiecień 2025 r. „na krawędzi”.** Ramy gotowości OpenAI v2 zgłosiły modele „u progu znaczącego pomagania nowicjuszom w tworzeniu znanych zagrożeń biologicznych”. Nie twierdzenie o zdolnościach – ostrzeżenie, że szczyt jest już blisko.

3. **Badanie Anthropic dotyczące pozyskiwania broni biologicznej w 2025 r.** Kontrolowane badanie z udziałem początkujących uczestników mierzyło względny sukces w zadaniach na etapie zdobywania. Odnotowano wzrost 2,53x. Niewystarczający, aby wykluczyć ASL-3 (lekcja 18) — próg poziomu 3 Polityki odpowiedzialnego skalowania firmy Anthropic został osiągnięty lub zbliżony.

### Krewny nowicjusz kontra absolutny ekspert

Kluczowe rozróżnienie:

- **Podniesienie względne dla nowicjusza.** W jakim stopniu model pomaga osobie niebędącej ekspertem? Mnożny. Względna przewaga jest duża, ponieważ nowicjusze wiedzą niewiele; nawet skromna informacja pomaga.
- **Możliwości absolutnie eksperckie.** Ile informacji generuje model przy maksymalnym wysiłku? Ekspert może wydobyć więcej niż nowicjusz. Absolutny pułap jest wysoki.

Przypadki bezpieczeństwa (Lekcja 18) dotyczą obu kwestii: „model nie może zapewnić nowicjuszowi wystarczającej poprawy do wykonania” oraz „ekspert nie może wydobyć informacji z modelu, który nie został jeszcze opublikowany”.

### Pułapka pomiarowa

WMDP to proxy możliwości, a nie pomiar wdrożenia. Model, który uzyskał wysokie wyniki w WMDP, może, ale nie musi, zostać wykorzystany przez nowicjusza w praktyce, w zależności od:
- Odporność na wzbudzenie (jak trudno jest uzyskać tę zdolność bez wyłączania filtrów bezpieczeństwa)
- Wiedza ukryta (zdolność wymagająca umiejętności mokrego laboratorium, a nie informacji)
- Bariery wykonawcze (zakupy, sprzęt)

Próba nabycia broni biologicznej przeprowadzona przez Anthropic w 2025 r. dodaje warstwę pozyskiwania nowicjuszy do możliwości w stylu WMDP: mierzy ona rzeczywisty sukces zadania, a nie zdolność wielokrotnego wyboru.

### Gdzie to pasuje do fazy 18

Lekcje 12-16 dotyczą narzędzi ataku i obrony na wynikach modelu. Lekcja 17 to warstwa zdolności podwójnego zastosowania – miara, którą oceniają graniczne ramy bezpieczeństwa (lekcja 18). Lekcja 30 zamyka wątek obecnymi dowodami na rozwój cyber/bio/chemiczny/nuklearny w 2026 roku.

## Użyj tego

`code/main.py` buduje zabawkową uprząż ewaluacyjną w kształcie WMDP. Model próbny jest testowany na pytaniach podzielonych na kategorie; raportowane są wyniki na domenę. Prosta interwencja polegająca na oduczeniu się (wyzerowanie reprezentacji specyficznej dla domeny) zmniejsza wyniki; możesz zmierzyć kompromis w stosunku do ogólnych możliwości.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-wmdp-eval.md`. Biorąc pod uwagę twierdzenie o możliwości podwójnego zastosowania („nasz model nie pomaga w znaczący sposób w przypadku broni biologicznej”), przeprowadza się kontrolę: jakie testy porównawcze przeprowadzono, jaką ścieżkę odmowy zastosowano do oceny (surowe ukończenie czy poddane kontroli polityki) oraz czy badania pozyskiwania nowicjuszy uzupełniają wynik wielokrotnego wyboru.

## Ćwiczenia

1. Uruchom `code/main.py`. Zgłaszaj dokładność dla poszczególnych domen przed i po etapie oduczania zabawki. Wyjaśnij kompromis w zakresie ogólnych możliwości.

2. Rozszerz WMDP zabawek o czwartą domenę (np. radiologiczną). W żółtej strefie określ dwa przykładowe typy pytań. Wyjaśnij, dlaczego tworzenie takich pytań jest trudniejsze niż dodawanie pytań w kształcie MMLU.

3. Przeczytaj sekcję 5 WMDP 2024 (metodologia RMU). Naszkicuj prostsze podejście do usuwania uczenia się (np. wyłącz górne k neuronów dla treści domeny) i opisz jego oczekiwany koszt w zakresie ogólnej zdolności.

4. Badanie Anthropic 2025 dotyczące pozyskania broni biologicznej wykazało 2,53-krotny wzrost. Opisz dwa sposoby odchylenia tej liczby w górę (wielkość próby nowicjuszy, wierność zadania) i dwa w dół (pułap wzbudzenia, bramka bezpieczeństwa modelu).

5. Wyraź, czego wymaga uzasadnienie bezpieczeństwa dla ASL-3 poza zaliczeniem oduczania WMDP. Wymień co najmniej dwa uzupełniające się badania wzbudzające.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|--------------------------------------|
| WMDP | „wskaźnik podwójnego zastosowania” | 4157 pytań MCQ z zakresu bio/cyber/chemii w żółtej strefie |
| Strefa żółta | „umożliwianie syntezy, ale nie” | Bliska wiedza związana ze szkodliwą zdolnością, nie będąca receptą na syntezę |
| RMU | „punkt bazowy oduczania się” | Reprezentacja Błędny kierunek dla oduczenia się; zmniejsza wyniki WMDP, zachowuje ogólną zdolność |
| Wzrost względny nowicjusza | „jak bardzo to pomaga nieekspertom” | Multiplikatywna przewaga nad wyszukiwaniem internetowym status quo dla nowicjusza |
| Absolutny ekspert | „sufit dla ekspertów” | Maksymalna ilość informacji możliwych do wydobycia z modelu przez zmotywowanego eksperta |
| Zadanie w fazie przejęcia | „kroki przed syntezą” | Zamówienia publiczne, sprzęt, pozwolenia — najwcześniejsze etapy ścieżki szkody |
| ITAR/Ucho | „przestrzeganie kontroli eksportu” | Ramy prawne ograniczające publikowanie określonej wiedzy wspomagającej |

## Dalsze czytanie

- [Li i in. — Benchmark WMDP (arXiv:2403.03218, ICML 2024)](https://arxiv.org/abs/2403.03218) — benchmark i dokument RMU
- [OpenAI — Gotowość Framework v2 (15 kwietnia 2025 r.)](https://openai.com/index/updating-our-preparedness-framework/) — język „na zakręcie”
– [Anthropic — Zasady odpowiedzialnego skalowania, wersja 3.0 (luty 2026 r.)](https://www.anthropic.com/responsible-scaling-policy) — Próg biologiczny ASL-3 i wyniki próby akwizycji
- [DeepMind — Frontier Safety Framework v3.0 (wrzesień 2025)](https://deepmind.google/blog/strengthening-our-frontier-safety-framework/) — bio-uplift CCL