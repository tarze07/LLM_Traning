# Natychmiastowe buforowanie i ekonomia buforowania semantycznego

> **Przegląd cen z dnia 2026-04.** Poniższe liczby liczbowe odzwierciedlają arkusze stawek dostawców zarejestrowane w publikacji tej lekcji; sprawdź w odniesieniu do połączonych dokumentów przed zacytowaniem ich w dalszej części tekstu.

> Buforowanie odbywa się w dwóch warstwach. Buforowanie podpowiedzi/prefiksów L2 (na poziomie dostawcy) ponownie wykorzystuje uwagę KV dla powtarzających się prefiksów — dokumentacja firmy Anthropic dotycząca buforowania podpowiedzi ogłasza redukcję kosztów o 90% i redukcję opóźnień o 85% w przypadku długich podpowiedzi; dla Claude 3.5 odczyty pamięci podręcznej Sonnet wynoszą $0.30/M vs $3,00/M świeże z 5-minutowym TTL i 2-krotną premią za zapis dla opcji 1-godzinnego TTL (docs.anthropic.com, 2026-04). Buforowanie podpowiedzi OpenAI jest stosowane automatycznie w przypadku zapytań zawierających ≥1024 tokenów, a dane wejściowe zapisane w pamięci podręcznej cen są dostępne z około 90% rabatem w porównaniu do świeżych danych (platform.openai.com, 2026–04); dokładna stawka buforowana dla każdego modelu zależy od aktualnego arkusza stawek. Buforowanie semantyczne L1 (na poziomie aplikacji) całkowicie pomija LLM po osadzeniu trafień podobieństwa. „Dokładność na poziomie 95%” dostawcy odnosi się do poprawności dopasowania, a nie współczynnika trafień — zgłaszane współczynniki trafień w produkcji wahają się od 10% (czat otwarty) do 70% (ustrukturyzowane często zadawane pytania); żaden z dostawców nie publikuje oficjalnych wartości bazowych, dlatego należy je traktować jako dane telemetryczne społeczności, a nie gwarancje. Pułapki produkcyjne: równoległość zabija buforowanie (N równoległych żądań wydanych przed pierwszym zapisem w pamięci podręcznej może kilkukrotnie zwiększyć wydatki), a dynamiczna zawartość wewnątrz prefiksu całkowicie zapobiega trafieniom w pamięci podręcznej. ProjectDiscovery zgłosiło zmianę współczynnika trafień z 7% do 74% (2025–2011) poprzez przeniesienie tekstu dynamicznego z prefiksu buforowanego.

**Typ:** Ucz się
**Języki:** Python (stdlib, zabawkowy symulator dwuwarstwowej pamięci podręcznej)
**Wymagania wstępne:** Faza 17 · 04 (vLLM obsługująca elementy wewnętrzne), faza 17 · 06 (SGLang RadixAttention)
**Czas:** ~60 minut

## Cele nauczania

- Odróżnij buforowanie podpowiedzi/prefiksów L2 (ponowne użycie KV u dostawcy) od buforowania semantycznego L1 (obejście LLM w podobnych podpowiedziach).
- Wyjaśnij wyraźne oznaczenie `cache_control` firmy Anthropic i dwie opcje TTL (5 minut vs 1 godzina) wraz z ich mnożnikami ceny.
- Oblicz oczekiwane miesięczne oszczędności, biorąc pod uwagę współczynnik trafień, kombinację podpowiedzi i odpowiedzi oraz ceny tokenów.
- Nazwij antywzorzec równoległości, który zawyża rachunki 5-10 razy, oraz antywzorzec z zawartością dynamiczną, który zmniejsza współczynnik trafień.

## Problem

Dodajesz buforowanie podpowiedzi do swojej usługi RAG. Rachunek pozostaje płaski. Mierzysz współczynnik trafień; jest to 7%. Twoje monity wyglądają na statyczne, ale tak nie jest — monit systemowy zawiera bieżącą datę sformatowaną w minutach, identyfikator żądania i losową przykładową zmianę kolejności w celu zapewnienia różnorodności. Każde żądanie zapisuje nowy wpis w pamięci podręcznej, odczytuje zero.

Oddzielnie agent uruchamia dziesięć równoległych wywołań narzędzi na każde pytanie użytkownika. Wszystkie dziesięć docierają do dostawcy przed zakończeniem pierwszego zapisu w pamięci podręcznej. Dziesięć zapisów, zero odczytów. Twój rachunek wynosi 5–10 razy tyle, ile miało kosztować „z buforowaniem”.

Buforowanie to protokół, a nie flaga. Dwie warstwy, dwa różne tryby awarii.

## Koncepcja

### L2 — buforowanie podpowiedzi/prefiksów dostawcy

Dostawca przechowuje uwagę KV dla prefiksu buforowanego i wykorzystuje go ponownie w następnym żądaniu pasującym do prefiksu. Płacisz raz za zapis, czytasz prawie za darmo.

**Antropiczny (seria Claude 3.5 / 3.7 / 4)**: wyraźny znacznik `cache_control` w żądaniu. Oznaczasz, które bloki można buforować. TTL: 5 minut (zapis kosztuje 1,25x podstawa) lub 1 godzina (zapis kosztuje 2x podstawa). Dane w pamięci podręcznej: $0.30/M on Claude 3.5 Sonnet vs $3,00/M świeże — 10 razy taniej (docs.anthropic.com, stan na 2026–04). Ceny różnią się w zależności od modelu (Opus/Haiku opublikowane osobno); zawsze sprawdzaj stronę z cenami na żywo.

**OpenAI**: automatyczne buforowanie podpowiedzi ≥1024 tokenów (platform.openai.com, 2026-04). Brak wyraźnej flagi. Dane wejściowe buforowane są w przybliżeniu 10 razy tańsze niż świeże w obecnych arkuszach stawek gpt-4o/gpt-5. Ani dokumenty, ani informacje o wydaniu nie podają oficjalnej wartości bazowej współczynnika trafień; raporty społeczności skupiają się wokół 30–60% przy starannym i szybkim projektowaniu. Monitoruj `usage.cached_tokens`, aby dokonać własnych pomiarów.

**Google (Gemini)**: buforowanie kontekstu poprzez jawne API; Kontekst tokena 1M oznacza, że ​​buforowanie opłaca się jeszcze bardziej.

**Własny hosting (vLLM, SGLang)**: Faza 17 · 06 obejmuje RadixAttention — ten sam wzorzec na własnych obliczeniach.

### L1 — buforowanie semantyczne na poziomie aplikacji

Zanim w ogóle wywołasz LLM, zahaszuj monit, osadź go i poszukaj podobnego żądania w pamięci podręcznej (podobieństwo cosinus powyżej progu, zwykle 0,95+). Po trafieniu zwróć odpowiedź z pamięci podręcznej. W przypadku nieudanego połączenia zadzwoń do LLM i zapisz wynik w pamięci podręcznej.

Oprogramowanie typu open source: podobieństwo wektorów Redis, GPTCache, Qdrant. Komercyjne: pamięć podręczna świstoklik, pamięć podręczna Helicone.

Twierdzenia dostawcy dotyczące dokładności odnoszą się do tego, jak często zwrócona odpowiedź z pamięci podręcznej była semantycznie odpowiednia, a nie do tego, jak często trafiałeś. Wskaźniki trafień produkcyjnych:

- Czat otwarty: 10-15%.
- Strukturalne FAQ / wsparcie: 40-70%.
- Pytania kodowe: 20-30% (małe warianty zabijają trafienia).
- Agenci głosowi powtarzający monity: 50-80% (ustawiona stała normalizacja głosu).

### Antywzorzec równoległości

Twój agent wykonuje 10 wywołań narzędzi równolegle. Wszystkie 10 mają ten sam monit systemowy z tokenem 4K. Zapisy w pamięci podręcznej Anthropic są dokonywane na żądanie; pierwszy zapis w pamięci podręcznej kończy się około 300 ms po wyświetleniu monitu przez dostawcę. Żądania 2–10 docierają w tym samym oknie milisekundowym i w każdym z nich występuje brak pamięci podręcznej. Płacisz 10 składek za zapis, 0 rabatów za odczyt.

Poprawka: wsadowa z najpierw sekwencyjnym — złóż samo żądanie 1, a następnie uruchom 2-10 po zapełnieniu pamięci podręcznej 1. Dodaje 300 ms do pierwszego wywołania narzędzia; oszczędza 5-10x rachunek.

### Antywzorzec zawartości dynamicznej

Podpowiedź systemowa wygląda następująco:

```
You are a helpful assistant. The current time is 14:32:17.
User ID: abc123. Today is Tuesday...
```

Każde żądanie jest wyjątkowe. Każda prośba jest zapisana. Zero trafień.

Poprawka: przenieś wszystko, co naprawdę statyczne, do prefiksu buforowanego; dołącz zawartość dynamiczną po granicy pamięci podręcznej:

```
[cacheable]
You are a helpful assistant. [rules, examples, instructions]
[/cacheable]
[dynamic, not cached]
Current time: 14:32:17. User: abc123.
```

ProjectDiscovery przesunęło w ten sposób współczynnik trafień w pamięci podręcznej z 7% do 74% i opublikowało anatomię.

### Zestaw wsadowy + pamięć podręczna dla obciążeń nocnych

Batch API (faza 17 · 15) daje 50% zniżki przy realizacji w ciągu 24 godzin. Buforowane dane wejściowe na górze dają ~10x więcej. W wyniku kumulowania obciążenia związane z klasyfikacją, etykietowaniem i generowaniem raportów w ciągu nocy mogą spaść do ~10% kosztu synchronicznego braku pamięci podręcznej.

### Liczby, które powinieneś zapamiętać

Punkty cenowe są pobierane w latach 2026-04 z powiązanych dokumentów dostawców i zmieniają się co kilka miesięcy — sprawdź je ponownie, zanim na nich zaczniesz polegać.

- Odczyt z pamięci podręcznej Anthropic: 0,30 USD/M w Claude 3.5 Sonnet, około 10 razy taniej niż świeże dane wejściowe (docs.anthropic.com).
- Antropiczna premia za zapis w pamięci podręcznej: 1,25x (5-min TTL) lub 2x (1-godzina TTL).
- Automatyczna pamięć podręczna OpenAI: dotyczy monitów ≥1024 tokenów; dane wejściowe w pamięci podręcznej wycenione na około 10% świeżych danych wejściowych w aktualnych arkuszach stawek (platforma.openai.com).
- Współczynnik trafień w pamięci podręcznej semantycznej (zgłoszony przez społeczność): ~10% otwartego czatu; do ~70% ustrukturyzowanych często zadawanych pytań. Nie jest to poziom bazowy udokumentowany przez dostawcę.
- ProjectDiscovery: 7% → 74% współczynnika trafień po przeniesieniu dynamiki z przedrostka (blog projektu, 2025–2011).
- Antywzorzec równoległości: typowe raporty o 5–10-krotnym zawyżeniu rachunku, gdy N równoległych żądań nie uwzględnia pierwszego zapisu w pamięci podręcznej.

## Użyj tego

`code/main.py` symuluje buforowanie L1 + L2 przy mieszanych obciążeniach. Raportuje współczynniki trafień, rachunki i pokazuje karę za zrównoleglenie.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-cache-auditor.md`. Biorąc pod uwagę szablon podpowiedzi i ruch, sprawdza możliwość buforowania i zaleca restrukturyzację.

## Ćwiczenia

1. Uruchom `code/main.py`. Przełącz flagę równoległości. Jak bardzo zmienia się rachunek?
2. Podpowiedź systemowa ma datę. Przesuń to. Pokaż obliczenia współczynnika trafień przed/po.
3. Oblicz próg rentowności dla 1-godzinnego TTL (2x zapis) w porównaniu z 5-minutowym TTL (1,25x zapis), biorąc pod uwagę współczynnik nadejścia żądań.
4. Semantyczna pamięć podręczna przy progu 0,95 osiąga 20%. Przy 0,85 osiąga 50%, ale widzisz nieprawidłowe odpowiedzi w pamięci podręcznej. Wybierz właściwy próg i uzasadnij.
5. Wsadowo tworzysz 10 równoległych zapytań podrzędnych na pytanie użytkownika. Przepisz, aby zapewnić przyjazność dla pamięci podręcznej, bez dodawania kompleksowych opóźnień.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Pamięć podręczna podpowiedzi L2 | „pamięć podręczna prefiksów” | Dostawca przechowuje KV dla powtarzającego się prefiksu |
| `cache_control` | „Antropiczny znacznik skrytki” | Jawne atrybuty oznaczające bloki buforowane |
| Premia za zapis w pamięci podręcznej | "napisz podatek" | Dodatkowy koszt za pierwszy błąd w pamięci podręcznej (1,25x lub 2x) |
| Semantyczna pamięć podręczna L1 | „osadzanie pamięci podręcznej” | Mieszaj i osadzaj na poziomie aplikacji przed wywołaniem LLM |
| Pamięć GPTC | „Biblioteka buforowania LLM” | Popularna biblioteka pamięci podręcznej OSS L1 |
| Współczynnik trafień w pamięci podręcznej | „trafienia / suma” | Część żądań obsłużonych z pamięci podręcznej |
| Antywzorzec równoległości | „pułapka zapisu N” | N równoległych żądań pomija pamięć podręczną N razy |
| Dynamiczna pułapka treści | „pułapka czasu” | Dynamiczne bajty w częstości zabijania prefiksów |
| RadixUwaga | „pamięć podręczna wewnątrz repliki” | Implementacja pamięci podręcznej prefiksów w SGLang |

## Dalsze czytanie

- [Anthropic Prompt Caching](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching) — oficjalna `cache_control` semantyka i TTL.
- [OpenAI Prompt Caching](https://platform.openai.com/docs/guides/prompt-caching) — zachowanie i uprawnienia automatycznego buforowania.
- [TianPan — buforowanie semantyczne do produkcji LLM](https://tianpan.co/blog/2026-04-10-semantic-caching-llm-production)
— [ProjectDiscovery — obniż koszty LLM o 59% dzięki szybkiemu buforowaniu](https://projectdiscovery.io/blog/how-we-cut-llm-cost-with-prompt-caching)
- [DigitalOcean / Anthropic — Szybkie buforowanie](https://www.digitalocean.com/blog/prompt-caching-with-digital-ocean)