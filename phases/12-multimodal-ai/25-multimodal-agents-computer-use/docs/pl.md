# Agenci multimodalni i korzystanie z komputera (Capstone)

> Produkt frontierowy 2026 to multimodalny agent, który odczytuje zrzuty ekranu, klika przyciski, porusza się po interfejsach internetowych, wypełnia formularze i kompleksowo realizuje przepływy pracy. SeeClick i CogAgent (2024) udowodniły, że jest to prymitywny sposób uziemienia GUI. Dodano urządzenie mobilne w interfejsie Ferret-UI. ChartAgent wprowadził wizualne wykorzystanie narzędzi do wykresów. VisualWebArena i AgentVista (2026) to punkty odniesienia, które gonią za granicami — i nawet Gemini 3 Pro i Claude Opus 4.7 uzyskują ~30% wyniku w trudnych zadaniach AgentVista. To zwieńczenie łączy każdy wątek fazy 12: percepcję (VLM w wysokiej rozdzielczości), rozumowanie (LLM z użyciem narzędzi), uziemienie (wyjście współrzędnych), pamięć długoterminową i ocenę.

**Typ:** Zwieńczenie
**Języki:** Python (stdlib, schemat akcji + szkielet pętli agenta)
**Wymagania wstępne:** Faza 12 · 05 (LLaVA), Faza 12 · 09 (Qwen-VL JSON), Faza 14 (Inżynieria agenta)
**Czas:** ~240 minut

## Cele nauczania

- Zaprojektuj multimodalną pętlę agenta: postrzegaj → powód → działaj → obserwuj → powtarzaj.
- Zbuduj schemat wyjściowy uziemienia GUI (kliknij współrzędne, wpisz tekst, przewiń, przeciągnij), który VLM może emitować jako JSON.
- Porównaj agentów wykonujących tylko zrzuty ekranu z agentami drzewa dostępności i agentami hybrydowymi.
- Skonfiguruj ocenę porównawczą agenta multimodalnego na małym wycinku VisualWebArena.

## Problem

Schemat działania witryny rezerwacyjnej: „znajdź mi lot do Tokio na 15 kwietnia, miejsce przy przejściu poniżej 800 USD, zarezerwuj”.

Agent multimodalny musi:

1. Zrób zrzut ekranu przeglądarki.
2. Przeanalizuj zrzut ekranu + adres URL + cel w planie.
3. Wykonaj akcję strukturalną: kliknij (przy x, y), wpisz „Tokio” (przy elemencie E), przewiń w dół, wybierz (przycisk radiowy).
4. Zastosuj akcję w przeglądarce.
5. Obserwuj nowy stan (kolejny zrzut ekranu).
6. Powtarzaj, aż zadanie zostanie ukończone.

Każdy krok jest multimodalnym wywołaniem VLM. Dane wyjściowe VLM muszą być analizowalne w formacie JSON. Błędy nakładają się na poszczególne etapy, więc odzyskiwanie ma znaczenie.

## Koncepcja

### Uziemienie GUI — prymitywne

Uziemienie GUI to: mając zrzut ekranu i instrukcję w języku naturalnym, wyprowadź współrzędne (x, y), aby kliknąć (lub wykonać inną akcję).

SeeClick (arXiv:2401.10935) był pierwszym otwartym wynikiem na dużą skalę: dostrojenie VLM na syntetycznych i rzeczywistych danych GUI, współrzędne wyjściowe w postaci zwykłego tekstu. Fabryka.

CogAgent (arXiv:2312.08914) dodał kodowanie w wysokiej rozdzielczości 1120x1120 dla gęstych interfejsów użytkownika. Wynik: ~84% w nawigacji internetowej.

Ferret-UI (arXiv:2404.05719) koncentruje się na mobilnych interfejsach użytkownika i integruje się z danymi dostępności systemu iOS.

Format wyjściowy to zwykle JSON:

```json
{"action": "click", "x": 384, "y": 220, "element_desc": "Search button"}
```

`element_desc` pomaga w odzyskaniu danych: jeśli współrzędne dryfują pomiędzy zrzutami ekranu, wskazówka semantyczna pozwala systemowi ponownie uziemić się.

### Schematy działania

Typowy schemat działania składa się z 6-10 typów działań:

- `click`: (x, y)
- `type`: (tekst, x?, y?)
- `scroll`: (kierunek, ilość)
- `drag`: (x0, y0, x1, y1)
- `select`: (indeks_opcji)
- `hover`: (x, y)
- `navigate`: (url)
- `wait`: (ms)
- `done`: (sukces, wyjaśnienie)

Agent emituje jedną akcję na krok. Opakowanie przeglądarki wykonuje się i zwraca nowy stan.

### Tylko zrzut ekranu a drzewo dostępności

Dwa tryby wprowadzania:

- Tylko zrzut ekranu: pełny obraz, brak informacji strukturalnych. Najbardziej ogólne; działa na dowolnej aplikacji.
- Drzewo dostępności: uporządkowane informacje o dostępności DOM / iOS. Znacznie bardziej niezawodne w przypadku uziemienia; działa tam, gdzie drzewo jest dostępne.
- Hybrydowe: zarówno z drzewem jako niezawodną podstawą działań atomowych, jak i zrzutem ekranu dla kontekstu semantycznego.

Agenci produkcyjni, jeśli to możliwe, korzystają z rozwiązań hybrydowych. Automatyzacja przeglądarki (Selenium + dostępność) zawsze ma drzewo; aplikacje komputerowe czasami to robią.

### Pamięć o długim horyzoncie

20-etapowy przepływ pracy generuje 20 zrzutów ekranu. Kontekst VLM zapełnia się szybko. Trzy strategie kompresji:

- Łańcuch podsumowań: po każdych 5 krokach podsumuj, co się wydarzyło, upuść stare zrzuty ekranu.
- Pomiń klatkę: zachowaj pierwszy, ostatni i co trzeci zrzut ekranu.
- Dziennik zarejestrowany przez narzędzie: wykonaj działania, prowadź dziennik tekstowy tego, co zostało zrobione; nie oglądaj ponownie starych zrzutów ekranu.

Interfejs API Claude'a do użytku komputerowego wykorzystuje wzór dziennika. Prostsze, bardziej niezawodne.

### Użycie narzędzi wizualnych

ChartAgent (arXiv:2510.04514) wprowadza narzędzie wizualne umożliwiające zrozumienie wykresów: kadrowanie, powiększanie, OCR, wywoływanie zewnętrznego wykrywania. Agent może wypisać „przytnij do regionu (100, 200, 300, 400), a następnie wywołaj OCR” jako wywołanie narzędzia. Narzędzie zwraca tekst; VLM kontynuuje rozumowanie.

Ten wzorzec uogólnia: monitowanie o zestaw znaków, adnotacja regionu i zewnętrzne narzędzia do wykrywania – wszystkie pasują do tego samego schematu „wyprowadź wywołanie narzędzia, otrzymaj ustrukturyzowaną odpowiedź”.

### Punkty odniesienia na rok 2026

- ScreenSpot-Pro. Podstawa GUI na ~1 tys. zrzutów ekranu z Internetu. Otwórz SOTA Qwen2.5-VL-72B ~85%. Granica ~90%.
- VisualWebArena. Kompleksowe zadania internetowe (sklep, forum, ogłoszenia). Otwórz SOTA ~20%. Gemini 3 Pro ~27%.
- AgentVista (arXiv:2602.23166). Najtrudniejszy benchmark na rok 2026. Realistyczne przepływy pracy w 12 domenach. Modele graniczne uzyskują wynik 27–40%; modele otwarte 10-20%.
- WebArena/Sklep internetowy. Starsze benchmarki; nasycony granicą.

### Dlaczego wciąż jest to trudne

Wąskie gardła w wydajności agenta:

1. Wizualne uziemienie w małej skali. „Kliknij mały X” często kończy się niepowodzeniem w rozdzielczości mobilnej.
2. Planowanie długoterminowe. Po 10 akcjach agent oddala się od celu.
3. Odzyskiwanie błędów. Gdy kliknięcie się nie powiedzie (zły przycisk), wykrywanie i odzyskiwanie danych rzadko jest trenowane.
4. Kontekst międzystronicowy. Przeskakiwanie pomiędzy zakładkami lub długimi formularzami traci stan.

Kierunki badań: architektury pamięci, jawne przeplanowanie, weryfikacja multimodalna (dopasowanie zrzutów ekranu dla powodzenia działania).

### Budowa zwieńczenia

Najważniejsze zadanie: zbuduj agenta do obsługi komputera, który:

1. Odczytuje kod HTML + zrzut ekranu fałszywej strony witryny rezerwacji.
2. Planuje sekwencję kilkuetapową: szukaj → wybierz → wypełnij formularz → wyślij.
3. Emituje akcje JSON pasujące do schematu akcji.
4. Ocenia ustalony segment składający się z 10 zadań.

Lekcja zawiera kod szkieletu, który można łatwo rozszerzyć na prawdziwą przeglądarkę.

## Użyj tego

`code/main.py` to zwieńczenie rusztowania:

- Definicja schematu akcji JSON (10 akcji).
- Próbuj stan przeglądarki jako dyktowany.
- Szkielet pętli agenta: stan odbioru, akcja emitowania, zastosowanie, pętla.
- Mini-benchmark składający się z 10 zadań (strony syntetyczne) do pomiaru kompleksowego wskaźnika sukcesu.
- Hak do odzyskiwania błędów w przypadku niepowodzenia akcji.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-multimodal-agent-designer.md`. Biorąc pod uwagę produkt do użytku komputerowego (domena, zestaw działań, cel oceny), projektuje pełną pętlę agenta, strategię pamięci, tryb uziemienia i oczekiwany wynik testu porównawczego.

## Ćwiczenia

1. Rozszerz schemat akcji o narzędzie `screenshot_region` (przytnij + powiększ). Jakie zadania przynoszą korzyści?

2. Przeczytaj AgentVista (arXiv:2602.23166). Opisz kategorię najtrudniejszych zadań i dlaczego modele pionierskie wciąż zawodzą.

3. Kompresja pamięci o długim horyzoncie: zaprojektuj łańcuch podsumowań zawierający ≤4 zrzutów ekranu przechowywanych na żywo i dowolną liczbę zarejestrowanych.

4. Zbuduj mechanizm odzyskiwania po błędzie: co agent robi dalej w przypadku niepowodzenia działania (nie znaleziono przycisku)?

5. Porównaj Claude 4.7 zawierający tylko zrzut ekranu z hybrydowym zrzutem ekranu + drzewem dostępności Qwen2.5-VL w 10 zadaniach sieciowych. Które wygrywa w jakich zadaniach?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|--------------------------------------|
| Uziemienie GUI | „Kliknij współrzędne” | Modeluj dane wyjściowe (x,y) dla celu instrukcji na zrzucie ekranu |
| Schemat działania | „Definicje narzędzi” | Opis JSON prawidłowych akcji (kliknij, wpisz, przewiń, przeciągnij) |
| Drzewo dostępności | „Strukturalny DOM” | Hierarchia interfejsu użytkownika do odczytu maszynowego z interfejsów API przeglądarki/iOS |
| Agent hybrydowy | „Zrzut ekranu + drzewo” | Wykorzystuje zarówno obraz, jak i informacje strukturalne; bardziej niezawodny niż którykolwiek z osobna |
| Użycie narzędzia wizualnego | „Powiększ/przytnij/wykryj” | Agent wywołuje zewnętrzne narzędzia wizyjne (OCR, wykrywanie) w połowie planu |
| Łańcuch podsumowujący | „Kompresja pamięci” | Okresowe podsumowania tekstowe zastępują długą historię zrzutów ekranu |
| VisualWebArena | „Ławka internetowa E2E” | Benchmark 2024 dla kompleksowych zadań internetowych |
| AgentVista | „Twarda ławka 2026” | Realistyczne przepływy pracy w 12 domenach; nawet Gemini 3 Pro osiąga ~30% |

## Dalsze czytanie

- [Cheng i in. — SeeClick (arXiv:2401.10935)](https://arxiv.org/abs/2401.10935)
- [Hong i in. — CogAgent (arXiv:2312.08914)](https://arxiv.org/abs/2312.08914)
- [Ty i in. — Ferret-UI (arXiv:2404.05719)](https://arxiv.org/abs/2404.05719)
- [ChartAgent (arXiv:2510.04514)](https://arxiv.org/abs/2510.04514)
- [Koh i in. — VisualWebArena (arXiv:2401.13649)](https://arxiv.org/abs/2401.13649)
- [AgentVista (arXiv:2602.23166)](https://arxiv.org/abs/2602.23166)