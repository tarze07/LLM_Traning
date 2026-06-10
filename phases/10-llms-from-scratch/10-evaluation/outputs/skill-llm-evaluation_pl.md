---

name: skill-llm-evaluation
description: Ramy decyzyjne dotyczące wyboru właściwej strategii oceny LLM w oparciu o rodzaj zadania, budżet i wymagania
version: 1.0.0
phase: 10
lesson: 10
tags: [evaluation, evals, benchmarks, llm-as-judge, elo, metrics]

---

# Strategia oceny LLM

Oceniając system LLM, zastosuj te ramy decyzyjne, aby wybrać właściwe podejście.

## Kiedy używać każdego typu eval

**Benchmarki (MMLU, HumanEval, SWE-bench):** Dokonujesz wstępnego wyboru modelu. Musisz zawęzić 10 potencjalnych modeli do 3. Testy porównawcze dają przybliżony ranking przy zerowym koszcie. Nie używaj benchmarków jako ostatecznej oceny.

**Ewaluacje niestandardowe:** Budujesz do produkcji. Masz określone zadanie z określonymi trybami awarii. Niestandardowe oceny są jedyną oceną, która przewiduje wydajność w świecie rzeczywistym. Minimum 50 przypadków testowych dla prototypu, ponad 200 dla produkcji.

**LLM-as-sędzia:** Twoje zadanie ma charakter otwarty (podsumowanie, pisanie, rozmowa). Dane dotyczące dopasowania dokładnego i nakładania się tokenów są zbyt sztywne. LLM-jako-sędzia kosztuje ~0,01 dolara za orzeczenie i zgadza się z ludźmi w ~80% przypadków. Zawsze używaj rubryk, a nie niejasnych podpowiedzi.

**Oceny dokonywane przez ludzi:** Stawka jest wysoka, a zautomatyzowane wskaźniki nie zgadzają się z tym. Ocena człowieka jest podstawową prawdą, ale kosztuje $0.10-$2.00 za osąd. Rezerwa na przypadki niejednoznaczne i okresową kalibrację automatycznych metryk.

**ELO z porównań parami:** porównujesz wiele modeli w ramach tego samego zadania. Metoda parami jest bardziej wiarygodna niż punktacja bezwzględna, ponieważ ludzie (i sędziowie LLM) są lepsi w ocenie względnej.

## Wybór funkcji punktacji

- **Dokładne dopasowanie**: klasyfikacja, wyodrębnianie jednostek, uporządkowane wyniki ze znanymi odpowiedziami
- **Token F1**: zadania wyodrębniania, w których liczy się częściowe zaliczenie
- **ROUGE-L**: podsumowanie, tłumaczenie
- **BLEU**: tłumaczenie maszynowe
- **LLM-as-sędzia**: otwarte pokolenie, jakość konwersacji, użyteczność
- **Oparte na wykonaniu**: generowanie kodu (uruchom kod, sprawdź, czy testy wyszły pomyślnie)
- **Zgodność schematu**: uporządkowane dane wyjściowe (czy JSON pasuje do schematu?)

## Czerwone flagi w projekcie ewaluacyjnym

- Zbiór ewaluacyjny mniejszy niż 50 przypadków: wyniki są statystycznie bez znaczenia
- Brak przypadków skrajnych: mierzysz wydajność szczęśliwej ścieżki, która jest zawsze wyższa niż w świecie rzeczywistym
- Pojedynczy wskaźnik: różne wskaźniki opowiadają różne historie, użyj co najmniej dwóch
- Brak wersjonowania: nie można śledzić ulepszeń bez wersjonowanych zestawów ewaluacyjnych
- Zanieczyszczenie zestawu ewaluacyjnego: nigdy nie dołączaj przykładów ewaluacji do danych dostrajających lub podpowiedzi dotyczących kilku strzałów
- Testowanie tylko jednego modelu: do porównania potrzebujesz linii bazowej (nawet prostej heurystyki).

## Lista kontrolna potoku Eval

1. Precyzyjnie zdefiniuj zadanie (nie „odpowiadaj na pytania”, ale „podziel zgłoszenia na 5 kategorii”)
2. Twórz przypadki testowe na podstawie szczęśliwej ścieżki, przypadków brzegowych i znanych regresji
3. Wybierz 2-3 funkcje scoringowe odpowiednie dla rodzaju zadania
4. Ustaw progi pozytywne/negatywne w oparciu o wymagania produkcyjne
5. Zautomatyzuj wykonanie: jedno polecenie uruchamia cały pakiet
6. Wersjonuj wszystko: przypadki testowe, funkcje scoringowe, podpowiedzi, wersje modeli
7. Uruchom przy każdej zmianie: natychmiastowe aktualizacje, zamiany modeli, wdrożenia kodu
8. Śledź trendy: pojedynczy wynik to szum, linia trendu to sygnał
9. Co kwartał przeprowadzaj kalibrację pod kątem oceny ludzkiej
10. Dodawaj przypadki regresji po wykryciu awarii produkcyjnej