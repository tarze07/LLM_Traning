# ColPali i dokument Vision-Native RAG

> Tradycyjny RAG przetwarza pliki PDF na tekst, dzieli je na fragmenty, osadza fragmenty i przechowuje wektory. Każdy krok powoduje utratę sygnału: OCR usuwa dane z wykresu, fragmentacja powoduje rozbicie wierszy tabeli, osadzanie tekstu ignoruje liczby. ColPali (Faysse i in., lipiec 2024) zadał prostsze pytanie: po co w ogóle wyodrębniać tekst? Osadź obraz strony bezpośrednio za pomocą PaliGemma, użyj późnej interakcji w stylu ColBERT do pobrania i zachowaj cały układ, rysunki, czcionki i sygnały formatowania zawarte w dokumencie. Opublikowane testy porównawcze: 20–40% lepsza dokładność od początku do końca w porównaniu z tekstowym RAG w przypadku dokumentów bogatych wizualnie. ColQwen2, ColSmol i VisRAG rozszerzyły wzór. W tej lekcji zapoznajemy się z natywną wizją tezy RAG i budujemy mały indeksator podobny do ColPali.

**Typ:** Kompilacja
**Języki:** Python (stdlib, indeksator wielowektorowy + narzędzie punktujące MaxSim)
**Wymagania wstępne:** Faza 11 (LLM Engineering — podstawy RAG), Faza 12 · 05 (LLaVA)
**Czas:** ~180 minut

## Cele nauczania

- Wyjaśnij różnicę pomiędzy pobieraniem za pomocą dwóch koderów (jeden wektor na dokument) a wyszukiwaniem po późnej interakcji (wiele wektorów na dokument).
- Opisz operację MaxSim ColBERT i sposób, w jaki ColPali uogólnia ją od tokenów tekstowych po łaty graficzne.
- Zbuduj mały indeksator podobny do ColPali: strona → osadzanie poprawek → MaxSim poprzez osadzanie terminów zapytania → strony z najwyższej półki.
- Porównaj generator ColPali + Qwen2.5-VL z tekstem-RAG + GPT-4 w przypadku użycia faktur/raportów finansowych.

## Problem

Text-RAG w plikach PDF powoduje wyrzucenie większości dokumentu. Wzrost przychodów w trzecim kwartale w raporcie finansowym jest zwykle przedstawiony na wykresie; wyniki raportu medycznego przedstawiono na obrazach z adnotacjami; Blok podpisu umowy prawnej jest faktem dotyczącym układu, a nie faktem tekstowym.

Potok tekst-RAG:

1. PDF → tekst poprzez OCR / pdftotext.
2. Tekst → 300-500 fragmentów tokenów.
3. Fragment → osadzanie dwóch koderów (jeden wektor).
4. Zapytanie użytkownika → osadzanie → podobieństwo cosinus → fragmentów top-k.
5. Kawałki + zapytanie → LLM.

Pięć stratnych kroków. Wykresy nie zostały przechwycone. Tabele podzielone na kawałki. Układ wielokolumnowy zostaje spłaszczony. Znikają adnotacje dotyczące rysunków.

Poprawka ColPali: pomiń OCR, osadź obraz strony bezpośrednio. Do pobierania używaj późnej interakcji w stylu ColBERT, aby model mógł uwzględnić drobne poprawki w czasie wykonywania zapytania.

## Koncepcja

### ColBERT (2020)

ColBERT (Khattab & Zaharia, arXiv:2004.12832) to metoda wyszukiwania tekstu. Zamiast jednego wektora na dokument, tworzy jeden wektor na token. W momencie zapytania:

- Tokeny zapytań mają własne osadzenie (wektory N_q).
- Tokeny dokumentów są osadzane (wektory N_d, zazwyczaj buforowane).
- Wynik = suma tokenów zapytania o max ponad tokenów dokumentu o podobieństwie cosinus: Σ_i max_j cos(q_i, d_j).

To jest operacja MaxSim. Każdy token zapytania „wybiera” najlepiej pasujący token dokumentu. Wynik końcowy jest sumą.

Plusy: silne zapamiętywanie, obsługuje semantykę na poziomie terminów. Wady: N_d wektorów na dokument, drogie przechowywanie.

### ColPali

ColPali (Faysse i in., arXiv:2407.01449) stosuje wzór ColBERT do obrazów.

- Każda strona jest kodowana przez PaliGemma (język ViT +) do osadzania łatek: N_p wektorów na stronę.
- Każde zapytanie użytkownika (tekst) jest kodowane w osadzonych tokenach zapytania: wektory N_q.
- Wynik = Σ_i max_j cos(q_i, p_j), tj. MaxSim na tokenach tekstu zapytania i poprawkach obrazu strony.
- Pobierz top-k stron według całkowitego wyniku.

W momencie przetwarzania dokumentu: osadzaj każdą stronę za pomocą PaliGemma, przechowuj wszystkie osadzone poprawki. W czasie zapytania: osadź tokeny zapytania, oblicz MaxSim względem wszystkich zapisanych osadzonych stron, zwróć liczbę stron z najwyższej półki.

Plusy: kompleksowość przewyższa tekst RAG o 20–40% w przypadku dokumentów bogatych wizualnie. Każdy wektor poprawki przechwytuje lokalny układ i zawartość.

Wady: N_p poprawek × 4-bajtowe liczby zmiennoprzecinkowe × wektory D-dim na stronę = pamięć szybko rośnie. Łagodzone przez kwantyzację PQ/OPQ.

### ColQwen2 i ColSmol

ColQwen2 (illuin-tech, 2024–2025) zamienia PaliGemmę na Qwen2-VL. Lepszy koder bazowy, lepsze odzyskiwanie.

ColSmol to wariant na mniejszą skalę do użytku lokalnego/krawędziowego. Retriever ColSmol przy parametrach ~1B działa na konsumenckim procesorze graficznym.

### VisRAG

VisRAG (Yu i in., arXiv:2410.10594) to inny wariant: zamiast MaxSim w łatkach, połącz każdą stronę w jeden wektor za pomocą VLM, a następnie pobierz za pomocą dwóch koderów. Szybsze indeksowanie + mniejsza pamięć, słabsze zapamiętywanie.

Kompromis jakość-koszt: ColPali to jakość, VisRAG to skala.

### M3DocRAG

M3DocRAG (Cho i in., arXiv:2411.04952) rozszerza wyszukiwanie wielomodalne na wielostronicowe rozumowanie z wieloma dokumentami. Pobiera strony w dokumentach, tworzy wielostronicowy kontekst dla VLM.

### ViDoRe — punkt odniesienia

Punkt odniesienia dla towarzysza ColPali. Wizualna ocena odzyskiwania dokumentów. Zadania obejmują raporty finansowe, artykuły naukowe, dokumenty administracyjne, dokumentację medyczną, instrukcje. Metryczne: nDCG@5.

ColPali-v1 osiąga ~80% nDCG@5 w ViDoRe; tekst-RAG na tych samych dokumentach osiąga ~50-60%.

### Kompleksowy rurociąg RAG

Dla RAG z wizją:

1. Pobranie: PDF → obrazy stron → kodowanie PaliGemma → przechowuj wszystkie osadzone poprawki.
2. Zapytanie: tekst użytkownika → osadzenie tokenu zapytania → MaxSim względem wszystkich zaindeksowanych stron → stron z najwyższej półki.
3. Wygeneruj: obrazy pierwszej strony + zapytanie → VLM (Qwen2.5-VL lub Claude) → odpowiedź.

Nigdzie nie ma OCR. Rysunki, wykresy, czcionki i układ – wszystko to składa się na odpowiedź.

### Matematyka dotycząca przechowywania

50-stronicowy raport finansowy z 729 poprawkami na stronie i 128 przyciemnionymi elementami osadzonymi:

- ColPali: 50 * 729 * 128 * 4 bajty = ~18 MB surowego, ~4 MB po PQ.
- Text-RAG: 50 fragmentów * 768-dim * 4 bajty = ~150 kB.

ColPali to ~30x więcej miejsca na dokument. W skali OPQ/PQ obniża je do ~5-10x, co jest zwykle akceptowalne.

### Gdy tekst-RAG nadal wygrywa

- Dokumenty czystego tekstu bez sygnału układu (artykuły wiki, dzienniki czatów). Text-RAG jest prostszy i tańszy w przechowywaniu.
- Wielomilionowe archiwa, w których dominują koszty przechowywania.
- Surowe wymogi regulacyjne wymagające wyodrębnienia tekstu OCR wraz z pobieraniem.

We wszystkim innym w roku 2026 – raportach finansowych, artykułach naukowych, umowach prawnych, dokumentacji medycznej, dokumentacji UX – RAG wygrywa z wizją.

## Użyj tego

`code/main.py`:

- Koder łatek zabawkowych: odwzorowuje „stronę” (małą siatkę wektorów cech) na tablicę osadzonych łatek.
- Wynik MaxSim: oblicza wynik w stylu ColBERT pomiędzy zestawem osadzania tokenu zapytania a zestawem poprawek strony.
- Indeksuje 5 stron z zabawkami, uruchamia 3 zapytania, zwraca top-k z wynikami.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-vision-rag-designer.md`. Biorąc pod uwagę projekt dokument-RAG, wybiera ColPali / ColQwen2 / VisRAG / tekst-RAG i rozmiar magazynu.

## Ćwiczenia

1. 200-stronicowy raport roczny, 729 poprawek na stronę, 128 przyciemnionych elementów osadzonych i 4 bajty zmiennoprzecinkowe. Oblicz surową pamięć masową i skompresowaną PQ (8x).

2. MaxSim to Σ_i max_j cos(q_i, p_j). Co oznacza ta suma, czego nie daje proste średnie podobieństwo?

3. ColPali indeksuje strony jako zestawy poprawek. Co się zmieni, jeśli zamiast tego indeksujemy na poziomie słowa (tak jak robi to ColBERT)? Kompromisy?

4. Zaprojektuj kompleksowy potok dla korpusu składającego się z 1 miliona stron z budżetem opóźnień wynoszącym 500 ms na zapytanie. Wybierz ColQwen2 / VisRAG i uzasadnij.

5. Przeczytaj M3DocRAG (arXiv:2411.04952). Opisz wielostronicowy wzór uwagi i czym różni się od jednostronicowego pobierania ColPali.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|--------------------------------------|
| Późna interakcja | „w stylu ColBERTA” | Pobieranie przy użyciu osadzania na token lub na poprawkę + MaxSim, a nie pojedynczy wektor dokumentu |
| MaxSim | „Maksymalna liczba łat” | Dla każdego tokenu zapytania wybierz token dokumentu o najwyższym podobieństwie; suma w zapytaniu |
| Bi-enkoder | „Jednowektorowy” | Jeden wektor na dokument; szybszy, ale traci szczegółowość |
| Wielowektorowy | „Wiele wektorów na dokument” | Przechowuj wektory N_p na dokument/stronę; koszty przechowywania rosną, ale poprawia się wycofanie |
| Osadzanie poprawek | „Funkcja strony” | Jeden wektor na fragment obrazu z kodera VLM, buforowany na stronę |
| ViDoRe | „Ławka dokumentacyjna Vision” | Zestaw testów porównawczych ColPali do wizualnego wyszukiwania dokumentów |
| Kwantyzacja PQ | „Kwantyzacja produktu” | Kompresja zachowująca podobieństwo wektorów przy jednoczesnym zmniejszaniu pamięci ~8x |

## Dalsze czytanie

- [Faysse i in. — ColPali (arXiv:2407.01449)](https://arxiv.org/abs/2407.01449)
- [Khattab i Zaharia — ColBERT (arXiv:2004.12832)](https://arxiv.org/abs/2004.12832)
- [Yu i in. — VisRAG (arXiv:2410.10594)](https://arxiv.org/abs/2410.10594)
- [Cho i in. — M3DocRAG (arXiv:2411.04952)](https://arxiv.org/abs/2411.04952)
- [illuin-tech/colpali GitHub](https://github.com/illuin-tech/colpali)