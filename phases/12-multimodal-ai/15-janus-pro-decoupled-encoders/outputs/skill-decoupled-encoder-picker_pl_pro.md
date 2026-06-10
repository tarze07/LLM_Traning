---

name: decoupled-encoder-picker
description: Decyduje, czy zunifikowany model VLM powinien mieć rozdzielone enkodery wizualne, oraz dokonuje wyboru między Janus-Pro, JanusFlow a InternVL-U.
version: 1.0.0
phase: 12
lesson: 15
tags: [janus-pro, janusflow, internvl-u, decoupled-encoders, unified-model]

---

Na podstawie specyfikacji zunifikowanego modelu (zrozumienie + generowanie, opcjonalna edycja/inpainting), budżetu obliczeniowego oraz wymagań dotyczących otwartych wag (open weights), rekomendujemy architekturę z rozdzielonymi enkoderami i proponujemy konkretną konfigurację.

Wygeneruj:

1. **Wybór architektury:** Janus-Pro (generowanie oparte na VQ), JanusFlow (generowanie z dopasowaniem przepływu - Rectified Flow), InternVL-U (natywne trenowanie wstępne + rozdzielone enkodery).
2. **Dobór enkoderów:** SigLIP-SO400m do zadań rozumienia; MAGVIT-v2 / IBQ VQ do dyskretnego generowania; VAE typu SD3 do generowania ciągłego.
3. **Harmonogram etapów uczenia na danych:** Etap 1 – dopasowanie (50–100 mln par), Etap 2 – zunifikowany (70+ mln par), Etap 3 – strojenie instrukcyjne (1+ mln próbek). Przytocz dane dotyczące 5,4-krotnego skalowania parametrów oraz 2,8-krotnego skalowania danych w Janus-Pro.
4. **Strategia routingu:** na podstawie specjalnych tokenów w promptach (jawne znaczniki `<understand>` / `<generate>`) lub z użyciem klasyfikatora zadań.
5. **Inicjalizacja współdzielonego korpusu:** inicjalizacja na bazie wstępnie wytrenowanego modelu LLM (DeepSeek, Qwen, Llama), zamiast trenowania od zera.
6. **Docelowy poziom jakości:** oczekiwane wyniki w benchmarkach MMMU (~60 dla wersji 7B) oraz GenEval (~0,80 dla Janus-Pro 7B / ~0,85+ dla InternVL-U).

Kryteria odrzucenia (Twarde reguły):
- Proponowanie zunifikowanego modelu z jednym wspólnym enkoderem (Show-o / Transfusion), gdy wymagana jakość w obu zadaniach (rozumienie i generowanie) musi być konkurencyjna. Podejście z rozdzielonymi enkoderami jest w tym przypadku jedyną właściwą drogą.
- Rekomendowanie trenowania wstępnego od zera dla modeli o rozmiarze <10B. Zamiast tego należy ponownie wykorzystać korpus wstępnie wytrenowanego LLM.
- Proponowanie pierwszej (oryginalnej) wersji Janus zamiast Janus-Pro w nowych projektach. Janus-Pro jest jego bezpośrednim i lepszym następcą.

Zasady odmowy (Rezygnacja z projektu):
- Jeśli użytkownik potrzebuje wyłącznie funkcji rozumienia obrazu, zrezygnuj z rozdzielania enkoderów i rekomenduj rodzinę LLaVA. Pojedynczy enkoder będzie w zupełności wystarczający.
- Jeśli użytkownik potrzebuje wyłącznie generowania obrazów, odmów realizacji i poleć Stable Diffusion 3 / Flux – wyspecjalizowane modele generatywne oferują znacznie wyższą jakość T2I.
- W przypadku budżetu obliczeniowego <50 tys. godzin GPU, odrzuć InternVL-U (wymaga natywnego trenowania wstępnego od zera) i zarekomenduj Janus-Pro (który wykorzystuje gotowy, wstępnie wytrenowany LLM).

Dane wyjściowe: Jednostronicowy plan zawierający wybór architektury, konfigurację enkoderów, harmonogram etapów uczenia, strategię routingu, sposób inicjalizacji współdzielonego korpusu oraz docelowe wskaźniki jakości. Na końcu umieść odnośniki do prac: arXiv 2501.17811 (Janus-Pro), 2411.07975 (JanusFlow), 2603.09877 (InternVL-U).
