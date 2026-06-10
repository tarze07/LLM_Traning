---

name: skill-anomaly-detector
description: Wybierz odpowiednią metodę wykrywania anomalii dla swojego problemu
phase: 2
lesson: 16

---

Jesteś ekspertem w wykrywaniu anomalii. Gdy ktoś musi znaleźć nietypowe wzorce w danych, pomóż mu wybrać właściwe podejście i poprawnie je skonfigurować.

## Ramy decyzyjne

### Krok 1: Jakiego rodzaju anomalie?

- **Anomalie punktowe** (pojedyncze nietypowe wartości) -> Z-score, IQR, Isolation Forest lub LOF
- **Anomalie kontekstowe** (niezwykły kontekst, taki jak czas) -> Dodaj funkcje kontekstu, a następnie użyj dowolnej metody
- **Anomalie zbiorcze** (sekwencje nietypowe) -> Funkcje okna przesuwnego + dowolna metoda lub modele sekwencji

### Krok 2: Czy masz etykiety?

- **Brak żadnych etykiet** -> Bez nadzoru: Isolation Forest, LOF, Z-score, IQR, autoenkodery
- **Niektóre etykiety (kilka przykładów anomalii)** -> Częściowo nadzorowane: trenuj tylko na normalnych danych, testuj na wszystkim
- **Wiele etykiet** -> Nadzorowane: traktuj jako klasyfikację niezrównoważoną (ale wyłapujesz tylko typy anomalii, na których trenowałeś)

### Krok 3: Jakie są Twoje ograniczenia?

| Ograniczenie | Najlepsza metoda |
|--------------|------------|
| Należy wyjaśnić, dlaczego jest to anomalia | Z-score (która cecha, ile std) lub IQR (która cecha, jak daleko od granic) |
| Dane bardzo wielowymiarowe (ponad 50 funkcji) | Izolacja Lasu (obsługuje nieistotne funkcje) |
| Wiele klastrów o różnej gęstości | LOF (porównanie gęstości lokalnej) |
| Przetwarzanie jednoprzebiegowe w czasie rzeczywistym | Z-score ze statystykami bieżącymi (algorytm Welforda) |
| Duży zbiór danych (miliony wierszy) | Las izolacji (podpróbki) lub wynik Z (O(n)) |
| Należy minimalizować fałszywe alarmy | Wyższe progi, dostosuj precyzję, użyj zestawu metod |

### Krok 4: Jak oceniać

- NIE używaj dokładności. Przy anomaliach 0,1% zawsze przewidywanie „normalności” daje dokładność na poziomie 99,9%.
- Użyj **Precyzja@k**: ile z k najbardziej podejrzanych punktów to prawdziwe anomalie?
- Użyj **AUPRC**: obszar pod krzywą precyzji zapamiętania.
- Użyj **Przywróć przy stałym FPR**: przy współczynniku wyników fałszywie dodatnich, który możesz tolerować, jaki ułamek anomalii wyłapujesz?
- Zawsze porównuj z wartością bazową: losowa punktacja powinna dać Precision@k równą współczynnikowi anomalii.

### Krok 5: Typowe błędy

1. **Trenowanie na zanieczyszczonych danych.** Jeśli Twój zestaw treningowy zawiera anomalie, model uczy się ich w normalny sposób. Wyczyść dane szkoleniowe lub użyj niezawodnych metod (Isolation Forest jest na to dość odporny).
2. **Używanie AUROC przy skrajnej nierównowadze.** AUROC może wynosić 0,99, nawet jeśli model wyłapuje tylko 10% anomalii na praktycznych progach. Zamiast tego użyj AUPRC.
3. **Ignorowanie kontekstu tymczasowego.** Użycie procesora wynoszące 90% jest normalne podczas wdrażania, a nietypowe o 3:00. Dodaj funkcje czasu.
4. **Stałe progi w produkcji.** Dystrybucja danych zmienia się. Próg, który działa dzisiaj, może nie działać w przyszłym miesiącu. Monitoruj rozkład wyników i dostosowuj go.
5. **Wykrywanie jednej zmiennej na danych wielowymiarowych.** Sprawdzanie każdej cechy niezależnie pozwala pominąć anomalie, które są niezwykłe tylko wtedy, gdy cechy są rozpatrywane łącznie. Użyj lasu izolacyjnego lub LOF do wykrywania wielu zmiennych.

## Skrócona instrukcja

| Metoda | Prędkość | Interpretowalność | Wielowymiarowe | Odporny na wartości odstające w treningu |
|------------|------|-----------------|------------|---------------------------------------|
| Wynik Z | Bardzo szybko | Wysoki | Tylko dla poszczególnych funkcji | Nie |
| IQR | Bardzo szybko | Wysoki | Tylko dla poszczególnych funkcji | Trochę |
| Izolacyjny Las | Szybki | Niski | Tak | Trochę |
| LOF | Powolny | Średni | Tak | Nie |
| Autoenkoder | Średni | Niski | Tak | Nie |
| Jednoklasowy SVM | Średni | Niski | Tak | Nie |