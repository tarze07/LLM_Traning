# Batch API — 50% zniżki jako standard branżowy

> Każdy większy dostawca dostarcza asynchroniczne API wsadowe z 50% rabatem i czasem realizacji w ciągu ~24 godzin. OpenAI, Anthropic, Google i większość platform wnioskowania (warstwa wsadowa Fireworks, wsadowa Together) implementują ten sam wzorzec. Wsadowe stosy z natychmiastowym buforowaniem i potokami nocnymi spadają do ~10% kosztu synchronicznego braku pamięci podręcznej. Zasada jest brutalnie prosta: jeśli coś nie jest interaktywne, to należy do partii. Potoki generowania treści, klasyfikacja dokumentów, ekstrakcja danych, generowanie raportów, etykietowanie zbiorcze, tagowanie katalogów — wszystko, co toleruje 24-godzinne opóźnienia, to pieniądze pozostawione na stole do czasu przejścia do partii. Wzorzec produkcyjny na rok 2026 polega na segregowaniu każdego nowego obciążenia LLM na trzy ścieżki: interaktywny (synchroniczny z buforowaniem), półinteraktywny (kolejka asynchroniczna z rezerwą), wsadowy (noc, buforowane dane wejściowe ułożone stosowo). Najbardziej marnują się obciążenia udające interaktywne, ale tolerujące minuty opóźnień.

**Typ:** Ucz się
**Języki:** Python (stdlib, symulator kosztów wsadowych zabawek i synchronizacji)
**Wymagania wstępne:** Faza 17 · 14 (buforowanie natychmiastowe i semantyczne)
**Czas:** ~45 minut

## Cele nauczania

- Wymień trzy interfejsy API wsadowe dostawców (OpenAI, Anthropic, Google) i typowe 50% zniżki + 24-godzinne gwarancje realizacji.
— Oblicz koszt układania danych wsadowych i danych wejściowych z pamięci podręcznej w przypadku nocnego obciążenia klasyfikacyjnego i porównaj z wartością bazową synchroniczną i bez pamięci podręcznej.
- Podziel obciążenie na interaktywne / półinteraktywne / wsadowe i uzasadnij pas.
- Nazwij dwie pułapki: częściowa interaktywność (użytkownik oczekuje, że będzie to szybciej niż 24 godziny) i dryf schematu wyjściowego (format pliku wsadowego różni się w zależności od dostawcy).

## Problem

Twój zespół dostarcza potok generowania raportów co wieczór. 50 000 dokumentów, podsumuj każdy, zgrupuj streszczenia, przygotuj brief wykonawczy. Synchroniczne działanie zajmuje 4 godziny przy cenie 2000 USD za noc. Słyszeliście o interfejsach API wsadowych.

W ramach partii otrzymasz rabat 50%. Włączasz także buforowanie podpowiedzi w wierszu poleceń systemowych (wspólne dla wszystkich wywołań 50 tys.). Po nałożeniu rachunek spada do 180 USD za noc — ~9% kwoty bazowej. Ten sam potok, trzy zmiany konfiguracji.

Batch to najtańsza dźwignia w zestawie narzędzi kosztowych LLM, z której nikt nie korzysta. Powód jest głównie organizacyjny: zespoły myślą „w czasie rzeczywistym”, podczas gdy umowa SLA w rzeczywistości jest „do rana”. Ta lekcja dotyczy tego, aby nie zostawiać 90% rachunku na stole.

## Koncepcja

### Trzy wsadowe interfejsy API

**OpenAI Batch API**: przesyłanie pliku JSONL z listą żądań. Obiecano czas realizacji w ciągu 24 godzin (zwykle w praktyce ~2-8 godzin). 50% zniżki na tokeny wejściowe i wyjściowe. `/v1/batches` punkt końcowy. Dane wejściowe kwalifikujące się do pamięci podręcznej również otrzymują wyższą cenę za dane wejściowe z pamięci podręcznej.

**Partie wiadomości antropicznych**: przesyłanie w formacie JSONL. Realizacja w ciągu 24 godzin. 50% zniżki. Obsługuje `cache_control` — zapisy w pamięci podręcznej są jawne, odczyty odbywają się automatycznie w ramach partii.

**Przewidywanie zbiorcze Google Vertex AI**: dane wejściowe BigQuery lub GCS. Podobny rabat 50% dla Gemini. Integruje się z rurociągami Vertex.

### Semantyczny: asynchroniczny, nie wolny

Partia brzmi „Obiecuję wrócić w ciągu 24 godzin”, a nie „To zajmie 24 godziny”. Typowy P50 wynosi 2-6 godzin. Dostawca planuje Twoją partię w okresach pozaszczytowych, gdy zasoby GPU nie są w pełni wykorzystywane.

### Stos z buforowaniem

Podsumowanie 50 tys. dokumentów z tym samym monitem systemowym dotyczącym 4 tys. tokenów:

- Synchroniczne bez pamięci podręcznej: 50000 × ($input × 4000 + $wyjście × 200) przy pełnej szybkości.
- Synchroniczna pamięć podręczna: monit systemowy buforowany po pierwszym zapisie; pozostałe 49999 otrzymasz 10 razy tańsze dane wejściowe.
- Bufor zbiorczy: wszystkie powyższe plus 50% zniżki na odczyt i zapis.

Stos: partia + pamięć podręczna = ~10% rachunku niezbuforowanego w synchronizacji. Każde obciążenie, które działa w nocy i ma udostępniony monit systemowy, powinno z tego korzystać.

### Selekcja obciążenia

**Interaktywny** — użytkownik czeka na odpowiedź. TTFT ma znaczenie. Wywołanie synchroniczne z szybkim buforowaniem. Nie można wsadowo.

**Półinteraktywny** — użytkownik przesyła zadanie, sprawdza je ponownie w ciągu kilku minut. Kolejka asynchroniczna z rezerwą do synchronizacji, jeśli partia nie jest dostępna. Pomyśl o indeksowaniu RAG o średniej wielkości.

**Pakiet** — użytkownik oczekuje wyników „do rana” lub „w następnej godzinie”. Potoki treści, klasyfikacja na dużą skalę, analiza offline. Zawsze wsadowo, zawsze buforując stos.

Częsty błąd: klasyfikowanie wszystkiego jako interaktywnego, ponieważ rurociąg to produkcja. Produkcja nie jest specyfikacją opóźnień — jest to umowa SLA.

### Pułapka częściowej interaktywności

Niektóre funkcje wyglądają na interaktywne, ale tolerują 5–10 minut. Przykład: nocny raport o stanie klienta z przyciskiem „odśwież”. Odśwież kliknięcia użytkownika; poczekaj 10 minut, będzie dobrze. Zespół dostarcza go jako synchroniczny. 50 równoczesnych odświeżeń kosztuje 10 razy tyle, ile kosztowałoby przetwarzanie zbiorcze i dostarczane pocztą elektroniczną.

Pytanie, które należy zadać: „Co oznacza 24 godziny na dobę dla tego użytkownika?” Jeśli odpowiedź brzmi „nie zauważyliby”, podziel to na partię.

### Pułapka schematu wyjściowego

Formaty plików wsadowych różnią się w zależności od dostawcy:

- OpenAI: JSONL, jedno żądanie w linii.
- Antropiczne: JSONL, jedna wiadomość w wierszu; osadzony format odpowiedzi.
- Wierzchołek: tabela BigQuery lub prefiks GCS z TFRecord.

Zapisanie „jednego klienta wsadowego” u różnych dostawców oznacza kod adaptera dla każdego dostawcy. Bramy reklamujące partię wielu dostawców (Portkey, LiteLLM na niektórych poziomach) nadal słabo owijają surowy format.

### Liczby, które powinieneś zapamiętać

- Rabat zbiorczy u dostawców: 50% ryczałtu na wejściu i wyjściu.
- SLA realizacji: gwarantowane 24 godziny, typowo 2-6 godzin P50.
- Partia skumulowana + dane wejściowe z pamięci podręcznej: ~10% kosztu synchronizacji bez pamięci podręcznej.
- Zasada segregacji obciążenia: jeśli akceptowalne jest 24-godzinne opóźnienie, zawsze wsadowo.

## Użyj tego

`code/main.py` oblicza koszty synchronizacji, synchronizacji+pamięci podręcznej, wsadu i wsadu+pamięci podręcznej dla obciążenia 50 tys. dokumentów. Raportuje oszczędności w dolarach i procentach.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-batch-triager.md`. Biorąc pod uwagę charakterystykę obciążenia, dokonuje się podziału na interaktywne/pół/wsadowe i szacuje oszczędności.

## Ćwiczenia

1. Uruchom `code/main.py`. W przypadku potoku o wielkości 100 tys. dokumentów z monitem systemowym o wielkości 3 tys. tokenów i danymi wyjściowymi o wielkości 500 tokenów oblicz oszczędności wynikające z pełnego stosu (partia + pamięć podręczna) w porównaniu z wartością bazową synchronizacji.
2. Wybierz trzy funkcje prawdziwego produktu, który znasz. Sortuj każdy na interaktywny/pół/wsadowy.
3. Użytkownik skarży się, że jego zgłoszenie zajęło 3 godziny. Czy była to błędna selekcja zbiorcza, czy uzasadniona interakcja? Zapisz kryterium decyzyjne.
4. Umowa SLA dotycząca zwrotu pakietu API wynosi 24 godziny, ale P99 to 20 godzin. Jak przekazać to użytkownikowi — jakie jest zachowanie systemu w przypadku urządzenia brzegowego?
5. Oblicz próg rentowności: przy jakiej długości współdzielonego prefiksu pakiet wsadowy + pamięć podręczna stają się tańsze niż uruchamianie przez noc na własnym, zarezerwowanym procesorze graficznym?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Wsadowe API | „rabat asynchroniczny” | 50% zniżki z czasem realizacji 24h |
| JSONL | „format wsadowy” | Jedno żądanie JSON na linię; Standard OpenAI/Anthropic |
| Partie wiadomości | „Partia antropiczna” | Nazwa produktu wsadowego API firmy Anthropic |
| Przewidywanie partii | „Partia wierzchołków” | Produkt wsadowy API firmy Vertex AI |
| Umowa SLA dotycząca zwrotu | „Obietnica 24h” | Gwarancja, nietypowa; typowy to 2-6h |
| Segregacja obciążenia | „decyzja interaktywna” | Decyzja o routingu interaktywnym / pół / wsadowym |
| Schemat wyjściowy | „format odpowiedzi” | Układ JSONL dla każdego dostawcy; nie przenośny |
| Skumulowany rabat | „partia + pamięć podręczna” | ~10% rachunku za synchronizację w pamięci podręcznej, gdy obowiązują oba |

## Dalsze czytanie

- [OpenAI Batch API](https://platform.openai.com/docs/guides/batch) — format JSONL i semantyka `/v1/batches`.
- [Anthropic Message Batches](https://docs.anthropic.com/en/docs/build-with-claude/batch-processing) — format wsadowy i interakcja `cache_control`.
– [Przewidywanie wsadowe Vertex AI](https://cloud.google.com/vertex-ai/generative-ai/docs/model-reference/batch-prediction) — Semantyka wsadowa Gemini.
- [Finout — ceny OpenAI vs Anthropic API 2026](https://www.finout.io/blog/openai-vs-anthropic-api-pricing-comparison)
– [Zen Van Riel — porównanie kosztów API LLM 2026](https://zenvanriel.com/ai-engineer-blog/llm-api-cost-comparison-2026/)