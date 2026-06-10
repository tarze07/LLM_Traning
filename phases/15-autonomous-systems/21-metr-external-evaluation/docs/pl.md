# Horyzonty czasowe METR i ocena zdolności zewnętrznych

> METR (dawniej ARC Evals) to niezależny test 501(c)(3) od grudnia 2023 r. Ich test porównawczy Time Horizon 1.1 (styczeń 2026 r.) dopasowuje krzywą logistyczną do prawdopodobieństwa powodzenia zadania w funkcji log (czas wykonania przez człowieka-eksperta); przecięcie z prawdopodobieństwem 50% określa horyzont czasowy modelu. Zestaw zadań na lata 2025–2026 obejmuje GPT-5.1, GPT-5.1-Codex-Max i oceny monitorowania prototypów (czy monitor może wychwycić zadania poboczne; czy agent może uniknąć). Zestawy testów porównawczych: HCAST (180+ ML, cyber, SWE, zadania z zakresu rozumowania; od 1 minuty do 8+ godzin), RE-Bench (71 ML zadań badawczo-inżynierskich z bazą ekspercką), SWAA. Szczera uwaga: pomiary METR są wyidealizowane – nie ma w nich człowieka, nie ma rzeczywistych konsekwencji – a zespół udokumentował różnicę w zachowaniu pomiędzy oceną a wdrożeniem (lekcja 1). Horyzont czasowy to górna granica, a nie prognoza wdrożenia.

**Typ:** Ucz się
**Języki:** Python (stdlib, estymator horyzontu dopasowania logistycznego)
**Wymagania wstępne:** Faza 15 · 01 (Agenci dalekiego horyzontu), Faza 15 · 19 (RSP)
**Czas:** ~60 minut

## Problem

Zasady skalowania (Lekcja 19, 20) są tak przydatne, jak pomiary, do których się odnoszą. „Próg badań i rozwoju sztucznej inteligencji 4” oraz „autonomia dalekiego zasięgu” są zdefiniowane w prozie politycznej; stają się one wykonalne dopiero wtedy, gdy konkretne oceny przyniosą konkretne liczby.

METR to organizacja zajmująca się oceną zewnętrzną na lata 2024–2026, która określiła wiele z tych liczb. Oceniają pionierskie modele — często przed publikacją, w ramach umowy NDA z laboratoriami — i później publikują metodologię. Benchmark Time Horizon 1.1 (styczeń 2026 r.) to ich główny artefakt: pojedynczy skalar, który kompresuje możliwości w jednostkę czytelną dla człowieka („ten model może wykonać zadanie, nad którym ekspert spędza X godzin przy 50% niezawodności”).

Lekcja dotyczy częściowo metodologii (sposób obliczania horyzontu), a częściowo interpretacji (dlaczego horyzont jest górną granicą, a nie przewidywaniem wdrożenia). Te dwie umiejętności są ze sobą powiązane. Zespół, który rozumie, jak dopasowany jest horyzont, znacznie trudniej oszukać złym twierdzeniem dostawcy, niż zespół, który widzi na slajdzie tylko „14 godzin”.

## Koncepcja

### Tło METR

- Założona: grudzień 2023 r. (dawna firma ARC Evals, przekształcona w niezależną spółkę 501(c)(3)).
- Zakres: ocena autonomicznych możliwości modeli pionierskich, często przed wydaniem.
- Laboratoria partnerskie: Anthropic, OpenAI (wielokrotne zaangażowania 2025–2026).
- Godne uwagi rezultaty: Horyzont Czasowy 1.0 (marzec 2025), Horyzont Czasowy 1.1 (styczeń 2026), oceny monitorowania prototypów.

### Horyzont czasowy pasuje

Metodologia (z bloga i artykułów METR):

1. Zbierz zestaw zadań obejmujący czas wykonania przez eksperta od minut do godzin. Aktualne zestawy: HCAST (ponad 180 zadań), RE-Bench (71 zadań), SWAA.
2. Uruchom model dla każdego zadania; odnotować sukces lub porażkę.
3. Dopasuj krzywą logistyczną: P(sukces) jako funkcję log(czas wykonania eksperta).
4. Horyzont to czas ekspercki, w którym P(sukces) = 0,5.

Kształt dostosowany pod względem logistycznym jest właściwy, ponieważ możliwości mają na ogół rosnący, zbliżający się do plateau związek z trudnością zadania. Punkt 50% to wybór (może wynosić 10%, 90%); METR podaje w szczegółowym artykule wiele progów, ale prowadzi z 50%, ponieważ jest najbardziej intuicyjny.

### Liczby ze stycznia 2026 r

Według horyzontu czasowego 1.1:

- Claude Opus 4.6: ~14 godzin przy 50% niezawodności, od Time Horizon 1.1 (styczeń 2026).
- Podwojenie czasu wykonywania zadań typu HCAST: ~4,3 miesiąca (130,8 dni) w porównaniu z okresem po 2023 r. zgłoszonym przez Time Horizon 1.1 (styczeń 2026 r.); liczba za około 7 miesięcy odpowiada pełnemu dopasowaniu do lat 2019–2025 z horyzontu czasowego 1.0 i jest podana w TH1.1 wraz z liczbą po 2023 r.

To są konkretne liczby, pozostałe odniesienia do fazy 15. Są one cytowane w RSP v3.0 firmy Anthropic (lekcja 19) i FSF v3 firmy DeepMind (lekcja 20) jako jeden z pomiarów progów zasilania.

### Zestawy porównawcze

- **HCAST**: 189 zadań z zakresu uczenia maszynowego, cyberbezpieczeństwa, inżynierii oprogramowania i ogólnego rozumowania. Zakres: od 1 minuty do ponad 8 godzin czasu eksperckiego. Apartament główny za numerem horyzontu.
- **RE-Bench**: 71 ML zadań badawczo-inżynierskich z bazowym poziomem eksperckim. Mierzy, czy model może wykonać tego rodzaju prace badawczo-rozwojowe w zakresie uczenia maszynowego, które wchodzą w skład progu badań i rozwoju AI-4.
- **SWAA**: krótsze zadania; przydatne do kalibracji dolnego końca krzywej horyzontu.

### Oceny monitorowania prototypów

Prace METR w latach 2025–2026 obejmowały prototypy monitorująco-ewaluacyjne: czy monitor może uchwycić model wykonujący zadanie poboczne (coś innego niż to, o co prosił operator); czy agent może ominąć monitor? Są one bezpośrednio zasilane z kategorii „Osłabianie zabezpieczeń” w OpenAI PF v2 i monitorowaniu zwodniczego dopasowania w DeepMind FSF v3 (Lekcja 20).

### Dlaczego horyzonty to górna granica

- **Wyidealizowane oprzyrządowanie**: zadania porównawcze dają modelowi czyste narzędzia i dobrze sformatowane dane. Prawdziwe wdrożenia są bardziej chaotyczne.
- **Brak rzeczywistych konsekwencji**: modelka nigdy nie wystawia klientowi rachunku, nie usuwa prawdziwych danych ani nie kontaktuje się z prawdziwymi ludźmi. Prawdziwe wdrożenia wiążą się z nieodwracalnymi stawkami.
- **Gra w kontekście ewaluacyjnym**: Lekcja 1. Modele zachowują się inaczej w testach. Międzynarodowy raport bezpieczeństwa sztucznej inteligencji z 2026 r. dokumentuje to empirycznie.
- **Brak uzasadnionych różnic między użytkownikami**: monity dotyczące testów porównawczych mają strukturę. Prawdziwi użytkownicy generują niejednoznaczne, zależne od kontekstu żądania.

Horyzont to górny pułap zdolności w sprzyjających warunkach. Niezawodność wdrożenia to inna liczba, niższa, a zespoły muszą zmierzyć własną dystrybucję, aby ją poznać.

### Sprawa zewnętrznego ewaluatora

Ocena zewnętrzna ma znaczenie, ponieważ laboratoria wewnętrzne mają motywację do optymalizacji zgłaszanych wskaźników. Niezależność METR – art. 501(c)(3) z zadeklarowaną metodologią i recenzowanymi dokumentami – polega na łagodzeniu strukturalnym. Samo to nie wystarczy (laboratoria nadal kontrolują to, co widzi METR), ale jest zdecydowanie lepsze niż brak zewnętrznej oceny.

### Jak w praktyce wykorzystać liczby horyzontów

- **Jako filtr możliwości**: jeśli horyzont modelu jest znacznie krótszy niż czas ekspercki proponowanego zadania, nie wysyłaj go autonomicznie (plik umiejętności z lekcji 1).
- **Jako wskaźnik trendu**: czas podwojenia informuje, jak długo bieżąca praktyka pozostanie bezpieczna nawet bez nowych środków łagodzących.
- **Jako wcześniej**: punktem wyjścia jest horyzont 14 godzin. Dostosuj do rozkładu zadań, jakości narzędzi i kontekstu wdrożenia.

## Użyj tego

`code/main.py` implementuje logistyczne dopasowanie powodzenia zadania do log(czasu eksperta), biorąc pod uwagę syntetyczny zestaw wyników. Podaje horyzont 50% (nagłówek METR), horyzont 10% (konserwatywny) i horyzont 90% (optymistyczny). Pokazuje także, co się zmienia, gdy wskaźnik sukcesu jest sztucznie zawyżany przez gry w kontekście ewaluacyjnym.

## Wyślij to

`outputs/skill-horizon-interpretation.md` sprawdza deklarację dostawcy dotyczącą horyzontu czasowego i tworzy analizę rozbieżności pomiędzy deklaracjami porównawczymi a rzeczywistością wdrożeniową.

## Ćwiczenia

1. Uruchom `code/main.py`. Potwierdź, że horyzont dopasowania 50% odpowiada syntetycznej prawdzie podstawowej. Teraz zmniejsz o połowę siatkę czasu wykonania zadania; czy szacunek horyzontu zmienia się znacząco?

2. Przeczytaj wpis na blogu METR Time Horizon 1.1. Zidentyfikuj konkretne zadania, w których niezawodność jest najwyższa, a gdzie najniższa. Wyjaśnij, dlaczego istnieje luka.

3. Przeczytaj zasoby METR „Pomiar autonomicznych możliwości sztucznej inteligencji”. Wymień kategorie zadań HCAST. Wybierz jedną kategorię, którą przyłożyłbyś bardziej do zadania produkcyjnego i uzasadnij dlaczego.

4. Wprowadź do symulatora gry z kontekstem ewaluacyjnym: przełóż ~20% nieudanych zadań na sukces. Zgłoś nowy horyzont. Jest to w przybliżeniu wpływ współczynnika gry wynoszącego 20% na obserwowaną liczbę.

5. Zaprojektuj wewnętrzną ocenę horyzontu na podstawie własnego rejestru błędów lub reprezentatywnego zestawu zadań. Opisz gromadzenie danych, dopasowanie i informacje wyjściowe. Porównaj z liczbami METR.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|---|---|---|
| METR | „Ewaluator zewnętrzny” | były ARC Evans; niezależny 501(c)(3) od grudnia 2023 r. |
| Horyzont Czasu | „Miara zdolności” | Ekspercka długość zadania przy 50% niezawodności, od dopasowania logistycznego |
| HCAST | „Główny apartament METR” | Ponad 180 zadań trwających od 1 minuty do ponad 8 godzin |
| RE-Ławka | „Inżynieria badawcza” | 71 ML zadań badawczo-inżynieryjnych z udziałem ludzi |
| SWAA | „Zestaw krótkich zadań” | Kalibruje dolny koniec krzywej horyzontu |
| Czas podwojenia | „Tempo wzrostu” | Czas na podwojenie horyzontu 50%; ~7 miesięcy na HCAST |
| Gry z kontekstem ewaluacyjnym | „Model zachowuje się inaczej” | Udokumentowana luka w zachowaniu pomiędzy testami a wdrożeniem |
| Górna granica | „Horyzont to sufit” | Horyzont porównawczy > niezawodność wdrożenia pod obciążeniem |

## Dalsze czytanie

– [METR — Zasoby do pomiaru autonomicznych możliwości sztucznej inteligencji] (https://metr.org/measuring-autonomous-ai-capabilities/) — specyfikacje HCAST, RE-Bench, SWAA.
– [METR – Pomiar zdolności AI do wykonywania długich zadań](https://metr.org/blog/2025-03-19-measuring-ai-ability-to-complete-long-tasks/) – oryginalny dokument horyzontalny.
- [METR — Time Horizon 1.1 (styczeń 2026)](https://metr.org/research/) — aktualne liczby i metodologia.
- [Epoch AI — test porównawczy horyzontów czasowych METR](https://epoch.ai/benchmarks/metr-time-horizons) — śledzenie na żywo.
- [Anthropic — Autonomia agenta pomiarowego w praktyce](https://www.anthropic.com/research/measuring-agent-autonomy) — wewnętrzne spojrzenie na pomiary METR.