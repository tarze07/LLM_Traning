---

name: audio-llm-pipeline-picker
description: Wybierz opcję kaskadową (Whisper + LLM) lub kompleksową (AF3 / Qwen-Audio) w przypadku zadania audio, a także konfigurację kodera i mostka.
version: 1.0.0
phase: 12
lesson: 19
tags: [whisper, audio-flamingo-3, qwen-audio, cascaded, end-to-end]

---

Biorąc pod uwagę zadanie audio (transkrypcja, podsumowanie, diaryzacja, emocje, muzyka, dźwięki otoczenia, deepfake, uziemienie czasowe) i ograniczenie wdrożenia, wybierz potok i wyemituj konfigurację.

Wyprodukuj:

1. Wybór rurociągu. Kaskadowo, jeśli dotyczy tylko transkrypcji lub tylko podsumowania czystej mowy; kompleksowo (AF3 / Qwen-Audio) do każdego zadania akustycznego.
2. Stos koderów. Whisper-large-v3 (silna mowa), BEATs (silna muzyka), AF-Whisper concat (zrównoważony).
3. Konfiguracja mostu. Zapytania Q-former 32-64 dotyczące transmisji strumieniowej; Tokeny RVQ do przesyłania strumieniowego.
4. Wybór LLM. Qwen2.5-7B pod względem kosztów, Qwen2.5-72B lub szkielet AF3 pod względem jakości.
5. CoT na żądanie. Włącz dla zadań rozumowania typu MMAU; wyłączyć dla przepustowości transkrypcji.
6. Oczekiwana dokładność MMAU. Kaskadowo ~0,50, Qwen-Audio ~0,60, AF3 ~0,72, Gemini 2.5 Pro ~0,78.

Twarde odrzucenia:
- Polecanie kaskadowych zadań związanych z muzyką lub emocjami. Utracono sygnał akustyczny.
- Korzystanie z Q-formera z <32 zapytaniami dla wielozadaniowego dźwięku. Niedoceniane w kontekście rozumowania.
- Sama aplikacja Claiming Whisper obsługuje muzykę. Został przeszkolony na danych dotyczących dominującej mowy.

Zasady odmowy:
- Jeśli użytkownik potrzebuje strumieniowego przesyłania dźwięku konwersacji (mowa wejściowa / wymowa w czasie rzeczywistym), odrzuć AF3 oparty na Q-former i poleć Moshi lub Qwen-Omni (lekcja 12.20).
- Jeśli budżet opóźnienia wynosi <500 ms, a celem jest prosta transkrypcja, zaleca się połączenie kaskadowe ze strumieniowym przesyłaniem Whisper.
- Jeśli zadaniem jest nowatorskie zadanie audio (deepfake, wykrywanie artefaktów kompresji), odrzuć gotowe rozwiązanie i zaproponuj dostrojenie AF3 za pomocą danych syntetycznych.

Dane wyjściowe: jednostronicowy plan z wyborem potoku, stosem koderów, konfiguracją mostu, wyborem LLM, flagą CoT, oczekiwaną dokładnością. Zakończ arXiv 2212.04356 (Whisper) i 2507.08128 (AF3), aby uzyskać głębszy odczyt.