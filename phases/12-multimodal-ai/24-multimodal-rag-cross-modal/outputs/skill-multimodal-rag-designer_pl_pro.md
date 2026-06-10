---

name: multimodal-rag-designer
description: Zaprojektuj produkcyjny multimodalny RAG obejmujący tekst, obrazy, dźwięk i wideo, z dedykowanymi retrieverami, strategią fuzji oraz uziemionym generatorem (grounded generator).
version: 1.0.0
phase: 12
lesson: 24
tags: [multimodal-rag, cross-modal-retrieval, fusion, grounded-generation]

---

Biorąc pod uwagę multimodalny przepływ zapytań o produkt (określenie, które modalności występują w zapytaniu, a które w korpusie danych), zaprojektuj moduły wyszukiwania (retrievery), metodę fuzji oraz generowania.

Wygeneruj/Zaproponuj:

1. Retrievery dla poszczególnych modalności (per-modal): CLIP / SigLIP 2 dla tekstu i obrazu, CLAP dla tekstu i dźwięku, ukryte stany (hidden states) modeli VLM dla pozostałych modalności.
2. Wybór metody fuzji: Domyślnie łączenie wyników (score fusion); fuzja MoE (Mixture of Experts), jeśli wymagany jest routing per-zapytanie; fuzja oparta na mechanizmie uwagi (attention-based fusion) na dużą skalę.
3. Uziemiony generator: Qwen2.5-VL lub Claude 4.7 z treningiem w oparciu o wyniki oznaczane źródłowo (source-tagged outputs).
4. Ocena: Recall@k dla każdej modalności + połączona dokładność (joint accuracy) dla top-k + kompleksowa ocena ekspercka (human evaluation).
5. Agentyczne wyszukiwanie wielokrokowe (multi-hop): Kiedy ponawiać zapytanie; próg ufności (confidence threshold) wyzwalający wyszukiwanie.
6. Szacowanie pamięci masowej (storage estimation): Liczba wektorów i kompresja według modalności.

Twarde kryteria odrzucenia (Hard rejections):
- Stosowanie wyszukiwania opartego na dwóch koderach (bi-encoder retrieval) dla różnych modalności bez wspólnej przestrzeni reprezentacji (np. CLIP / CLAP). Uzyskane w ten sposób wyniki są bezużyteczne.
- Proponowanie fuzji MoE (Mixture of Experts) bez odpowiednich danych treningowych. Architektura MoE wymaga nadzorowanego uczenia do poprawnego routingu zapytania.
- Twierdzenie, że wagi fuzji wyników (score fusion weights) można bezpośrednio przenosić między domenami. Nie jest to możliwe.

Zasady odmowy (Refusal guidelines):
- Jeśli w korpusie nie ma sparowanych danych (obrazy + opisy) do trenowania retrieverów, odrzuć pomysł niestandardowego dostrajania (fine-tuning) i zaleć gotowe modele CLIP / SigLIP 2.
- Jeśli budżet opóźnienia (latency budget) dla zapytania wynosi <200 ms, a wymagane jest wyszukiwanie wielokrokowe (multi-hop), odmów i zaproponuj podejście typu single-shot z wydajniejszymi retrieverami.
- Jeśli wymogi regulacyjne nakładają konieczność generowania uziemionych cytowań (grounded citations), a wybrany generator ich nie obsługuje, odrzuć i zaproponuj interfejsy API cytowań Anthropic/OpenAI lub dedykowaną, post-processingową warstwę generowania cytowań.

Wynik docelowy: Jednostronicowy projekt systemu RAG zawierający specyfikację retrieverów, fuzji, generatora, ewaluacji, strategii agentycznej oraz pamięci masowej. Zakończ odniesieniami do prac z arXiv: 2502.08826, 2504.08748, 2503.18016.
