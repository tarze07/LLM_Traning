# Ekonomia platformy wnioskowania — fajerwerki, razem, baseten, modalne, replikowane, dowolna skala

> Rynek wnioskowania na rok 2026 nie jest już wynajmem czasu GPU. Dzieli się na niestandardowe krzemy (Groq, Cerebras, SambaNova), platformy GPU (Baseten, Together, Fireworks, Modal) i rynki oparte na API (Replicate, DeepInfra). Fireworks podnosi cenę $1/hr per GPU on May 1, 2026, and $Wycena 4B przy ponad 10 tonach tokenów dziennie pokazuje, że model oparty na wolumenie działa. Baseten zamknął $300M Series E at $5B w styczniu 2026 r. Zasada pozycjonowania konkurencyjnego jest prosta: Fireworks optymalizuje opóźnienia, Together optymalizuje szerokość katalogu, Baseten optymalizuje język korporacyjny, Modal optymalizuje DX natywny dla Pythona, Replicate optymalizuje zasięg multimodalny, Anyscale optymalizuje rozproszony Python. Ta lekcja daje ci matrycę, którą możesz przekazać założycielowi.

**Typ:** Ucz się
**Języki:** Python (stdlib, komparator ekonomii zabawek na połączenie)
**Wymagania wstępne:** Faza 17 · 01 (zarządzane platformy LLM), faza 17 · 04 (wewnętrzne elementy obsługujące vLLM)
**Czas:** ~60 minut

## Cele nauczania

- Nazwij trzy segmenty rynku (krzem niestandardowy, platformy GPU, przede wszystkim API) i przyporządkuj każdego dostawcę do segmentu.
— Wyjaśnij, dlaczego model cenowy interfejsu API „na token” kompresuje się w kierunku krzywej kosztów silnika obsługującego, a nie sprzętu.
- Oblicz efektywny koszt żądania u co najmniej trzech dostawców i wyjaśnij, kiedy na minutę (Baseten, Modal) bije na token.
- Zidentyfikuj, która platforma jest odpowiednią domyślną platformą dla danego obciążenia (intensywność bezserwerowa, stała wysoka przepustowość, dopracowane warianty, multimodalność).

## Problem

Oceniłeś zarządzane platformy hiperskalera. Zdecydowałeś, że potrzebujesz węższego, szybszego dostawcy — Fireworks w przypadku opóźnień, Together w zakresie szerokości, Baseten w przypadku precyzyjnie dostrojonego modelu niestandardowego. Teraz masz sześć rzeczywistych wyborów, a strony z cenami nie pokrywają się. Pokazy sztucznych ogni $/M tokens; Baseten shows $/minutę; Modal pokazuje $/second; Replicate shows $/prediction. Nie można ich bezpośrednio porównać bez modelowania obciążenia pracą.

Co gorsza, model biznesowy każdej strony z cenami jest inny. Fireworks obsługuje własny, niestandardowy silnik (FireAttention) na współdzielonych procesorach graficznych; stawka za token odzwierciedla krzywą ich wykorzystania. Baseten oferuje Truss + dedykowane procesory graficzne; na minutę odzwierciedla wyłączność. Modal to prawdziwy Python bezserwerowy — naliczanie sekundowe i zimne uruchamianie w czasie krótszym niż sekunda. Ten sam wynik (odpowiedź LLM), trzy różne funkcje kosztu.

Ta lekcja modeluje szóstkę i informuje, kiedy każda z nich wygrywa.

## Koncepcja

### Trzy segmenty

**Krzem na zamówienie** — Groq (LPU), Cerebras (GPW), SambaNova (RDU). Zwykle 5–10 razy szybsze dekodowanie niż klaster oparty na GPU w tym samym modelu. Wyższa cena za token (Groq wynosiła ~0,99 USD/M na Llama-70B pod koniec 2025 r.), ale była nie do pobicia w przypadkach zastosowań wrażliwych na opóźnienia. Groq to rozwiązanie produkcyjne dla agentów głosowych i tłumaczeń w czasie rzeczywistym.

**Platformy GPU** — Baseten, Together, Fireworks, Modal, Anyscale. Działa na NVIDIA (H100, H200, B200 w 2026 r.) lub czasami na AMD. Warstwa ekonomiczna pomiędzy „wynajem surowego procesora graficznego” (RunPod, Lambda) a „usługą zarządzaną przez hiperskaler” (Bedrock).

**Rynki oparte na interfejsie API** — Replicate, DeepInfra, OpenRouter, Fal. Szeroki katalog, płatność za prognozę lub płatność za sekundę, kładą nacisk na czas do pierwszego połączenia.

### Fireworks — platforma GPU zoptymalizowana pod kątem opóźnień

- Silnik FireAttention (niestandardowy); sprzedawany jako 4x mniejsze opóźnienie niż vLLM w równoważnych konfiguracjach.
— Warstwa wsadowa przy ~50% szybkości bezserwerowej dla obciążeń nieinteraktywnych.
- Dopracowany model obsługiwany w tej samej cenie co model podstawowy — to prawdziwy wyróżnik w porównaniu z dostawcami, którzy pobierają opłatę za Twoją LoRA.
— Połowa 2026 r.: wyższa stawka za wynajem procesora graficznego na żądanie o 1 dolara za godzinę obowiązująca od 1 maja 2026 r. Ceny hurtowe do negocjacji w zależności od skali.
- Sygnał finansowy: wycena na poziomie 4 miliardów dolarów, obsługa ponad 10 tokenów dziennie.

### Razem — zoptymalizowany pod kątem szerokości

- Ponad 200 modeli, w tym wersje open source w ciągu kilku dni od publikacji.
- 50-70% tańsze niż replikacja w równoważnych modelach LLM — pozycjonowanie „AI Native Cloud” obejmuje objętość i katalog.
- Wnioskowanie + dostrajanie + szkolenie w jednym API.

### Baseten — zoptymalizowany pod kątem języka korporacyjnego

- Framework Truss: pakowanie modeli z zależnościami, sekretami i konfiguracją obsługi w jednym manifeście.
- Zakres GPU od T4 do B200. Rozliczanie minutowe z rozsądnym ograniczeniem zimnego rozruchu.
- SOC 2 Typ II, gotowy na HIPAA. Powszechny wybór technologii fintech i opieki zdrowotnej.
- $5B valuation, January 2026 Series E ($300 mln od CapitalG, IVP, NVIDIA).

### Modalne — zoptymalizowane pod kątem języka Python

- Infrastruktura jako kod w czystym Pythonie. Udekoruj funkcję za pomocą `@modal.function(gpu="A100")` i wdrażaj za pomocą jednego polecenia.
- Naliczanie sekundowe. Zimny ​​start 2-4 s ze wstępnym nagrzaniem; <1 s dla małych modeli.
- $87M Series B at $1,1B wycena (2025). Najwyższy wynik doświadczenia programistów w niezależnych ankietach.

### Replikacja — szerokość multimodalna

- Płatność za prognozę. Domyślna platforma dla modeli obrazu, wideo i audio.
- Ekosystem integracyjny (wtyczki Zapier, Vercel, CMS).
- Mniej konkurencyjny pod względem stawek LLM za token, ale wygrywa w przypadku różnorodności multimodalnej.

### Dowolna skala — natywna dla promieni Ray

- Zbudowany na Rayu; RayTurbo to zastrzeżony silnik wnioskowania firmy Anyscale (konkurujący z vLLM).
— Najlepsze w przypadku rozproszonych obciążeń języka Python, gdzie krokiem wnioskowania jest jeden węzeł na większym wykresie.
- Zarządzane klastry Ray; ścisła integracja z Ray AIR i Ray Serve.

### Na token zamiast na minutę — gdy każdy wygrywa

Opłata za token ma sens, gdy obciążenie nie jest wrażliwe na opóźnienia i jest bardzo intensywne — płacisz tylko za to, z czego korzystasz. Wartość na minutę ma sens, gdy wykorzystanie jest wysokie i przewidywalne — pokonujesz każdy token po nasyceniu procesora graficznego.

Ogólna zasada: w przypadku obciążeń powyżej ~30% ciągłego wykorzystania dedykowanego procesora graficznego, liczba minut na minutę (Baseten, Modal) zaczyna bić na token (Fireworks, Together). Poniżej tego wygrywa za token, ponieważ unikasz płacenia za bezczynność.

### Niestandardowy silnik to prawdziwa fosa

Każda platforma powyżej vLLM i SGLang ma własny silnik. FireAttention, RayTurbo, stos wnioskowania Basetena. Niestandardowe silniki twierdzą, że marketing cienia — uczciwe sformułowanie jest takie, że vLLM + SGLang reprezentują około 80% wnioskowania o otwartym kodzie źródłowym produkcji, a wyróżnikami w warstwie platformy są DX, atrybucja i umowy SLA.

### Liczby, które powinieneś zapamiętać

- Wynajem procesora graficznego Fireworks: podwyżka o 1 USD/godz. obowiązująca od 1 maja 2026 r.
- Twierdzenie Fireworks: 4x mniejsze opóźnienie niż vLLM w równoważnych konfiguracjach.
- Razem: 50-70% taniej niż replikacja na LLM.
- Wycena Baseten: $5B (Series E, Jan 2026, $300M rundy).
- Wycena modalna: 1,1 miliarda dolarów (seria B, 2025).
- Uderzenia na minutę na token powyżej ~30% ciągłego wykorzystania.

## Użyj tego

`code/main.py` porównuje sześciu dostawców pod kątem syntetycznego obciążenia w różnych modelach cenowych. Raporty $/day and effective $/M tokenów. Uruchom go, aby znaleźć próg rentowności między tokenem a minutą.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-inference-platform-picker.md`. Biorąc pod uwagę profil obciążenia, umowę SLA i budżet, wybiera główną platformę wnioskowania i wyznacza drugą.

## Ćwiczenia

1. Uruchom `code/main.py`. Przy jakim stałym wykorzystaniu Baseten (na minutę) pokonuje Fireworks (na token) dla modelu 70B na jednym H100? Sam wyprowadź zwrotnicę i porównaj z praktyczną zasadą.
2. Twój produkt umożliwia generowanie obrazu, czat i zamianę mowy na tekst. Wybierz platformy dla każdej modalności i nazwij wzorzec bramy, który je jednoczy.
3. Fireworks podnosi ceny Twojego podstawowego modelu o 1 USD/godz. Modeluj wpływ kosztów mieszanych, jeśli 40% ruchu zostanie przeniesione do warstwy wsadowej (50% zniżki).
4. Klient regulowany wymaga SOC 2 Type II + HIPAA + dedykowanych procesorów graficznych. Które trzy platformy są opłacalne i która wygrywa na FinOps?
5. Porównaj koszt 1000 prognoz dla Llama 3.1 70B w wersji bezserwerowej Fireworks, Together na żądanie, dedykowanej wersji Baseten i API replikacji. Który jest najtańszy przy 10 przewidywaniach dziennie? Na 10 000?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Niestandardowy silikon | „chipy inne niż GPU” | Groq LPU, Cerebras WSE, SambaNova RDU — zoptymalizowane pod kątem dekodowania |
| OgieńUwaga | „Silnik sztucznych ogni” | Niestandardowe jądro uwagi; sprzedawany z 4 razy mniejszym opóźnieniem niż vLLM |
| Kratownica | „Format Basetena” | Wzór manifestu opakowania; zależności + sekrety + konfiguracja serwowania |
| Za token | „Ceny API” | Opłata za zużyte tokeny; płacić za brak bezczynności |
| Na minutę | „dedykowane ceny” | Ładowanie według czasu GPU zegara ściennego; wygrywa przy wysokim wykorzystaniu |
| Według przewidywań | „Powtórz ceny” | Opłata za wywołanie modelu; wspólne dla obrazu/wideo |
| RayTurbo | „Silnik dowolnej skali” | Zastrzeżone wnioski dotyczące Raya; konkuruje z vLLM w klastrach Ray |
| Poziom partii | „50% zniżki” | Kolejka nieinteraktywna z obniżoną stawką; powszechne w Fireworks, OpenAI |
| Dostrojone przy stawce podstawowej | „Fajerwerki LoRA” | Naliczaj żądania obsługiwane przez LoRA według stawki modelu podstawowego (różnica) |

## Dalsze czytanie

– [Ceny programu Fireworks](https://fireworks.ai/pricing) — stawki za token, poziom wsadowy, wynajem procesora graficznego.
– [Baseten Pricing](https://www.baseten.co/pricing/) — stawki za minutę, zatwierdzona pojemność, poziomy korporacyjne.
- [Cennik modalny](https://modal.com/pricing) — stawki GPU za sekundę i poziom bezpłatny.
- [Together AI Pricing](https://www.together.ai/pricing) — katalog modeli i stawki za token.
– [Anyscale Pricing](https://www.anyscale.com/pricing) – RayTurbo i zarządzane ceny Ray.
- [Northflank — Alternatywy AI Fireworks](https://northflank.com/blog/7-best-fireworks-ai-alternatives-for-inference) — ocena porównawcza.
- [Infrabase — dostawcy API wnioskowania AI 2026](https://infrabase.ai/blog/ai-inference-api-providers-compared) — krajobraz dostawców.