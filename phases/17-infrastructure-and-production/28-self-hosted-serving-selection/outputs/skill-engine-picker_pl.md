---

name: engine-picker
description: Wybierz własny silnik LLM (llama.cpp, Ollama, TGI, vLLM, SGLang) biorąc pod uwagę sprzęt, skalę i obciążenie. Nazwij tryb konserwacji 2026 TGI jako wyzwalacz migracji.
version: 1.0.0
phase: 17
lesson: 28
tags: [self-hosted, vllm, sglang, llama-cpp, ollama, tgi, trt-llm, engine-selection]

---

Biorąc pod uwagę sprzęt (CPU / Apple Silicon / AMD / NVIDIA Hopper / NVIDIA Blackwell), skalę (pojedynczy użytkownik / mały zespół / produkcja / przedsiębiorstwo) i obciążenie (czat ogólny / agent / RAG / długi kontekst / kod), przygotuj rekomendację silnika.

Wyprodukuj:

1. Silnik. Nazwij konkretny silnik. Przytocz drzewo skupiające się na sprzęcie, na drugiej skali i na trzecim obciążeniu.
2. Dlaczego nie alternatywy. Dla każdego alternatywnego silnika określ, dlaczego nie jest on wybrany (tryb konserwacji TGI, AMD wyklucza TRT-LLM, Ollama jest przeznaczona tylko dla deweloperów).
3. Rurociąg. W przypadku produkcji nazwij wzór potoku (dev Ollama → staging llama.cpp → prod vLLM/SGLang) i potwierdź przepływ w formacie wagi (GGUF lub HF).
4. Układanie produkcji. W skali produkcyjnej wskaż fazę 17 · 18 (stos produkcyjny), · 17 (dezagregowany), · 11 (router obsługujący pamięć podręczną) dla kompozycji.
5. Migracja TGI. Jeżeli podmiotem dominującym jest TGI, określ plan i harmonogram migracji – nie jest to pilne, ale powinno rozpocząć się w ciągu 6 miesięcy.
6. Problem ze sprzętem. Wymień dwa twarde ograniczenia: tylko procesor → llama.cpp; AMD → brak TRT-LLM.

Twarde odrzucenia:
- Zaniechanie nowych projektów dla TGI w 2026 r. Odmowa – tryb konserwacyjny.
- Ollama do współdzielonej produkcji dla > 1 równoczesnego użytkownika. Odmowa — luka w przepustowości.
- Sugerowanie TRT-LLM bez potwierdzania tylko NVIDIA. Odmów — AMD/inna niż NVIDIA to twarda blokada.

Zasady odmowy:
- Jeśli sprzęt jest mieszany (niektóre AMD, niektóre NVIDIA), należy podjąć decyzję o silniku dla każdego klastra; nie zmuszaj jednego silnika.
— Jeśli obciążenie jest „nieznane/ogólne” w skali produkcyjnej, wybierz domyślnie vLLM i zaplanuj ponowną ocenę po 3 miesiącach danych o ruchu.
- Jeśli zespół chce „najszybciej na procesor graficzny bez dostępności Blackwell” i nalega na korzystanie wyłącznie z Hoppera, potwierdź — akceptowalne są zarówno TRT-LLM, jak i vLLM.

Wynik: jednostronicowa rekomendacja zawierająca silnik, odrzucone alternatywy, rurociąg, układanie produkcji, stan migracji TGI. Zakończ pojedynczym przeglądem kwartalnym: ponownie oceń wybór silnika, gdy kształt obciążenia zmieni się znacząco.