---

name: skill-physical-plausibility-checks
description: Automatyczne sprawdzanie trwałości, grawitacji i ciągłości obiektu w każdym wygenerowanym materiale wideo przed wysyłką
version: 1.0.0
phase: 4
lesson: 28
tags: [video-generation, quality, physics, evaluation]

---

# Kontrole wiarygodności fizycznej

Wdrożenia produkcyjne wygenerowanego wideo wymagają zautomatyzowanych poręczy. Przegląd ręczny nie jest skalowany; kontrole fizyczne wychwytują klasyczne tryby awarii.

## Kiedy używać

- Dowolny produkt generujący wideo na podstawie podpowiedzi tekstowych lub graficznych.
- Automatyzacja kontroli jakości w punkcie końcowym API generowania wideo.
- Monitorowanie zmiany jakości modelu wideo po dostrojeniu lub aktualizacji modelu podstawowego.

## Wejścia

- `video`: tensor `(T, H, W, 3)` lub ścieżka do pliku mp4.
- Opcjonalne informacje referencyjne: oczekiwana liczba obiektów, początkowy opis sceny.

## Kontrole

### 1. Trwałość obiektu
Śledź każde wykrycie w ramkach za pomocą SAM 3.1 Object Multiplex. Oznacz, gdy stabilny utwór zniknie dla <=3 frames and reappears — the model lost the object temporarily. Hard fail when an object disappears near the frame centre (not at an edge); soft fail at edges.

### 2. Motion smoothness
Optical flow between consecutive frames should be mostly continuous. Sudden per-pixel flow spikes indicate teleportation. Compute flow with RAFT; flag frames where the 99th-percentile flow magnitude exceeds the median by a factor > 10.

### 3. Grawitacja / wsparcie
W przypadku obiektów uznanych za stałe (żywność, kulki, narzędzia) sprawdź, czy ich położenie w pionie nie zwiększa się w przypadku braku działania podnoszącego. Flaga dryfuje w górę, chyba że w pobliżu obiektu wykryta zostanie „chwytająca dłoń”.

### 4. Spójność tożsamości
W przypadku osób lub postaci użyj funkcji rozpoznawania twarzy osadzanej w ramkach. Aby zapewnić trwałą tożsamość, podobieństwo cosinusa powinno pozostać > 0,8 w oknach 5-klatkowych. Poniżej progu oznacza, że ​​postać uległa przemianie.

### 5. Dłonie i kończyny
Uruchom estymator pozycji (lekcja 21). Oznacz klatki, w których ręka ma > 5 lub < 4 visible fingers; where an arm length doubles between frames; where limbs intersect the body through a surface.

### 6. Text rendering (if prompt asked for text)
If the user prompt included a string in quotes, OCR the generated frames and compute CER against the requested string. Flag > 20% CER.

## Zgłoś

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

## Zasady

- Nie blokuj na stałe żadnego pojedynczego czeku; sumuj wyniki i przechowuj wideo do sprawdzenia, gdy łączna liczba anomalii przekroczy próg.
- Najwyższe naruszenia związane z dryfowaniem tożsamości i trwałością wagi - użytkownicy zauważają je jako pierwsi.
- Rejestruj współczynniki awaryjności poszczególnych kontroli w czasie; tendencja wzrostowa zwykle oznacza aktualizację modelu podstawowego lub zmianę dystrybucji natychmiastowej.
- Nigdy nie usuwaj oznaczonego filmu; zachowaj go do debugowania modelu i sekcji zwłok.
– W przypadku treści wrażliwych (ludzie, dzieci, osoby publiczne) wymagaj ręcznej weryfikacji każdego filmu niezależnie od wyniku.