# Obserwowalność agentów: Langfuse, Phoenix, Opik

> W 2026 r. na rynku dominują trzy otwartoźródłowe (open-source) platformy do obserwowalności agentów: Langfuse (licencja MIT) – ponad 6 mln instalacji miesięcznie, oferująca śledzenie (tracing), zarządzanie promptami, ewaluację oraz odtwarzanie sesji; Arize Phoenix (licencja Elastic 2.0) – zapewniająca głęboką ewaluację specyficzną dla agentów, ocenę trafności RAG oraz automatyczną instrumentację OpenInference; oraz Comet Opik (licencja Apache 2.0) – skupiająca się na automatycznej optymalizacji promptów, zabezpieczeniach (guardrails) i wykrywaniu halucynacji przy użyciu LLM jako sędziego.

**Typ:** Ucz się
**Języki:** Python (stdlib)
**Wymagania wstępne:** Faza 14 · 23 (OTel GenAI)
**Czas:** ~45 minut

## Cele nauczania

- Wymień trzy najlepsze platformy open-source do obserwowalności agentów oraz ich licencje.
- Wskaż główne zalety i zastosowania każdej z nich: Langfuse (zarządzanie promptami + sesje), Phoenix (ewaluacja RAG + automatyczna instrumentacja), Opik (optymalizacja promptów + guardrails).
- Wyjaśnij, dlaczego do 2026 roku aż 89% organizacji planuje wdrożyć obserwowalność agentów.
- Zaimplementuj potok śledzenia (tracing pipeline) z ewaluacją LLM przesyłający dane do prostego pulpitu nawigacyjnego opartego na bibliotece standardowej (stdlib).

## Problem

Standard OpenTelemetry (OTel) GenAI (lekcja 23) dostarcza schemat danych. Wciąż jednak potrzebujesz platformy, która zbiera spany (zakresy), przeprowadza ewaluacje, wersjonuje prompty i wizualizuje regresje. Każdy z trzech głównych konkurentów kładzie nacisk na inne etapy cyklu życia aplikacji.

## Koncepcja

### Langfuse (MIT)

- Ponad 6 mln pobrań SDK miesięcznie, ponad 19 tys. gwiazdek na GitHubie.
- Funkcje: śledzenie (tracing), zarządzanie promptami z wersjonowaniem i piaskownicą (playground), ewaluacje (LLM jako sędzia, opinie użytkowników, metryki niestandardowe), odtwarzanie sesji.
- Czerwiec 2025 r.: dotychczasowe moduły komercyjne (LLM-as-a-judge, kolejki adnotacji, eksperymenty z promptami, piaskownica) zostały udostępnione jako open-source na licencji MIT.
- Największe zalety: kompleksowa obserwowalność i ścisła integracja z pętlą zarządzania promptami.

### Arize Phoenix (Elastic License 2.0)

- Zaawansowana ewaluacja specyficzna dla agentów: grupowanie śladów (trace clustering), wykrywanie anomalii, ocena trafności wyszukiwania RAG.
- Natywna, automatyczna instrumentacja OpenInference.
- Możliwość połączenia z zarządzaną platformą Arize AI w środowisku produkcyjnym.
- Brak wersjonowania promptów – narzędzie pozycjonowane jest jako system do analizy dryfu behawioralnego i regresji, działający obok szerszych platform APM.
- Największe zalety: ewaluacja RAG, analiza dryfu behawioralnego, wykrywanie anomalii.

### Comet Opik (Apache 2.0)

- Automatyczna optymalizacja promptów poprzez eksperymenty A/B.
- Mechanizmy zabezpieczające (guardrails) – np. usuwanie danych osobowych (PII), blokowanie tematów poza zakresem.
- Wykrywanie halucynacji przy użyciu LLM jako sędziego.
- Wyniki wewnętrznych testów wydajnościowych Comet: zapisywanie logów i ewaluacja w Opik zajęły 23,44 s w porównaniu do 327,15 s w Langfuse (~14-krotna różnica) – testy wydajnościowe dostawców należy jednak traktować poglądowo.
- Największe zalety: pętle optymalizacyjne, automatyczne eksperymenty, egzekwowanie guardrails.

### Dane branżowe

Raport Maxima (badania rynkowe z 2026 r.) wskazuje, że 89% organizacji wdrożyło już rozwiązania do obserwowalności agentów. Największą barierą przed wdrożeniem produkcyjnym pozostaje jakość działania modeli (wskazuje na to 32% respondentów).

### Wybór odpowiedniego narzędzia

| Potrzeba | Wybór |
|------|------|
| Kompleksowe rozwiązanie z zarządzaniem promptami | Langfuse |
| Zaawansowana ewaluacja RAG + dryf | Phoenix |
| Automatyczna optymalizacja + guardrails | Opik |
| W pełni otwarta licencja (bez ELv2) | Langfuse (MIT) lub Opik (Apache 2.0) |
| Integracja z Datadog / New Relic | Dowolne – wszystkie obsługują eksport OTel |

### Gdzie ten wzorzec może zawieść

- **Brak strategii ewaluacji.** Samo śledzenie (tracing) bez oceny jakości to po prostu kosztowne logowanie.
- **Autonomiczny sędzia LLM bez uziemienia (grounding).** Obowiązuje tu zasada CRITIC (lekcja 05) – sędziowie potrzebują zewnętrznych narzędzi do weryfikacji faktów.
- **Wersje promptów niepowiązane ze śladami.** Gdy w aplikacji dochodzi do regresji, bez powiązania śladów z konkretną wersją promptu nie da się szybko ustalić przyczyny błędu.

## Zbuduj to

Plik `code/main.py` implementuje prosty kolektor śladów (oparty na stdlib) oraz moduł ewaluacji LLM:

- Odbieranie i parsowanie spanów w formacie GenAI.
- Grupowanie według sesji oraz oznaczanie nieudanych uruchomień (wyzwolenie guardrails, niskie oceny pewności).
- Skryptowy sędzia LLM, który ocenia odpowiedzi agenta na podstawie określonych kryteriów.
- Podsumowanie w formie pulpitu nawigacyjnego: współczynnik błędów, główne przyczyny niepowodzeń oraz rozkład wyników ewaluacji.

Uruchomienie:

```
python3 code/main.py
```

Dane wyjściowe: wyniki ewaluacji poszczególnych sesji oraz kategoryzacja błędów odzwierciedlająca to, co normalnie wyświetlają platformy takie jak Langfuse, Phoenix czy Opik.

## Użyj tego

- **Langfuse**: lokalnie (self-hosted) lub w chmurze; integracja poprzez OTel lub dedykowane SDK.
- **Arize Phoenix**: lokalnie (self-hosted); automatyczna instrumentacja za pomocą OpenInference.
- **Comet Opik**: lokalnie (self-hosted) lub w chmurze; automatyczna pętla optymalizacji.
- **Datadog LLM Observability**: dla zespołów utrzymaniowych i ML, które korzystają już z ekosystemu Datadog.

## Wyślij to

Plik `outputs/skill-obs-platform-wiring.md` opisuje proces wyboru platformy oraz integracji śladów, ocen i wersji promptów z istniejącym agentem.

## Ćwiczenia

1. Wyeksportuj tygodniowe ślady OTel do chmury Langfuse (darmowy pakiet). Które sesje zakończyły się błędem i dlaczego?
2. Zdefiniuj kryteria ewaluacji LLM (rubrykę) specyficzne dla Twojej domeny (np. poprawność faktograficzna, ton wypowiedzi, zgodność z tematem). Przetestuj je na 50 śladach.
3. Porównaj funkcję wersjonowania promptów w Langfuse z grupowaniem śladów w Phoenix. Które podejście pozwala szybciej wykryć, co uległo awarii?
4. Przeczytaj dokumentację dotyczącą guardrails w Opik. Zintegruj mechanizm usuwania danych osobowych (PII) z jednym z przepływów swojego agenta.
5. Przeprowadź własne porównanie wydajności i stabilności tych trzech narzędzi na swoim zbiorze danych. Zamiast opierać się na danych dostawców, zmierz własne wyniki.

## Kluczowe terminy

| Termin | Co potocznie się mówi | Co to oznacza w rzeczywistości |
|------|----------------|--------------------------------------|
| Śledzenie (Tracing) | „Zbieranie spanów” | Pozyskiwanie spanów (zakresów) przez OTel/SDK i indeksowanie ich według sesji |
| Zarządzanie promptami | „CMS dla promptów” | Wersjonowanie promptów bezpośrednio powiązane ze śladami wykonania |
| LLM jako sędzia | „Automatyczna ewaluacja” | Wydzielony model LLM oceniający wyniki agenta na podstawie rubryki (kryteriów) |
| Odtwarzanie sesji | „Replay ścieżki” | Analiza krok po kroku wcześniejszych wywołań w celu debugowania |
| Trafność RAG | „Jakość wyszukiwania” | Sprawdzenie, czy pobrany kontekst pasuje do zapytania użytkownika |
| Grupowanie śladów | „Grupowanie behawioralne” | Klastrowanie podobnych uruchomień w celu wykrywania dryfu |
| Egzekwowanie guardrails | „Reguły walidacji w locie” | Kontrola danych pod kątem PII, toksyczności lub tematyki podczas logowania |

## Dalsze czytanie

- [Dokumentacja Langfuse](https://langfuse.com/) – śledzenie, ewaluacja, zarządzanie promptami
- [Dokumentacja Arize Phoenix](https://docs.arize.com/phoenix) – automatyczna instrumentacja, wykrywanie dryfu
- [Comet Opik](https://www.comet.com/site/products/opik/) – optymalizacja promptów i guardrails
- [Konwencje semantyczne OpenTelemetry GenAI](https://opentelemetry.io/docs/specs/semconv/gen-ai/) – wspólny schemat używany przez wszystkie trzy platformy
