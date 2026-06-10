# Agenci przeglądarki i długoterminowe zadania sieciowe

> Agent ChatGPT (lipiec 2025 r.) połączył Operatora i szczegółowe badania w jednym agencie przeglądarki/terminalu i ustawić BrowseComp SOTA na 68,9%. OpenAI zamknęło Operatora 31 sierpnia 2025 r. — konsolidacja na poziomie produktu. Przejęcie firmy Anthropic Vercept przeniosło Claude'a Sonneta w OSWorld z poniżej 15% do 72,5%. WebArena-Verified (ServiceNow, ICLR 2026) naprawiła 11,3 punktów procentowych współczynnika wyników fałszywie ujemnych w oryginalnej aplikacji WebArena i dostarczyła podzbiór Hard składający się z 258 zadań. Liczby są prawdziwe. Podobnie jest z powierzchnią ataku: szef przygotowania OpenAI oświadczył publicznie, że pośrednie, natychmiastowe wprowadzenie do agentów przeglądarki „nie jest błędem, który można w pełni załatać”. Udokumentowane ataki z lat 2025–2026: Tainted Memories (Atlas CSRF), HashJack (Cato Networks) i przejęcia jednym kliknięciem w Perplexity Comet.

**Typ:** Ucz się
**Języki:** Python (stdlib, model powierzchni ataku z pośrednim wtryskiem)
**Wymagania wstępne:** Faza 15 · 10 (Tryby uprawnień), Faza 15 · 01 (Agenci z dalekiego horyzontu)
**Czas:** ~45 minut

## Problem

Agent przeglądarki to agent o długim horyzoncie czasowym, który odczytuje niezaufane treści i podejmuje odpowiednie działania. Każda strona odwiedzana przez agenta jest danymi wejściowymi, których użytkownik nie napisał. Każdy formularz na każdej stronie jest potencjalnym kanałem poleceń. Korpus ataków z lat 2025–2026 pokazuje, że nie jest to hipotetyczne: Tainted Memories umożliwia osobie atakującej powiązanie złośliwych instrukcji z pamięcią agenta za pośrednictwem spreparowanej strony; HashJack ukrywa polecenia we fragmentach adresów URL odwiedzanych przez agenta; Perplexity Comet porywa jednym kliknięciem.

Obraz defensywny jest niewygodny. Szef przygotowania OpenAI wypowiedział głośno cichą część: pośrednie wprowadzenie natychmiastowe „nie jest błędem, który można w pełni załatać”. Dzieje się tak, ponieważ atak przebiega na granicy odczytu i działania agenta, która jest niejasna pod względem architektonicznym — każdy token odczytany przez model może w zasadzie zostać odczytany jako instrukcja.

W tej lekcji wymieniono powierzchnię ataku, nadano krajobraz wzorcowy (BrowseComp, OSWorld, WebArena-Verified) i przedstawiono model minimalnego scenariusza pośredniego wstrzyknięcia, dzięki czemu można uzasadnić rzeczywiste mechanizmy obronne w lekcjach 14 i 18.

## Koncepcja

### Krajobraz na rok 2026, po jednym akapicie na każdy system

**Agent ChatGPT (OpenAI).** Uruchomiony w lipcu 2025 r. Ujednolica operatora (przeglądanie) i głębokie badania (badania wielogodzinne). Zamknięcie samodzielnego Operatora 31 sierpnia 2025 r. SOTA w BrowseComp na poziomie 68,9%; dobre wyniki w OSWorld i WebArena-Verified.

**Claude Sonnet + Vercept (Anthropic).** Przejęcie firmy Anthropic firmy Vercept skupiło się na możliwościach obsługi komputera. Przeniesiono Claude’a Sonneta na OSWorld z <15% do 72,5%. Claude Computer Użyj statków jako narzędzia API.

**Gemini 3 Pro z przeglądarką (DeepMind).** Integracja z przeglądarką umożliwia kontrolę korzystania z komputera; FSF v3 (kwiecień 2026 r., lekcja 20) śledzi autonomię w szczególności w dziedzinie badań i rozwoju ML.

**WebArena-Verified (ServiceNow, ICLR 2026).** Naprawia dobrze udokumentowany problem: oryginalna WebArena miała ~11,3% współczynnika wyników fałszywie negatywnych (zadania oznaczone jako zakończone niepowodzeniem, które faktycznie zostały rozwiązane). Wersja zweryfikowana podlega ponownej ocenie na podstawie kryteriów sukcesu wybranych przez człowieka i dodaje podzbiór trudny składający się z 258 zadań (artykuł ICLR 2026, openreview.net/forum?id=94tlGxmqkN).

### PrzeglądajComp kontra OSWorld czy WebArena

| punkt odniesienia | Co mierzy | Horyzont |
|---|---|---|
| PrzeglądajKomp | Znajdowanie konkretnych faktów w otwartej sieci pod presją czasu | minuty |
| OSŚwiat | Agent obsługujący pełny pulpit (mysz, klawiatura, powłoka) | kilkadziesiąt minut |
| Zweryfikowano na WebArenie | Transakcyjne zadania sieciowe w symulowanych witrynach | minuty |
| Podzbiór twardy | Zadania zweryfikowane przez WebArena z wielostronicowymi przejściami stanu | kilkadziesiąt minut |

Różne osie. Wysoki wynik BrowseComp oznacza, że ​​agent znajduje fakty; nie jest napisane, że agent może zarezerwować lot. Wynik OSWorld jest bliższy „czy to działa na moim komputerze”. WebArena-Verified jest bliższe „czy może zakończyć przepływ”. Każda decyzja produkcyjna wymaga punktu odniesienia odpowiadającego podziałowi zadań.

### Powierzchnia ataku o nazwie

1. **Pośrednie wstrzyknięcie monitu.** Treść niezaufanej strony zawiera instrukcje. Agent je czyta. Agent je wykonuje. Publiczne przykłady: 2024 Kai Greshake i in., 2025 artykuł Tainted Memories, 2026 HashJack (Cato Networks).
2. **Fragment adresu URL / wstrzyknięcie zapytania.** `#fragment` lub ciąg zapytania przeszukanego adresu URL zawiera polecenia. Nigdy nie renderowane w widoczny sposób; nadal w kontekście agenta.
3. **Ataki wiążące pamięć.** Strona instruuje agenta, aby zapisał pamięć trwałą (Lekcja 12 omawia stan trwały). Podczas następnej sesji pamięć uruchamia ładunek bez widocznego wyzwalacza.
4. **Ataki w kształcie CSRF na sesje uwierzytelnione.** Klasa Tainted Memories: agent jest gdzieś zalogowany; strona atakującego wysyła żądania zmieniające stan, które agent wykonuje przy użyciu plików cookie użytkownika.
5. **Przejęcie jednym kliknięciem.** Wizualnie nieszkodliwy przycisk przenosi ładunek, za którym podąża agent. Klasa komety.
6. **Dziury w polityce bezpieczeństwa treści na powierzchni hosta agenta.** Warstwy renderowania i narzędzi mogą same w sobie być wektorami ataku; stos przeglądarki w agencie przeglądarki jest szeroki.

### Dlaczego „nie można w pełni załatać”

Atak jest izomorficzny w stosunku do możliwości agenta. Agent musi czytać niezaufane treści, aby wykonać swoje zadanie. Wszelkie treści, które agent czyta, mogą zawierać instrukcje. Wszelkie instrukcje, których przestrzega agent, mogą być niezgodne z rzeczywistym żądaniem użytkownika. Obrony (granice zaufania, klasyfikatory, listy dozwolonych narzędzi, HITL w przypadku działań następczych) zwiększają koszt ataku i zmniejszają jego promień wybuchu. Nie zamykają zajęć.

Jest to ten sam schemat rozumowania, co w twierdzeniu Loba (lekcja 8): agent nie może udowodnić, że następny żeton jest bezpieczny; może jedynie skonfigurować system, w którym niebezpieczne tokeny są łatwiej wykrywalne.

### Postawa obronna, która faktycznie służy do statku

- **Granica odczytu/zapisu.** Odczyt nigdy nie ma konsekwencji. Pisanie (wysłanie formularza, opublikowanie treści, wywołanie narzędzia z efektami ubocznymi) wymaga świeżej zgody człowieka, jeśli treść inicjująca pochodzi spoza granicy zaufania.
- **Lista dozwolonych narzędzi według zadania.** Agent może przeglądać; nie może zainicjować przelewu, chyba że to narzędzie zostało wyraźnie włączone do tego zadania. Lekcja 13 dotyczy budżetów.
- **Izolacja sesji.** Sesje agenta przeglądarki działają wyłącznie z poświadczeniami o określonym zakresie. Brak autoryzacji produkcyjnej, brak osobistego adresu e-mail. Dzienniki każdego żądania HTTP przechowywane do celów audytu.
- **Oczyszczanie treści.** Pobrany kod HTML jest usuwany ze znanych, złych wzorców przed połączeniem go z kontekstem modelu. (Redukuje łatwe ataki; nie zatrzymuje wyrafinowanych ładunków.)
- **HITL w przypadku działań wynikowych.** Wzorzec „zaproponuj, a następnie zatwierdź” (lekcja 15).
- **Tokeny Canary w pamięci.** Jeśli wpis do pamięci zostanie uruchomiony, użytkownik go zobaczy (Lekcja 14).

## Użyj tego

`code/main.py` modeluje małego agenta przeglądarki działającego na trzech syntetycznych stronach. Jedna strona jest łagodna, druga ma bezpośredni blob wstrzykujący w widocznym tekście, a druga ma wstrzyknięty fragment adresu URL (niewidoczny, ale znajdujący się w kontekście agenta). Skrypt pokazuje (a) co zrobiłby naiwny agent, (b) co wychwytuje granica odczytu/zapisu, (c) co wychwytuje środek dezynfekujący, (d) czego nie przechwytuje żaden z nich.

## Wyślij to

`outputs/skill-browser-agent-trust-boundary.md` określa zakres proponowanego wdrożenia agenta przeglądarki: jakich stref zaufania dotyka, do czego jest upoważniony do zapisu i jakie zabezpieczenia muszą zostać zastosowane przed pierwszym uruchomieniem.

## Ćwiczenia

1. Uruchom `code/main.py`. Zidentyfikuj, który atakuje przechwyty środka dezynfekującego, ale nie granica odczytu/zapisu, a które atakują tylko blokady granicy odczytu/zapisu.

2. Rozszerz moduł sanityzujący, aby wykrywał jedną klasę wstrzykiwania fragmentu adresu URL w stylu HashJack. Zmierz odsetek wyników fałszywie pozytywnych w przypadku łagodnych adresów URL zawierających prawidłowe fragmenty.

3. Wybierz jeden znany sobie sposób działania prawdziwego agenta przeglądarki (np. „zarezerwuj lot”). Wypisz każdy odczyt i każdy zapis. Zaznacz, który pisze, że potrzebujesz HITL i dlaczego.

4. Przeczytaj artykuł ICLR 2026 zweryfikowany przez WebArena. Zidentyfikuj jedną kategorię zadań, w przypadku których pierwotna punktacja WebAreny była niewiarygodna i wyjaśnij, w jaki sposób podzbiór zweryfikowanych rozwiązuje ten problem.

5. Zaprojektuj kanarek pamięci dla ustawień agenta przeglądarki. Co byś przechowywał, gdzie i co uruchamia alarm?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|---|---|---|
| Pośredni wtrysk natychmiastowy | „Zły tekst na stronie” | Niezaufana zawartość strony, którą czyta agent, zawiera instrukcje, które agent wykonuje |
| Skażone wspomnienia | „Atak pamięci” | Agent zapisuje instrukcję dostarczoną przez atakującego w trwałej pamięci; wywołał następną sesję |
| HashJack | „Atak na fragment adresu URL” | Ładunek ukryty we fragmencie adresu URL/ciągu zapytania znajduje się w kontekście agenta, ale nie jest renderowany w widoczny sposób |
| Przejęcie jednym kliknięciem | „Zły przycisk” | Widoczna afordancja wiąże się z kolejnym ładunkiem wykonywanym przez agenta |
| PrzeglądajKomp | „Porównanie wyszukiwania w sieci” | Znajdowanie konkretnych faktów w otwartej sieci; horyzont w skali minutowej |
| OSŚwiat | „Porównanie wydajności komputerów stacjonarnych” | Pełna kontrola systemu operacyjnego; wieloetapowe zadania GUI |
| Zweryfikowano na WebArenie | „Naprawiono test porównawczy zadań internetowych” | Ulepszona platforma WebArena firmy ServiceNow z podzbiorem Hard |
| Granica odczytu/zapisu | „Brama skutków ubocznych” | Czytanie nigdy nie jest konsekwentne; pisanie wymaga nowego zatwierdzenia, jeśli treść nie jest zaufana |

## Dalsze czytanie

- [OpenAI — Przedstawiamy agenta ChatGPT](https://openai.com/index/introducing-chatgpt-agent/) — połączenie Operatora i głębokich badań; PrzeglądajComp SOTA.
- [OpenAI — Agent korzystający z komputera](https://openai.com/index/computer-using-agent/) — rodowód Operatora i architektura, która stała się agentem ChatGPT.
- [Zhou i in. — WebArena](https://webarena.dev/) — oryginalny benchmark.
– [WebArena-Verified (OpenReview)](https://openreview.net/forum?id=94tlGxmqkN) — artykuł ICLR 2026 ze stałym podzbiorem.
— [Anthropic — Pomiar autonomii agentów w praktyce](https://www.anthropic.com/research/measuring-agent-autonomy) — obejmuje dyskusję na temat powierzchni ataku dla agentów korzystających z komputera.