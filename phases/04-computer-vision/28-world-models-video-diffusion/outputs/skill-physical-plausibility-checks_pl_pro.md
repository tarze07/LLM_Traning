---

name: skill-physical-plausibility-checks
description: Automatyczna weryfikacja spójności fizycznej (trwałość obiektów, grawitacja, płynność ruchu) wygenerowanego wideo przed udostępnieniem
version: 1.0.0
phase: 4
lesson: 28
tags: [video-generation, quality, physics, evaluation]

---

# Weryfikacja spójności fizycznej wideo (Video Physical Plausibility Checks)

Wdrożenie systemów generowania wideo na produkcji wymaga zautomatyzowanych filtrów i barier ochronnych (guardrails). Ręczna weryfikacja nie jest skalowalna, dlatego automatyczne testy fizyczne są niezbędne do wykrywania typowych błędów generacji.

## Kiedy używać

- W systemach generujących wideo na podstawie promptów tekstowych lub graficznych.
- Automatyczna kontrola jakości na wyjściu API do generowania wideo.
- Monitorowanie zmian jakości po dostrojeniu (fine-tuning) lub aktualizacji modelu bazowego.

## Dane wejściowe

- `video`: tensor o kształcie `(T, H, W, 3)` lub ścieżka do pliku wideo MP4.
- Opcjonalnie dane referencyjne: oczekiwana liczba obiektów w scenie, opis początkowy.

## Rodzaje weryfikacji

### 1. Trwałość i ciągłość obiektów (Object Permanence)
Śledź każdą wykrytą instancję na przestrzeni klatek za pomocą SAM 3.1 Object Multiplex. Oznacz przypadek, gdy stabilnie śledzony obiekt znika na okres $\le 3$ klatek, po czym pojawia się ponownie (chwilowa utrata obiektu przez model). Zaklasyfikuj jako krytyczny błąd (hard fail), jeśli obiekt znika w centralnej części kadru; zaklasyfikuj jako ostrzeżenie (soft fail), gdy znika przy krawędziach.

### 2. Płynność ruchu (Motion Smoothness)
Przepływ optyczny (optical flow) między kolejnymi klatkami powinien być ciągły. Nagłe skoki wartości przepływu w pikselach wskazują na efekt teleportacji (nagłego przesunięcia). Wylicz przepływ za pomocą modelu RAFT i oznacz klatki, na których wielkość przepływu dla 99. percentyla przekracza medianę ponad 10-krotnie.

### 3. Grawitacja i stabilność podparcia
Dla obiektów sklasyfikowanych jako ciała stałe (np. jedzenie, kulki, narzędzia) weryfikuj, czy ich pionowa pozycja nie unosi się bez uzasadnionej przyczyny fizycznej (brak kontaktu z innym obiektem). Oznaczaj anomalie polegające na dryfowaniu w górę (brak działania grawitacji), chyba że w pobliżu obiektu wykryto interakcję (np. dłoń chwytającą przedmiot).

### 4. Spójność tożsamości (Identity Consistency)
Dla postaci ludzkich lub animowanych stosuj analizę osadzeń twarzy (face embeddings) w poszczególnych klatkach. W celu zachowania tożsamości podobieństwo cosinusowe powinno utrzymywać się na poziomie $> 0.8$ w 5-klatkowych oknach czasowych. Spadek poniżej tego progu sygnalizuje niepożądaną deformację (metamorfozę) postaci.

### 5. Anatomia dłoni i kończyn
Uruchom model estymacji pozy (lekcja 21). Oznaczaj klatki, w których widoczna dłoń posiada $> 5$ lub $< 4$ palców, długość kończyny ulega nagłemu podwojeniu między klatkami lub kończyny nienaturalnie przecinają geometrię ciała.

### 6. Renderowanie tekstu (jeśli prompt wymagał tekstu)
Jeśli prompt użytkownika zawierał tekst w cudzysłowie, przeprowadź analizę OCR wygenerowanych klatek i oblicz wskaźnik CER (Character Error Rate) względem tekstu wejściowego. Oznacz jako błąd wartości CER $> 20\%$.

## Raport (Wyjście)

```
[plausibility]
  video frames:           <T>
  permanence violations:  <N>
  smoothness violations:  <N>
  gravity violations:     <N>
  identity drift:         <N of 5-frame windows>
  limb anomalies:         <N>
  OCR CER vs requested:   <float>

[verdict]
  ship | hold | reject

[samples for review]
  frame ranges where each failure occurred
```

## Reguły

- Nie odrzucaj nagrania na podstawie pojedynczego testu; wyliczaj skumulowaną ocenę punktową anomalii i kieruj wideo do ręcznej weryfikacji po przekroczeniu globalnego progu.
- Przypisuj najwyższe wagi kar (najsurowsze oceny) dla błędów spójności tożsamości oraz trwałości obiektów — są one najbardziej zauważalne dla odbiorców.
- Rejestruj statystyki błędów w czasie; nagły wzrost liczby anomalii sygnalizuje zazwyczaj degradację po aktualizacji modelu bazowego lub zmianę w dystrybucji promptów użytkowników (prompt drift).
- Nigdy nie usuwaj automatycznie wideo oznaczonych jako wadliwe; zachowaj je w celach debugowania i analizy błędów (post-mortem).
- Dla treści o podwyższonej wrażliwości (wizerunki osób, dzieci, postaci publicznych) wymagaj obowiązkowej weryfikacji manualnej każdego klipu bez względu na wynik automatycznych testów.
