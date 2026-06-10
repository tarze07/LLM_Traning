# Postępowanie zgodnie z instrukcją jako sygnał wyrównania

> Każda późniejsza krytyka RLHF odnosi się do opisanego tu potoku. Zanim jednak przeanalizujesz, jak presja optymalizacyjna zniekształca miarę zastępczą (proxy), musisz najpierw dobrze poznać ten model. InstructGPT (Ouyang i in., 2022) zdefiniował architekturę referencyjną: nadzorowane dostrajanie (SFT) na parach prompt-odpowiedź, model nagrody trenowany na podstawie rankingów preferencji par oraz optymalizację polityki za pomocą PPO w odniesieniu do modelu nagrody, z nałożoną karą KL względem polityki SFT. Wersja InstructGPT o rozmiarze 1.3B była preferowana nad bazowym GPT-3 o rozmiarze 175B. Ten pojedynczy wynik jest powodem, dla którego w 2026 r. każde liczące się laboratorium wciąż stosuje potok poszkoleniowy (post-training) oparty na RLHF.

**Typ:** Teoria i koncepcje
**Języki:** Python (biblioteka standardowa, uproszczony trzyetapowy potok)
**Wymagania wstępne:** Faza 10 · 06 (SFT), Faza 10 · 07 (RLHF), Faza 10 · 08 (DPO)
**Czas:** ~45 minut

## Cele nauczania

- Wymień trzy etapy potoku InstructGPT oraz funkcje kosztu (straty) stosowane w każdym z nich.
- Wyjaśnij, dlaczego model 1.3B dostrojony zgodnie z instrukcjami jest lepiej oceniany pod kątem ludzkich preferencji niż surowy model GPT-3 175B.
- Określ, przed czym chroni kara KL na etapie 3. i dlaczego jej usunięcie prowadzi do zapadania się rozkładu wokół jednej mody (mode-seeking behavior).
- Opisz zjawisko podatku wyrównawczego (alignment tax) oraz metodę PPO-ptx zastosowaną przez Ouyanga i in. w celu jego złagodzenia.

## Problem

Pretrenowane modele językowe są zorientowane na uzupełnianie tekstu – nie odpowiadają bezpośrednio na pytania. Jeśli poprosisz GPT-3: „napisz funkcję w Pythonie odwracającą listę”, często otrzymasz po prostu kolejny prompt (polecenie), ponieważ większość danych treningowych to teksty pobrane z internetu, które z reguły zawierają kolejne powiązane pytania lub listy zadań. Model wykonuje swoje zadanie poprawnie (przewiduje kolejne tokeny) – to cel został błędnie sformułowany.

Miarą zastępczą (proxy), której używa każde liczące się laboratorium, aby rozwiązać ten problem, są ludzkie preferencje. Dwie wygenerowane odpowiedzi trafiają do osoby oceniającej (anotatora); ta wybiera lepszą z nich, a model nagrody (reward model) uczy się naśladować te wybory. Następnie pętla uczenia ze wzmocnieniem (RL) modyfikuje politykę (policy) modelu w stronę generowania odpowiedzi najwyżej ocenianych przez model nagrody. Oto cała idea InstructGPT streszczona w trzech zdaniach. Reszta artykułu to czysta inżynieria.

## Koncepcja

### Etap 1: Nadzorowane dostrajanie (SFT)

Zbierz pary prompt-odpowiedź, gdzie odpowiedź jest zgodna z tym, co napisałby pomocny człowiek o dobrych intencjach. Ouyang i in. wykorzystali 13 tysięcy promptów pochodzących od anotatorów oraz z interfejsu API OpenAI. Dostrój model bazowy na tych danych za pomocą standardowej funkcji straty entropii krzyżowej (cross-entropy loss).

Co daje SFT: model zaczyna odpowiadać na pytania zamiast po prostu kontynuować tekst. Czego nie daje: nie dostarcza sygnału wskazującego, którą odpowiedź preferuje oceniający, gdy dostępnych jest wiele wiarygodnych wariantów.

### Etap 2: Model nagrody (RM)

Dla każdego promptu generuje się K przykładowych odpowiedzi z modelu SFT. Anotator ocenia je (tworząc ranking). Następnie trenuje się model nagrody (RM), który ocenia dowolną parę (prompt, odpowiedź) w taki sposób, aby dla par, w których preferowano `y_w` (wygraną) nad `y_l` (przegraną), zachodziło:

```
L_RM = -log sigmoid(r(x, y_w) - r(x, y_l))
```

Jest to strata preferencji dla par Bradleya-Terry'ego. RM jest zazwyczaj inicjowany na bazie modelu SFT, w którym głowicę językową (LM head) zastąpiono głowicą skalarną (wyjściem jednowymiarowym).

Model nagrody jest stosunkowo mały: wersja 6B wystarczyła do obsłużenia InstructGPT 175B. Są one jednak również podatne na błędy (delikatne) – sekcja 5 publikacji skupia się głównie na zjawisku hakowania nagród (reward hacking), które pojawiało się nawet przy niewielkiej skali.

### Etap 3: PPO z karą KL

Zdefiniuj cel optymalizacji:

```
J(pi) = E_{x~D, y~pi(.|x)} [ r(x, y) ] - beta * KL(pi(.|x) || pi_SFT(.|x))
```

Maksymalizuj ten cel za pomocą PPO. Składnik kary KL zapobiega zbytniemu oddalaniu się polityki `pi` od polityki referencyjnej SFT (`pi_SFT`). Bez niego optymalizator znajduje przykłady adwersaryjne (adversarial examples) – ciągi znaków, które uzyskują bardzo wysokie oceny od modelu nagrody tylko dlatego, że model ten nigdy ich wcześniej nie widział, a nie dlatego, że rzeczywiście są preferowane przez ludzi.

Współczynnik kary KL `beta` to kluczowy hiperparametr w RLHF. Zbyt niski: dochodzi do hakowania nagród (reward hacking). Zbyt wysoki: brak jakiejkolwiek poprawy względem SFT.

### Podatek wyrównawczy (Alignment Tax)

Po zastosowaniu RLHF model jest lepiej oceniany przez ludzi, ale wykazuje regresję w standardowych benchmarkach akademickich (SQuAD, HellaSwag, DROP). Ouyang i in. nazywają to podatkiem wyrównawczym (alignment tax) i rozwiązują ten problem za pomocą metody PPO-ptx: mieszają gradienty z etapu pretreningu z celem optymalizacji RL, dzięki czemu model nie zapomina, jak wykonywać zadania, za które nie otrzymuje bezpośredniej nagrody.

```
J_ptx(pi) = J(pi) + gamma * E_{x~D_pretrain} [ log pi(x) ]
```

Metoda PPO-ptx stała się standardem w branży. Anthropic, DeepMind i Meta używają jej wariantów.

### Wyniki

W około 70% przypadków anotatorzy preferowali model InstructGPT 1.3B (SFT + RM + PPO-ptx) zamiast bazowego GPT-3 175B. Różnica ta staje się jeszcze wyraźniejsza w przypadku rzeczywistych (produkcyjnych) promptów testowych. Z tej zależności płyną dwa ważne wnioski:

1. Wyrównanie (alignment) i zdolności modelu (capabilities) to dwie różne osie. Model 175B posiadał większe możliwości ogólne, natomiast model 1.3B był lepiej wyrównany. Anotatorzy preferowali model lepiej wyrównany.
2. Minimalny poziom możliwości (zdolności) modelu jest określany przez jego wersję bazową. Uczenie ze wzmocnieniem (RLHF) nie sprawi, że model nagle pozna fakty, których nie widział w trakcie pretreningu.

### Dlaczego jest to punkt odniesienia dla fazy 18

Każda krytyka przedstawiona w kolejnych tematach – hakowanie nagród (temat 2), DPO (temat 3), sykofancja/pochlebstwo (temat 4), CAI (temat 5), uśpieni agenci (temat 7) czy fałszowanie wyrównania (temat 9) – uderza w konkretną część tego potoku przetwarzania. Hakowanie nagród dotyczy etapu 2. DPO łączy i upraszcza etapy 2 i 3. CAI (Constitutional AI) zastępuje ludzkiego oceniającego. Sykofancja pokazuje, że oceny anotatorów bywają obarczone błędem systematycznym. Fałszowanie wyrównania (alignment faking) udowadnia, że model może w pełni obejść etap 3. Aby zrozumieć te zjawiska, należy najpierw dobrze opanować strukturę klasycznego potoku RLHF.

## Uruchomienie kodu

Skrypt `code/main.py` symuluje wspomniane trzy etapy przy użyciu uproszczonych danych preferencji. Bazowa polityka (policy) to rzut niesymetryczną monetą wybierającą spośród akcji {A, B, C}. Etap 1 (SFT) naśladuje zachowanie anotatora na 200 promptach. Etap 2 dopasowuje model nagrody Bradleya-Terry'ego na bazie 500 porównań parzystych. Etap 3 realizuje uproszczoną aktualizację PPO z uwzględnieniem kary KL względem polityki SFT. Możesz obserwować wzrost nagrody, zmianę rozbieżności KL oraz ewolucję polityki. Możesz również wyłączyć karę KL, aby zaobserwować, jak hakowanie nagrody objawia się w ciągu 50 kroków aktualizacji.

Na co warto zwrócić uwagę:

- Przebieg wartości nagrody dla `beta = 0.1` w porównaniu z `beta = 0.0`.
- Zachowanie rozbieżności KL `KL(pi || pi_SFT)` w trakcie procesu treningowego.
- Ostateczny rozkład prawdopodobieństwa akcji w porównaniu z preferencjami anotatorów.

## Generowane pliki wyjściowe

Ta lekcja tworzy plik `outputs/skill-instructgpt-explainer.md`. Narzędzie to, na podstawie opisu potoku RLHF lub streszczenia artykułu naukowego, identyfikuje, który z trzech etapów ulega modyfikacji, jakie funkcje straty są stosowane oraz czy wdrożono karę KL lub jej odpowiednik regulacyjny.

## Ćwiczenia

1. Uruchom skrypt `code/main.py`. Ustaw `beta = 0.0` i przeanalizuj rozkład prawdopodobieństwa akcji po 200 krokach PPO. Wyjaśnij w jednym akapicie zjawisko dążenia do pojedynczej mody (mode-seeking behavior).

2. Zmodyfikuj model nagrody tak, aby faworyzował akcję B o dodatkowe +0.5 (symulacja błędu systematycznego w modelu nagrody). Uruchom PPO z parametrem `beta = 0.1`. Czy kara KL zapobiega eksploatacji tego błędu przez politykę? Przy jakiej wartości `beta` można zaobserwować eksploatację błędu?

3. Zapoznaj się z Rysunkiem 1 w pracy Ouyang i in. (arXiv:2203.02155). Spróbuj odtworzyć krzywą preferencji oceniających poprzez uruchomienie PPO odpowiednio na 1, 5, 20 i 100 kroków, a następnie zmierz odsetek preferencji w stosunku do bazowego modelu SFT.

4. W sekcji 4.3 wspomnianego artykułu autorzy podają, że InstructGPT 1.3B wygrywa z GPT-3 175B w około 70% przypadków. Dlaczego współczynnik ten może być wyższy dla rzeczywistych promptów produkcyjnych w porównaniu do promptów przygotowanych bezpośrednio przez anotatorów?

5. Zastąp funkcję straty PPO metodą DPO (Faza 10 · 08), korzystając z tych samych danych preferencji. Porównaj ostateczne odchylenie polityki (dywergencję KL względem SFT) oraz końcową nagrodę. Która metoda wykazuje większą stabilność przy danej nagrodzie?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|--------------------------------------|
| SFT | „strojenie instrukcji” | Etap 1: dostrajanie za pomocą entropii krzyżowej na parach prompt-odpowiedź |
| Model nagrody | "RM" | Regresor skalarny przyjmujący parę (prompt, odpowiedź), trenowany z użyciem straty Bradleya-Terry'ego na rankingach porównawczych |
| Bradley-Terry | „utrata preferencji par” | Funkcja straty oparta na porównaniach par: `-log sigmoid(r_w - r_l)`; sprowadza problem rankingu do klasyfikacji binarnej |
| Kara KL | „regulator” | `beta * KL(pi \|\| pi_SFT)` — utrzymuje politykę RL w pobliżu kotwicy SFT |
| PPO-ptx | „PPO z mieszanką przedtreningową” | Dodaje ważony człon log-prawdopodobieństwa z pretreningu do celu PPO, aby złagodzić podatek wyrównawczy |
| Podatek wyrównawczy | „regresja RLHF” | Spadek wyników w standardowych benchmarkach po zastosowaniu RLHF (w zadaniach, które nie były bezpośrednim celem optymalizacji RL) |
| Preferencje osoby zajmującej się etykietowaniem | „podstawowa prawda” | Próbka ludzkich ocen porównawczych; RM stanowi statystyczne przybliżenie (proxy) tych ocen, a nie definicję „ludzkich wartości” |

## Polecana literatura

- [Ouyang i in. — Szkolenie modeli językowych w zakresie wykonywania instrukcji na podstawie informacji zwrotnych od ludzi (arXiv:2203.02155)](https://arxiv.org/abs/2203.02155) — praca naukowa wprowadzająca InstructGPT, stanowiąca fundament współczesnych potoków RLHF
- [Stiennon i in. — Nauka podsumowywania na podstawie informacji zwrotnych od ludzi (arXiv:2009.01325)](https://arxiv.org/abs/2009.01325) — pionierskie zastosowanie RLHF do zadania streszczania tekstów
- [Christiano i in. — Uczenie się przez głębokie wzmacnianie na podstawie ludzkich preferencji (arXiv:1706.03741)](https://arxiv.org/abs/1706.03741) — pierwotne sformułowanie uczenia ze wzmocnieniem na bazie ludzkich preferencji
- [Bai i in. — Szkolenie pomocnego i nieszkodliwego asystenta za pomocą RLHF (arXiv:2204.05862)](https://arxiv.org/abs/2204.05862) — rozszerzenie potoku InstructGPT o aspekty pomocności i nieszkodliwości (HH) autorstwa firmy Anthropic
