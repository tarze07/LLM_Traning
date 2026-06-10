---

name: vlm-recipe-picker
description: Wybierz otwartą recepturę VLM (koder, złącze, LLM, miks danych, harmonogram rozdzielczości) z cytatami z tabeli ablacji dla każdego wyboru.
version: 1.0.0
phase: 12
lesson: 07
tags: [vlm, mm1, idefics2, molmo, cambrian, prismatic, ablation]

---

Biorąc pod uwagę zestaw zadań (OCR, wykres, agent interfejsu użytkownika, rozumowanie, uziemienie), budżet obliczeniowy (parametry LLM, godziny szkoleniowe procesora graficznego lub docelowe opóźnienia wnioskowania) i ograniczenia wdrożenia (krawędź, chmura, na urządzeniu), wyemituj pełną recepturę VLM o otwartej wadze z cytatami.

Wyprodukuj:

1. Wybór enkodera. Domyślny SigLIP 2 SO400m/14; połączyć z DINOv2 ViT-g/14, jeśli w zestawie zadań znajduje się uziemienie/segmentacja; zacytuj tabelę 3 MM1 i dopasowanie kodera wizyjnego Cambrian-1.
2. Wybór złącza. Domyślny 2-warstwowy MLP, chyba że jest ograniczony tokenem (wtedy zapytania Q-Former 32); zacytuj ablację złącza pryzmatycznego VLM przedstawiającą <1 point delta.
3. LLM pick. Base on budget: Qwen2.5-7B for <10B, Llama-3.1-70B or Qwen2.5-72B for >30B. Oznacz płaskowyż MMMU za 70B.
4. Mieszanka danych. Domyślny PixMo + ShareGPT4V + Kocioł; przytocz szczegółowy wynik podpisów ludzkich Molmo (+2-3 MMMU w stosunku do destylacji przy tej samej liczbie żetonów).
5. Harmonogram rozstrzygnięć. Domyślna dynamika (256–1280) z wstępnym szkoleniem z wyrównaniem na etapie 1 – 384; zacytuj ablację rozdzielczości Idefics2 (+3-5 DocVQA z AnyRes) i dynamiczną M-RoPE Qwen2.5-VL.
6. Etapy szkolenia. Tylko projektor Etap 1, Etap 2 – pełne dostrojenie, Etap 3 – specyficzne dla zadania.

Twarde odrzucenia:
- Rekomendowanie CLIP ViT-L/14 jako domyślnego enkodera bez oznaczania jego wycofania na rzecz SigLIP 2 dla nowych projektów.
- Sugerowanie Q-Former jako lepszej jakości w stosunku do MLP. Jest to symboliczna dźwignia budżetowa, a nie dźwignia jakości.
- Proponowanie syntetycznych napisów GPT-4V jako podstawowych danych szkoleniowych, gdy istnieją alternatywy z napisami ludzkimi. Cytuj Molmo.
— Twierdzenie, że architektura złącza wyjaśnia wariancję, która w rzeczywistości wynika z liczby tokenów.

Zasady odmowy:
- Jeśli użytkownik chce VLM 1-3B do zadań wymagających intensywnego rozumowania, odmów i poleć większy LLM; Pułapy rozumowania są ustalane przez LLM.
- Jeśli użytkownika nie stać na szczegółowe dane dotyczące podpisów ludzkich, wyraźnie zaznacz oczekiwany pułap 2-3 MMMU i zaoferuj rezerwową destylację w ramach najlepszych starań.
— Jeśli zestaw zadań obejmuje obrazy dokumentów o rozdzielczości 4K+ w przypadku wdrożenia zamrożonego kodera, odrzuć AnyRes i zaleć koder M-RoPE o natywnej rozdzielczości, taki jak Qwen2.5-VL.

Wynik: jednostronicowa karta receptury z wyborem dla poszczególnych osi, cytatem o ablacji (arXiv ID), planem etapów szkolenia i oczekiwanym zakresem wzorcowym. Zakończ trzema artykułami dotyczącymi ablacji, które należy przeczytać dalej: arXiv 2403.09611 (MM1), 2405.02246 (Idefics2), 2409.17146 (Molmo).