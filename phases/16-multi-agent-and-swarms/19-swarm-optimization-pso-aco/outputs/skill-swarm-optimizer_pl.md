---

name: swarm-optimizer
description: Wybierz pomiędzy PSO, ACO, algorytmami genetycznymi i optymalizatorami opartymi na gradiencie dla danego problemu LLM lub optymalizacji agenta. Algorytmy roju inspirowane biologią są wolne od gradientów i nadają się do obciążeń w epoce LLM, w których przestrzeń wyszukiwania jest dyskretna lub funkcja dopasowania jest czarną skrzynką.
version: 1.0.0
phase: 16
lesson: 19
tags: [multi-agent, swarm-optimization, PSO, ACO, prompt-optimization, routing]

---

Biorąc pod uwagę problem LLM lub optymalizacji agenta, wybierz odpowiedni optymalizator.

Wyprodukuj:

1. **Odcisk palca problemu.** Przestrzeń wyszukiwania (ciągłe liczby, ciąg znaków podpowiedzi, wagi modeli, wykres routingu), sygnał sprawności (test automatyczny, ocena LLM, osoba oceniająca, biznesowy KPI), czas uzyskania wartości (minuty, godziny, dni).
2. **Wybór optymalizatora.** PSO, ACO, algorytm genetyczny, DPO/RL, strojenie ręczne. Każdy ma domyślny przypadek użycia:
   - ciągła liczba na ograniczonej przestrzeni → PSO
   - wybór trasy lub ścieżki → ACO
   - dyskretne symboliczne / programy → algorytmy genetyczne
   - zróżnicowana nagroda → DPO/RL
   - niskowymiarowa, szybka ewaluacja → wyszukiwanie siatki/losowe
3. **Wielkość populacji.** 10-30 dla PSO/GA, wielkość matrycy feromonowej dla ACO. Obliczenie budżetu: N × T × koszt ewaluacji. Nie twórz rojów, które kosztują więcej niż wartość, którą wytwarzają.
4. **Fitness + bramka jakości.** Jaka funkcja wyróżnia kandydata? Jaki próg jakości w przypadku routingu ACO powoduje osadzanie się feromonów?
5. **Monitorowanie zbieżności.** Rejestrowanie g_best lub stabilności feromonów na iterację. Alarm w przypadku dywergencji (katastrofalnego dryfu) i przedwczesnej konwergencji (optimum lokalne).
6. **Trening rozpadu/eksploracji.** Bezwładność PSO i wagi poznawcze/społeczne; Szybkość zaniku feromonu ACO i ilość osadu. Kompromis: niski spadek → zatrzymanie się na wczesnym zwycięzcy; wysoki zanik → brak pamięci.
7. **Zresetuj warunki.** Kiedy zmieni się rozkład ewaluacji lub zmieni się wzór rozmieszczenia, zresetuj tymczasowo g_best lub zeruj feromony. Nieaktualne wspomnienia są gorsze niż ich brak.

Twarde odrzucenia:

- Optymalizatory roju w zadaniach, w których sprawność wymaga sprawdzenia przez człowieka. Budżet kosztu per iteracji jest karłowaty.
- Liczebność populacji > 50 bez jasnego uzasadnienia budżetowego. Dominują malejące zyski.
- Kierowanie feromonów bez bramki jakości. Szybcy, ale niewłaściwi agenci zamykają się.
- PSO w dyskretnych przestrzeniach poszukiwań, które nie mają naturalnego ciągłego osadzania. Zamiast tego użyj GA lub symulowanego wyżarzania.

Zasady odmowy:

- Jeśli użytkownik próbuje zoptymalizować coś bez jasnej funkcji sprawności, zalecamy najpierw zdefiniowanie sprawności. Optymalizatory roju nie mogą pomóc bez oceniającego.
- Jeśli budżet użytkownika jest niższy niż 100 dolarów, zalecamy ręczne dostrajanie + buforowanie zamiast rojów.
- Jeśli dystrybucja zmienia się codziennie, zalecaj naukę online lub bandytów, a nie optymalizatory roju.

Wynik: jednostronicowy brief. Zacznij od jednozdaniowej rekomendacji („Użyj ACO z depozytami feromonów bramkowanych jakością w przypadku problemu z routingiem typu 3 agentów × 4 zadania. Zanik 0,05, próg 0,6, 200 zadań rozgrzewkowych.”), a następnie siedem sekcji powyżej. Zakończ szacunkowym budżetem i 1-tygodniowym planem wdrożenia.