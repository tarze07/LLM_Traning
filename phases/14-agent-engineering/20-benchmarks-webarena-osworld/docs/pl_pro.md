# Testy porównawcze: WebArena i OSWorld

> WebArena testuje możliwości agentów internetowych (web agents) w czterech samodzielnie hostowanych aplikacjach. OSWorld ocenia zdolności agentów desktopowych (desktop agents) w środowiskach Ubuntu, Windows i macOS. W momencie publikacji tych benchmarków (lata 2023–2024) wykazały one ogromną przepaść między skutecznością najlepszych agentów a wynikami ludzi. Choć dystans ten stopniowo się zmniejsza, główne typy błędów popełnianych przez modele pozostają bez zmian.

**Typ:** Ucz się
**Języki:** Python (stdlib)
**Wymagania wstępne:** Faza 14 · 19 (SWE-bench, GAIA)
**Czas:** ~60 minut

## Cele nauczania

- Opisać cztery samodzielnie hostowane aplikacje wchodzące w skład WebArena i wyjaśnić znaczenie oceny opartej na weryfikacji wykonania (execution-based evaluation).
- Wyjaśnić, dlaczego OSWorld wykorzystuje zrzuty ekranu rzeczywistego systemu operacyjnego zamiast opierać się na API ułatwień dostępu (accessibility APIs).
- Wymienić dwa główne powody niepowodzeń w OSWorld: uziemienie interfejsu graficznego (GUI grounding) oraz brak wiedzy operacyjnej.
- Podsumować, jakie dodatkowe wartości wnoszą zestawy OSWorld-G oraz OSWorld-Human do podstawowego benchmarku.

## Problem

Agenci ogólnego przeznaczenia potrafią sprawnie wywoływać proste narzędzia. Czy jednak potrafią pokierować przeglądarką wykonując 20 kliknięć, aby dokończyć zakupy? Albo czy potrafią skonfigurować system Linux, korzystając wyłącznie z wirtualnej klawiatury i myszy? Na te właśnie pytania odpowiadają benchmarki WebArena oraz OSWorld.

## Koncepcja

### WebArena (Zhou i in., ICLR 2024)

- Zawiera 812 złożonych zadań realizowanych w czterech samodzielnie hostowanych aplikacjach webowych: sklepie internetowym, forum dyskusyjnym, systemie GitLab (narzędzie deweloperskie) oraz biznesowym systemie zarządzania treścią (CMS).
- Dodatkowe narzędzia pomocnicze: mapa, kalkulator, notatnik.
- Ocena bazuje na weryfikacji stanu końcowego (execution-based) za pomocą API w stylu OpenAI Gym – np. czy zamówienie zostało poprawnie złożone, czy ticket został zamknięty lub czy strona w CMS została zaktualizowana?
- W momencie debiutu: najlepszy agent oparty na GPT-4 osiągnął 14,41% skuteczności, podczas gdy wynik człowieka wynosił 78,24%.

Samodzielne hostowanie infrastruktury ma kluczowe znaczenie – benchmark jest stabilny i odtwarzalny, ponieważ wersje aplikacji docelowych są ściśle zdefiniowane i niezmienne.

### Rozszerzenia

- **VisualWebArena** – zadania o charakterze wizualnym, w których sukces zależy od interpretacji obrazów (gdzie zrzuty ekranu są głównym źródłem informacji).
- **TheAgentCompany** – rozszerza środowisko o dostęp do terminala oraz zadania programistyczne, lepiej odwzorowując realne warunki pracy zdalnej.

### OSWorld (Xie i in., NeurIPS 2024)

- Zawiera 369 rzeczywistych zadań desktopowych w systemach Ubuntu, Windows oraz macOS.
- Pełna kontrola nad wirtualną klawiaturą i myszą w realnych aplikacjach.
- Obserwacja oparta wyłącznie na analizie zrzutów ekranu w rozdzielczości 1920×1080.
- W momencie debiutu: najlepszy model osiągnął 12,24% skuteczności, podczas gdy człowiek uzyskał 72,36%.

### Główne przyczyny błędów (Tryby awarii)

1. **Uziemienie GUI (GUI Grounding).** Tłumaczenie współrzędnych pikseli na konkretne elementy interfejsu. Modele często mają trudności z precyzyjnym lokalizowaniem przycisków czy pól tekstowych na ekranie o rozdzielczości 1920×1080.
2. **Wiedza operacyjna (Operational Knowledge).** Znajomość struktury systemu (np. w którym menu znajdują się dane opcje, jakie skróty klawiszowe zastosować, jak nawigować po panelu sterowania). Jest to specyficzna wiedza domenowa, którą ludzie zdobywają latami.

### Rozszerzenia benchmarku

- **OSWorld-G** – zestaw zawierający 564 próbek testowych skupiających się wyłącznie na uziemieniu graficznym GUI, co pozwala oddzielić problem precyzji lokalizacji od planowania działań.
- **OSWorld-Human** – baza optymalnych ścieżek postępowania (tzw. złotych trajektorii). Wykazała ona, że nawet skuteczni agenci wykonują średnio od 1,4 do 2,7 raza więcej kroków niż człowiek (luka efektywności).

### Dlaczego ma to kluczowe znaczenie

Wspomniane funkcje sterowania komputerem (Claude Computer Use, OpenAI Computer Using Agent, Gemini Computer Use - Lekcja 21) są trenowane na zadaniach ustrukturyzowanych analogicznie do WebArena i OSWorld. Te benchmarki wyznaczają cele rozwoju modeli nowej generacji.

### Słabe punkty w obecnej metodologii

- **Ignorowanie formy danych wejściowych.** OSWorld opiera się na czystej analizie obrazu (zrzutów ekranu). Ocenianie w tym samym rankingu agentów, którzy mają bezpośredni dostęp do drzewa DOM lub API ułatwień dostępu, zniekształca wyniki, omijając kluczowy problem uziemienia wizualnego.
- **Pomijanie długości ścieżki (trajektorii).** Skupienie się wyłącznie na ostatecznym sukcesie (success rate) maskuje ogromną nieefektywność agentów (wykonujących o 1,4-2,7x więcej ruchów niż człowiek).
- **Ryzyko dezaktualizacji środowisk.** Samodzielnie hostowane aplikacje w WebArena wymagają konkretnych wersji oprogramowania; każda niezarejestrowana aktualizacja systemu uniemożliwia rzetelne porównanie wyników.

## Przykład implementacji

Plik `code/main.py` zawiera uproszczone środowisko testowe dla agenta przeglądarkowego:

- Zaimplementowano uproszczoną maszynę stanów imitującą sklep internetowy (`list_items`, `add_to_cart`, `checkout`).
- Przygotowano optymalne ścieżki wykonania (złote trajektorie) dla 3 scenariuszy.
- Stworzono skryptowanego agenta realizującego te zadania.
- Wdrożono ewaluację opartą na stanie końcowym oraz analizę efektywności ścieżki (liczba wykonanych kroków w odniesieniu do trajektorii optymalnej).

Uruchomienie:

```
python3 code/main.py
```

Dane wyjściowe przedstawiają współczynnik sukcesu dla każdego zadania oraz efektywność trajektorii, obrazując metodologię stosowaną w OSWorld-Human.

## Podsumowanie zastosowań

- **WebArena** uruchomiona lokalnie/w chmurze na potrzeby ciągłej weryfikacji agentów webowych.
- **OSWorld** działający na dedykowanej flocie maszyn wirtualnych do oceny agentów desktopowych.
- **Agenci sterujący systemem (Computer Use)** (Lekcja 21) – wiodące modele od Anthropic, OpenAI czy Google są trenowane pod kątem takich właśnie scenariuszy.
- **Własne scenariusze testowe** – zdefiniuj i utrwal złote trajektorie dla 20 kluczowych operacji w swoim systemie i regularnie uruchamiaj na nich testy regresyjne.

## Zadanie wdrożeniowe

Plik `outputs/skill-web-desktop-harness.md` opisuje proces tworzenia środowiska testowego dla agentów webowych i desktopowych, mierzącego poprawność wykonania zadań oraz efektywność ich ścieżek.

## Ćwiczenia praktyczne

1. Rozbuduj uproszczone środowisko testowe o nową aplikację (np. forum dyskusyjne). Zdefiniuj dla niej 3 zadania i optymalne ścieżki ich wykonania.
2. Wygeneruj szczegółowe raporty efektywności ścieżki. Sprawdź, czy Twój agent wykonuje 1x, 2x, czy może 3x więcej kroków niż wynosi minimum.
3. Wprowadź do interfejsu elementy odwracające uwagę (distractors), które nie występują w optymalnej ścieżce. Przetestuj, czy agent da się zmylić.
4. Przeanalizuj założenia projektu OSWorld-G. W czym sposób oddzieliłbyś błędy wynikające z niedokładnej lokalizacji elementów (GUI grounding) od błędów w planowaniu logicznym?
5. Zapoznaj się z plikiem README projektu WebArena. Jakie konsekwencje niesie za sobą samodzielna aktualizacja bibliotek lub wersji jednej z przypiętych aplikacji?

## Kluczowe terminy

| Termin | Potoczne określenie | Co to dokładnie oznacza |
|------|----------------|--------------------------------------|
| WebArena | „Benchmark agentów internetowych” | Zestaw 812 zadań w 4 samodzielnie hostowanych aplikacjach webowych; ocena stanu środowiska (Gym API) |
| VisualWebArena | „Wizualna WebArena” | Wersja WebArena opierająca się na analizie graficznej (zrzutach ekranu) |
| OSWorld | „Benchmark agentów desktopowych” | Zestaw 369 zadań realizowanych na rzeczywistych systemach operacyjnych (Ubuntu/Windows/macOS) |
| Uziemienie GUI | „Pozycjonowanie elementów GUI” | Zdolność modelu do precyzyjnego odnajdywania współrzędnych elementów na ekranie o rozdzielczości 1920x1080 |
| Wiedza operacyjna | „Znajomość systemu operacyjnego” | Intuicyjna wiedza o rozmieszczeniu opcji w systemie, skrótach klawiszowych i zachowaniu aplikacji |
| OSWorld-G | „Zestaw do oceny uziemienia” | Wydzielony podzbiór 564 zadań skupiających się wyłącznie na precyzji lokalizacji elementów graficznych |
| OSWorld-Human | „Złote trajektorie” | Zbiór optymalnych, ręcznie zarejestrowanych przez ludzi ścieżek wykonania zadań |
| Efektywność trajektorii | „Stosunek liczby kroków” | Liczba kroków wykonana przez agenta podzielona przez minimalną liczbę kroków wykonaną przez człowieka |

## Dalsze czytanie

- [Zhou i in., WebArena (arXiv:2307.13854)](https://arxiv.org/abs/2307.13854) — test sieciowy czterech aplikacji
- [Xie i in., OSWorld (arXiv:2404.07972)](https://arxiv.org/abs/2404.07972) — test porównawczy komputerów stacjonarnych z różnymi systemami operacyjnymi
- [Wprowadzenie do funkcji Computer Use (Anthropic)](https://www.anthropic.com/news/3-5-models-and-computer-use) — możliwości Claude’a w kształcie wzorca
- [Agent korzystający z komputera (OpenAI)](https://openai.com/index/computer-using-agent/) — numery OSWorld i WebArena
