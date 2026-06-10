---

name: vad-tuner
description: Wybierz model VAD, próg, wyciszenie kaca, pre-roll i strategię wykrywania skrętu dla agenta głosowego.
version: 1.0.0
phase: 6
lesson: 14
tags: [vad, silero, cobra, turn-detection, flush-trick]

---

Biorąc pod uwagę obciążenie pracą (konsument / call center / brzeg / dostępność; profil szumów; mieszanka języków; opóźnienie), wynik:

1. VAD. Silero VAD (domyślnie) · Cobra (dokładność komercyjna) · Segmentacja pyannote (stopień diaryzacji) · WebRTC VAD (starsze / małe). Powód w jednym zdaniu.
2. Parametry. Próg (0,3-0,5), min. mowa (200-300 ms), wyciszenie kaca (400-800 ms), pre-roll (250-500 ms).
3. Semantyczne wykrywanie skrętu. Włączone (czujnik skrętu LiveKit lub niestandardowy MLP) czy nie. Powód powiązany z oczekiwanymi wzorcami mowy użytkownika.
4. Sztuczka z kolorem. Włączone (jeśli STT to obsługuje — Kyutai / Deepgram) lub nie. Oczekiwane oszczędności w zakresie opóźnień.
5. Strażnicy. Odrzucaj mowę krótszą niż minuta; zawsze miej pre-roll; obejście wyciszenia kaca na użytkownika; otwarcie awaryjne, jeśli usługa VAD nie działa (traktuj wszystko jako mowę).

Odrzuć VAD zasilany wyłącznie energią na potrzeby produkcji – jest zbyt głośny. Odmów zero ciszy i kaca — będzie przeszkadzać użytkownikom. Odrzuć VAD oparty na szeptach, gdy dostępny jest dedykowany Silero (wolniejszy, mniej dokładny).

Przykładowe wejście: „IVR dla call center do zmiany rezerwacji linii lotniczych. Hałaśliwe tło (lotnisko). Angielski + hiszpański. &lt; Wykrywanie skrętu w ciągu 500 ms.”

Przykładowe wyjście:
- VAD: Cobra (komercyjny) ze względu na przewagę w zakresie odporności na hałas. Jeśli koszty są zbyt wysokie, wróć do Silero.
- Parametry: próg 0,4 (poziom hałasu lotniska jest wysoki); min. mowa 300 ms; wyciszyć kaca 600 ms (użytkownicy często zatrzymują się podczas IVR, aby odczytać numery lotów); przed filmem 400 ms.
- Zwrot semantyczny: włączony czujnik skrętu LiveKit — częste przerwy w połowie zdania („Muszę zmienić lot… na jutro”).
- Sztuczka Flush: włączona w streamingu Deepgram. Oczekiwane oszczędności: 400 ms → 150 ms opóźnienia na końcu obrotu.
- Strażnicy: otwarcie awaryjne, jeśli Cobra/Deepgram jest nieosiągalny; dziennik audytu każdego zdarzenia związanego z uruchomieniem VAD w celu dostrojenia.