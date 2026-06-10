# Postępowanie zgodnie z instrukcją jako sygnał wyrównania

> Każda późniejsza krytyka RLHF przemawia przeciwko temu rurociągowi. Zanim przeanalizujesz, jak presja optymalizacyjna zniekształca serwer proxy, musisz go zobaczyć. InstructGPT (Ouyang i in., 2022) zdefiniował architekturę referencyjną: nadzorowane dostrajanie par instrukcja-odpowiedź, model nagrody trenowany na podstawie rankingów preferencji par oraz PPO w porównaniu z modelem nagrody z karą KL w stosunku do polityki SFT. Preferowano wersję 1.3B InstructGPT zamiast 175B GPT-3. Ten pojedynczy wynik jest powodem, dla którego w 2026 r. każde laboratorium graniczne będzie nadal dostarczać rurociąg poszkoleniowy w kształcie RLHF.

**Typ:** Ucz się
**Języki:** Python (stdlib, trzystopniowy potok zabawek)
**Wymagania wstępne:** Faza 10 · 06 (SFT), Faza 10 · 07 (RLHF), Faza 10 · 08 (DPO)
**Czas:** ~45 minut

## Cele nauczania

- Wymień trzy etapy potoku InstructGPT i straty występujące w każdym z nich.
- Wyjaśnij, dlaczego model 1.3B dostrojony zgodnie z instrukcjami jest lepszy od surowego modelu 175B GPT-3 w ocenie preferencji człowieka.
- Określ, przed czym chroni kara KL na etapie 3 i dlaczego jej usunięcie sprowadza się do zachowania polegającego na poszukiwaniu modu.
- Opisać podatek wyrównawczy i łagodzenie PPO-ptx. Ouyang i in. użyte przeciwko niemu.

## Problem

Wstępnie przeszkolone modele językowe uzupełniają tekst. Nie odpowiadają na pytania. Zapytaj GPT-3 „napisz funkcję Pythona, która odwraca listę”, a często otrzymasz kolejny monit, ponieważ większość dystrybucji szkoleniowej to tekst internetowy, który zawiera więcej tekstu internetowego. Modelka wykonuje swoją pracę – zadanie jest złe.

Serwerem proxy, którego używa każde poważne laboratorium do naprawienia tego problemu, są ludzkie preferencje. Dwa uzupełnienia trafiają do osoby oceniającej; oceniający wybiera lepszy; model nagrody uczy się oceniającego. Następnie pętla RL przesuwa politykę w stronę wyników, w których model nagrody osiąga wysokie wyniki. Oto pełna teza InstructGPT w trzech zdaniach. Pozostała część artykułu to inżynieria.

## Koncepcja

### Etap 1: nadzorowane dostrajanie (SFT)

Zbierz pary szybkich odpowiedzi, w których odpowiedzią jest to, co napisałby człowiek mający dobre intencje. Ouyang i in. wykorzystano 13 tys. podpowiedzi od osób zajmujących się etykietowaniem i interfejsu API OpenAI. Dostosuj model podstawowy na podstawie tych danych przy standardowej stracie entropii krzyżowej.

Co daje Ci SFT: model odpowiada teraz na pytania, zamiast je kontynuować. Czego ci to nie daje: żadnego sygnału wskazującego, którą odpowiedź preferuje oceniający, jeśli wiele z nich jest wiarygodnych.

### Etap 2: model nagrody (RM)

Dla każdego podpowiedzi podaj przykładowe K uzupełnień z modelu SFT. Osoba zajmująca się etykietowaniem ocenia je. Wytrenuj model nagrody, który ocenia dowolną parę szybkiej odpowiedzi, tak aby w przypadku par, w których preferowano `y_w` zamiast `y_l`:

```
L_RM = -log sigmoid(r(x, y_w) - r(x, y_l))
```

Jest to utrata preferencji par Bradley-Terry. RM jest zwykle inicjowany z modelu SFT z głowicą LM zastąpioną głowicą skalarną.

Modele nagród są małe: 6B wystarczyło dla 175B InstructGPT. Są również delikatne — sekcja 5 artykułu dotyczy głównie zachowań związanych z hakowaniem nagród, które pojawiły się na małą skalę.

### Etap 3: PPO z karą KL

Zdefiniuj cel:

```
J(pi) = E_{x~D, y~pi(.|x)} [ r(x, y) ] - beta * KL(pi(.|x) || pi_SFT(.|x))
```

Maksymalizuj dzięki PPO. Termin KL zapobiega oddalaniu się `pi` od polityki dotyczącej transakcji finansowanych z użyciem papierów wartościowych. Bez tego optymalizator znajduje kontradyktoryjne przykłady — ciągi znaków, które uzyskują wysokie wyniki poniżej RM, ponieważ RM ich nigdy nie widział, a nie dlatego, że ludzie tak naprawdę je preferują.

Współczynnik KL `beta` jest najważniejszym hiperparametrem RLHF. Za niski: hakowanie z nagrodami. Zbyt wysoka: brak poprawy w stosunku do SFT.

### Podatek wyrównawczy

Po RLHF model jest preferowany przez ludzi, ale wykazuje regres w standardowych testach porównawczych (SQuAD, HellaSwag, DROP). Ouyang i in. nazwij to podatkiem od wyrównania i napraw to za pomocą PPO-ptx: zmieszaj gradienty przedtreningowe z celem RL, aby model nie zapomniał, jak wykonywać dalsze zadania, za które nigdy nie był nagradzany.

```
J_ptx(pi) = J(pi) + gamma * E_{x~D_pretrain} [ log pi(x) ]
```

PPO-ptx stał się standardem. Anthropic, DeepMind i Meta używają jakiegoś wariantu.

### Wynik

W około 70% przypadków osoby zajmujące się etykietowaniem preferują wersję 1.3B InstructGPT (SFT + RM + PPO-ptx) zamiast bazowego GPT-3 175B. Luka zwiększa się w przypadku ukrytych monitów testowych z ruchu produkcyjnego. Dwie rzeczy do odczytania z tej liczby:

1. Dopasowanie to inna oś niż możliwości. Model 175B miał większe możliwości; model 1.3B miał większe wyrównanie; wytwórcy etykiet woleli wyrównany.
2. Minimalny poziom możliwości jest ustalany przez model podstawowy. Nie można RLHF modelu podstawowego poznać fakty, których nigdy nie widział.

### Dlaczego jest to punkt odniesienia dla fazy 18

Każda krytyka przedstawiona w późniejszych lekcjach — hakowanie z nagrodami (lekcja 2), DPO (lekcja 3), pochlebstwo (lekcja 4), CAI (lekcja 5), uśpieni agenci (lekcja 7), fałszowanie ustawień (lekcja 9) — przemawia przeciwko jakiejś części tego rurociągu. Ataki hakerskie z nagrodami etap 2. DPO załamuje etapy 2 i 3. CAI zastępuje ludzkiego etykietującego. Pochlebstwo pokazuje, że osoba etykietująca jest stronniczym sygnałem. Fałszowanie dostosowania pokazuje, że polityka może całkowicie ominąć etap 3. Nie możesz śledzić żadnej z tych krytyk bez uprzedniego potoku w głowie.

## Użyj tego

`code/main.py` symuluje trzy etapy na podstawie danych o preferencjach zabawek. Podstawowa „polityka” to stronnicza moneta w stosunku do działań {A, B, C}. Etap 1 SFT naśladuje działania osoby etykietującej na 200 monitach. Etap 2 pasuje do modelu nagrody Bradleya-Terry'ego z 500 rankingów parami. Etap 3 przeprowadza uproszczoną aktualizację PPO z karą KL do polityki SFT. Możesz obserwować wzrost nagrody, wzrost rozbieżności KL i zmianę polityki – możesz też wyłączyć termin KL, aby zobaczyć, jak hakowanie nagród pojawi się w ciągu 50 kroków aktualizacji.

Na co zwrócić uwagę:

- Trajektoria nagrody z `beta = 0.1` vs `beta = 0.0`.
- KL(pi || pi_SFT) na etapach szkoleniowych.
- Ostateczny rozkład działań w porównaniu z preferencjami osoby etykietującej.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-instructgpt-explainer.md`. Biorąc pod uwagę opis rurociągu RLHF lub streszczenie artykułu, identyfikuje, który z trzech etapów jest modyfikowany, jakie straty są stosowane na każdym etapie i czy występuje kara KL lub równoważny regulator.

## Ćwiczenia

1. Uruchom `code/main.py`. Ustaw `beta = 0.0` i zgłoś rozkład akcji po 200 krokach PPO. Wyjaśnij zachowanie polegające na poszukiwaniu trybu w jednym akapicie.

2. Zmodyfikuj model nagrody tak, aby miał odchylenie +0,5 dla działania B (błąd symulowanej nagrody). Uruchom PPO za pomocą `beta = 0.1`. Czy kara KL zapobiega wykorzystywaniu stronniczości przez politykę? Kiedy `beta` widać wykorzystanie?

3. Przeczytaj Ouyang i in. (arXiv:2203.02155) Rysunek 1. Odtwórz krzywą preferencji osoby etykietującej, uruchamiając PPO dla 1, 5, 20, 100 kroków i mierząc preferencje w stosunku do modelu SFT.

4. W części 4.3 artykułu podano, że InstructGPT 1.3B pokonuje 175B GPT-3 w około 70% przypadków. Dlaczego współczynnik miałby być wyższy w przypadku ukrytych podpowiedzi produkcyjnych niż w przypadku podpowiedzi wytwórcy etykiet?

5. Zamień utratę PPO na DPO (faza 10 · 08) na tych samych danych preferencji. Porównaj ostateczną zmianę polityki (KL do SFT) i ostateczną nagrodę. Która metoda jest bardziej skuteczna przy dopasowanej nagrodzie?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|--------------------------------------|
| SFT | „strojenie instrukcji” | Etap 1: dostrojenie między entropią w parach szybkiego reagowania |
| Model nagrody | "RM" | Regresor skalarny ponad (podpowiedź, odpowiedź) przeszkolony z Bradleyem-Terrym na etykietach parami |
| Bradley-Terry | „utrata preferencji par” | -log sigmoid(r_w - r_l); redukuje ranking parami do klasyfikacji binarnej |
| Kara KL | „regulator” | `beta * KL(pi \|\| pi_SFT)` — utrzymuje politykę RL w pobliżu kotwicy SFT |
| PPO-ptx | „PPO z mieszanką przedtreningową” | Dodaje ułamek logarytmicznego prawdopodobieństwa przed treningiem do celu PPO, aby zrównoważyć podatek wyrównawczy |
| Podatek wyrównawczy | „regresja RLHF” | Spadek standardowych wskaźników referencyjnych po RLHF, które nie były celem RLHF |
| Preferencje osoby zajmującej się etykietowaniem | „podstawowa prawda” | Próbka rankingów ludzkich; RM jest statystycznym wskaźnikiem zastępczym tego, a nie „wartości ludzkich” |

## Dalsze czytanie

- [Ouyang i in. — Szkolenie modeli językowych w zakresie wykonywania instrukcji na podstawie informacji zwrotnych od ludzi (arXiv:2203.02155)](https://arxiv.org/abs/2203.02155) — artykuł InstructGPT, będący podstawą każdego kolejnego rurociągu RLHF
- [Stiennon i in. — Nauka podsumowywania na podstawie informacji zwrotnych od ludzi (arXiv:2009.01325)](https://arxiv.org/abs/2009.01325) — poprzednik RLHF-for-summarization
- [Christiano i in. — Uczenie się przez głębokie wzmacnianie na podstawie ludzkich preferencji (arXiv:1706.03741)](https://arxiv.org/abs/1706.03741) — oryginalne sformułowanie RL oparte na preferencjach
- [Bai i in. — Szkolenie pomocnego i nieszkodliwego asystenta za pomocą RLHF (arXiv:2204.05862)](https://arxiv.org/abs/2204.05862) — Rozszerzenie HH rurociągu InstructGPT firmy Anthropic