# Optymalizacja roju dla LLM (PSO, ACO)

> Optymalizacja inspirowana biologią powraca w LLM. **LMPSO** (arXiv:2504.09247) wykorzystuje PSO, gdzie prędkość każdej cząstki jest podpowiedzią, a LLM generuje kolejnego kandydata; działa dobrze na wynikach o uporządkowanej sekwencji (wyrażenia matematyczne, programy). **Model Swarms** (arXiv:2410.11163) traktuje każdego eksperta LLM jako cząstkę PSO na rozmaitości wag modelu i raportuje **średni wzrost o 13,3%** w 12 liniach bazowych w 9 zbiorach danych z zaledwie 200 instancjami. **SwarmPrompt** (ICAART 2025) hybrydyzuje PSO i Gray Wolf w celu szybkiej optymalizacji. **AMRO-S** (arXiv:2603.12933) to inspirowany ACO specjalista od feromonów do wieloagentowego routingu LLM — **przyspieszenie 4,7x**, interpretowalne dowody routingu, asynchroniczna aktualizacja bramkowana pod względem jakości, która oddziela wnioskowanie od uczenia się. Ta lekcja implementuje PSO w przestrzeni parametrów podpowiedzi i ACO w routingu agentów, mierzy, dlaczego te klasyczne algorytmy pasują do ery LLM, a kiedy nie.

**Typ:** Ucz się + Buduj
**Języki:** Python (stdlib)
**Wymagania wstępne:** Faza 16 · 09 (Równoległe sieci roju), Faza 16 · 14 (Konsensus i BFT)
**Czas:** ~75 minut

## Problem

Masz podpowiedź, która w ocenie zadania uzyskała 62% punktów. Chcesz to poprawić. Naiwnym posunięciem jest ręczne poprawianie bez gradientów, które źle się skaluje. Uczenie się przez wzmacnianie wymaga sygnałów nagrody i wystarczającej liczby wdrożeń, aby móc trenować. Podparcie za pomocą podpowiedzi nie jest w rzeczywistości możliwe — zachęta jest dyskretnym ciągiem znaków, a nie różniczkowalnym parametrem.

Klasyczna optymalizacja inspirowana biologią — PSO dla przestrzeni ciągłego przeszukiwania, ACO dla wyboru ścieżki — została zaprojektowana dokładnie dla tego reżimu: bez gradientów, w oparciu o populację, tania w przeliczeniu na ocenę. Połącz je z LLM, aby uzyskać krok wyszukiwania bez gradientów, a otrzymasz zaskakująco praktyczny optymalizator.

Te same wzorce dotyczą *routowania* agentów w systemach wieloagentowych. Ślad feromonowy w stylu ACO rejestruje, który agent najlepiej sprawdził się przy danym typie zadania, umożliwia routerowi wykorzystanie śladu i rozkłada feromony, dzięki czemu można ponownie odkryć trasy.

## Koncepcja

### Przypomnienie PSO (Kennedy i Eberhart 1995)

Optymalizacja roju cząstek: populacja cząstek w ciągłej przestrzeni poszukiwań. Każda cząstka ma położenie `x_i` i prędkość `v_i`. Każda iteracja:

```
v_i <- w * v_i + c1 * r1 * (p_best_i - x_i) + c2 * r2 * (g_best - x_i)
x_i <- x_i + v_i
evaluate fitness(x_i)
update p_best_i if improved
update g_best if global best
```

Gdzie `p_best` to najlepszy wynik cząstki, `g_best` to najlepszy wynik roju, `w, c1, c2` to wagi bezwładności + poznawcze + społeczne, `r1, r2` to czynniki losowe.

### PSO na wyjściach LLM — LMPSO

arXiv:2504.09247 dostosowuje PSO do ustrukturyzowanych wyników generowanych przez LLM (wyrażenia matematyczne, programy). Każda cząstka jest potencjalnym wyjściem. Prędkość to *podpowiedź* opisująca sposób modyfikowania prądu wyjściowego w celu uzyskania najlepszego wyniku osobistego/globalnego. LLM generuje nowe dane wyjściowe z podpowiedzi prędkości. „Bezwładność” prędkości jest podpowiedzią typu „dokonaj małych, stopniowych zmian”.

Działa to dobrze, gdy:
- Dane wyjściowe mają strukturę (można je analizować i oceniać).
- Fitness jest automatyczny (przebiegi testowe, ocena arytmetyczna).
- Populacja jest mała (~10-30 cząstek), więc całkowita liczba połączeń LLM jest łatwa do zarządzania.

Nie sprawdza się to dobrze, gdy sprawność wymaga sprawdzenia przez człowieka – koszt jednej iteracji staje się zaporowy.

### Modelowe roje

arXiv:2410.11163 usuwa PSO z warstwy wyjściowej i przenosi je do warstwy *modelu*. Każda „cząstka” to ekspert LLM (parametry). Rój przesuwa parametry w kierunku najlepszych ze wszystkich poprzez aktualizację bez gradientów. Zgłoszone: średni zysk 13,3% w porównaniu z 12 wartościami bazowymi w 9 zbiorach danych, przy zaledwie 200 wystąpieniach na iterację.

Kluczowym spostrzeżeniem jest to, że modele eksperckie LLM są już obecne w rozmaitości wspólnych parametrów (wagi adapterów, delty LoRA). PSO w tej niskowymiarowej podprzestrzeni jest tanie i skuteczne.

### Odświeżacz ACO (Dorigo 1992)

Optymalizacja kolonii mrówek: mrówki przemierzają wykres; każda ścieżka ma ślad feromonowy. Prawdopodobieństwo ruchu mrówek zależy od siły feromonów. Mrówki, które wykonają zadanie, odkładają feromon proporcjonalnie do jakości roztworu. Feromony z czasem ulegają rozkładowi.

### AMRO-S — ACO do routingu agentów

arXiv:2603.12933 używa funkcji ACO do routingu wieloagentowego. Każdy typ zadania jest „miejscem docelowym”; każdy agent jest możliwą trasą. Feromony wzmacniają szlaki, które dają dobre wyniki. Kluczowy wkład:

- **Zrozumiały dowód przesłania.** Siła feromonów to sygnał czytelny dla człowieka.
- **Asynchroniczna aktualizacja sterowana jakością.** Feromony aktualizują się dopiero po przejściu kontroli jakości, oddzielając wnioskowanie od uczenia się.
- **Przyspieszenie 4,7x** w teście porównawczym routingu wieloagentowego.

Bramka jakości ma znaczenie: bez niej szybcy, ale niewłaściwi agenci gromadzą feromon, a system blokuje się na złych trasach.

### Kiedy używać PSO/ACO w przypadku LLM

**Użyj PSO, gdy:**
- Przestrzeń wyszukiwania jest ciągła lub jest odwzorowywana na parametry ciągłe (osadzanie podpowiedzi, wagi LoRA, parametry generowania liczb).
- Fitness jest tani i automatyczny.
- Populacja może być mała (10-30).

**Użyj ACO, gdy:**
- Wystąpił problem z routingiem lub wyborem ścieżki.
- Decyzje utrwalają się z biegiem czasu (powracają te same typy zadań).
- Aby podjąć decyzję o trasie, potrzebne są możliwe do zinterpretowania dowody.

**Nie stosować, gdy:**
- Sprawność wymaga przeglądu przez człowieka (zbyt kosztowna w przeliczeniu na iterację).
- Przestrzeń poszukiwań jest dyskretna i kombinatoryczna w sposób, którego nie obejmuje PSO (zamiast tego użyj algorytmów genetycznych).
- Decyzje podejmowane w czasie rzeczywistym wymagają ścisłego opóźnienia (PSO/ACO zbliżają się powoli w porównaniu z heurystyką jednoprzebiegową).

### Dlaczego inspiracje biologiczne wciąż wygrywają

Metody oparte na gradiencie wymagają różniczkowalnych sygnałów. Wyniki LLM i decyzje dotyczące routingu nie są w trywialny sposób różnicowalne. Metody pseudogradientowe (routery uczące się przez wzmocnienie, tunery podpowiedzi w stylu DPO) działają, ale wymagają kosztownego szkolenia.

PSO i ACO potrzebują jedynie funkcji *ewaluatora*. Jeśli możesz ocenić potencjalny wynik lub decyzję o skierowaniu, możesz zoptymalizować przestrzeń. To sprawia, że ​​poprzeczka możliwości zastosowania jest znacznie niższa.

### Praktyczne ograniczenia

- **Budżet populacji.** N cząstek × T iteracje × koszt na ewaluację. W przypadku ocen LLM o ~$0.02 / call, a 20-particle PSO running 50 iterations costs ~$20. Zaplanuj odpowiednio.
- **Eksploracja a eksploatacja.** Stopień zaniku feromonów i kompromis w zakresie bezwładności PSO; zbyt szybki zanik → zapomnieć o rozwiązaniach; zbyt wolny → utknął na wczesnych lokalnych optimach.
- **Katastrofalny dryf.** Obydwa algorytmy mogą się zbiegać, a następnie różnić, jeśli zmieni się krajobraz sprawności (nowa dystrybucja danych). Monitoruj stabilność najlepszej kondycji.

## Zbuduj to

`code/main.py` implementuje:

- `LMPSO` — PSO w stosunku do numerycznych parametrów podpowiedzi (temperatura, top_k wag). „Generowanie LLM” każdej cząstki jest symulowane jako skryptowa funkcja przystosowania. Uruchamia algorytm przez 30 iteracji i pokazuje zbieżność g_best.
- `AMRO_S` — routing w stylu ACO. 3 agentów, 4 typy zadań, matryca feromonowa, 100 zadań kierowanych. Drukuje rozkład (typ_zadania → wybory agenta) w czasie, aby pokazać powstawanie szlaku.
- Porównanie: routing losowy i routing ACO w tym samym strumieniu zadań. Mierzy jakość i opóźnienie.

Uruchom:

```
python3 code/main.py
```

Oczekiwany wynik:
- LMPSO: sprawność g_best poprawia się od losowej do niemal optymalnej w ciągu 30 iteracji.
- AMRO-S: tabela feromonów stabilizuje właściwy środek w zależności od rodzaju zadania; Routing ACO przewyższa losowy o ~30-40% pod względem jakości, a także zmniejsza opóźnienia (mniej ponownych prób).

## Użyj tego

`outputs/skill-swarm-optimizer.md` pomaga wybrać pomiędzy PSO, ACO, algorytmami genetycznymi i optymalizatorami opartymi na gradientach w przypadku problemów LLM/optymalizacji agentów.

## Wyślij to

- **Zacznij od małego.** 10–20 cząstek, 20–50 iteracji. Skaluj w górę tylko wtedy, gdy krzywa konwergencji wykazuje wyraźny wzrost.
- ** Rejestruj feromony lub g_best na iterację.** Debugowanie optymalizatorów roju bez śladu jest bolesne.
- **Aktualizacje bramek jakości.** Specjalnie dla routingu ACO: szybcy i niewłaściwi agenci nie mogą gromadzić feromonów.
- **Zresetuj zanik przy zmianie dystrybucji.** Kiedy zmienia się dystrybucja ewaluacyjna, stare feromony stają się nieaktualne; tymczasowo zresetować lub podwoić szybkość zaniku.
- **Ogranicz koszt iteracji.** Emituj metrykę kosztu iteracji. Usługa PSO, która kosztuje 500 USD za iterację i zyskuje 0,5%, nie podlega wysyłce.

## Ćwiczenia

1. Uruchom `code/main.py`. Obserwuj zbieżność LMPSO. Zmieniaj wielkość populacji 5, 10, 20, 50. W jakim rozmiarze następuje nasycenie czasu do konwergencji?
2. Przeprowadź eksperyment z „katastrofalnym dryfem”: po 30. iteracji zmień funkcję przystosowania. Jak szybko dostosowuje się PSO? Czy resetowanie `p_best` pomaga?
3. Dodaj bramkę jakości do AMRO-S: osadzanie się feromonów tylko w seriach z oceną punktową > 0,7. Jak to zmienia zbieżność w porównaniu z wersją niebramkową?
4. Przeczytaj LMPSO (arXiv:2504.09247). Odwzoruj „prędkość papieru jako podpowiedź” z powrotem na prędkość numeryczną. Co zostaje utracone w symulacji, a co zostaje zachowane?
5. Przeczytaj AMRO-S (arXiv:2603.12933). Zaimplementuj oddzieloną „szybką ścieżkę wnioskowania” z asynchroniczną aktualizacją feromonów. Jak zmienia to opóźnienie systemu przy ciągłym obciążeniu?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| PSO | „Optymalizacja roju cząstek” | Kennedy-Eberhart 1995. Optymalizator bezgradientowy oparty na populacji. |
| ACO | „Optymalizacja kolonii mrówek” | Dorigo 1992. Optymalizacja ścieżki/trasy za pomocą śladów feromonowych. |
| LMPSO | „PSO z generacją LLM” | arXiv:2504.09247. Prędkość jest podpowiedzią; LLM produkuje kandydatów. |
| Modelowe roje | „PSO na wagach eksperckich” | arXiv:2410.11163. Bezgradientowa aktualizacja podprzestrzeni parametrów modelu. |
| AMRO-S | „ACO dla routingu agentów” | arXiv:2603.12933. Matryca feromonów względem typu zadania × agenta. |
| p_best / g_best | „Osobisty/najlepszy świat” | Najlepsze dotychczas znalezione rozwiązania dotyczące poszczególnych cząstek i całego roju. |
| Feromon | „Pamięć routingu” | Siła na krawędzi; zanika z czasem; depozyty na jakość. |
| Aktualizacja oparta na jakości | „Ucz się tylko na dobrych biegach” | Depozyt feromonowy uwarunkowany kontrolą jakości. |
| Katastrofalny dryf | „Przesunięcie dystrybucji” | Zmiany w krajobrazie fitness; stare p_best i feromony stają się nieaktualne. |

## Dalsze czytanie

- [Kennedy i Eberhart — Optymalizacja roju cząstek] (https://ieeexplore.ieee.org/document/488968) — artykuł PSO z 1995 r.
- [Dorigo — Optymalizacja kolonii mrówek] (https://www.aco-metaheuristic.org/about.html) — 1992 Założenie ACO
— [LMPSO — Optymalizacja roju cząstek modelu językowego](https://arxiv.org/abs/2504.09247) — PSO dla ustrukturyzowanych wyników LLM
- [Model Swarms — specjalistyczna optymalizacja LLM bez gradientów](https://arxiv.org/abs/2410.11163) — PSO w podprzestrzeni wagi modelu
- [AMRO-S — routing wieloagentowy dla kolonii mrówek](https://arxiv.org/abs/2603.12933) — routing oparty na feromonach z bramką jakości