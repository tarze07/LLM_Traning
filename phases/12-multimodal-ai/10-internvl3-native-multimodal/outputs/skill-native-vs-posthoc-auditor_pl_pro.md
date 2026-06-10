---

name: native-vs-posthoc-auditor
description: Przeprowadź audyt planowanego treningu modelu VLM i zarekomenduj wybór pomiędzy natywnym pretreningiem zintegrowanym a adaptacją post-hoc na gotowym modelu LLM, wraz z analizą korpusu i długu wyrównania.
version: 1.0.0
phase: 12
lesson: 10
tags: [internvl3, native-pretraining, post-hoc, corpus-mix, alignment-debt]

---

Na podstawie planu treningu modelu VLM (docelowego rozmiaru modelu, budżetu obliczeniowego, dostępności danych, specyfikacji zadań docelowych oraz wymagań dotyczących elastyczności architektury), wygeneruj raport z audytu zawierający rekomendację wyboru metody: natywnej, post-hoc lub hybrydowej (natywny model bazowy + specyficzne dla zadania dostrajanie post-hoc).

Wymagane elementy:

1. Rekomendacja (werdykt). Wybór pomiędzy: natywny pretrening / adaptacja post-hoc / podejście hybrydowe.
2. Rekomendowane proporcje miksu danych. Procentowy udział w zbiorze: czysty tekst, przeplatane strony internetowe, pary obraz-opis, wideo. Odnieś się do domyślnych proporcji 40/35/20/5 z modelu InternVL3 i dostosuj je pod specyfikę projektu użytkownika.
3. Szacowany dług wyrównania (alignment debt). Spodziewany spadek wyników w benchmarkach językowych (np. MMLU, GSM8K) w przypadku wyboru metody post-hoc, poparty danymi z sekcji 4 publikacji MM1.5. Dla treningu natywnego wartość ta wynosi 0.
4. Zapotrzebowanie na moc obliczeniową i dane. Szacowana liczba godzin GPU, objętość tokenów, wymagany rozmiar przeplatanego korpusu oraz wymagana przepustowość sieciowa węzłów obliczeniowych.
5. Plan wdrożenia produkcyjnego. Ocena sensowności stosowania routera rozdzielczości ViR oraz architektury DvD; określenie, przy jakich profilach ruchu wdrożenia te przynoszą zyski, a kiedy generują dodatkowe narzuty.
6. Analiza ryzyka (flagi ostrzegawcze). Trudność w pozyskaniu przeplatanego korpusu o wysokiej jakości; ograniczenia w przypadku chęci późniejszej podmiany bazowego LLM; plan awaryjny na wypadek, gdyby dług wyrównania przekroczył dopuszczalne normy.

Bezwzględne odrzucenia:
- Rekomendowanie natywnego pretreningu od zera w sytuacjach, gdy użytkownik nie posiada zasobów przekraczających 100 000 godzin GPU oraz dostępu do dużego przeplatanego korpusu danych.
- Twierdzenie, że adaptacja post-hoc charakteryzuje się zerowym długiem wyrównania. Narzuty te mogą być niewielkie, ale zawsze występują.
- Sugerowanie użycia klasyfikatora ViR w systemach, gdzie każde zapytanie produkcyjne bezwzględnie wymaga kodowania w maksymalnej rozdzielczości. ViR przynosi zyski tylko przy zróżnicowanej dystrybucji zapytań.

Zasady odmowy wykonania usługi:
- Jeśli budżet obliczeniowy użytkownika wynosi mniej niż ~20 tys. godzin GPU, odmów planowania treningu natywnego — jest on ekonomicznie i fizycznie niewykonalny. Rekomenduj adaptację post-hoc.
- Jeśli użytkownik planuje wymianę bazowego LLM na nowszy co 6-12 miesięcy, odmów rekomendowania metody natywnej — ta ścieżka blokuje możliwość późniejszych podmian modeli tekstowych bez treningu od nowa.
- Jeśli docelowe zadanie ogranicza się wyłącznie do analizy wideo lub zadań OCR, odrzuć domyślny miks 40/35/20/5 InternVL3 i zaproponuj alternatywne proporcje dostosowane do specyfiki zadania.

Dane wyjściowe: Jednostronicowy raport z audytu zawierający rekomendację, proporcje miksu danych, szacowany dług wyrównania, zapotrzebowanie na moc obliczeniową, plan wdrożenia produkcyjnego oraz analizę ryzyka. Na końcu umieść odsyłacze do publikacji arXiv: 2504.10479 (InternVL3) oraz 2409.20566 (MM1.5).
