# Obserwowalność agenta: Langfuse, Phoenix, Opik

> W 2026 r. dominują trzy platformy umożliwiające obserwację agentów typu open source. Langfuse (MIT) — ponad 6 mln instalacji miesięcznie, śledzenie + szybkie zarządzanie + ocena + powtarzanie sesji. Arize Phoenix (Elastic 2.0) — głębokie oceny specyficzne dla agenta, trafność RAG, automatyczne oprzyrządowanie OpenInference. Kometa Opik (Apache 2.0) — automatyczna optymalizacja natychmiastowa, poręcze, wykrywanie halucynacji przez sędziego LLM.

**Typ:** Ucz się
**Języki:** Python (stdlib)
**Wymagania wstępne:** Faza 14 · 23 (OTel GenAI)
**Czas:** ~45 minut

## Cele nauczania

- Wymień trzy najlepsze platformy obserwacji agentów typu open source i ich licencje.
- Rozróżnij, w czym każdy z nich jest najmocniejszy: Langfuse (szybkie zarządzanie + sesje), Phoenix (RAG + automatyczne oprzyrządowanie), Opik (optymalizacja + poręcze).
- Wyjaśnij, dlaczego 89% organizacji twierdzi, że do 2026 r. wprowadzi możliwość obserwowania agentów.
- Zaimplementuj potok śledzenia do pulpitu nawigacyjnego stdlib z oceną LLM.

## Problem

Otel GenAI (lekcja 23) podaje schemat. Nadal potrzebujesz platformy, która pozyskuje zakresy, przeprowadza oceny, przechowuje wersje podpowiedzi i wyświetla regresje. Każdy z trzech pretendentów kładzie nacisk na różne części cyklu życia.

## Koncepcja

### Langfuse (MIT)

- Ponad 6 mln instalacji pakietu SDK miesięcznie, ponad 19 tys. gwiazdek na GitHubie.
- Funkcje: śledzenie, szybkie zarządzanie z wersjonowaniem + plac zabaw, oceny (LLM-jako sędzia, opinie użytkowników, niestandardowe), powtórki sesji.
- Czerwiec 2025 r.: poprzednio komercyjne moduły (LLM-as-a-judge, kolejki adnotacji, szybkie eksperymenty, plac zabaw) udostępnione na zasadach open source w ramach MIT.
- Najmocniejszy ze względu na: kompleksową obserwowalność i ścisłą pętlę szybkiego zarządzania.

### Arize Phoenix (licencja elastyczna 2.0)

- Głębsza ocena specyficzna dla agenta: grupowanie śladów, wykrywanie anomalii, trafność wyszukiwania dla RAG.
- Natywne automatyczne oprzyrządowanie OpenInference.
- Łączy się z zarządzanym Arize AX na potrzeby produkcji.
- Brak szybkiego wersjonowania — pozycjonowane jako narzędzie dryfu/regresji behawioralnej obok szerszych platform.
- Najsilniejszy w zakresie: trafności RAG, dryfu behawioralnego, wykrywania anomalii.

### Kometa Opik (Apache 2.0)

- Automatyczna optymalizacja natychmiastowa poprzez eksperymenty A/B.
- Poręcze (redakcja informacji umożliwiających identyfikację, ograniczenia tematyczne).
- Wykrywanie halucynacji przez sędziego LLM.
- Test porównawczy z własnych pomiarów Comet: dzienniki Opik + ewaluacje w 23,44 s w porównaniu z Langfuse 327,15 s (przerwa ~ 14x) — przyjmij testy porównawcze dostawców jako kierunkowe.
- Najsilniejszy w przypadku: pętli optymalizacji, automatycznych eksperymentów, egzekwowania poręczy.

### Dane branżowe

Według Maxima (analiza terenowa z 2026 r.): 89% organizacji ma wdrożoną możliwość obserwowania agentów; Największą barierą produkcji są kwestie jakościowe (powołuje je 32% respondentów).

### Wybieram jedno

| Potrzebuję | Wybierz |
|------|------|
| Wszystko w jednym z szybkim zarządzaniem | Langfuse |
| Głęboka ocena RAG + dryf | Feniks |
| Zautomatyzowana optymalizacja + poręcze | Opik |
| Licencja otwarta, bez ELv2 | Langfuse (MIT) lub Opik (Apache 2.0) |
| Integracja Datadog / New Relic | Dowolne — wszystkie eksportują Otel |

### Gdzie ten wzorzec jest błędny

- **Brak strategii oceny.** Śledzenie bez oceny jest po prostu kosztownym rejestrowaniem.
- **Samodzielny sędzia LLM bez uziemienia.** Obowiązuje wzorzec KRYTYCZNY (lekcja 05) — sędziowie potrzebują zewnętrznych narzędzi do weryfikacji faktów.
- **Wersje podpowiedzi nie są powiązane ze śladami.** Kiedy produkt ulega regresji, nie można podzielić na pół monitu, który to spowodował.

## Zbuduj to

`code/main.py` implementuje moduł zbierający ślady stdlib + moduł oceniający LLM:

- Połknij rozpiętości w kształcie GenAI.
- Grupuj według sesji, nieudane przebiegi tagów (wyzwolenia poręczy, oceny o niskim poziomie pewności).
- Skryptowany sędzia LLM, który ocenia odpowiedzi agentów w rubryce.
- Podsumowanie przypominające pulpit nawigacyjny: wskaźnik awaryjności, główne przyczyny niepowodzeń, rozkład wyników eval.

Uruchom to:

```
python3 code/main.py
```

Dane wyjściowe: wyniki oceny poszczególnych sesji i kategoryzacja błędów odpowiadająca temu, co pokazałyby Langfuse/Phoenix/Opik.

## Użyj tego

- **Langfuse** na własnym serwerze lub w chmurze; drutu przez Otel lub ich SDK.
- **Arize Phoenix** na własnym serwerze; automatyczny instrument OpenInference.
- **Comet Opik** na własnym serwerze lub w chmurze; automatyczna pętla optymalizacji.
- **Obserwowalność Datadog LLM** dla zespołów zajmujących się operacjami mieszanymi i uczeniem maszynowym, które już korzystają z Datadog.

## Wyślij to

`outputs/skill-obs-platform-wiring.md` wybiera platformę i łączy ślady, oceny i wersje podpowiedzi z istniejącym agentem.

## Ćwiczenia

1. Wyeksportuj tygodniowe ślady Otel do chmury Langfuse (warstwa bezpłatna). Które sesje się nie powiodły? Dlaczego?
2. Napisz rubrykę oceny LLM dla swojej domeny (poprawność faktyczna, ton, zgodność z zakresem). Przetestuj na 50 śladach.
3. Porównaj wersjonowanie podpowiedzi Langfuse z grupowaniem śledzenia Phoenix. Co mówi ci, co zepsuło się szybciej?
4. Przeczytaj dokumentację dotyczącą poręczy Opika. Podłącz poręcz redakcyjną umożliwiającą identyfikację osób do jednego z przebiegów agenta.
5. Dokonaj porównania trzech elementów w swoim korpusie. Ignoruj ​​liczby opublikowane przez dostawcę; zmierzyć swój.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Śledzenie | „Kolekcjoner przęseł” | Pozyskuj zakresy OTel/SDK; indeks według sesji |
| Szybkie zarządzanie | „Podpowiedź CMS” | Wersjonowane monity powiązane ze śladami |
| LLM jako sędzia | „Automatyczna ocena” | Oddzielny LLM ocenia wyniki agenta w rubryce |
| Powtórka sesji | „Odtwarzanie ścieżki” | Przejdź przez poprzednie przebiegi debugowania |
| Trafność RAG | „Jakość wyszukiwania” | Czy pobrany kontekst pasuje do zapytania |
| Grupowanie śladów | „Grupowanie behawioralne” | Klaster podobnych przebiegów do wykrywania dryfu |
| Egzekucja poręczy | „Zasady w czasie logowania” | Kontrole PII/toksyczności/zakresu zarejestrowanych treści |

## Dalsze czytanie

- [Dokumentacja Langfuse](https://langfuse.com/) — śledzenie, ewaluacja, monit mgmt
– [Dokumentacja Arize Phoenix](https://docs.arize.com/phoenix) — automatyczne oprzyrządowanie, drift
- [Kometa Opik](https://www.comet.com/site/products/opik/) — optymalizacja + poręcze
- [Konwencje semantyczne OpenTelemetry GenAI](https://opentelemetry.io/docs/specs/semconv/gen-ai/) — schemat wykorzystuje wszystkie trzy