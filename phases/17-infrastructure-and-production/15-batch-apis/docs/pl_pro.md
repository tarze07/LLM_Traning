# Batch API — 50% zniżki jako standard branżowy

> **Przegląd cen z dnia 2026-04.** Poniższe wartości odzwierciedlają stawki dostawców zarejestrowane w momencie publikacji tej lekcji; przed zacytowaniem ich w dalszej części tekstu zweryfikuj je z aktualną dokumentacją.

> Wszyscy wiodący dostawcy oferują asynchroniczne API wsadowe (Batch API) z 50% rabatem i czasem realizacji do 24 godzin. OpenAI, Anthropic, Google oraz większość platform inferencyjnych (np. Fireworks Batch, Together Batch) stosują ten sam schemat. Połączenie przetwarzania wsadowego z buforowaniem promptów w nocnych potokach danych (nightly pipelines) pozwala obniżyć koszty do zaledwie ~10% ceny synchronicznego przetwarzania bez cache. Zasada jest banalnie prosta: jeśli proces nie wymaga natychmiastowej interakcji z użytkownikiem, powinien być przetwarzany wsadowo. Potoki generowania treści, klasyfikacja dokumentów, ekstrakcja danych, generowanie raportów, masowe etykietowanie czy tagowanie katalogów – wszystko, co może poczekać do 24 godzin, generuje niepotrzebne koszty, jeśli nie jest uruchamiane w trybie wsadowym. Nowoczesny wzorzec architektoniczny polega na dzieleniu każdego nowego zadania LLM na trzy ścieżki: interaktywną (synchroniczna z buforowaniem), półinteraktywną (kolejka asynchroniczna) oraz wsadową (nocne przetwarzanie z buforowaniem). Największe marnotrawstwo budżetu generują zadania, które udają interaktywne, choć w rzeczywistości mogłyby tolerować nawet kilkunastominutowe opóźnienia.

**Typ:** Teoria i praktyka
**Języki:** Python (stdlib, uproszczony symulator porównujący koszty synchronizacji i przetwarzania wsadowego)
**Wymagania wstępne:** Faza 17 · 14 (Buforowanie promptów i buforowanie semantyczne)
**Czas:** ~45 minut

## Cele naukowe

- Omówienie oferty Batch API trzech wiodących dostawców (OpenAI, Anthropic, Google) – w tym 50% rabatu oraz 24-godzinnej gwarancji realizacji (SLA).
- Obliczanie oszczędności wynikających z połączenia przetwarzania wsadowego z buforowaniem promptów dla nocnych zadań klasyfikacyjnych w porównaniu do standardowego przetwarzania synchronicznego bez cache.
- Klasyfikacja zadań na interaktywne, półinteraktywne i wsadowe wraz z uzasadnieniem biznesowym.
- Zidentyfikowanie dwóch kluczowych pułapek: pozornej interaktywności (gdy użytkownik oczekuje wyniku szybciej niż w ciągu doby) oraz różnic w schematach wyjściowych (format plików wsadowych różni się w zależności od dostawcy).

## Problem

Twój zespół uruchamia co wieczór potok generujący raporty. Proces obejmuje 50 000 dokumentów: należy podsumować każdy z nich, zgrupować streszczenia i przygotować raport dla zarządu. Wykonywanie tego synchronicznie zajmuje 4 godziny i kosztuje 2000 USD każdej nocy. Słyszałeś o możliwościach Batch API.

Korzystając z przetwarzania wsadowego, otrzymujesz 50% zniżki na start. Dodatkowo włączasz buforowanie promptu systemowego (który jest wspólny dla wszystkich 50 tys. wywołań). Po połączeniu tych dwóch optymalizacji rachunek spada do zaledwie 180 USD za noc – to zaledwie ~9% kosztu bazowego. Ten sam potok, zaledwie kilka zmian w konfiguracji.

Batch API to najprostsze i najtańsze narzędzie do redukcji kosztów LLM, z którego wciąż korzysta niewiele zespołów. Powód jest zazwyczaj organizacyjny: zespoły projektują systemy z myślą o czasie rzeczywistym, podczas gdy biznesowe SLA wymaga jedynie dostarczenia danych „na rano”. Ta lekcja pokaże Ci, jak nie przepłacać o 90% za zadania, które mogą poczekać.

## Koncepcja

### Oferta Batch API u wiodących dostawców

**OpenAI Batch API**: polega na przesłaniu pliku JSONL zawierającego listę zapytań. Gwarantowany czas realizacji to 24 godziny (w praktyce wynosi on zwykle od 2 do 8 godzin). Oferuje 50% zniżki na tokeny wejściowe i wyjściowe. Obsługiwane przez punkt końcowy `/v1/batches`. Dodatkowo, tokeny kwalifikujące się do prompt cache podlegają standardowym zniżkom za buforowanie.

**Anthropic Message Batches**: przesyłanie zadań w formacie JSONL z tym samym czasem realizacji do 24 godzin i rabatem 50%. W pełni obsługuje parametr `cache_control` – zapisy do pamięci podręcznej są jawne, a odczyty następują automatycznie wewnątrz przetwarzanego pakietu.

**Google Vertex AI Batch Prediction**: obsługuje dane wejściowe bezpośrednio z BigQuery lub Google Cloud Storage (GCS). Zapewnia analogiczny rabat 50% dla modeli z rodziny Gemini. Łatwo integruje się z potokami Vertex Pipelines.

### Specyfika czasu realizacji: Asynchronicznie nie oznacza wolno

Gwarancja SLA na poziomie 24 godzin to maksymalny czas oczekiwania, a nie standardowy czas trwania procesu. Typowa mediana czasu realizacji (P50) wynosi od 2 do 6 godzin. Dostawcy przetwarzają te zadania w momentach mniejszego obciążenia infrastruktury, gdy zasoby GPU nie są w pełni wykorzystywane.

### Łączenie Batch API z Prompt Caching (optymalizacja stosu)

Rozważmy przykład podsumowania 50 000 dokumentów ze wspólnym promptem systemowym o długości 4K tokenów i odpowiedzią 200 tokenów:

- **Synchronicznie bez cache**: 50 000 × ($cena_wejscia × 4000 + $cena_wyjscia × 200) przy pełnej stawce.
- **Synchronicznie z cache**: prompt systemowy jest zapisywany w cache przy pierwszym zapytaniu; dla kolejnych 49 999 zapytań koszt przetwarzania wejścia jest około 10 razy niższy.
- **Wsadowo z cache (Batch + Cache)**: łączymy powyższe buforowanie z dodatkowym 50% rabatem na wszystkie operacje wejścia/wyjścia.

Efekt: Batch + Cache = ~10% kosztu wyjściowego. Każde zadanie uruchamiane okresowo (np. w nocy) ze wspólnym promptem systemowym powinno korzystać z tego stosu.

### Klasyfikacja zadań (Triage)

- **Interaktywne**: Użytkownik czeka na odpowiedź na żywo. Liczy się czas do pierwszego tokena (TTFT). Wymaga wywołań synchronicznych z szybkim buforowaniem. Nie nadaje się do przetwarzania wsadowego.
- **Półinteraktywne**: Użytkownik zleca zadanie i oczekuje wyniku w ciągu kilku minut. Stosuje się tu kolejki asynchroniczne z możliwością przełączenia na tryb synchroniczny w razie braku zasobów. Przykład: generowanie raportu na życzenie dla średniej wielkości dokumentu.
- **Wsadowe (Batch)**: Użytkownik oczekuje wyników „na rano” lub w ciągu kilku godzin. Generowanie treści marketingowych, klasyfikacja danych na dużą skalę, analizy offline. Zawsze przetwarzane wsadowo, najlepiej z wykorzystaniem prompt caching.

Częsty błąd: Klasyfikowanie wszystkich zadań jako interaktywnych tylko dlatego, że działają na produkcji. Produkcja określa krytyczność systemu, a nie dopuszczalne opóźnienia – o tym decyduje umowa SLA.

### Pułapka pozornej interaktywności

Niektóre funkcjonalności wydają się wymagać trybu rzeczywistego, lecz w praktyce tolerują opóźnienie rzędu 5–10 minut. Przykład: raport o statusie klienta z przyciskiem „Odśwież”. Gdy użytkownik kliknie przycisk, kilkuminutowe oczekiwanie jest dla niego w pełni akceptowalne. Zespół programistów wdraża to jednak synchronicznie. W efekcie 50 jednoczesnych kliknięć generuje koszty 10-krotnie wyższe niż gdyby zadania zostały wysłane do kolejki Batch i dostarczone asynchronicznie.

Kluczowe pytanie: „Czy opóźnienie w dostarczeniu danych wpłynie negatywnie na pracę użytkownika?”. Jeśli nie, proces należy przenieść do trybu wsadowego.

### Pułapka różnic w schematach wyjściowych (Output Schema)

Formaty plików wejściowych i wyjściowych dla zadań wsadowych różnią się w zależności od dostawcy API:

- OpenAI: format JSONL, jedno zapytanie na linijkę.
- Anthropic: format JSONL, zagnieżdżona struktura wiadomości w każdej linii.
- Vertex AI: tabele BigQuery lub pliki na Google Cloud Storage (np. format TFRecord).

Napisanie uniwersalnego kodu obsługującego przetwarzanie wsadowe u wielu dostawców wymaga stworzenia warstwy abstrakcji (adaptera) dla każdego z nich. Zewnętrzne bramy API (AI Gateways, takie jak Portkey czy LiteLLM) wciąż mają ograniczone możliwości ujednolicania tych struktur w trybie asynchronicznym.

### Kluczowe statystyki do zapamiętania

- Rabat w ramach Batch API: stałe 50% zniżki na tokeny wejściowe i wyjściowe.
- Czas realizacji (SLA): gwarantowane 24 godziny, w praktyce zwykle 2–6 godzin (mediana P50).
- Skumulowana optymalizacja (Batch + Prompt Cache): ~10% kosztu wariantu synchronicznego bez cache.
- Złota zasada: jeśli biznes akceptuje 24-godzinny czas dostarczenia danych, zawsze stosuj przetwarzanie wsadowe.

## Praktyczne zastosowanie

Skrypt `code/main.py` oblicza koszty dla wariantu synchronicznego, synchronicznego z buforowaniem, wsadowego oraz wsadowego z buforowaniem dla wolumenu 50 tys. dokumentów. Wyniki prezentowane są kwotowo i procentowo.

## Zadanie wdrożeniowe

W ramach tej lekcji przygotowano plik `outputs/skill-batch-triager.md`. Narzędzie to analizuje charakterystykę zadań, dokonuje klasyfikacji na tryby: interaktywny / półinteraktywny / wsadowy i szacuje potencjalne oszczędności.

## Ćwiczenia

1. Uruchom `code/main.py`. Dla potoku przetwarzającego 100 tys. dokumentów ze wspólnym promptem systemowym o rozmiarze 3K tokenów i odpowiedzią 500 tokenów, oblicz oszczędności wynikające z zastosowania pełnego stosu (Batch + Cache) w porównaniu do klasycznej synchronizacji.
2. Wybierz trzy rzeczywiste funkcjonalności z dowolnego systemu. Przydziel je do odpowiednich kategorii: interaktywna, półinteraktywna, wsadowa.
3. Klient zgłasza reklamację, że wygenerowanie raportu zajęło 3 godziny. Czy była to błędna klasyfikacja zadania do trybu wsadowego, czy też w pełni uzasadnione zachowanie systemu? Zaproponuj kryteria oceny takiego przypadku.
4. Gwarantowany czas realizacji (SLA) dla Batch API wynosi 24 godziny, ale percentyl P99 wynosi 20 godzin. Jak należy zakomunikować to użytkownikowi w interfejsie i jak system powinien obsłużyć sytuacje skrajne (edge cases)?
5. Oblicz próg opłacalności: przy jakiej długości współdzielonego prefiksu promptu stos Batch + Cache staje się tańsze niż utrzymywanie własnej, dedykowanej instancji GPU przez całą noc?

## Słownik pojęć

| Termin | Popularne określenie | Rzeczywiste znaczenie |
|------|----------------|--------------------------------------|
| Batch API | „asynchroniczny LLM” | Dostęp do modeli z 50% zniżką przy czasie realizacji do 24 godzin |
| JSONL | „format wsadowy” | Format pliku wejściowego, gdzie każda linia to pojedynczy obiekt JSON (standard OpenAI/Anthropic) |
| Message Batches | „wsad w Anthropic” | Nazwa usługi przetwarzania wsadowego w API Anthropic |
| Batch Prediction | „wsad w Vertex” | Usługa asynchronicznej inferencji w Google Cloud / Vertex AI |
| SLA realizacji | „okno 24-godzinne” | Gwarancja maksymalnego czasu zwrotu wyników, choć zwykle wynosi on 2–6 godzin |
| Klasyfikacja zadań (Triage) | „routing obciążenia” | Podział zadań na interaktywne, półinteraktywne i wsadowe |
| Schemat wyjściowy (Output Schema) | „format odpowiedzi” | Struktura odpowiedzi JSONL; specyficzna dla każdego dostawcy i nieprzenośna bezpośrednio |
| Skumulowany rabat | „Batch + Cache” | Obniżenie kosztów do ~10% ceny bazowej przy jednoczesnym zastosowaniu obu metod |

## Materiały uzupełniające

- [OpenAI Batch API](https://platform.openai.com/docs/guides/batch) – specyfikacja formatu JSONL i obsługa punktu końcowego `/v1/batches`.
- [Anthropic Message Batches](https://docs.anthropic.com/en/docs/build-with-claude/batch-processing) – szczegóły asynchronicznego API oraz integracja z `cache_control`.
- [Vertex AI Batch Prediction](https://cloud.google.com/vertex-ai/generative-ai/docs/model-reference/batch-prediction) – dokumentacja przetwarzania wsadowego modeli Gemini w chmurze Google.
- [Finout – OpenAI vs Anthropic API pricing comparison](https://www.finout.io/blog/openai-vs-anthropic-api-pricing-comparison)
- [Zen Van Riel – LLM API cost comparison](https://zenvanriel.com/ai-engineer-blog/llm-api-cost-comparison-2026/)
