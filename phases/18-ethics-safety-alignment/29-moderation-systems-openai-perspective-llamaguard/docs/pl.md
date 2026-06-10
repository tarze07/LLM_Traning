# Systemy moderacji — OpenAI, Perspective, Llama Guard

> Systemy moderacji produkcji operacjonalizują zasady bezpieczeństwa określone w lekcjach 12-16. OpenAI Moderation API: `omni-moderation-latest` (2024) zbudowany na GPT-4o klasyfikuje tekst i obrazy w jednym wywołaniu; 42% lepsze w przypadku wielojęzycznego zestawu testowego niż poprzednia wersja; schemat odpowiedzi zwraca 13 kategorii boolowskich — molestowanie, molestowanie/groźby, nienawiść, nienawiść/groźby, nielegalne, nielegalne/brutalne, samookaleczenie, samookaleczenie/zamiar, samookaleczenie/instrukcje, seksualne, seksualne/nieletni, przemoc, przemoc/grafika; bezpłatny dla większości programistów. Wzorce warstwowe: moderacja danych wejściowych (przed generacją), moderacja wyników (po generacji), moderacja niestandardowa (reguły domeny). Asynchroniczne połączenia równoległe ukrywają opóźnienia; odpowiedzi zastępcze na fladze. Llama Guard 3/4 (Lekcja 16): 14 zagrożeń MLCommons, nadużycie interpretera kodu, 8 języków (v3), wiele obrazów (v4). Perspective API (Google Jigsaw): ocena toksyczności sprzed fali LLM jako moderatora; głównie toksyczność jednowymiarowa z wariantami ciężkiej toksyczności/obrazy/wulgaryzmów; punkt odniesienia dla badań nad moderacją treści. Wycofanie: usługa Azure Content Moderator została wycofana w lutym 2024 r., wycofana w lutym 2027 r. i zastąpiona przez usługę Azure AI Content Safety.

**Typ:** Kompilacja
**Języki:** Python (stdlib, trójwarstwowa uprząż moderacyjna)
**Wymagania wstępne:** Faza 18 · 16 (Strażnik Lamy / Garak / PyRIT)
**Czas:** ~60 minut

## Cele nauczania

- Opisz taksonomię kategorii interfejsu API OpenAI Moderation i czym różni się ona od zestawu MLCommons Llama Guard 3.
- Opisz trzy wzorce warstw moderacji (wejście, wyjście, niestandardowe) i podaj po jednym trybie awarii każdego z nich.
- Opisz pozycję Perspective API jako punktu odniesienia sprzed ery LLM i dlaczego nadal jest ona wykorzystywana w badaniach.
— Podaj harmonogram wycofania platformy Azure.

## Problem

Lekcje 12-16 opisują ataki i narzędzia obronne. Lekcja 29 omawia wdrożone systemy moderacji, które uruchamiają zabezpieczenia na powierzchni, gdzie użytkownicy dotykają produktu. Wzór trójwarstwowy to domyślna konfiguracja na rok 2026.

## Koncepcja

### API moderacji OpenAI

`omni-moderation-latest` (2024). Zbudowany na GPT-4o. Klasyfikuje tekst i obrazy w jednym wywołaniu. Bezpłatna dla większości programistów.

Kategorie (13 wartości logicznych w schemacie odpowiedzi):
- molestowanie, molestowanie/groźby
- nienawiść, nienawiść/groźba
- samookaleczenie, samookaleczenie/zamierzenie, samookaleczenie/instrukcje
- seksualne, seksualne/nieletni
- przemoc, przemoc/grafika
- nielegalne, nielegalne/brutalne

Obsługa multimodalna dotyczy `violence`, `self-harm` i `sexual`, ale nie `sexual/minors`; reszta to tylko tekst.

W przypadku wiązki kodu w `code/main.py` zwijamy podkategorie `/threatening`, `/intent`, `/instructions` i `/graphic` do ich rodzice na najwyższym poziomie za prostotę pedagogiczną. Kod produkcyjny powinien wykorzystywać pełny schemat 13 kategorii.

42% lepiej w przypadku wielojęzycznego zestawu testowego niż punkt końcowy moderacji poprzedniej generacji. Wyniki według kategorii; aplikacje ustalają progi.

### Strażnik Lamy 3/4

Omówione w lekcji 16. 14 kategorii zagrożeń MLCommons (zorganizowanych inaczej niż 13 wartości logicznych schematu odpowiedzi OpenAI). Obsługuje 8 języków (v3). Llama Guard 4 (kwiecień 2025 r.) jest natywnie multimodalny, 12B.

Taksonomie OpenAI i Llama Guard pokrywają się, ale różnią. OpenAI ma „nielegalne” jako szeroką kategorię; Llama Guard ma osobno „przestępstwa z użyciem przemocy” i „przestępstwa bez użycia przemocy”. Wdrożenia wybierane są na podstawie dopasowania do taksonomii zasad.

### Perspektywa API (Google Jigsaw)

System punktacji toksyczności sprzed fali LLM w roli moderatora (przed 2020 r.). Kategorie: TOKSYCZNOŚĆ, POWAŻNA_TOKSYCZNOŚĆ, OBRAŻA, WŁAŚCIWOŚCI, ZAGROŻENIE, IDENTITY_ATTACK. Jednowymiarowy wynik główny (TOXICITY) z wariantami podwymiarowymi.

Powszechnie stosowany jako punkt odniesienia w badaniach nad moderacją treści, ponieważ interfejs API jest stabilny, udokumentowany i zawiera dane kalibracyjne pochodzące z lat. W przypadku nowoczesnych zastosowań związanych z LLM zazwyczaj lepiej pasuje moderacja Llama Guard lub OpenAI.

### Wzór trójwarstwowy

1. **Moderacja wprowadzania danych.** Klasyfikuj podpowiedzi użytkownika przed wygenerowaniem. Odrzuć, jeśli został oznaczony. Opóźnienie: jedno wywołanie klasyfikatora.
2. **Moderacja wyników.** Sklasyfikuj wyniki modelu przed dostawą. Zastąp odmową, jeśli została oznaczona. Opóźnienie: jedno wywołanie klasyfikatora po generacji.
3. **Moderacja niestandardowa.** Reguły specyficzne dla domeny (regex, listy dozwolonych, zasady biznesowe). Działa na wejściu lub wyjściu.

Te trzy warstwy są z założenia sekwencyjne: moderowanie danych wejściowych musi zostać zakończone przed generacją, a moderowanie wyjściowe odbywa się po wygenerowaniu. W obrębie warstwy obowiązuje paralelizm — jednoczesne uruchomienie wielu klasyfikatorów (np. Moderacja OpenAI + Llama Guard + Perspective) na tym samym tekście powoduje ukrycie opóźnienia poszczególnych klasyfikatorów. W ramach opcjonalnej optymalizacji może zostać wyświetlona odpowiedź zastępcza („jedna chwila, sprawdzanie…”) po zakończeniu moderowania danych wejściowych i odroczeniu przesyłania strumieniowego tokenu-1. Zachowanie flagi można konfigurować: odmowa, oczyszczenie, przekazanie do sprawdzenia przez człowieka.

### Tryby awarii

- **Tylko wejście.** Nie wychwytuje halucynacji wyjściowych (Lekcja 12-14 ataki kodujące omijają klasyfikatory wejściowe).
- **Tylko dane wyjściowe.** Umożliwia dotarcie do modelu dowolnym sygnałom wejściowym; zwiększa koszty; ujawnia napastnikowi wewnętrzne rozumowanie.
- **Tylko niestandardowe.** Brak solidności w różnych kategoriach; wyrażenia regularne są kruche.

Opcja warstwowa jest ustawieniem domyślnym. Pasek i szelki.

### Wycofanie platformy Azure

Azure Content Moderator: przestarzałe w lutym 2024 r., wycofane w lutym 2027 r. Zastąpione przez usługę Azure AI Content Safety, która jest oparta na LLM i integruje się z platformą Azure OpenAI. Migracja to projekt na poziomie pola na lata 2024–2027 dotyczący wdrożeń platformy Azure.

### Gdzie to pasuje do fazy 18

Lekcja 16 omawia narzędzia moderacyjne w kontekście drużyny czerwonej. Lekcja 29 dotyczy wdrożenia moderacji. Lekcja 30 kończy się obecnymi dowodami dotyczącymi możliwości podwójnego zastosowania.

## Użyj tego

`code/main.py` tworzy trójwarstwową wiązkę moderacji: moderator wprowadzania (słowo kluczowe + wynik kategorii), moderator wyników (ten sam klasyfikator na wyjściu), moderator niestandardowy (reguły domeny). Możesz przepuszczać dane wejściowe i obserwować, która warstwa co przechwytuje.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-moderation-stack.md`. Biorąc pod uwagę wdrożenie, zaleca konfigurację stosu moderacji: który klasyfikator na wejściu, który na wyjściu, jakie reguły niestandardowe i co ocenia w przypadkach brzegowych.

## Ćwiczenia

1. Uruchom `code/main.py`. Przeprowadź łagodny, graniczny i szkodliwy sygnał wejściowy przez wszystkie trzy warstwy. Zgłoś, która warstwa zostanie uruchomiona dla każdej z nich.

2. Rozszerz zakres o punktację toksyczności w stylu Perspective API dla określonej kategorii. Porównaj zachowanie progowe z wynikiem w kategorii.

3. Przeczytaj dokumentację API OpenAI Moderation API i listę kategorii Llama Guard 3. Przypisz każdą kategorię OpenAI do najbliższych kategorii Llama Guard. Zidentyfikuj trzy kategorie, które nie dają dokładnego odwzorowania.

4. Zaprojektuj stos moderacji dla wdrożenia asystenta kodu (np. GitHub Copilot). Zidentyfikuj najbardziej i najmniej istotne kategorie i zaproponuj niestandardowe reguły.

5. Usługa Azure Content Moderator odchodzi w lutym 2027 r. Zaplanuj migrację do usługi Azure AI Content Safety. Zidentyfikuj element migracji obarczony najwyższym ryzykiem.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|--------------------------------------|
| Moderacja OpenAI | „omni-moderacja-najnowsza” | Klasyfikator 13 kategorii (tekstowy) oparty na GPT-4o z częściową obsługą multimodalną |
| Perspektywa API | „Toksyczność Google Jigsaw” | Podstawowa ocena toksyczności sprzed ery LLM |
| Strażnik Lamy | „Kategoria MLCommons 14” | Klasyfikator zagrożeń Meta (wersja 3: tekst 8B, 8 języków; wersja 4: 12B, multimodalny) |
| Moderacja wejściowa | „filtr przedgeneracyjny” | Klasyfikator w podpowiedzi użytkownika przed wywołaniem modelu |
| Moderacja wyników | „filtr pogeneracyjny” | Klasyfikator na wyjściu modelu przed dostawą |
| Moderacja niestandardowa | "reguły domeny" | Reguły specyficzne dla wdrożenia (regex, lista dozwolonych, zasady) |
| Moderacja warstwowa | „wszystkie trzy warstwy” | Standardowy wzorzec wdrożenia produkcyjnego |

## Dalsze czytanie

- [Dokumentacja API OpenAI Moderation API](https://platform.openai.com/docs/api-reference/moderations) — punkt końcowy moderacji omni
– [Meta PurpleLlama + Llama Guard](https://github.com/meta-llama/PurpleLlama) — repozytorium Llama Guard
- [Google Jigsaw Perspective API](https://perspectiveapi.com/) — ocena toksyczności
— [Bezpieczeństwo treści Azure AI](https://learn.microsoft.com/en-us/azure/ai-services/content-safety/) — wymiana platformy Azure