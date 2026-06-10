# Testy porównawcze: WebArena i OSWorld

> WebArena testuje możliwości agenta internetowego w czterech samodzielnie hostowanych aplikacjach. OSWorld testuje możliwości agenta komputerowego w systemach Ubuntu, Windows i macOS. W momencie premiery (2023–2024) oba wykazały dużą przepaść między najlepszymi w swojej klasie agentami a ludźmi. Różnica się zmniejsza; tryby awarii nie uległy zmianie.

**Typ:** Ucz się
**Języki:** Python (stdlib)
**Wymagania wstępne:** Faza 14 · 19 (SWE-bench, GAIA)
**Czas:** ~60 minut

## Cele nauczania

- Opisz cztery samodzielnie hostowane aplikacje WebArena i dlaczego ocena oparta na wykonaniu jest istotna.
- Wyjaśnij, dlaczego OSWorld używa zrzutów ekranu prawdziwego systemu operacyjnego zamiast interfejsów API ułatwień dostępu.
- Wymień dwa podstawowe tryby awarii OSWorld: uziemienie GUI i wiedza operacyjna.
- Podsumuj, co OSWorld-G i OSWorld-Human dodają do podstawowego testu porównawczego.

## Problem

Agenci generalistyczni mogą wywoływać narzędzia. Czy mogą sprawić, że przeglądarka wykona 20 kliknięć, aby zakończyć zakupy? Czy mogą skonfigurować system Linux przy użyciu wyłącznie klawiatury i myszy? Oto pytania, na które odpowiadają WebArena i OSWorld.

## Koncepcja

### WebArena (Zhou i in., ICLR 2024)

- 812 długoterminowych zadań w czterech hostowanych aplikacjach internetowych: witryna zakupów, forum, narzędzie programistyczne podobne do GitLab, biznesowy CMS.
- Plus narzędzia: mapa, kalkulator, notatnik.
- Ocena opiera się na wykonaniu poprzez API siłowni — czy złożono zamówienie, czy problem został zamknięty, czy strona CMS została zaktualizowana?
- W chwili premiery: najlepszy agent GPT-4 osiągnął 14,41% sukcesu w porównaniu z człowiekiem 78,24%.

Ramy hostowane na własnym serwerze mają znaczenie — test porównawczy nie jest zawodny, ponieważ aplikacje docelowe są przypięte i odtwarzalne.

### Rozszerzenia

- **VisualWebArena** — zadania o charakterze wizualnym, w których powodzenie zależy od interpretacji obrazów (zrzuty ekranu jako pierwszorzędne obserwacje).
- **TheAgentCompany** (grudzień 2024) — dodaje terminal + kodowanie; bardziej jak prawdziwe środowisko pracy zdalnej.

### OSWorld (Xie i in., NeurIPS 2024)

- 369 rzeczywistych zadań komputerowych w Ubuntu, Windows i macOS.
- Swobodna kontrola klawiatury i myszy w rzeczywistych aplikacjach.
- Zrzuty ekranu w rozdzielczości 1920×1080 jako obserwacja.
- W chwili premiery: najlepszy model 12,24% w porównaniu z człowiekiem 72,36%.

### Podstawowe tryby awarii

1. **Uziemienie GUI.** Mapowanie pikseli → elementów. Modele mają trudności z niezawodną lokalizacją elementów interfejsu użytkownika w rozdzielczości 1920 × 1080.
2. **Wiedza operacyjna.** Które menu zawiera ustawienia, jaki skrót klawiaturowy, który panel preferencji. Ogon wiedzy, który ludzie budują latami.

### Dalsze działania

- **OSWorld-G** — 564-próbkowy zestaw uziemiający + zestaw szkoleniowy Jedi. Rozkłada uziemienie na planowanie, dzięki czemu można je mierzyć osobno.
- **OSWorld-Human** — ręcznie wybrane złote trajektorie akcji. Pokazuje, że najlepsi agenci wykorzystują 1,4–2,7 razy więcej kroków niż to konieczne (luka między trajektorią a efektywnością).

### Dlaczego to ma znaczenie

Korzystanie z komputera Claude, OpenAI CUA, korzystanie z komputera Gemini 2.5 (lekcja 21) – wszystkie te elementy są trenowane na obciążeniach kształtowanych przez WebArena i OSWorld. Punkty odniesienia są celem; Modele produkcyjne są wysłaną odpowiedzią.

### Gdzie benchmarking się nie udaje

- **Ewaluacja wyłącznie na podstawie zrzutów ekranu.** OSWorld działa na podstawie zrzutów ekranu; ocenianie agenta korzystającego z DOM lub interfejsów API dostępności w OSWorld pomija wyzwanie związane z uziemieniem.
- **Ignorowanie długości trajektorii.** Tylko wskaźnik sukcesu pomija stopień nieefektywności wynoszący 1,4–2,7x na powierzchniach OSWorld-Human.
- **Nieaktualne aplikacje hostowane samodzielnie.** Aplikacje WebArena przypinają określone wersje; aktualizacja bez ponownego sprawdzania przerywa porównywalność.

## Zbuduj to

`code/main.py` implementuje zabawkową uprząż agenta internetowego:

- Minimalna maszyna stanu „aplikacja zakupowa”: list_items, add_to_cart, checkout.
- Złote trajektorie dla 3 zadań.
- Agent skryptowy, który wykonuje każde zadanie.
- Ocena oparta na wykonaniu (kontrola stanu) i metryka efektywności trajektorii (kroki vs złoto).

Uruchom to:

```
python3 code/main.py
```

Wynik: wskaźnik powodzenia każdego zadania i efektywność trajektorii, odzwierciedlający metodologię OSWorld-Human.

## Użyj tego

- **WebArena Verified** hostowane samodzielnie w wewnętrznym klastrze w celu ciągłej oceny.
- **OSWorld** we flocie maszyn wirtualnych dla agentów stacjonarnych.
- **Agenci korzystający z komputera** (Lekcja 21) — Claude, OpenAI CUA, Gemini — wszyscy przeszkoleni w zakresie takich obciążeń.
- **Twoje własne przepływy produktów** — rejestruj złote trajektorie dla swoich 20 najważniejszych zadań; co tydzień wystawiaj przeciwko nim agentów.

## Wyślij to

`outputs/skill-web-desktop-harness.md` tworzy wiązkę agenta internetowego/komputerowego z metryką wydajności opartą na wykonaniu i trajektorii.

## Ćwiczenia

1. Rozszerz uprząż zabawki o drugą aplikację (forum). Napisz 3 zadania i złote trajektorie.
2. Dodaj raporty dotyczące efektywności trajektorii dla każdego zadania. Czy na twojej zabawce agent jest 1x, 2x czy 3x nad złotem?
3. Wdrożyj narzędzie „odwracające uwagę” – takie, którego nigdy nie używa złota trajektoria. Czy agent skryptowy ulega pokusie?
4. Przeczytaj OSWorld-G. Jak oddzieliłbyś awarie uziemienia od awarii planowania we własnych ewaluacjach?
5. Przeczytaj plik README aplikacji WebArena. Co się dzieje po uaktualnieniu jednej z przypiętych wersji aplikacji?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| WebArena | „Benchmark agenta internetowego” | 812 zadań w 4 hostowanych aplikacjach; ocena stylu siłowni |
| VisualWebArena | „Wizualna WebArena” | Wizualnie ugruntowana WebArena; zrzuty ekranu są obserwacjami |
| OSŚwiat | „Benchmark agenta pulpitu” | 369 zadań na prawdziwym Ubuntu/Windows/macOS |
| Uziemienie GUI | „Mapowanie pikseli na elementy” | Model lokalizujący elementy interfejsu użytkownika w rozdzielczości 1920x1080 |
| Wiedza operacyjna | „Wiedza o systemie operacyjnym” | Które menu, jaki skrót, który panel preferencji |
| OSWorld-G | „Zestaw uziemiający” | 564 próbki tylko do uziemienia + zestaw treningowy |
| OSWorld-Human | „Złote trajektorie” | Ręczne sekwencje działań eksperckich w celu pomiaru efektywności |
| Wydajność trajektorii | „Kroki nad złotem” | Liczba kroków agenta podzielona przez minimum ludzkie |

## Dalsze czytanie

- [Zhou i in., WebArena (arXiv:2307.13854)](https://arxiv.org/abs/2307.13854) — test sieciowy czterech aplikacji
— [Xie i in., OSWorld (arXiv:2404.07972)](https://arxiv.org/abs/2404.07972) — test porównawczy komputerów stacjonarnych z różnymi systemami operacyjnymi
– [Anthropic, Wprowadzenie do korzystania z komputera](https://www.anthropic.com/news/3-5-models-and-computer-use) — możliwości Claude’a w kształcie wzorca
- [OpenAI, Agent korzystający z komputera](https://openai.com/index/computer-using-agent/) — numery OSWorld i WebArena