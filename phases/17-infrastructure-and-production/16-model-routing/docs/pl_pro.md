# Routing modelowy jako prymitywna metoda redukcji kosztów

> **Przegląd cen z dnia 2026-04.** Poniższe wartości odzwierciedlają stawki dostawców zarejestrowane w momencie publikacji tej lekcji; przed zacytowaniem ich w dalszej części tekstu zweryfikuj je z aktualną dokumentacją.

> Dynamiczny broker analizuje każde zapytanie (typ zadania, liczbę tokenów, podobieństwo osadzeń wektorowych, pewność modelu) i kieruje proste zadania do tańszego modelu, eskalując te skomplikowane do modelu klasy frontier. Metoda ta nazywana jest również kaskadowaniem modeli (model cascading). Studia przypadków z wdrożeń produkcyjnych w USA, Wielkiej Brytanii i UE pokazują redukcję kosztów o 20–60% przy zachowaniu identycznej jakości (ISO-quality); w przypadku systemów SaaS o dużym natężeniu ruchu poprawa wydajności routingu o 30% przekłada się na sześciocyfrowe oszczędności w skali roku. W 2026 roku koszty inferencji LLM spadają średnio 10-krotnie rocznie – cena za milion tokenów klasy GPT-4 spadła z ~$20/M pod koniec 2022 roku do ~$0.40/M w roku 2026. Ten spadek wynika głównie z optymalizacji stosu technologicznego (omówionych w fazie 17 · 04-09), a nie tylko z ulepszeń sprzętowych. Routing pozwala przełożyć te spadki cen bezpośrednio na wyższą marżę biznesową bez ryzyka pogorszenia jakości produktu. Głównym scenariuszem awarii jest dryf modelu tańszego: router kieruje 40% zapytań do słabszego modelu, a jakość odpowiedzi w zadaniach wymagających logicznego rozumowania spada o 3–5%, czego nikt nie wykrywa przez cały kwartał. Rozwiązaniem jest kontrolowanie routingu za pomocą metryk jakościowych online (w czasie rzeczywistym), a nie wyłącznie statycznych testów offline.

**Typ:** Teoria i praktyka
**Języki:** Python (stdlib, uproszczony symulator routera kaskadowego)
**Wymagania wstępne:** Faza 17 · 01 (Zarządzane platformy LLM), faza 17 · 19 (Bramy AI - Gateways)
**Czas:** ~60 minut

## Cele naukowe

- Wyjaśnienie mechanizmu kaskadowania modeli: próba obsługi zapytania przez tańszy model i eskalacja do droższego w przypadku niskiej pewności odpowiedzi.
- Omówienie czterech sygnałów sterujących routingiem (klasyfikacja zadania, długość promptu, podobieństwo osadzeń do znanych trudnych przypadków, pewność odpowiedzi po pierwszej próbie).
- Obliczanie oczekiwanego kosztu hybrydowego przy zakładanym podziale ruchu oraz akceptowalnym poziomie jakości.
- Wskazanie metryk monitorowania dryfu (bramki jakości online) wykrywających degradację działania tańszego modelu.

## Problem

Utrzymanie Twojej aplikacji kosztuje 80 000 USD miesięcznie przy użyciu modelu GPT-5. Analizy wykazują jednak, że aż 70% zapytań użytkowników to proste komendy, takie jak „Która godzina w Paryżu?” czy „Przeredaguj to zdanie”. Lekki model klasy Haiku doskonale poradzi sobie z tymi zadaniami za zaledwie 3% ceny. Pozostałe 30% wymaga zaawansowanego wnioskowania z użyciem GPT-5 – np. pisania kodu, obliczeń matematycznych czy wieloetapowego planowania.

If skierujesz te 70% prostych zapytań do tańszego modelu, a 30% trudnych do droższego, Twój rachunek spadnie o około 65% przy zachowaniu identycznej jakości końcowej. Na tym polega dynamiczny routing. Wyzwanie tkwi w stworzeniu brokera routingu, który nie spowoduje niezauważalnej utraty jakości.

## Koncepcja

### Cztery sygnały routingu

1. **Klasyfikacja zadań**: podział na kategorie takie jak prosty czat, pisanie kodu, matematyka czy analizy. Klasyfikacja może odbywać się za pomocą reguł (regex), miniaturowego modelu LLM (np. klasy Haiku za $0.25/M) lub porównywania osadzeń wektorowych (embeddings). Wynik decyduje o skierowaniu na ścieżkę tanią, zrównoważoną lub zaawansowaną (frontier).
2. **Długość promptu**: zapytania powyżej 4K tokenów często wymagają modeli klasy frontier do utrzymania spójności kontekstu. Krótkie zapytania (<500 tokenów) zazwyczaj radzą sobie świetnie na mniejszych modelach.
3. **Podobieństwo osadzeń do trudnych przypadków (Hard Cases)**: jeśli zapytanie leży blisko (podobieństwo cosinusowe > 0.88) znanych zapytań sprawiających trudność małym modelom, jest natychmiast kierowane do modelu frontier.
4. **Pewność odpowiedzi po pierwszej próbie (Self-Confidence Check)**: zapytanie trafia najpierw do taniego modelu. Jeśli logarytmy prawdopodobieństwa (logprobs) wygenerowanych tokenów wskazują na niską pewność, model zwraca odmowę lub używa wymijających sformułowań – następuje automatyczna próba z modelem klasy frontier. Zwiększa to opóźnienie w percentylu P95 dla około 10% ruchu, ale pozwala zaoszczędzić ponad 50% na pozostałych 90%.

### Trzy wzorce routingu

- **Pre-routing (klasyfikator na wejściu)**: klasyfikuje zapytanie przed wysłaniem ga do jakiegokolwiek LLM. Dodatkowe opóźnienie wynosi zaledwie 5–10 ms – to najszybsza metoda.
- **Kaskadowanie (Cascade)**: zapytanie jest najpierw przetwarzane przez tani model. W razie niskiej pewności następuje eskalacja do modelu zaawansowanego. Średnie opóźnienie to ~1.2x (wykonanie + weryfikacja), a przy eskalacji ~2x. Zapewnia doskonały kompromis jakościowy.
- **Konsylium modeli (Ensemble / Consensus)**: równoległe wysłanie zapytania do taniego i drogiego modelu dla wybranej próbki ruchu i wybór odpowiedzi na podstawie modelu oceniającego (reward model). Najwyższa jakość, ale i najwyższy koszt; stosowany głównie w krytycznych testach A/B.

### Narzędzia i wdrożenie

Dynamiczny routing jest natywnie wspierany przez bramy AI (omówione w fazie 17 · 19). LiteLLM oferuje moduł `router` z obsługą fallbacków i routingu kosztowego. Portkey zawiera funkcje strażników (guardrails) i routingu. Bramka Kong AI Gateway posiada routing wtyczkowy. Platforma OpenRouter udostępnia dedykowane API rekomendacji modeli.

Projekty Open Source i SaaS: RouteLLM (LMSYS), Not Diamond (rozwiązanie komercyjne), Prompt Mule.

### Zmiany cenników LLM

| Klasa modelu | Koniec 2022 r. | 2026 r. | Różnica |
|------------|----------|------|-------|
| Jakość klasy GPT-4 | ~$20/M | ~$0.40/M | 50x taniej |
| Klasa Frontier (GPT-5, Claude 4) | — | ~$3-10/M | Nowy poziom |

Ten spadek cen wynika z optymalizacji infrastrukturalnych – rozwiązania opisane w fazach 17 · 04-09 przełożyły się na tańsze utrzymanie u dostawców. Dynamiczny routing pozwala natychmiast czerpać z tego korzyści w aplikacji, zamiast czekać na ogólne obniżki dla flagowych modeli.

### Ryzyko dryfu (Model Drift)

Załóżmy, że router przekierowuje 40% ruchu do tańszego modelu. W ciągu kilku miesięcy zmienia się charakterystyka zapytań (użytkownicy piszą bardziej złożone i dłuższe prompty). Router tego nie wykrywa, ponieważ jego klasyfikator bazuje na starych danych treningowych. Jakość aplikacji po cichu spada, a spadek o 3-5% w zadaniach logicznych jest trudny do wychwycenia na podstawie prostych logów. Dowiadujesz się o problemie dopiero z benchmarków konkurencji.

Jak monitorować jakość routingu na żywo (Online Quality Gates):

- Analiza ocen użytkowników (kciuk w górę / kciuk w dół) dla każdej ścieżki.
- Automatyczna ocena (LLM-as-a-judge) losowej próby (np. 5%) zapytań z każdej trasy.
- Monitorowanie współczynnika eskalacji: jeśli odsetek eskalacji w kaskadzie wzrasta o >30%, oznacza to konieczność rekalibracji routera.
- Analiza wskaźnika odmów (refusal rate) na poszczególnych ścieżkach.

### Kluczowe statystyki do zapamiętania

- Realne oszczędności dzięki routingowi (ISO-quality) w 2026 r.: 20-60% budżetu inferencji.
- Roczne tempo spadku cen LLM (2022-2026): około 10-krotna obniżka rocznie.
- Koszt klasy GPT-4 (2022 vs 2026): ~$20/M → ~$0.40/M.
- Wpływ kaskadowania na opóźnienia: mediana opóźnienia ~1.2x, przy eskalacji ~2x (dotyczy ok. 10% ruchu).

## Praktyczne zastosowanie

Skrypt `code/main.py` symuluje działanie metod: pre-routingu, kaskady oraz konsylium (ensemble) na zróżnicowanym ruchu zapytań. Generuje raport dotyczący kosztów hybrydowych, zachowania jakości i wskaźników eskalacji.

## Zadanie wdrożeniowe

W ramach tej lekcji przygotowano plik `outputs/skill-router-plan.md`. Narzędzie to analizuje charakterystykę ruchu oraz wymagania jakościowe, dobierając optymalny wzorzec routingu i sygnały sterujące.

## Ćwiczenia

1. Uruchom `code/main.py`. Jak wypada dokładność metody kaskadowej w porównaniu z klasycznym pre-routingiem?
2. Twoja baza użytkowników składa się w 30% z kont Enterprise (skomplikowane zapytania) i w 70% z darmowych kont Free (proste zapytania). Zaprojektuj logikę routingu. Jaka metryka online pozwoli kontrolować ten proces?
3. Wdrożenie routingu obniża jakość zapytań o 2%, ale przynosi 40% oszczędności. Czy warto wdrożyć to na produkcję? Przedstaw argumenty za i przeciw w zależności od typu aplikacji.
4. Zaimplementuj mechanizm oceny pewności modelu (confidence check) za pomocą prawdopodobieństw tokenów (logprobs) z API OpenAI/Anthropic. Od jakiego progu zaczniesz filtrowanie?
5. W ciągu 6 miesięcy wskaźnik eskalacji wzrósł z 8% do 22%. Zdiagnozuj trzy potencjalne przyczyny i zaproponuj rozwiązania dla każdej z nich.

## Słownik pojęć

| Termin | Popularne określenie | Rzeczywiste znaczenie |
|------|----------------|--------------------------------------|
| Model Routing | „broker modeli” | Dynamiczny wybór i przekierowywanie zapytania do optymalnego LLM |
| Model Cascade | „kaskadowanie” | Próba wykonania zadania przez lekki model i eskalacja do klasy frontier przy braku pewności |
| Pre-routing | „klasyfikator wejściowy” | Klasyfikacja i wybór modelu na etapie przyjmowania zapytania, bez ponawiania prób |
| Ensemble Routing | „konsylium modeli” | Równoległe wysłanie zapytania do kilku modeli i wybór najlepszej odpowiedzi na podstawie ocen |
| Współczynnik eskalacji | „escalation rate” | Procentowy udział zapytań, które musiały zostać przekierowane do wyższej klasy modelu w trybie kaskady |
| RouteLLM | „router LMSYS” | Popularna biblioteka open-source do routingu modeli |
| Not Diamond | „komercyjny router SaaS” | Gotowe, komercyjne rozwiązanie chmurowe do dynamicznego routingu LLM |
| Dryf modelu | „model drift” | Niezauważalna zmiana struktury ruchu użytkowników, powodująca spadek skuteczności routera |
| Bramka jakości online | „online quality gate” | Zautomatyzowany sędzia LLM (LLM-as-a-judge) na bieżąco analizujący jakość odpowiedzi produkcyjnych |

## Materiały uzupełniające

- [AbhyashSuchi – Model Routing LLM 2026 Best Practices](https://abhyashsuchi.in/model-routing-llm-2026-best-practices/)
- [Lukas Brunner – Rise of Inference Optimization 2026](https://dev.to/lukas_brunner/the-rise-of-inference-optimization-the-real-llm-infra-trend-shaping-2026-4e4o)
- [Dokumentacja i kod RouteLLM](https://github.com/lm-sys/RouteLLM)
- [Not Diamond – Model Routing Platform](https://www.notdiamond.ai/)
- [OpenRouter](https://openrouter.ai/) – platforma pośrednicząca (API gateway) z funkcjami routingu modeli.
