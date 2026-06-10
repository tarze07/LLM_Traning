# Społeczeństwo umysłu i debata wieloagentowa

> Założenie Minsky'ego z 1986 r., że inteligencja to społeczeństwo specjalistów, jest odkrywane na nowo co dekadę. W 2023 r. Du i in. przekształciło go w konkretny algorytm: wiele instancji LLM proponuje odpowiedzi, czyta nawzajem odpowiedzi, krytykuje i aktualizuje. W ciągu N rund osiągają konsensus, który pokonuje zero-shot CoT i refleksję na temat sześciu zadań związanych z rozumowaniem i faktami. Liczą się dwa ustalenia: zarówno **wielu agentów**, jak i **wiele rund** wnoszą niezależny wkład. Społeczeństwo pokonuje monolog jednego agenta; wymiana obejmująca wiele rund bije na głowę głosowanie jednym strzałem.

**Typ:** Ucz się + Buduj
**Języki:** Python (stdlib)
**Wymagania wstępne:** Faza 16 · 04 (model prymitywny)
**Czas:** ~60 minut

## Problem

Spójność własna — wielokrotne próbowanie jednego modelu i przyjęcie większości odpowiedzi — to najtańsze usprawnienie rozumowania, na jakie możesz się zdecydować. Działa, ale szybko się nasyca. Możesz podwoić próbki i nie zobaczyć kolejnego znaczącego skoku.

Debata przełamuje nasycenie. Zamiast N niezależnych próbek z jednego modelu, N agentów czyta sobie nawzajem rozumowanie i koryguje je. Korelacja między próbkami spada (nie są już i.i.d), a punkt zbieżności jest często prawidłowy tam, gdzie i.i.d. głosowanie było zdecydowanie błędne.

## Koncepcja

### Du i in. Algorytm 2023

Z arXiv:2305.14325 (ICML 2024):

1. Każdy z N agentów udziela wstępnej odpowiedzi na pytanie.
2. Dla rundy r = 2..R: każdemu agentowi pokazywane są odpowiedzi pozostałych agentów w rundzie r-1 i pytanie: „biorąc pod uwagę te odpowiedzi, podaj zaktualizowaną odpowiedź”.
3. Po rundach R, większością głosów zagłosuj na ostateczne odpowiedzi.

Artykuł sprawdza testy MMLU, GSM8K, biografii, MATH i testów porównawczych faktów. Debata konsekwentnie pokonuje CoT i autorefleksję.

### Dwa niezależne pokrętła

Ablacje z tej samej pracy:

- **Sama liczba agentów** (1 runda, większość głosów N) przewyższa pojedynczego agenta w większości zadań, ale plateau.
- **Samo liczenie rund** (1 agent widzi własne wcześniejsze rozumowanie) ledwo pomaga — znana słabość refleksji.
- **Oba razem** dają duże skoki. Wielorundowa wymiana zdań między wieloma agentami napędza zysk.

### Dlaczego to działa

Dwa mechanizmy:

1. **Narażenie na brak zgody.** Kiedy agent widzi, że inny agent wyciąga inny wniosek z łańcucha rozumowania, musi to uzasadnić lub zaktualizować. Tak czy inaczej, kontekst rundy r+1 jest bogatszy niż rundy r.
2. **Skorelowana redukcja błędów.** W przypadku spójności wewnętrznej wszystkie próbki pochodzą z tego samego modelu, więc błędy są ze sobą skorelowane — średnia daje zdecydowanie błędną odpowiedź. Różne modele lub różne nasiona są ze sobą powiązane. Różne *dyskusyjne poglądy* dalej korelują.

### Niejednorodna debata

A-HMAD i powiązane działania uzupełniające wykorzystują *różne modele podstawowe* dla różnych agentów. Debata Lama + Claude + GPT zmniejsza upadek monokultury (lekcja 26), ponieważ skorelowane błędy jednej rodziny modeli nie są wspólne dla pozostałych.

Wada: słaby model uczestniczący w debacie może sprowadzić konsensus w kierunku błędnej odpowiedzi (patrz „Czy powinniśmy popadać w szaleństwo?”, arXiv:2311.17371).

### NLSOM — rozszerzenie obsługujące 129 agentów

Zhuge i in. („Mindstorms in Natural Language-Based Societies of Mind”, arXiv:2305.17066) rozszerzył tę koncepcję na społeczeństwa liczące 129 członków. Rezultat: specjalizacja i samoorganizacja pojawiają się wraz ze skalą, a system przewyższa działanie pojedynczego agenta w zadaniach takich jak wizualne odpowiadanie na pytania.

### Tryby awarii

- **Kaskada pochlebstw.** Wszyscy agenci wybierają tego, który wydaje się najbardziej pewny siebie. Debata zapada się do najgłośniejszego głosu. Pomocne jest monitowanie o role przeciwstawne („jeden agent musi argumentować przeciwne stanowisko”).
- **Zmiana tematu.** Debaty trwające wiele rund odbiegają od pierwotnego pytania. Łagodzenie: ponownie zadaj pytanie w każdej rundzie.
- **Powiększenie obliczeń.** N agentów × R rund = N·R wywołań LLM, każdy z rosnącym kontekstem. Debata obejmująca 5 agentów i 5 rund to 25 rozmów na temat rosnącego kontekstu. Koszt jednego pytania może przekroczyć 10× pojedynczego połączenia CoT.

## Zbuduj to

`code/main.py` prowadzi debatę składającą się z 3 agentów × 3 rund na pytanie matematyczne, w której każdy agent zaczyna od innej (prawdopodobnie błędnej) odpowiedzi. Agenci są sterowani skryptami — każdy „aktualizuje” poprzez uśrednianie odpowiedzi sąsiadów ważonych według zaufania skryptu. Zbieżność jest widoczna w dzienniku runda po rundzie.

Demo pokazuje dwa kluczowe efekty:

- Pojedyncza runda wymiany przybliża agentów do prawidłowej odpowiedzi.
- Dodatkowe rundy po rundzie 2 wykazują malejące zyski (odpowiada plateau Du i in.).

Uruchom:

```
python3 code/main.py
```

## Użyj tego

`outputs/skill-debate-configurator.md` konfiguruje debatę dla nowego zadania: liczba agentów, liczba rund, heterogeniczność (ten sam model vs model mieszany), przydział ról (symetryczny vs jeden kontradyktoryjny). Szacuje również koszt tokena przed uruchomieniem.

## Wyślij to

Jeśli wyślesz debatę:

- **Cap zaokrągla się na poziomie 3.** Du i in. pokaż 3 rundy, zdobądź większość zysku. Więcej to koszt, a nie jakość.
- **Agenci ograniczający poziom na poziomie 5.** Powyżej 5 dominuje rozdęcie kontekstu i koszty.
- **Domyślnie heterogeniczny.** Co najmniej dwa różne modele podstawowe w puli.
- **Slot kontradyktoryjny.** Jeden z agentów mimo wszystko poprosił o wyrażenie zgody. Łamie pochlebstwa.
- **Zapisuj każdą rundę.** Systemy debat, które ukrywają rundy pośrednie, nie mogą być debugowane ani kontrolowane.

## Ćwiczenia

1. Uruchom `code/main.py`, następnie ustaw liczbę rund na 5 i obserwuj malejące zyski. W której rundzie kończy się dodatkowa zbieżność?
2. Dodaj czwartego agenta z rolą przeciwnika: zawsze nie zgadzaj się z obecną większością. Czy to zakłóca lub poprawia konwergencję?
3. Wykreśl (wydrukuj) wynik zgodności w każdej rundzie (ułamek agentów odpowiadających odpowiedziom większości). Kiedy osiąga wartość 1.0 i czy jest to równoznaczne z „poprawnym”?
4. Przeczytaj Du i in. Sekcja 4 Ablacje. Powtórz wynik „tylko agenci”, „tylko rundy” i „oba”, używając tego kodu.
5. Przeczytaj „Czy powinniśmy popaść w szaleństwo?” (arXiv:2311.17371) i wymień dwa warianty debaty wykraczające poza tryb okrężny – np. debata prowadzona przez sędziego, debata oparta na łańcuchu debat, kontradyktoryjna.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Społeczeństwo umysłu | „Pomysł Minsky’ego” | Inteligencja jako współpracujący specjaliści; Ramowanie z 1986 r. zostało teraz operacjonalizowane w drodze debaty LLM. |
| Debata wieloagentowa | „Agenci kłócą się” | N agentów proponuje, krytykuje się nawzajem, weryfikuje w rundach R, głosuje większością. |
| Konsensus | „Zgadzają się” | Nie prawda epistemiczna – tylko odpowiedź ułamka na większość. Można się z całą pewnością mylić. |
| Rundy | „Wymień kroki” | Jedna runda = każdy agent czyta pozostałych i aktualizuje się raz. |
| Heterogeniczna debata | „Mieszanie rodzin modeli” | Używanie różnych modeli podstawowych do dekorelacji błędów. |
| Kaskada pochlebstw | „Wszyscy zgadzają się z tym głośnym” | Debata na temat niepowodzenia, w przypadku której agenci wybierają najbardziej pewnego siebie agenta, niezależnie od poprawności. |
| NLSOM | „Społeczeństwo 129 agentów” | Społeczeństwo umysłu oparte na języku naturalnym; Skalowana wersja Zhuge i wsp. |
| Skorelowany błąd | „Ten sam model, ten sam błąd” | Dlaczego nasyca się spójność własna; debata pomiędzy różnymi poglądami jest dekorelowana. |

## Dalsze czytanie

- [Du i in. — Poprawa faktów i rozumowania w modelach językowych poprzez debatę wieloagentową](https://arxiv.org/abs/2305.14325) — dokument referencyjny, ICML 2024
- [Zhuge i in. — Burze umysłów w społeczeństwach umysłu opartych na języku naturalnym](https://arxiv.org/abs/2305.17066) — 129-agent NLSOM
- [Czy powinniśmy wpaść w szał? Spojrzenie na strategie debat wieloagentowych dla LLM](https://arxiv.org/abs/2311.17371) — porównuje warianty debaty
– [Strona projektu Debate](https://composable-models.github.io/llm_debate/) — kod, demonstracje i szczegóły ablacji Du i innych