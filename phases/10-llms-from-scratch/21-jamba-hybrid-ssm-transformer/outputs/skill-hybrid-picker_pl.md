---

name: hybrid-picker
description: Wybierz pomiędzy czystym Transformerem, hybrydą w stylu Jamba i czystym SSM dla danego obciążenia.
version: 1.0.0
phase: 10
lesson: 21
tags: [jamba, mamba, ssm, hybrid, long-context, memory-budget, architecture]

---

Biorąc pod uwagę specyfikację obciążenia (profil długości kontekstu p50/p99, zestawienie zadań, budżet pamięci na procesor graficzny, docelowa przepustowość, priorytet jakość/szybkość), polecam pomiędzy czystym Transformerem (+MoE +MLA), hybrydą w stylu Jamba i czystym modelem Mamba.

Wyprodukuj:

1. Wiadro o długości kontekstu. Krótkie (poniżej 16 tys.), średnie (16–64 tys.), długie (64–256 tys.) lub bardzo długie (ponad 256 tys.). Podejmuje decyzję za pierwszym podejściem.
2. Rekomendacja architektoniczna. Wybierz jeden z czystych Transformerów, hybryd 1:7, hybryd 1:3, hybryd 1:15 lub czystej Mamby. Uzasadnij użycie segmentu kontekstu oraz wymagań związanych z przywołaniem kontekstu zadania.
3. Sprawdzenie budżetu pamięci. Oblicz pamięć podręczną KV + stan SSM w kontekście docelowym. Upewnij się, że pasuje do docelowego akceleratora po uwzględnieniu wag i pamięci aktywacyjnej (zwykle 10–20 GB oprócz wag i pamięci podręcznej KV).
4. Ujawnianie kompromisów w zakresie jakości. Udokumentuj koszt jakości wybranego poziomu rzadkości. Hybrydy o stosunku poniżej 1:7 ulegają degradacji podczas wyszukiwania w kontekście w mierzalnych ilościach; czysta Mamba nie wykonuje niektórych zadań związanych ze śledzeniem stanu.
5. Zgodność stosu wnioskowania. Potwierdź, że wybrana architektura jest obsługiwana przez stos docelowy (vLLM, TensorRT-LLM, SGLang, llama.cpp). Hybrydy mają cieńsze pokrycie narzędzi niż czyste transformatory.

Twarde odrzucenia:
- Hybryda w stylu Jamba dla kontekstu poniżej 16 tys. Koszty architektoniczne nie są uzasadnione.
- Czysta Mamba do zadań wymagających intensywnego rozumowania lub zadań związanych z odsyłaczami do wielu dokumentów. Śledzenie stanu ogranicza ukąszenia.
- Przełożenia hybrydowe poniżej 1:15. Poniżej tego przywoływanie w kontekście jest zawodne.
— Wszelkie zalecenia, które nie mieszczą się w obliczonym budżecie pamięci dla określonego akceleratora.

Zasady odmowy:
— Jeśli obciążenie rzeczywiście obejmuje krótki i długi kontekst, odrzuć rekomendację hybrydową i poleć czysty Transformer (z MLA, jeśli to możliwe) — hybrydy sprawdzają się szczególnie w przypadku obciążeń długokontekstowych.
- Jeśli akcelerator jest klasy konsumenckiej (24 GB lub mniej), odrzuć modele hybrydowe i zaleć destylowaną małą hybrydę lub skwantowany czysty transformator.
— Jeśli obciążenie dotyczy wrażliwej na opóźnienia generacji partii 1, a model jest nowy (nie ma istniejącej ścieżki wdrożenia), odrzuć i zarekomenduj dobrze obsługiwany czysty transformator z dekodowaniem spekulatywnym (faza 10 · 15) jako prostszą ścieżkę.

Dane wyjściowe: jednostronicowe rekomendacje zawierające listę kontekstów, wybraną architekturę, pamięć podręczną KV w kontekście docelowym, ujawnienie kompromisów w zakresie jakości i zgodność stosu wnioskowania. Zakończ akapitem „co monitorować”, wymieniając konkretną ocenę w długim kontekście (LIMINA, LongBench, igła w stogu siana), która potwierdziłaby zalecenie w przypadku pierwszych 10 tys. żądań produkcyjnych.