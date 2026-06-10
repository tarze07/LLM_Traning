---

name: tripwire-design
description: Przeprowadź audyt proponowanego systemu zabezpieczeń agenta (wyłącznik awaryjny, wyłączniki automatyczne, tokeny kanarkowe) i wskaż brakujące mechanizmy ochronne przed pierwszym autonomicznym uruchomieniem.
version: 1.0.0
phase: 15
lesson: 14
tags: [kill-switch, circuit-breaker, canary, honeytoken, detection-and-response]

---

Dla proponowanego systemu detektorów we wdrożeniu agenta przeprowadź audyt w oparciu o trzy kluczowe filary: wyłącznik awaryjny (kill switch), wyłącznik automatyczny (circuit breaker) oraz token kanarkowy (canary). Wskaż komponenty brakujące, niewłaściwie skonfigurowane lub podatne na manipulację przez agenta.

Przygotuj:

1. **Audyt wyłącznika awaryjnego (Kill Switch).** Określ lokalizację wyłącznika (flaga funkcji, baza Redis, podpisana konfiguracja). Upewnij się, że dane uwierzytelniające agenta nie posiadają uprawnień do zmiany stanu wyłącznika. Potwierdź, czy stan wyłącznika jest weryfikowany przed każdą kolejną akcją, a nie tylko podczas startu sesji. Potwierdź, czy ponowne włączenie wymaga świadomej i ręcznej decyzji administratora.
2. **Rejestr wyłączników automatycznych (Circuit Breakers).** Wymień wzorce zachowań monitorowane przez wyłączniki (zapętlenia wywołań, powtarzające się awarie narzędzi, częstotliwość zapytań, uruchomienie ryzykownego narzędzia po odczytaniu niezaufanych danych). Określ próg aktywacji oraz czas wyciszenia (cool-off) dla każdego z nich. Progi aktywacji powyżej 10 powtórzeń są zazwyczaj zbyt wysokie.
3. **Projekt tokenów kanarkowych (Canary Design).** Wymień wszystkie tokeny kanarkowe wdrożone w środowisku. Dla każdego z nich określ: typ (fałszywe dane uwierzytelniające, rekord przynęta w bazie, plik przynęta, kanarek pamięci), lokalizację, akcję wyzwalającą alert oraz osobę powiadamianą. Upewnij się, że agent nie ma żadnego uzasadnionego powodu do interakcji z tymi zasobami w normalnych warunkach.
4. **Łączenie limitów statystycznych ze sztywnymi regułami.** Upewnij się, że wdrożono co najmniej jedno sztywne ograniczenie (o charakterze konstytucyjnym, patrz Lekcja 17) jako uzupełnienie dla detektorów statystycznych (takich jak EWMA czy z-score). Systemy opierające się wyłącznie na statystykach są podatne na zignorowanie powolnego dryfu zachowania agenta.
5. **Procedura kwarantanny (Quarantine Flow).** Zdefiniuj działania po aktywacji detektora: całkowite zatrzymanie procesu, zablokowanie konkretnej ścieżki wykonania, przekierowanie ruchu sieciowego (kwarantanna eBPF/Cilium do Honeypota) czy wyłącznie generowanie alertów. Upewnij się, że cały scenariusz reagowania został przetestowany w praktyce przynajmniej raz.

Kryteria odrzucenia (Hard Rejections):
- Wdrożenie agenta bez zewnętrznego wyłącznika awaryjnego (kill switch).
- Zapisywanie tokenów kanarkowych w systemach, w których agent posiada uprawnienia zapisu.
- Stosowanie wyłącznie detekcji statystycznej, bez zdefiniowania sztywnych limitów bezpieczeństwa.
- Wyłączniki automatyczne, które po okresie wyciszenia wznawiają pracę automatycznie bez weryfikacji przez człowieka.
- Uruchamianie nienadzorowanych sesji, w których stan wyłącznika awaryjnego jest sprawdzany tylko na starcie, a nie przed każdą akcją agenta.

Zasady odmowy wykonania zadania (Denial Policies):
- Jeśli użytkownik nie potrafi wskazać konkretnych systemów zewnętrznych (znajdujących się poza uprawnieniami agenta), w których zaimplementowano wyłącznik awaryjny, należy odmówić wykonania zadania. Podejście typu „używamy pliku konfiguracyjnego odczytywanego przez agenta” nie stanowi wyłącznika awaryjnego, jeśli agent ma uprawnienia do edycji tego pliku.
- Jeśli użytkownik traktuje klasyfikator bezpieczeństwa trybu automatycznego (patrz Lekcja 10) jako alternatywę dla mechanizmów detekcji zagrożeń (tripwires/canaries), należy odmówić. Klasyfikator działa niezależnie od systemów wykrywania i reagowania.
- Jeśli proponowane tokeny kanarkowe są zlokalizowane w systemach, które agent musi odczytywać w ramach normalnej pracy, należy odmówić i zażądać przeprojektowania architektury.

Format danych wyjściowych:

Przedstaw raport z audytu systemów Tripwire zawierający:
- **Architekturę wyłącznika awaryjnego** (lokalizacja, częstotliwość weryfikacji, procedura ponownego włączenia)
- **Tabelę wyłączników automatycznych** (monitorowany wzorzec, próg aktywacji, okres wyciszenia)
- **Tabelę tokenów kanarkowych** (typ kanarka, lokalizacja, akcja alarmowa, osoba odpowiedzialna)
- **Analizę warstwowości zabezpieczeń** (czy wdrożono jednocześnie statystykę i sztywne limity [tak/nie])
- **Procedurę kwarantanny** (kryteria aktywacji, podejmowane akcje, status testów [tak/nie])
- **Rekomendację wdrożeniową** (wdrożenie produkcyjne / staging / środowisko badawcze)
