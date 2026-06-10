# Narzędzia zespołu Red — Garak, Llama Guard, PyRIT

> Trzy narzędzia produkcyjne stanowią ramę zespołu czerwonych na rok 2026. Llama Guard (Meta) — klasyfikator Llama-3.1-8B dostosowany do 14 kategorii zagrożeń MLCommons; Llama Guard 4 2025 to natywnie multimodalny klasyfikator 12B wycięty z Llama 4 Scout. Garak (NVIDIA) — skaner podatności LLM typu open source ze statycznymi, dynamicznymi i adaptacyjnymi sondami pod kątem halucynacji, wycieków danych, natychmiastowego wstrzyknięcia, toksyczności i jailbreaków. PyRIT (Microsoft) — wieloturowe kampanie drużyny czerwonej z Crescendo, TAP i niestandardowymi łańcuchami konwerterów do głębokiej eksploatacji. Llama Guard 3 jest udokumentowana w „Llama 3 Herd of Models” Meta (arXiv:2407.21783); Strażnik Lamy 3-1B-INT4 w arXiv:2411.17713; Architektura sondy Garaka na github.com/NVIDIA/garak. Narzędzia te stanowią interfejs produkcyjny na rok 2026 pomiędzy badaniami zespołu czerwonego (lekcje 12–15) a wdrażaniem (lekcja 17+).

**Typ:** Kompilacja
**Języki:** Python (stdlib, symulator architektury narzędzi i makieta klasyfikatora w stylu Llama Guard)
**Wymagania wstępne:** Faza 18 · 12-15 (jailbreaki i IPI)
**Czas:** ~75 minut

## Cele nauczania

- Opisz pozycję Llama Guard 3/4 w stosie bezpieczeństwa: klasyfikator wejściowy, klasyfikator wyjściowy lub oba.
- Wymień 14 kategorii zagrożeń MLCommons i podaj jedną nieoczywistą (nadużycie interpretera kodów).
- Opisać architekturę sondy Garaka: sondy, detektory, wiązki przewodów.
- Opisz wieloturową strukturę kampanii PyRIT i jej współpracę z sondami Garak.

## Problem

Lekcje 12-15 przedstawiają powierzchnię ataku. Wdrożenia produkcyjne wymagają powtarzalnej i skalowalnej oceny. W roku 2026 dominują trzy narzędzia: Llama Guard (klasyfikator obronny), Garak (skaner), PyRIT (organizator kampanii). Każdy z nich jest ukierunkowany na inną warstwę cyklu życia drużyny czerwonych.

## Koncepcja

### Strażnik Lamy (Meta)

Llama Guard 3 to model Llama-3.1-8B dostosowany do klasyfikacji wejść/wyjść w 14 kategoriach MLCommons AILuminate:
- Przestępstwa z użyciem przemocy, przestępstwa bez użycia przemocy, przestępstwa na tle seksualnym, CSAM, zniesławienie
- Specjalistyczne porady, prywatność, własność intelektualna, masowa broń, nienawiść
- Samobójstwo/samookaleczenie, treści o charakterze seksualnym, wybory, nadużycie interpretera kodów

Obsługuje 8 języków. Sposób użycia: umieść przed LLM (moderacja wejścia), po LLM (moderacja wyjścia) lub jedno i drugie. Obydwa zastosowania generują różne rozkłady szkoleń — Llama Guard 3 jest statkiem jako pojedynczy model obsługujący oba.

Llama Guard 3-1B-INT4 (arXiv:2411.17713, 440MB, ~30 tokenów/s na mobilnym procesorze) to skwantowany wariant brzegowy.

Llama Guard 4 (kwiecień 2025) to 12B, natywnie multimodalny, przycięty z Llama 4 Scout. Zastępuje poprzedników tekstu 8B i wizji 11B jednym klasyfikatorem, który przetwarza tekst i obrazy.

### Garak (NVIDIA)

Skaner podatności na oprogramowanie typu open source. Architektura:
- **Sondy.** Generatory ataków na halucynacje, wycieki danych, natychmiastowe wstrzyknięcia, toksyczność, jailbreaki. Statyczne (stałe podpowiedzi), dynamiczne (generowane podpowiedzi), adaptacyjne (reagują na docelowe dane wyjściowe).
- **Detektory.** Oceń wyniki pod względem oczekiwanych trybów awarii — toksycznych, wyciekających, jailbreakowanych.
- **Wiązki.** Zarządzaj parami sonda-detektor, prowadź kampanie, generuj raporty.

TrustyAI integruje Garaka z tarczami Llama-Stack (klasyfikator wejściowy Prompt-Guard-86M, klasyfikator wyjściowy Llama-Guard-3-8B) w celu kompleksowej oceny chronionego celu. Punktacja oparta na poziomach (TBSA) zastępuje binarny wynik pozytywny/negatywny — model może przejść pozytywnie na poziomie ważności 3 i zakończyć się niepowodzeniem na poziomie ważności 5 w tej samej sondzie.

### PyRIT (Microsoft)

Zestaw narzędzi do identyfikacji ryzyka w języku Python. Wieloturowe kampanie drużyny czerwonej. Zbudowany wokół:
- **Konwertery.** Przekształć podpowiedź zalążkową — parafrazuj, koduj, tłumacz, odgrywaj role.
- **Orkiestratorzy.** Uruchom kampanię: Crescendo (eskalacja), TAP (rozgałęzianie), RedTeaming (pętla niestandardowa).
- **Punktacja.** LLM jako sędzia lub klasyfikator jako sędzia.

PyRIT jest cięższym kuzynem Garaka. Garak obsługuje tysiące sond jednoobrotowych; PyRIT prowadzi głębokie, wieloobrotowe kampanie zaprojektowane w celu przełamania określonych trybów awarii.

### Stos

Umieść Llamę Guard po obu stronach modelu. Uruchamiaj Garaka co noc w celu uzyskania regresji. Uruchom PyRIT dla kampanii przedpremierowych. Jest to domyślna konfiguracja na rok 2026 dla większości wdrożeń produkcyjnych.

### Pułapki w ocenie

- **Tożsamość sędziego.** Wszystkie trzy narzędzia mogą korzystać z sędziego LLM; ocenić dyski kalibracyjne zgłoszone ASR (lekcja 12). Określ sędziego obok narzędzia.
- **Sonda nieaktualności.** Garak bada wiek w miarę łatania modeli. Sondy adaptacyjne (w kształcie PAR) starzeją się wolniej niż sondy statyczne.
- **FPR Llama Guard dotyczący łagodnych treści.** Wczesne wersje Llama Guard nadmiernie zgłaszały treści polityczne i LGBTQ+; Kalibracje Llama Guard 3/4 zostały ulepszone, ale nie są kalibrowane przy każdym rozmieszczeniu.

### Gdzie to pasuje do fazy 18

Lekcje 12-15 to rodziny ataków. Lekcja 16 to oprzyrządowanie produkcyjne. Lekcja 17 (WMDP) to ocena możliwości podwójnego zastosowania. Lekcja 18 to graniczne ramy bezpieczeństwa, które obejmują te narzędzia w strukturze polityki.

## Użyj tego

`code/main.py` buduje zabawkowy klasyfikator w stylu Llama Guard (słowo kluczowe + cechy semantyczne w 14 kategoriach), zabawkową uprząż Garak (pętla sonda-detektor) i wieloobrotowy łańcuch konwertera w stylu PyRIT. Możesz uruchomić te trzy narzędzia względem fałszywego celu i obserwować różne sygnatury pokrycia.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-red-team-stack.md`. Biorąc pod uwagę opis wdrożenia, wskazuje, które z trzech narzędzi jest odpowiednie, co należy skonfigurować w każdym z nich i jaką częstotliwość regresji należy uruchomić.

## Ćwiczenia

1. Uruchom `code/main.py`. Porównaj współczynnik wykrywania klasyfikatora typu Llama-Guard w atakach jedno- i wieloturowych.

2. Zaimplementuj nową sondę Garak: szkodliwe żądanie zakodowane w formacie Base64. Zmierz jego wykrywanie za pomocą klasyfikatora typu Llama-Guard.

3. Rozszerz łańcuch konwerterów w stylu PyRIT o konwerter „przetłumacz na francuski, a następnie sparafrazuj”. Ponownie zmierz skuteczność ataku.

4. Przeczytaj listę kategorii zagrożeń Llama Guard 3. Zidentyfikuj dwie kategorie, w przypadku których dane szkoleniowe w realistyczny sposób generowałyby wysoki odsetek wyników fałszywie dodatnich w przypadku legalnych treści programistów.

5. Porównaj zasady projektowania Garaka i PyRIT. Argumentuj za wdrożeniem, w którym każde z nich jest właściwym narzędziem.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|--------------------------------------|
| Strażnik Lamy | „klasyfikator” | Dopracowany klasyfikator bezpieczeństwa Llama-3.1-8B/4-12B z 14 kategoriami zagrożenia |
| Garak | "skaner" | Skaner luk w zabezpieczeniach typu open source firmy NVIDIA; sondy, detektory, wiązki |
| PyRIT | „narzędzie kampanii” | Microsoft wieloobrotowy orkiestrator zespołu czerwonego; konwertery, orkiestratorzy, scoring |
| Strażnik podpowiedzi | „mały klasyfikator” | Klasyfikator natychmiastowego wtrysku 86M firmy Meta w połączeniu z Llama Guard |
| TBSA | „punktacja oparta na poziomach” | Oparta na poziomach pass/fail Garaka zastępująca wyniki binarne |
| Łańcuch konwertera | „parafraza + kodowanie + …” | Prymitywna kompozycja PyRIT do budowania ataków wieloetapowych |
| Kategorie zagrożeń MLCommons | „14 taksonomii” | Standardowa w branży taksonomia Cele Straży Lamy |

## Dalsze czytanie

– [Meta — Llama Guard 3 (w artykule Llama 3 Herd, arXiv:2407.21783)](https://arxiv.org/abs/2407.21783) — klasyfikator 8B
- [Meta — Llama Guard 3-1B-INT4 (arXiv:2411.17713)](https://arxiv.org/abs/2411.17713) — kwantyzowany klasyfikator mobilny
- [NVIDIA Garak — GitHub](https://github.com/NVIDIA/garak) — repozytorium i dokumentacja skanera
- [Microsoft PyRIT — GitHub](https://github.com/Azure/PyRIT) — zestaw narzędzi kampanii