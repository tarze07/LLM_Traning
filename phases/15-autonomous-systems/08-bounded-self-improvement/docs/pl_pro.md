# Ograniczone projekty samodoskonalenia

> Badania nad bezpieczeństwem skupiły się wokół czterech podstawowych metod ograniczania pętli samodoskonalenia: (1) Niezmienniki formalne, które muszą obowiązywać w trakcie i po każdej edycji kodu. (2) Kotwice dopasowania, których celów pętla nie może w żaden sposób zmodyfikować. (3) Ograniczenia wielokryteriowe, gdzie każdy wymiar bezpieczeństwa (ochrona danych, solidność, zgodność z zasadami) musi zostać zachowany, a nie tylko sama wydajność. (4) Wykrywanie regresji, które automatycznie zatrzymuje pętlę, gdy dane historyczne wskazują na utratę dotychczasowych zdolności. Żadne z tych rozwiązań nie daje 100% gwarancji – prawa teorii informacji (złożoność Kołmogorowa, twierdzenie Löba) nakładają sztywne limity na to, co dany system może udowodnić na temat swoich następców. Te metody stanowią jednak środki zaradcze, które drastycznie podnoszą koszt i wykrywalność cichych awarii.

**Typ:** Ucz się
**Języki:** Python (biblioteka standardowa, pętla ograniczona z kontrolą niezmienników)
**Wymagania wstępne:** Faza 15 · 07 (RSI), Faza 15 · 04 (DGM)
**Czas:** ~60 minut

## Problem

Symulator wyścigu przedstawiony w Lekcji 7 wykazał, że niewielkie różnice w tempie przyrostu możliwości i dopasowania kumulują się z czasem, tworząc ogromne luki bezpieczeństwa. Z kolei studium przypadku DGM z Lekcji 4 pokazało, że autonomiczne pętle potrafią aktywnie oszukiwać własne ewaluatory. Oba te wnioski prowadzą do identycznego pytania inżynieryjnego: jakie ograniczenia można nałożyć na pętlę samodoskonalenia, aby te zabezpieczenia nie zostały po cichu wyeliminowane przez sam system w procesie samoedycji?

Podsumowanie warsztatów RSI ICLR 2026 (openreview.net/pdf?id=OsPQ6zTQXV) definiuje cztery takie elementy podstawowe (primitives). Zarówno polityka RSP v3.0 firmy Anthropic (Lekcja 19), jak i ramy FSF v3 od DeepMind (Lekcja 20) odwołują się do nich przy określaniu progów krytycznych możliwości. Projekty takie jak Meta HyperAgents oraz otwarte platformy społecznościowe wdrażają obecnie wybrane podzbiory tych rozwiązań w środowiskach testowych.

Powiedzmy sobie jasno: są to jedynie środki zaradcze (mitigations). Prawa teorii informacji ograniczają to, co dany system jest w stanie udowodnić na temat swojego następcy. Dobrze ograniczona pętla jest nieporównywalnie bezpieczniejsza od pętli całkowicie swobodnej, ale nie gwarantuje bezpieczeństwa absolutnego.

## Koncepcja

### Element podstawowy 1: niezmienniki formalne

Niezmiennik to właściwość systemowa, która musi być bezwzględnie prawdziwa przed i po każdej samomodyfikacji kodu. Przykłady:

- Dystrybucja wyników (promptów) jest zawsze uwarunkowana stałym nagłówkiem konstytucyjnym (Lekcja 17).
- Żadne wywołanie narzędzia nie może być kierowane do adresów spoza białej listy.
- Operacje zapisu do pamięci trwałej przechodzą wyłącznie przez zatwierdzony, cyfrowo podpisany moduł.
- Suma kontrolna (hash) ewaluatora zgadza się z zatwierdzoną wersją referencyjną.

Niezmienniki są weryfikowane przez kod zewnętrzny, którego pętla agenta nie może edytować. Jeśli proponowana modyfikacja narusza choćby jeden niezmiennik, zostaje natychmiast odrzucona. Wychwytuje to próby manipulowania ewaluatorem w stylu DGM (Lekcja 4).

Największym wyzwaniem inżynieryjnym jest dobór takich niezmienników, które chronią bezpieczeństwo, a jednocześnie dają się wydajnie obliczyć. Zbyt restrykcyjne reguły paraliżują postęp (stalls progress), podczas gdy zbyt luźne pozwalają pętli na obchodzenie kluczowych zabezpieczeń.

### Element podstawowy 2: kotwice dopasowania (alignment anchors)

Kotwica dopasowania to niezmienna reprezentacja głównego celu i zasad pętli, umieszczona całkowicie poza obszarem, do którego agent ma uprawnienia zapisu. Przykłady:

- Tekst konstytucyjny (Lekcja 17) ładowany z lokalizacji tylko do odczytu przy każdym uruchomieniu agenta.
- Ewaluator umieszczony w odrębnym repozytorium z niezależną i rygorystyczną kontrolą dostępu.
- Manifest uprawnień do korzystania z narzędzi podpisany cyfrowo przez człowieka i weryfikowany w każdym cyklu.

Rolą kotwicy jest zapobieganie dryfowi celu (objective drift). Pętla może optymalizować sposoby realizacji zadań, ale nie ma prawa modyfikować samego celu.

Subtelny tryb awarii: pętla, która nie może edytować samej kotwicy, może podjąć próbę reinterpretacji jej zapisów. Konstytucyjna sztuczna inteligencja (Lekcja 17) opiera się na procesach rozumowania, aby radzić sobie w nowych sytuacjach – i to właśnie w tej warstwie interpretacji może pojawić się dryf. Kotwice są więc konieczne, ale niewystarczające.

### Element podstawowy 3: ograniczenia wielokryteriowe (multi-objective constraints)

Pętla optymalizująca system pod kątem pojedynczej wartości skalarnej (np. wydajności kodu) niemal zawsze znajdzie niebezpieczne skróty. Jeśli jednak system musi jednocześnie spełniać szereg twardych ograniczeń na różnych osiach, przestrzeń potencjalnych oszustw drastycznie maleje. Typowe osie kontrolne:

- Skuteczność (wyniki zadań na benchmarku).
- Bezpieczeństwo (odsetek odmów przy próbach generowania niebezpiecznych treści, oceny red-teamingowe).
- Sprawiedliwość (limity wpływu na grupy wrażliwe).
- Solidność (testy na zestawach OOD, odporność na ataki typu adversarial).

Modyfikacja kodu zostaje zaakceptowana tylko wtedy, gdy system zaliczy testy na wszystkich zdefiniowanych osiach.

### Element podstawowy 4: wykrywanie regresji

Wyniki każdego cyklu są automatycznie porównywane z rozkładem historycznym. Spadek skuteczności na dowolnej z osi poza zdefiniowaną tolerancję natychmiast zatrzymuje pętlę. Pozwala to na wykrycie sytuacji, w których optymalizacja pod kątem nowej funkcji po cichu psuje inne, dotychczas stabilne mechanizmy.

Praktyczna implementacja: zapisuj wyniki poszczególnych zadań z ostatnich N iteracji. W nowym cyklu oblicz przyrost (deltę) dla każdego zadania. Jeśli któraś delta wykaże spadek poniżej dopuszczalnego progu, modyfikacja jest odrzucana, a system wstrzymuje pracę i oczekuje na weryfikację przez człowieka.

### Ograniczenia wynikające z teorii informacji

Złożoność Kołmogorowa oraz twierdzenie Löba wyznaczają matematyczne granice tego, co dany system jest w stanie udowodnić na swój własny temat. Formalna Maszyna Gödla Schmidhubera (Lekcja 4) miała na celu osiągnięcie tej teoretycznej granicy, jednak nikomu nie udało się przeprowadzić dla niej pełnego, nietrywialnego dowodu. Twierdzenie Löba mówi w skrócie: jeśli system opiera się na założeniu „zrobię X pod warunkiem, że udowodnię, iż powinienem zrobić X”, to wykona on czynność X bez rzeczywistego udowodnienia jej poprawności (jest to klasyczny błąd autoreferencji).

Konsekwencja: opisane elementy podstawowe nie rozwiążą problemu bezpieczeństwa w sposób absolutny. Ich celem jest podniesienie kosztu ewentualnego nadużycia. Złośliwy lub zdryfowany agent, który w prostym systemie po cichu ominąłby brakujące zabezpieczenie, w systemie ograniczonym musi podjąć jawną próbę sabotowania struktur ewaluacji – co generuje wyraźną i łatwą do wykrycia sygnaturę anomalii.

### Przykład ograniczonego potoku

Załóżmy, że agent proponuje modyfikację kodu. Proces weryfikacji wygląda następująco:

1. **Test niezmienników:** weryfikacja sum kontrolnych modułów, manifestu uprawnień narzędzi i nagłówka konstytucyjnego.
2. **Test zakotwiczenia:** potwierdzenie, że cel wpisany w kodzie zgadza się bit po bicie z wersją referencyjną.
3. **Ocena wielokryteriowa:** pomiar sprawności na osiach: skuteczność, bezpieczeństwo, sprawiedliwość, solidność.
4. **Wykrywanie regresji:** sprawdzenie, czy sprawność na żadnej z osi nie spadła poniżej tolerancji.

Aby edycja została wdrożona, system musi pomyślnie przejść wszystkie cztery etapy. Pojedynczy błąd na dowolnym kroku wstrzymuje cały proces.

## Użyj tego

Skrypt `code/main.py` uruchamia ograniczoną pętlę samodoskonalenia na bazie symulatora agenta (w stylu DGM z Lekcji 4), ale z nałożonymi czterema elementami podstawowymi. Każde z tych zabezpieczeń można włączać i wyłączać niezależnie. Symulacja pokazuje, jak poszczególne elementy wykrywają konkretne klasy awarii i w jaki sposób wyłączenie któregoś z nich otwiera drogę do nadużyć.

## Wdrożenie

Szablon `outputs/skill-bounded-loop-review.md` ułatwia audytowanie proponowanej pętle pod kątem tego, które z czterech zabezpieczeń zostały w niej rzeczywiście zaimplementowane.

## Ćwiczenia

1. Uruchom `code/main.py` ze wszystkimi włączonymi zabezpieczeniami. Potwierdź, że pętla poprawia główną metrykę wydajności, nie pozwalając agentowi na hakowanie nagród.

2. Wyłącz moduł wykrywania regresji. Skonstruuj takie dane wejściowe, które doprowadzą do zaakceptowania modyfikacji powodującej ukryty spadek zdolności systemu.

3. Wyłącz ograniczenia wielokryteriowe. Wykaż, że pętla szybko optymalizuje system na osi skuteczności kosztem drastycznego spadku wskaźników bezpieczeństwa.

4. Zaprojektuj kotwicę dopasowania dla agenta generującego kod. Określ: jaki tekst konstytucyjny zastosujesz, gdzie będzie przechowywany i w jaki sposób weryfikowany.

5. Przeczytaj podsumowanie warsztatów RSI ICLR 2026. Wybierz jedno z czterech zabezpieczeń i zaproponuj konkretną metodę jego technicznego usprawnienia.

## Kluczowe terminy

| Termin | Co mówią ludzie | Co to naprawdę oznacza |
|---|---|---|
| Niezmiennik | „Zasada zawsze prawdziwa” | Właściwość systemowa weryfikowana przez kod zewnętrzny przed i po każdej modyfikacji |
| Kotwica dopasowania | „Zablokowany cel nadrzędny” | Niezmienna reprezentacja celu systemu umieszczona poza obszarem zapisu pętli |
| Ograniczenie wielokryteriowe | „Testy na wielu osiach” | Wymóg jednoczesnego zaliczenia testów skuteczności, bezpieczeństwa, sprawiedliwości i solidności |
| Wykrywanie regresji | „Blokada po spadku formy” | Automatyczne zatrzymanie pętli, gdy delty historyczne wskazują na pogorszenie działania systemu |
| Granica Kołmogorowa | „Limit teorii informacji” | Teoretyczna granica określająca, ile informacji system może posiąść i udowodnić na temat swojego następcy |
| Twierdzenie Löba | „Pułapka samoodniesienia” | Dowód matematyczny na to, że system może podjąć działanie bez rzeczywistego udowodnienia jego poprawności |
| Stos weryfikacyjny | „Weryfikacja warstwowa” | Sekwencyjne uruchamianie wielu różnych mechanizmów kontrolnych; błąd na dowolnym etapie odrzuca zmianę |
| Ograniczone samodoskonalenie | „Środki zaradcze, nie dowód absolutny” | Metody podnoszące koszt i wykrywalność błędów; nie rozwiązują problemu bezpieczeństwa w 100% |

## Dalsze czytanie

- [Podsumowanie warsztatów RSI ICLR 2026 (OpenReview)](https://openreview.net/pdf?id=OsPQ6zTQXV) – omówienie czterech filarów zabezpieczeń.
- [Responsible Scaling Policy v3.0 od Anthropic](https://anthropic.com/responsible-scaling-policy/rsp-v3-0) – specyfikacja wielokryteriowych progów bezpieczeństwa.
- [DeepMind — Frontier Safety Framework v3](https://deepmind.google/blog/strengthening-our-frontier-safety-framework/) – wykorzystanie monitorowania zachowań jako niezmiennika systemowego.
- [Schmidhuber (2003). Gödla Machines](https://people.idsia.ch/~juergen/goedelmachine.html) – formalna, matematyczna próba wdrożenia tych założeń.
- [Claude's Constitution (Anthropic, styczeń 2026)](https://www.anthropic.com/news/claudes-constitution) – praktyczny przykład kotwicy dopasowania.
