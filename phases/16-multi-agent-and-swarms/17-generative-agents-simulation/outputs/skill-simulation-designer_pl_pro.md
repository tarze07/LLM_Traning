---

name: simulation-designer
description: Zaprojektuj symulację agenta generatywnego (w stylu Smallville) dla danego scenariusza. Określa schemat pamięci, częstotliwość refleksji, horyzont planu, ograniczenia przestrzenne/społeczne i metryki oceny.
version: 1.0.0
phase: 16
lesson: 17
tags: [multi-agent, simulation, generative-agents, emergence, memory]

---

Zaprojektuj symulację dla podanego scenariusza wymagającego emergentnych zachowań populacji agentów (np. symulacja społeczna, NPC w grach, analiza polityki społecznej, dynamika rynku).

Opracuj następujące elementy:

1. **Wielkość i heterogeniczność populacji.** Liczba agentów (N); informacja, czy korzystają z tego samego modelu bazowego, czy z różnych; rodziny promptów; podział ról. W eksperymencie Smallville użyto 25 homogenicznych agentów o zindywidualizowanych osobowościach; większe populacje zyskują dzięki wprowadzeniu heterogeniczności.
2. **Schemat pamięci.** Pola w pojedynczym wpisie: `(ts, kind, content, importance, embedding_ref, source_ids)`. Stała zaniku aktualności; procedura oceny ważności; metryka trafności (podobieństwo cosinusowe wektorów osadzeń modelu X). Strategia retencji danych w celu kompresji pamięci.
3. **Częstotliwość refleksji.** Wyzwalacz: gdy suma ważności nieprzetworzonych wspomnień przekroczy próg, co N obserwacji lub co określoną liczbę kroków symulacji (ticks). Liczba refleksji na jedno wyzwolenie. Szablon promptu do generowania refleksji.
4. **Horyzont planowania.** Podział na poziomy: dobowy, godzinowy i konkretnych działań. Określenie, które z nich są obowiązkowe, a które opcjonalne. Wyzwalacz rewizji planu: nowa obserwacja o ważności powyżej określonego progu, sprzeczna z aktualnym planem.
5. **Model świata.** Siatka przestrzenna (spatial grid), graf relacji społecznych, ograniczenia zasobów. Definicja tego, co stanowi obserwację (np. pole widzenia, bezpośrednia rozmowa, powiadomienie). Ograniczenia normatywne, których architektura NIE uczy się samodzielnie i które muszą być jawnie zakodowane (np. limity pojemności pomieszczeń, godziny otwarcia, strefy prywatne).
6. **Cele początkowe (seeds).** Przypisanie konkretnych priorytetów wybranym agentom. Zdefiniowanie celów nakładających się (mogących prowadzić do konfliktu) oraz celów niezależnych (które powinny współistnieć).
7. **Budżet.** Liczba zapytań do LLM na jeden krok (tick) per agent (obserwacja + wyszukiwanie + refleksja + planowanie + działanie). Oczekiwana liczba tokenów na jeden krok per agent. Szacowany koszt całkowity symulacji dla T kroków.
8. **Metryki ewaluacji.** Ocena wiarygodności przez sędziów (human evaluation), wskaźnik realizacji celów, liczba udanych zdarzeń koordynacyjnych oraz liczba naruszeń norm przestrzennych jako wskaźnik błędów.

Kryteria twardego odrzucenia projektu:

- Brak jawnego zakodowania norm przestrzennych i społecznych. Bez tego architektura zacznie je naruszać (np. wchodzenie do zamkniętych obiektów lub jednoczesne korzystanie z jednoosobowej łazienki).
- Zastosowanie modyfikowalnej pamięci. Pamięć musi być typu append-only (wyłącznie do dopisywania); wszelkie korekty muszą być wprowadzane jako nowe rekordy.
- Uruchamianie procesu refleksji w każdym kroku (tick). Jest to nieefektywne budżetowo; refleksja jest kosztowną operacją i powinna być wyzwalana na podstawie progów.
- Symulacje z dużą liczbą agentów (N > 50) bez wdrożonej strategii kompresji pamięci. Koszt i czas wyszukiwania wspomnień rosną wraz z długością strumienia pamięci.

Zasady odmowy wykonania zadania (rekomendacje alternatywne):

- Jeśli scenariusz wymaga emergentnego *wykonywania zadań*, a nie emergentnych *zachowań społecznych*, zarekomenduj wzorce oparte na koordynatorze, rolach i prymitywach (Faza 16, lekcje 05-08). Architektura typu Smallville służy do symulacji społecznych.
- Jeśli całkowity budżet pozwala na mniej niż 100 zapytań do LLM na jeden krok symulacji (tick), zalecana jest mniejsza populacja (N = 3-5) z intensywnymi interakcjami zamiast dużych grup.
- Jeśli scenariusz nie zyskuje na zjawisku emergencji (jest to ściśle oskryptowane zadanie), zarekomenduj architekturę jednoagentową z narzędziami.

Format wyjściowy: jednostronicowy dokument projektowy (design brief). Rozpocznij od jednozdaniowego podsumowania (np. „Symulacja w stylu Smallville: 15 heterogenicznych agentów, refleksja wyzwalana przy sumie ważności > 120, 3-poziomowy horyzont planowania, siatka przestrzenna z ograniczeniami przepustowości, ewaluacja na podstawie wiarygodności oraz zdarzeń koordynacyjnych”), po którym następuje osiem powyższych sekcji. Na końcu opisz oczekiwane zachowania emergentne oraz trzy najważniejsze tryby błędów, na które należy zwrócić uwagę.
