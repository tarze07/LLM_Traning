# FinOps dla LLM — ekonomia jednostek i atrybucja wielu najemców

> Tradycyjne przerwy FinOps na wydatki LLM. Koszty dotyczą transakcji tokenowych, a nie czasu sprawności zasobów. Tagi nie są mapowane — wywołanie API to transakcja, a nie zasób. Decyzje inżynieryjne (szybki projekt, okno kontekstowe, długość wydruku) są decyzjami finansowymi. Podręcznik na rok 2026 ma trzy wymiary atrybucji do instrumentu już pierwszego dnia: na użytkownika (`user_id`) w przypadku cen stanowisk i ekspansji, na zadanie (`task_id` + `route`) w przypadku kosztów powierzchni produktu i ustalania priorytetów, na dzierżawcę (`tenant_id`) w zakresie ekonomii jednostek i odnawiania. Cztery warstwy tokenów – monit, narzędzie, pamięć, odpowiedź – jeden segment ukrywa wydatki. Drabina egzekwowania w przypadku produktów z wieloma dzierżawcami: limity stawek na dzierżawcę (oczekiwany szczyt 2-3x, wyczyść 429 + ponowna próba po); dzienny limit wydatków (1,5-3x zakontraktowany pułap; powoduje zaostrzenie stóp procentowych + alarm); przełączniki zabijania przy wydawaniu wyniku Z > 4 (automatyczna pauza + strona w trakcie połączenia). Wzorce atrybucji: tagi i agregaty, łączniki telemetryczne (identyfikator śledzenia → fakturowanie; najwyższa dokładność), próbkowanie i ekstrapolacja, alokacja oparta na modelu, źródła zdarzeń, przesyłanie strumieniowe w czasie rzeczywistym. Metryka jednostkowa: koszt rozwiązanego zapytania, koszt wygenerowanego artefaktu — nie tokenów $/M. Tagowanie wsteczne zawsze chybia; instrument na żądanie utworzenia.

**Typ:** Ucz się
**Języki:** Python (stdlib, symulator atrybucji kosztów zabawek z wyłącznikiem awaryjnym)
**Wymagania wstępne:** Faza 17 · 13 (obserwowalność), faza 17 · 14 (buforowanie)
**Czas:** ~60 minut

## Cele nauczania

- Wyjaśnij, dlaczego tradycyjne FinOps (tagi + poziomy) psują się w wydatkach na LLM i podaj trzy nowe wymiary atrybucji.
- Wymień cztery warstwy tokenów (podpowiedź, narzędzie, pamięć, odpowiedź) i dlaczego rozliczenia z jednym segmentem ukrywają koszty.
- Zaprojektuj drabinę egzekwowania (stawka → limit wydatków → wyłącznik awaryjny) dla produktu dla wielu dzierżawców.
- Wybierz metrykę jednostkową (koszt rozwiązanego zapytania/artefaktu) zamiast tokenów $/M.

## Problem

Twój rachunek mówi o 40 000 dolarów. Nie wiesz:
- Który najemca je wydał.
- Jaka cecha produktu to spowodowała.
- Czy jakikolwiek indywidualny użytkownik dopuścił się nadużycia.
- Czy winowajcą było szybkie wzdęcie, wywołanie narzędzi lub wzmocnienie pamięci.

Tagowanie i agregowanie po stronie dostawcy działa w przypadku zasobów w chmurze (EC2, S3), gdzie tagi są propagowane do elementów zamówienia. Wywołania API LLM nie są automatycznie tagowane — musisz oznaczyć użytkownika/zadanie/najemcę w witrynie wywołania i przeprowadzić je. Atrybucja wsteczna zawsze pomija przypadki skrajne.

## Koncepcja

### Trzy wymiary atrybucji

**Na użytkownika** (`user_id`): kto ile kosztuje. Kieruje cenami stanowisk, prowadzi rozmowy dotyczące rozszerzenia, identyfikuje zaawansowanych użytkowników.

**Za zadanie** (`task_id` + `route`): jaka powierzchnia produktu kosztuje. Napędy umożliwiają ustalanie priorytetów i podejmowanie decyzji o kosztownych funkcjach.

**Na najemcę** (`tenant_id`): który klient przynosi zyski. Wpływa na ekonomię jednostek, ceny odnowień i progi poziomów.

Oprzyj wszystkie trzy elementy na miejscu wezwania pierwszego dnia. Retroaktywność jest zawsze gorsza.

### Cztery warstwy tokenów

| Warstwa | Przykład | Typowy% całości |
|-------|---------|-------------------------|
| Podpowiedź | system + dane wejściowe użytkownika | 40-60% |
| Narzędzie | wyniki wywołań narzędzi z informacją zwrotną | 20-40% (obciążenie agentów) |
| Pamięć | wcześniejsza rozmowa / odzyskane dokumenty | 10-30% |
| Odpowiedź | wyjście modelu | 10-30% |

Łączenie wszystkich czterech razem sprawia, że ​​optymalizacja jest ślepa. Rozdziel je w swoim schemacie atrybucji.

### Drabina egzekwowania

1. **Limit stawek** na najemcę. 2-3x oczekiwany szczyt. Zwróć 429 z `Retry-After`. Najemca widzi tarcia; bez niespodzianki w rachunku.

2. **Dzienny limit wydatków** na najemcę. Sufit zakontraktowany 1,5-3x. Wyzwalacz: zaostrzenie limitu stawki + powiadomienie o sukcesie klienta.

3. **Wyłącznik awaryjny** przy wydatkach Z-score > 4 w stosunku do wartości bazowej najemcy. Automatyczne wstrzymywanie najemcy; strona na wezwanie; eskaluj do ops + CS.

### Wzorce atrybucji

- **Znacznik i agregacja**: nagłówki metadanych stempla; agregować później. Prosty; surowy.
- **Łącznik telemetryczny**: dołącz ślady do rozliczeń za pomocą identyfikatorów śledzenia. Najwyższa dokładność. Co robią dojrzałe zespoły.
- **Pobieranie próbek + ekstrapolacja**: próbka 5-10%, pomnożyć. Opłacalne w przypadku trudnych wydatków; brakuje ogonów.
- **Alokacja oparta na modelu**: regresja w celu wywnioskowania czynnika kosztowego. W przypadku starszych danych bez tagów.
- **Źródło zdarzenia**: koszt jako zdarzenia w strumieniu (Kafka / Kinesis). W czasie rzeczywistym.
- **Przesyłanie strumieniowe w czasie rzeczywistym**: aktualizacja panelu w ciągu sekundy.

### Koszt na X to metryka jednostkowa

Tokeny $/M to kwestia dostawcy. Dane produktu:

- Koszt za rozwiązane zgłoszenie pomocy technicznej.
- Koszt wygenerowanego artykułu.
- Koszt za pomyślnie zakończone zadanie agenta.
- Koszt za minutę sesji użytkownika.

Powiąż koszt z wynikiem produktu. W przeciwnym razie optymalizacja nie będzie zakotwiczona.

### Kształt śledzenia przypisania kosztów

```
trace_id: abc123
  user_id: u_42
  tenant_id: t_7
  task_id: task_classify_doc
  route: model_haiku
  layers:
    prompt_tokens: 1800
    tool_tokens: 600
    memory_tokens: 400
    response_tokens: 150
  cost_usd: 0.0135
  cached_input: true
  batch: false
```

Emituj przy każdym połączeniu. Przechowuj w jeziorze danych. Łącznie według wymiaru. Stos obserwowalności fazy 17 · 13 jest miejscem, w którym to się znajduje.

### Stos oszczędności złożonych

Stos: pamięć podręczna + partia + trasa + brama. Z całą czwórką:
- Pamięć podręczna L2 (faza 17 · 14): ~10x tańsze wejście.
- Partia (faza 17 · 15): 50% zniżki.
- Droga do taniego modelu (faza 17 · 16): 60% redukcji kosztów.
- Wydajność bramki (faza 17 · 19): redundancja + ponowne próby.

Najlepszy przypadek skumulowany: ~5-10% naiwnej wartości bazowej. Większość zespołów ma włączone 2-3 dźwignie; kilka stosów wszystkie cztery.

### Liczby, które powinieneś zapamiętać

- Wymiary atrybucji: na użytkownika, na zadanie, na najemcę.
- Cztery warstwy tokenów: zachęta, narzędzie, pamięć, odpowiedź.
- Przełącznik zabijania: wydaj Z-score > 4.
- Metryka jednostkowa: koszt rozwiązanego zapytania, a nie tokenów $/M.
- Optymalizacje skumulowane: możliwe ~5-10% wartości bazowej.

## Użyj tego

`code/main.py` symuluje usługę LLM dla wielu dzierżawców z trójstopniową drabiną egzekwowania. Wstrzykuje agresywnego najemcę i demonstruje uruchomienie wyłącznika awaryjnego.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-finops-plan.md`. Biorąc pod uwagę produkt i skalę, projektuje schemat atrybucji i drabinę egzekwowania.

## Ćwiczenia

1. Uruchom `code/main.py`. Przy jakim wyniku Z uruchamia się wyłącznik awaryjny? Jak wybrać próg?
2. Zaprojektuj panel kosztów dla poszczególnych najemców i zadań. Jakich 5 widoków tworzysz jako pierwsze?
3. Twój największy najemca ma ujemną ekonomikę jednostkową. Zaproponuj trzy interwencje uporządkowane według wpływu na klienta.
4. Oblicz koszt rozwiązanego zgłoszenia dla produktu wsparcia: 3M tokenów/bilet, ~800 biletów/dzień, stawka za buforowanie GPT-5.
5. Przedyskutuj, czy tagowanie z mocą wsteczną może w ogóle zadziałać. Kiedy jest to dopuszczalne?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Atrybucja według użytkownika | „koszt na poziomie użytkownika” | `user_id` stemplowany przy każdym połączeniu |
| Atrybucja według zadania | „koszt funkcji” | `task_id` + `route` identyfikacja powierzchni produktu |
| Przypisanie według najemcy | „koszt klienta” | `tenant_id`; napędza ekonomię jednostki |
| Cztery warstwy żetonów | „warstwy kosztów” | zachęta + narzędzie + pamięć + odpowiedź |
| Limit stawki | „Strażnik 429” | Limit przypadający na jednego najemcę egzekwowany na bramce |
| Dzienny limit wydatków | „pułap dzienny” | Budżet ograniczony do najemcy z alertem |
| Przełącznik zabijania | "automatyczna pauza" | Wydaj wynik Z > 4, aby uruchomić automatyczne zawieszenie |
| Koszt rozwiązania | „metryka jednostki produktu” | Koszt powiązany z wynikiem produktu, a nie z tokenami |
| Łącznik telemetryczny | „śledzenie płatności” | Wzór atrybucji o najwyższej dokładności |
| Ułożona optymalizacja | „pamięć podręczna+partia+trasa+brama” | Łączne oszczędności do ~5-10% wartości bazowej |

## Dalsze czytanie

– [Fundacja FinOps — przegląd FinOps for AI](https://www.finops.org/wg/finops-for-ai-overview/)
– [Szkoła FinOps — przewodnik dotyczący kosztów jednostkowych na rok 2026](https://finopsschool.com/blog/cost-per-unit/)
– [Digital Applied – przypisanie kosztów agenta LLM 2026](https://www.digitalapplied.com/blog/llm-agent-cost-attribution-guide-production-2026)
— [PointFive — zarządzane LLM w Azure OpenAI](https://www.pointfive.co/blog/finops-for-ai-economics-of-managed-llms-in-azure-open-ai)