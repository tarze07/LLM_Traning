# Testowanie A/B Funkcje LLM — GrowthBook, Statsig i problem wibracji

> Tradycyjne testy A/B nie zostały zbudowane dla niedeterministycznych LLM. Kluczowe rozróżnienie: odpowiedź evals „czy model może wykonać to zadanie?” Testy A/B odpowiadają na pytanie „czy użytkownikom to zależy?” Obydwa są wymagane; wysyłka kontroli wibracyjnych dobiegła końca. Co testować w 2026 r.: szybka inżynieria (sformułowanie), wybór modelu (GPT-4 vs GPT-3.5 vs OSS; dokładność vs koszt vs opóźnienie), parametry generacji (temperatura, top-p). Prawdziwe przypadki: wariant modelu chatbota z nagrodami zapewnił +70% długości rozmowy i +30% retencji; Eksperymenty tematyczne dotyczące sztucznej inteligencji Nextdoor zapewniły +1% CTR po udoskonaleniu funkcji nagrody; Khan Academy Khanmigo iterował na osi opóźnienie vs dokładność matematyczna. Podział platformy: **Statsig** (przejęty przez OpenAI za 1,1 miliarda dolarów we wrześniu 2025 r.) — testowanie sekwencyjne, CUPED, wszystko w jednym. **GrowthBook** — open source, natywny dla hurtowni, silniki Bayesian + Frequencyist + Sequential, CUPED, kontrole SRM, poprawki Benjamini-Hochberg + Bonferroni. Wybierasz na podstawie preferencji hurtowni-SQL i tego, czy „nabyte przez OpenAI” ma znaczenie dla Twojej organizacji.

**Typ:** Ucz się
**Języki:** Python (stdlib, symulator testów sekwencyjnych zabawek)
**Wymagania wstępne:** Faza 17 · 13 (obserwowalność), faza 17 · 20 (wdrażanie progresywne)
**Czas:** ~60 minut

## Cele nauczania

- Odróżnij oceny („czy model może wykonać zadanie”) od testów A/B („czy to obchodzi użytkowników”).
- Wylicz trzy testowalne osie (podpowiedź, model, parametry) i wybierz metrykę dla każdej.
- Wyjaśnij CUPED, testy sekwencyjne i poprawki wielokrotnych porównań Benjaminiego-Hochberga.
- Wybierz Statsig lub GrowthBook na podstawie postawy hurtowni-SQL i postawy przejęć korporacyjnych.

## Problem

Ręcznie dostroiłeś monit systemowy. Czuję się lepiej. Wysyłasz to. Konwersja zmienia się pod wpływem szumu. Obwiniasz metrykę. Albo wysłałeś nowy model, a konwersja nie uległa zmianie — czy model uległ degradacji, czy też zmiana była zbyt mała, aby ją wykryć? Nie wiesz, ponieważ wysłałeś bez A/B.

Wartości ewaluacyjne odpowiadają na pytanie, czy model może wykonać zadanie na oznaczonym zbiorze. Nie odpowiadają, czy użytkownicy wolą dane wyjściowe. Odpowiedzi na to pytanie udziela tylko kontrolowany eksperyment online i tylko wtedy, gdy eksperyment ma wystarczającą moc, kontroluje niedeterminizm i koryguje wielokrotne porównania.

## Koncepcja

### Ewaluacje a testy A/B

**Evals** — offline, zestaw z etykietą, sędzia (rubryka lub LLM-jako sędzia lub człowiek). Odpowiedź: „Czy wynik jest poprawny/przydatny/bezpieczny w tej stałej dystrybucji?”

**Test A/B** — online, użytkownicy na żywo, losowo. Odpowiedź: „Czy nowy wariant przesuwa istotne dane na poziomie użytkownika?”

Obydwa wymagane. Evals wychwytuje regresje przed ekspozycją; A/B potwierdza wpływ produktu po.

### Co przetestować

1. **Szybka inżynieria** — sformułowania, struktura podpowiedzi systemowych, przykłady. Metryka: sukces zadania, utrzymanie użytkownika, koszt/żądanie.
2. **Wybór modelu** — GPT-4 vs GPT-3.5-Turbo vs Llama-OSS. Metryka: dokładność (zadanie) + koszt/żądanie + opóźnienie P99. Wielocelowy.
3. **Parametry generacji** — temperatura, top-p, max_tokens. Metryka: specyficzna dla zadania (różnorodność wyników vs determinizm).

### CUPED — redukcja wariancji

Eksperymenty kontrolowane z wykorzystaniem danych sprzed eksperymentu. Wycofuj wariancję przed okresem przed porównaniem po okresie. Typowa redukcja wariancji: 30-70%. Efektywna wielkość próbki zwiększa się bezpłatnie.

Wdrożenie: wdrożenie zarówno Statsig, jak i GrowthBook.

### Testowanie sekwencyjne

Klasyczna metoda A/B zakłada stałą wielkość próby. Testy sekwencyjne („zobacz i zdecyduj”) kontrolują odsetek wyników fałszywie dodatnich w przypadku wielokrotnego sprawdzania. Zawsze ważne procedury sekwencyjne (mSPRT, sekwencje ufności Howarda) pozwalają wcześnie zatrzymać się w przypadku wyraźnych zwycięzców.

### Korekty wielokrotnego porównania

Przeprowadzenie 20 testów A/B przy 95% pewności daje przypadkowo jeden fałszywie pozytywny wynik. Korekta Bonferroniego zaostrza α w teście; Benjamini-Hochberg kontroluje odsetek fałszywych odkryć. GrowthBook wdraża oba.

### SRM — niedopasowanie proporcji próbkowania

Hash przypisania losuje użytkowników do wariantów. Jeśli podział 50/50 daje 47/53, coś jest zepsute — kontrola SRM to sygnalizuje. Obie platformy wdrażają.

### Statystyki kontra GrowthBook

**Statystyka**:
- Przejęty przez OpenAI za 1,1 miliarda dolarów (wrzesień 2025). Hostowane, SaaS.
- Testy sekwencyjne, CUPED, populacje wstrzymane.
- Wszystko w jednym: flagi funkcji + eksperymentowanie + obserwowalność.
- Najlepsze dopasowanie: zespół już chce produktu w pakiecie i nie przejmuje się posiadaniem OpenAI.

**Księga Rozwoju**:
- Otwarte oprogramowanie (MIT); natywny dla magazynu (odczytuje bezpośrednio z Snowflake/BigQuery/Redshift).
- Wiele silników: Bayesowski, częsty, sekwencyjny.
- poprawki CUPED, SRM, Bonferroni, BH.
- Chmura hostowana samodzielnie lub zarządzana.
- Najlepsze dopasowanie: hurtownia-SQL shop, zespół danych kontroluje warstwę metryczną, chce OSS.

### Niedeterminizm komplikuje władzę

Ten sam monit generuje różne wyniki. Tradycyjne obliczenia mocy zakładają obserwacje IID. W przypadku niedeterminizmu LLM efektywna wielkość próby jest mniejsza niż nominalna. Pomnóż wymaganą wielkość próbki przez ~1,3-1,5x jako margines bezpieczeństwa.

### Wyniki rzeczywistych przypadków

- Wariant modelu nagrody Chatbota: +70% długości rozmowy, +30% retencji.
- Tematy Nextdoor: +1% CTR po udoskonaleniu funkcji nagrody.
- Khan Academy Khanmigo: iteracyjny handel między opóźnieniami a dokładnością matematyczną.

### Antywzorzec: wysyłka oparta na wibracjach

Każdy starszy inżynier może wymienić funkcję, która została dostarczona, ponieważ „wydaje się lepsza” bez A/B. Większość z nich dokonała regresji wskaźników produktu, których zespół nie zauważył od miesięcy. A/B to funkcja wymuszająca.

### Liczby, które powinieneś zapamiętać

- Statsig przejęty przez OpenAI: 1,1 miliarda dolarów, wrzesień 2025.
- GrowthBook: MIT typu open source; Bayesowski + częsty + sekwencyjny.
- Redukcja wariancji CUPED: 30-70%.
- Niedeterminizm LLM → +30-50% bufora wielkości próbki.

## Użyj tego

`code/main.py` symuluje sekwencyjny test A/B ze stałymi i sekwencyjnymi granicami. Pokazuje, jak sekwencja umożliwia wcześniejsze zatrzymanie.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-ab-plan.md`. Biorąc pod uwagę zmianę funkcji, obciążenie pracą, linię bazową, wybiera platformę, bramki, wielkość próbki.

## Ćwiczenia

1. Uruchom `code/main.py`. Dla oczekiwanego wzrostu o 5% przy bazowej konwersji na poziomie 3%, jaka wielkość próbki do mocy 80%?
2. Wybierz Statsig lub GrowthBook dla klienta premium objętego opieką zdrowotną.
3. Zaprojektuj analizę A/B, która testuje GPT-4 w porównaniu z GPT-3.5 w oparciu o koszt rozwiązanego biletu. Jaka jest metryka podstawowa, metryka poręczy, metryka drugorzędna?
4. Twój kanarek przechodzi, ale A/B wykazuje konwersję -1,2%. Czy wysyłasz? Zapisz kryteria eskalacji.
5. Zastosuj CUPED na okres przedokresowy z 60% wariancją postu. Oblicz wzmocnienie efektywnej wielkości próbki.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Ewa | „test offline” | Ocena możliwości modelu w oparciu o zestaw etykiet |
| Test A/B | „eksperyment” | Randomizowane porównanie użytkowników na żywo |
| CUPOWANY | „redukcja wariancji” | Regresja przed okresem w celu zmniejszenia wariancji |
| Test sekwencyjny | „test peek-ok” | Zawsze obowiązująca procedura umożliwiająca wcześniejsze zatrzymanie |
| Porównanie wielokrotne | „błąd rodzinny” | Wykonywanie wielu testów zwiększa liczbę fałszywych alarmów |
| Bonferroniego | „ścisła korekta” | Podziel α przez liczbę testów |
| Benjamini-Hochberg | „BH FDR” | Kontrola współczynnika fałszywych odkryć, mniej konserwatywna |
| SRM | „zły podział” | Niedopasowanie proporcji próbki; błąd przydziału |
| Statystyka | „Właściciel OpenAI” | Komercyjne urządzenie wielofunkcyjne, nabyte w 2025 r. |
| Księga wzrostu | „ten OSS” | Platforma natywna dla hurtowni MIT |
| mSPRT | „sekwencyjny test współczynnika prawdopodobieństwa” | Klasyczna procedura sekwencyjna |

## Dalsze czytanie

- [GrowthBook — Jak testować A/B AI](https://blog.growthbook.io/how-to-a-b-test-ai-a-practical-guide/)
— [Statsig — Poza podpowiedziami: optymalizacja LLM oparta na danych](https://www.statsig.com/blog/llm-optimization-online-experimentation)
– [Porównanie Statsig i GrowthBook](https://www.statsig.com/perspectives/ab-testing-feature-flags-comparison-tools)
- [Deng i in. — CUPED](https://www.exp-platform.com/Documents/2013-02-CUPED-ImprovingSensitivityOfControlledExperiments.pdf)
– [Howard — Sekwencje ufności](https://arxiv.org/abs/1810.08240)