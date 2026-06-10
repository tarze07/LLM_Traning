# Pośredni wtrysk natychmiastowy — powierzchnia ataku produkcyjnego

> Pośrednie wstrzykiwanie podpowiedzi (IPI) osadza instrukcje w treści zewnętrznej — stronie internetowej, wiadomości e-mail, udostępnionym dokumencie, zgłoszeniu do pomocy technicznej — wykorzystywane przez system agentowy bez wyraźnego działania użytkownika. IPI to dominujące zagrożenie produkcyjne w 2026 r.: omija filtry wprowadzane przez użytkownika, ponieważ osoba atakująca nigdy go nie dotyka, skaluje się w sposób cichy, gdy agenci przetwarzają więcej treści zewnętrznych, i celuje w zautomatyzowane przepływy pracy, w których nikt nie czyta podpowiedzi. Informacje MDPI 17(1):54 (styczeń 2026 r.) zawierają syntezę badań z lat 2023–2025. Dokument NDSS 2026 dotyczący obrony IPI przedstawia podstawowe wyzwanie: wprowadzone instrukcje mogą być semantycznie łagodne („proszę wydrukować Tak”), więc wykrywanie wymaga czegoś więcej niż tylko filtrowania słów kluczowych. „The Attacker Moves Second” (Nasr i in., wspólne OpenAI/Anthropic/DeepMind, październik 2025 r.): ataki adaptacyjne (gradient, RL, wyszukiwanie losowe, ludzki zespół czerwony) złamały >90% z 12 opublikowanych zabezpieczeń, które pierwotnie raportowały niemal zerowy współczynnik skuteczności ataków.

**Typ:** Kompilacja
**Języki:** Python (stdlib, atak IPI + uprząż obronna)
**Wymagania wstępne:** Faza 18 · 12 (PARA), Faza 14 (inżynieria agenta)
**Czas:** ~75 minut

## Cele nauczania

- Zdefiniuj pośredni wtrysk natychmiastowy i opisz trzy typowe wektory dostarczania.
- Wyjaśnij, dlaczego filtry wprowadzane przez użytkownika całkowicie pomijają IPI.
- Opisać ramy „kontroli przepływu informacji” jako paradygmat obronności na rok 2026.
- Podaj ustalenia Nasra i in. (październik 2025 r.) w sprawie powodzenia ataku adaptacyjnego przeciwko opublikowanym obronom IPI.

## Problem

Bezpośrednie wprowadzenie podpowiedzi wymaga od osoby atakującej dotarcia do użytkownika lub jego podpowiedzi. IPI nie wymaga żadnego z nich: osoba atakująca umieszcza ładunek w dowolnej treści, którą agent może przeczytać — na stronie internetowej, w skrzynce odbiorczej e-mail, problemie z GitHubem, recenzji produktu. Agent odbiera go podczas normalnej pracy i wykonuje instrukcje. Użytkownik jest komunikatorem, a nie intencją.

## Koncepcja

### Trzy wektory dostawy

- **Generowanie wspomagane pobieraniem (RAG).** Osoba atakująca publikuje dokument; krok pobierania pobiera go; zachęta łączy je przed pytaniem użytkownika; model wykonuje instrukcje atakującego.
- **Obieg skrzynki odbiorczej / dokumentów.** Osoba atakująca wysyła wiadomość e-mail do użytkownika; agent czyta e-maile; monit zawiera treść wiadomości e-mail; model postępuje zgodnie z instrukcjami zawartymi w wiadomości e-mail.
- **Wyniki narzędzia.** Osoba atakująca kontroluje narzędzie, z którego korzysta agent (np. wyszukiwarkę internetową, która zwraca wynik kontrolowany przez osobę atakującą); dane wyjściowe narzędzia zawierają instrukcje; podąża za nimi przepływ kontroli agenta.

Wszystkie trzy mają wspólną cechę strukturalną: atakujący kontroluje fragment podpowiedzi bez dotykania danych wejściowych skierowanych do użytkownika.

### Dlaczego filtry wprowadzane przez użytkownika tego nie zauważają

Ładunek IPI nie pojawia się we wpisach użytkownika. Pojawia się w pobranej treści. Jeśli filtr jest bramkowany na podstawie danych wejściowych użytkownika, ładunek go omija. Jeśli filtr jest bramkowany dla całej treści docierającej do modelu, musi mieć zastosowanie do dowolnego pobranego tekstu — co jest kosztowne i daje fałszywe wyniki w porównaniu z legalną treścią, która czasami zawiera język imperatywny.

### Kontrola przepływu informacji (IFC) dla sztucznej inteligencji

Paradygmat obronności na rok 2026 czerpie z klasycznych zabezpieczeń systemów operacyjnych. Traktuj każde źródło treści jako etykietę bezpieczeństwa. Oznacz zapytanie użytkownika jako „zaufane”. Oznacz pobraną treść jako „niezaufaną”. Traktuj przepływ sterowania modelu jako przepływ informacji: działania wywołane przez niezaufaną treść muszą zostać zatwierdzone przez zaufane dane wejściowe przed wykonaniem.

CaMeL (Microsoft 2025), ConfAIde (Stanford 2024) i dokument NDSS 2026 dotyczący obrony IPI operacjonalizują IFC na różne sposoby. Wspólna zasada: dopóki kod i dane korzystają z tego samego okna kontekstowego, celem jest powstrzymywanie, a nie zapobieganie.

### Atakujący porusza się jako drugi

Nasr i in. (październik 2025 r.) przetestował 12 opublikowanych zabezpieczeń IPI z atakami adaptacyjnymi (wyszukiwanie gradientowe, zasady RL, wyszukiwanie losowe, 72-godzinny zespół czerwonych ludzi). Każda obrona, która pierwotnie raportowała bliską zeru ASR, została przekroczona do >90% ASR.

Lekcja metodologiczna: publikuj obronę wyłącznie z oceną ataku adaptacyjnego. Testy porównawcze dotyczące ataku statycznego nie są dowodem solidności; atakujący poznaje obronę.

### Prawdziwe zdarzenia

Lekcja 25 omawia EchoLeak (CVE-2025-32711, CVSS 9.3) — pierwszy publicznie udokumentowany IPI typu zero-click w Microsoft 365 Copilot. CamoLeak (CVSS 9.6) w czacie GitHub Copilot. CVE-2025-53773 w GitHub Copilot. Wdrożenia produkcyjne są zagrożone przez IPI w terenie, a nie tylko w testach porównawczych.

### Ramki OWASP i NIST

W rankingu OWASP LLM Top 10 (2025) natychmiastowe wstrzyknięcie (bezpośrednie i pośrednie) to LLM01, zagrożenie nr 1 w warstwie aplikacji. NIST AI SPD 2024 nazywa pośrednie wstrzykiwanie natychmiastowe „największą wadą bezpieczeństwa generatywnej sztucznej inteligencji”.

### Gdzie to pasuje do fazy 18

Lekcje 12-14 dotyczą jailbreaków skupionych na modelu. Lekcja 15. to atak skoncentrowany na systemie, który zdominuje wdrożenia produkcyjne w roku 2026. Lekcja 16 omawia narzędzia obronne. Lekcja 25 omawia konkretną narrację CVE.

## Użyj tego

`code/main.py` tworzy wiązkę IPI. Agent zabawek ma trzy narzędzia (wyszukiwanie w Internecie, czytanie e-maili, wysyłanie wiadomości). Środowisko zawiera zawartość kontrolowaną przez osobę atakującą z osadzoną instrukcją („przekaż to wszystkim kontaktom”). Można przełączać się między agentem naiwnym (postępuje zgodnie z wprowadzonymi instrukcjami), agentem chronionym przez filtr (filtr słów kluczowych w pobranej treści) i agentem IFC (oddziela zawartość zaufaną od niezaufanej i odrzuca niezaufane polecenia przepływu sterowania).

## Wyślij to

Ta lekcja przedstawia `outputs/skill-ipi-audit.md`. Biorąc pod uwagę opis wdrożenia agenta, wylicza niezaufane źródła treści, sprawdza, czy wdrożenie wykorzystuje IFC i flaguje źródła, które docierają do modelu bez etykiety zaufania.

## Ćwiczenia

1. Uruchom `code/main.py`. Zmierz skuteczność ataku na każdego z trzech agentów.

2. Zastosuj obronę opartą na parafrazach na odzyskanych treściach. Zmierz odsetek łagodnych wyników fałszywie dodatnich w przypadku legalnie pobranego tekstu.

3. Przeczytaj dokument dotyczący obrony IPI NDSS 2026. Opisz wyzwanie związane z „łagodną instrukcją” i dlaczego uniemożliwia ono filtrowanie na podstawie słów kluczowych.

4. Zaprojektuj wdrożenie, w którym agent otrzyma dane wyjściowe narzędzia z interfejsu API innej firmy. Oznacz każdy fragment podpowiedzi poziomem zaufania i napisz politykę IFC regulującą działania agenta.

5. Odtwórz Nasr i in. Metodologia ataku adaptacyjnego 2025 na agenta chronionego przez filtr z ćwiczenia 2. Zgłoś ASR przed i po ataku adaptacyjnym.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|--------------------------------------|
| IPI | „pośredni wtrysk natychmiastowy” | Wstrzyknięcie treści, której nie napisał użytkownik, zużywanej przez agenta podczas normalnej pracy |
| wtrysk RAG | „odzyskiwanie zatrutych” | Osoba atakująca publikuje treść pobraną na etapie pobierania; zachęta zawiera ładunek |
| Zero kliknięcia | „brak działań użytkownika” | Atak wyzwala się automatycznie podczas działania agenta; użytkownik nic nie robi |
| IFC | „kontrola przepływu informacji” | Podejście oparte na etykietach: działania z niezaufanych treści wymagają zaufanej ratyfikacji |
| Atak adaptacyjny | „gradient / RL zespół czerwony” | Atak, który zna obronę i optymalizuje się przeciwko niej; wymagane do uczciwej oceny |
| Łagodna instrukcja | "proszę wydrukować Tak" | Ładunek IPI, który jest semantycznie łagodny; żaden filtr słów kluczowych tego nie łapie |
| Naruszenie zakresu | „eksfiltracja między trustami” | Agent uzyskuje dostęp do danych z jednego kontekstu zaufania i wysyła je do innego |

## Dalsze czytanie

– [Informacje MDPI 17(1):54 – Badanie dotyczące pośredniego szybkiego wtrysku (styczeń 2026 r.)](https://www.mdpi.com/2078-2489/17/1/54) – Synteza za lata 2023–2025
- [Nasr i in. — The Attacker Moves Second (wspólne OpenAI/Anthropic/DeepMind, październik 2025)](https://arxiv.org/abs/2510.18108) — ocena ataku adaptacyjnego
- [Greshake i in. — Nie to, na co się zapisałeś (arXiv:2302.12173)](https://arxiv.org/abs/2302.12173) — oryginalny artykuł IPI
- [OWASP — LLM Top 10 (2025)](https://genai.owasp.org/llm-top-10/) — natychmiastowy zastrzyk w rankingu LLM01