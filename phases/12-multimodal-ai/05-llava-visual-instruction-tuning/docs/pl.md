# Strojenie LLaVA i instrukcji wizualnych

> LLaVA (kwiecień 2023) to najczęściej kopiowana architektura multimodalna na świecie. Zastąpił Q-Former BLIP-2 dwuwarstwowym MLP, zastąpił bramkowaną uwagę krzyżową Flamingo naiwną konkatenacją tokenów i trenował na 158 tys. obrotów instrukcji wizualno-instrukcyjnych generowanych przez GPT-4 z podpisów tekstowych. Każdy praktyk, który zbudował VLM w latach 2023–2026, zbudował jakiś wariant LLaVA. LLaVA-1.5 dodał AnyRes. LLaVA-NeXT podniosła rozdzielczość. LLaVA-OneVision ujednolicony obraz, wiele obrazów i wideo w jednym przepisie. W tej lekcji czytamy przepis, wdrażamy projektor i wyjaśniamy, dlaczego „wygrało prostsze”.

**Typ:** Kompilacja
**Języki:** Python (stdlib, projektor + narzędzie do tworzenia szablonów instrukcji)
**Wymagania wstępne:** Faza 12 · 02 (CLIP), Faza 11 (LLM Engineering — strojenie instrukcji)
**Czas:** ~180 minut

## Cele nauczania

- Zbuduj 2-warstwowy projektor MLP, który mapuje osadzanie łaty ViT (wymiar 1024) na wymiar osadzania LLM (wymiar 4096).
- Przejdź według dwuetapowego przepisu LLaVA: (1) wyrównanie projektora na 558 tys. par napisów, (2) dostrojenie instrukcji wizualnych na 158 tys. obrotów generowanych przez GPT-4.
- Skonstruuj zachętę w formacie LLaVA z symbolem zastępczym tokenu obrazu, podpowiedzią systemową i zwrotami użytkownika/asystenta.
- Wyjaśnij, dlaczego społeczność przeniosła się z Q-Former do MLP pomimo wygranej w postaci symbolicznego budżetu.

## Problem

Q-Former BLIP-2 (lekcja 12.03) kompresuje obraz do 32 tokenów. Czysty, wydajny, dobry do testów porównawczych. Ale ma dwa problemy.

Po pierwsze, Q-Formera można wyszkolić, ale jego utrata nie jest ostatecznym zadaniem. Etap 1 szkoli ITC+ITM+ITG. Etap 2 trenuje utratę LM. Zapytania uczą się pośredniej reprezentacji, którą LLM musi następnie zdekodować. Informacje giną w wąskim gardle.

Po drugie, Q-Former ma 188 milionów parametrów, a w skali LLaVA na rok 2023 trzeba było go wspólnie zaprojektować z docelowym LLM. Zmień LLM, przekwalifikuj Q-Formera. Zmień koder wizji, przekwalifikuj się. Każda kombinacja była odrębnym projektem badawczo-rozwojowym.

Odpowiedź LLaVA była zawstydzająca w swojej prostocie: weź 576 tokenów łatek ViT, przepuść każdy przez 2-warstwowy MLP (`1024 → 4096 → 4096`) i wrzuć wszystkie 576 do sekwencji wejściowej LLM. Brak wąskiego gardła. Żadnego wstępnego szkolenia na pierwszym etapie z dziwnymi celami. Po prostu trenuj MLP na bezpośredniej stracie LM.

Skąd pochodzą dane? Drugie spostrzeżenie LLaVA: użyj GPT-4 (tylko tekst) do wygenerowania danych instrukcji. Podaj GPT-4 podpis COCO i dane ramki granicznej obrazu, poproś go o utworzenie rozmów, opisów i złożonych pytań uzasadniających. 158 tys. obrotów instrukcji-odpowiedzi za darmo. Brak ludzkiej adnotacji.

Rezultat: VLM, który działał na 8 A100 przez jeden dzień, pokonał Flamingo na MMMU i dostarczył otwarty punkt kontrolny, który społeczność mogła rozszerzyć. Do końca 2023 r. powstało ponad 50 rozwidleń.

## Koncepcja

### Architektura

LLaVA-1,5 w 13B:
- Enkoder wizyjny: CLIP ViT-L/14 @ 336 (zamrożony w etapie 1, opcjonalnie odmrożony w etapie 2).
- Projektor: 2-warstwowy MLP z aktywacją GELU, `1024 → 4096 → 4096`.
- LLM: Vicuna-13B (później Lama-3.1-8B).

Przekaż dalej obraz + monit tekstowy:

```
img -> ViT -> 576 patches of dim 1024
patches -> MLP -> 576 tokens of dim 4096
prompt: system + "<image>" placeholder + user question
replace <image> token with the 576 projected tokens
feed the full sequence to the LLM
decode response
```

Obraz zajmuje 576 tokenów kontekstu LLM. W kontekście 2048 pozostawia to 1472 tokeny dla tekstu. W kontekście 32k jest to błąd zaokrąglenia.

### Etap 1: ustawienie projektora

Zamroź ViT. Zamroź LLM. Trenuj tylko 2-warstwowy MLP. Zbiór danych: 558 tys. par obrazów i podpisów (LAION-CC-SBU). Strata: modelowanie języka na podpisie, uwarunkowane rzutowanymi tokenami obrazu.

W pojedynczej epoce w partii 128 odbywa się to w ciągu kilku godzin. Projektor uczy się mapować przestrzeń ViT na przestrzeń LLM. Brak nadzoru nad konkretnym zadaniem.

### Etap 2: dostrajanie instrukcji wizualnych

Odblokuj projektor (nadal można go trenować). Odblokuj LLM (zwykle całkowicie, czasami LoRA). Trenuj na 158 tys. zakrętów z instrukcją wizualną.

Dane instrukcji to sztuczka. Liu i in. wygenerował to przez:
1. Zrób zdjęcie COCO.
2. Wyodrębnij opis tekstu (5 podpisów ludzkich + lista obwiedni).
3. Wyślij do GPT-4 za pomocą trzech szablonów podpowiedzi:
   - Rozmowa: „Wygeneruj ciągły dialog między użytkownikiem a asystentem na temat tego obrazu”.
   - Opis szczegółowy: „Podaj bogaty, szczegółowy opis obrazu”.
   - Złożone rozumowanie: „Zadaj pytanie wymagające uzasadnienia na temat obrazu, a następnie odpowiedz na nie”.
4. Podziel wyjście GPT-4 na pary (instrukcja, odpowiedź).

Nic z tego nie dotyczy bezpośrednio obrazu – tylko opis tekstowy. GPT-4 halucynuje wiarygodną treść obrazu. Trochę hałasu, ale zadziałało: 158 tys. obrotów wystarczyło, aby odblokować dialog.

### Dlaczego społeczność to skopiowała

- Brak strat specyficznych dla etapu 1 do dostrojenia. Strata LM w całym meczu.
- Projektor trenuje w ciągu godzin, a nie dni.
- LLM można zamienić (LLaVA-Llama2, LLaVA-Mistral, LLaVA-Llama3) poprzez przekwalifikowanie samego projektora.
- Potok danych instrukcji wizualnych wykorzystuje GPT-4 i jest tani w regeneracji dla nowej domeny.

### LLaVA-1.5 i LLaVA-NeXT

Dodano LLaVA-1.5 (październik 2023 r.):
- Dane dotyczące zadań akademickich (VQA, OKVQA, RefCOCO) wmieszane w dostrajanie instrukcji.
- Lepszy monit systemowy.
- Kontekst 2048 → 32 tys.

Dodano LLaVA-NeXT (styczeń 2024 r.):
- AnyRes: dzielenie obrazów o wysokiej rozdzielczości na siatkę 2x2 lub 1x3 z kadrami o wymiarach 336x336 i jedną globalną miniaturą o niskiej rozdzielczości. Każda uprawa to 576 żetonów; łącznie około 2880 tokenów wizualnych na obraz. Zadania OCR i wykresy wzrosły.
- Lepsza mieszanka danych instrukcji z ShareGPT4V (wysokiej jakości napisy GPT-4V).
- Silniejsze podstawowe LLM (Mistral-7B, Yi-34B).

### LLaVA-OneVision

Lekcja 12.08 szczegółowo opisuje OneVision. Wersja krótka: ten sam projektor, ale przeszkolony w oparciu o program obejmujący pojedynczy obraz, wiele obrazów i wideo w jednym modelu ze wspólnym budżetem na symbole wizualne.

### Porównanie do Q-Formera

| | Q-Former (BLIP-2) | MLP (LLaVA) |
|---|---|---|
| Tokeny wizualne na obraz | 32 | 576 (podstawowy) lub 2880 (AnyRes) |
| Parametry nadające się do szkolenia | 188M + LM | 40M + LM |
| Strata w pierwszym etapie | ITC+ITM+ITG | Tylko LM |
| Spotkanie LLM | Wymaga przekwalifikowania | Zamień przy minimalnym przeszkoleniu |
| Wiele obrazów | Niezręczne | Naturalne (połączone) |
| Wideo | Niezręczne | Naturalne (łączenie na klatkę) |
| Budżet symboliczny | Mały | Duży |

MLP wygrywa prostotą i elastycznością tokenów. Q-Former wygrywa na symbolicznym budżecie. Pod koniec 2023 roku budżet tokenowy nie był już wiążącym ograniczeniem (konteksty LLM urosły do ​​32 tys.-128 tys.+) i dominowała prostota.

### Format podpowiedzi

```
A chat between a curious human and an artificial intelligence assistant. The assistant gives helpful, detailed, and polite answers to the human's questions. USER: <image> Describe this image in detail. ASSISTANT: The image shows ...
```

`<image>` to token zastępczy. Przed tokenizacją jest zastępowany 576 tokenami wizualnymi (lub 2880 w przypadku AnyRes). Tokenizer widzi nieco dłuższą sekwencję, niż została przeszkolona, ​​ale LLM obsługuje nowe dane wejściowe, ponieważ nauczył tego etap 1.

### Oszczędność parametrów

Podział LLaVA-1.5-7B:
- CLIP ViT-L/14 @ 336: 303M (zamrożony etap 1, często niezamrożony etap 2).
- Projektor (2x liniowy): ~22M z możliwością przeszkolenia.
- Lama-7B: 7B.
- Razem: 7,3B parametrów. Możliwość szkolenia na etapie 2: pełny projektor 7B + 22M.

Koszt szkolenia dla etapu 2: ~20 godzin na 8xA100. To jest kluczowa liczba – jeden dzień, jeden węzeł, powtarzalność. Dlatego LLaVA się rozprzestrzeniła.

## Użyj tego

`code/main.py` implementuje:

1. 2-warstwowy projektor MLP (wymiar 16 → 32 → 32 dla skali zabawkowej) w czystym Pythonie.
2. Potok budowania podpowiedzi: zachęta systemowa + `<image>` zastąpione N wyświetlanymi tokenami + tura użytkownika + symbol zastępczy generowania asystenta.
3. Wizualizator pokazujący, jak wygląda blok wizualny 576 tokenów w kontekście LLM (procent wykorzystania kontekstu 2 tys. / 32 tys. / 128 tys.).

## Wyślij to

Ta lekcja przedstawia `outputs/skill-llava-vibes-eval.md`. Biorąc pod uwagę punkt kontrolny rodziny LLaVA, uruchamia on zestaw oceny wibracji składający się z 10 podpowiedzi (3 napisy, 3 VQA, 2 uzasadnienia, 2 odmowy) i raportuje czytelną dla człowieka kartę wyników. Nie stanowi punktu odniesienia; test dymu, aby potwierdzić, że projektor i LLM dobrze się łączą.

## Ćwiczenia

1. Oblicz liczbę parametrów możliwych do wyszkolenia dla 2-warstwowego projektora MLP w `1024 → 4096 → 4096`. Biorąc pod uwagę GELU i stronniczość, jaką część LLaVA-13B reprezentuje?

2. Skonstruuj monit LLaVA w przypadku „odmowy” — obraz przedstawia osobę prywatną. Zapisz oczekiwaną odpowiedź asystenta. Dlaczego LLaVA miałaby odrzucić tę propozycję zerową i jakie dane szkoleniowe byłyby potrzebne, aby wzmocnić odmowę?

3. Przeczytaj sekcję AnyRes na blogu LLaVA-NeXT. Oblicz liczbę tokenów wizualnych dla obrazu o rozdzielczości 1344 x 672 w AnyRes. Porównaj z tokenami podstawowymi 576 w rozdzielczości 336 x 336.

4. Projektor LLaVA stage-1 jest szkolony ze stratą LM w napisach. Co się stanie, jeśli pominiesz etap 1 i przejdziesz od razu do etapu 2 (dostrajanie instrukcji wizualnych)? Aby uzyskać odpowiedź, zacytuj ablację pryzmatycznych VLM (arXiv:2402.07865).

5. LLaVA-Instruct-150k wykorzystuje GPT-4 z napisami COCO do generowania instrukcji. W przypadku nowej domeny (prześwietlenia medyczne, zdjęcia satelitarne) opisz czteroetapowy potok danych w celu wygenerowania instrukcji dotyczących domeny. Co może pójść nie tak na każdym etapie?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Projektor | „Most MLP” | 2-warstwowy MLP z mapowaniem GELU ViT dim na LLM dim |
| Token obrazu | „<image> symbol zastępczy” | Znacznik podpowiedzi zastąpiony przez N wyświetlanych znaczników wizualnych przed wnioskowaniem |
| Strojenie instrukcji wizualnych | „LLaVA etap 2” | Szkolenie na temat trójek generowanych przez GPT-4 (obraz, instrukcja, odpowiedź) |
| Dopasowanie etapu 1 | „Przygotowanie projektora” | Zamrożenie ViT i LLM, projektor pociągu z utratą LM w podpisach |
| DowolnaRes | „Układanie płytek wieloplonowych” | Podziel obraz w wysokiej rozdzielczości na siatkę kafelków i połącz znaczniki wizualne każdego kafelka |
| Instrukcja LLaVA | „Wygenerowane przez GPT-4” | 158 tys. par instrukcja-odpowiedź zsyntetyzowanych z podpisów COCO + GPT-4 |
| Zamrożenie kodera wizyjnego | „Zablokowany kręgosłup” | Wagi CLIP nie aktualizują się na etapie 1, czasem też nie na etapie 2 |
| UdostępnijGPT4V | „Lepsze napisy” | 1M gęstych napisów generowanych przez GPT-4V, używanych do wyrównania wyższej jakości |
| VQA | „Wizualna odpowiedź na pytanie” | Zadanie odpowiedzi na pytanie swobodne dotyczące obrazu |
| Pryzmatyczne VLM | „Papier projektowo-przestrzenny” | Ablacja Karamcheti 2024 systematycznie testuje wybór projektora i danych |

## Dalsze czytanie

- [Liu i in. — Strojenie instrukcji wizualnych (arXiv:2304.08485)](https://arxiv.org/abs/2304.08485) — artykuł LLaVA.
- [Liu i in. — Ulepszone linie bazowe z dostrajaniem instrukcji wizualnych (arXiv:2310.03744)](https://arxiv.org/abs/2310.03744) — LLaVA-1.5.
- [Chen i in. — ShareGPT4V (arXiv:2311.12793)](https://arxiv.org/abs/2311.12793) — gęsty zbiór danych napisów.
- [Karamcheti i in. — Pryzmatyczne VLM (arXiv:2402.07865)](https://arxiv.org/abs/2402.07865) — ablacje w przestrzeni projektowej.
- [Li i in. — LLaVA-OneVision (arXiv:2408.03326)](https://arxiv.org/abs/2408.03326) — ujednolicony pojedynczy obraz, wiele obrazów, wideo.