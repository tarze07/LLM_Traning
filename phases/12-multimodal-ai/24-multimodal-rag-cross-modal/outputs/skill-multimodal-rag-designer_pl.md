---

name: multimodal-rag-designer
description: Zaprojektuj produkcyjny wielomodalny RAG obejmujący tekst, obrazy, dźwięk i wideo z aporterami, strategię fuzji i uziemiony generator.
version: 1.0.0
phase: 12
lesson: 24
tags: [multimodal-rag, cross-modal-retrieval, fusion, grounded-generation]

---

Biorąc pod uwagę wielomodalny przepływ zapytań o produkt (które modalności w zapytaniu, które w korpusie), projektowanie modułów pobierania, fuzja i generowanie.

Wyprodukuj:

1. Retrievery permodalne. CLIP / SigLIP 2 dla tekstu+obrazu, CLAP dla tekstu+dźwięku, ukryte stany VLM dla czegokolwiek innego.
2. Wybór fuzji. Domyślne łączenie wyników; Fuzja MoE, jeśli potrzebne jest routing na zapytanie; fuzja uwagi na dużą skalę.
3. Uziemiony generator. Qwen2.5-VL lub Claude 4.7 ze szkoleniem na temat wyników ze znacznikiem źródłowym.
4. Ocena. Recall@k na modalność + połączona dokładność najwyższej k + kompleksowa ocena przez człowieka.
5. Agentyczny multi-hop. Kiedy ponownie zapytać; próg ufności, który ma zostać uruchomiony.
6. Szacunek przechowywania. Zliczanie i kompresja wektorów według modalności.

Twarde odrzucenia:
- Korzystanie z wyszukiwania za pomocą dwóch koderów w różnych modalnościach bez wspólnej przestrzeni (CLIP / CLAP). Wyniki są bez znaczenia.
- Proponowanie fuzji MoE bez danych szkoleniowych. Ministerstwo Środowiska potrzebuje nadzoru, aby prawidłowo poprowadzić trasę.
- Twierdzenie, że wagi fuzji wyników są przesyłane między domenami. Oni nie.

Zasady odmowy:
- Jeśli w korpusie nie ma danych dotyczących pary obrazów i podpisów dla aporterów szkolących, odrzuć niestandardowe dostrajanie i zaleć gotowy CLIP / SigLIP 2.
- Jeśli budżet opóźnienia zapytania wynosi <200 ms i wymagane jest wielokrotne przeskakiwanie, odmów; zaproponuj pojedynczy strzał z lepszymi retrieverami.
- Jeśli uzasadnione cytaty są wymogiem regulacyjnym i żaden generator ich nie obsługuje, odrzuć i zaproponuj interfejsy API cytowań Anthropic/OpenAI lub wyraźną warstwę cytatów przetwarzaną później.

Wynik: jednostronicowy projekt RAG z aporterami, fuzją, generatorem, oceną, strategią agenta, przechowywaniem. Zakończ arXiv 2502.08826, 2504.08748, 2503.18016.