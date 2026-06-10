---

name: vllm-scheduler-reader
description: Zdiagnozuj konfigurację obsługi vLLM, czytając pokrętła na poziomie programu planującego i identyfikując, które z nich: PagedAttention, ciągłe przetwarzanie wsadowe i wstępne wypełnianie fragmentami stanowi wąskie gardło.
version: 1.0.0
phase: 17
lesson: 04
tags: [vllm, paged-attention, continuous-batching, chunked-prefill, serving, scheduler]

---

Biorąc pod uwagę konfigurację obsługi vLLM (model, typ d, sprzęt, `--gpu-memory-utilization`, `--max-num-batched-tokens`, `--enable-chunked-prefill`, `--speculative-model` lub `--speculative-config`, maksymalna współbieżność i obserwowany zestaw metryk wynoszący średnią TTFT/P99, średnią ITL/P99, przepustowość tok/s), utwórz diagnozę na poziomie harmonogramu.

Wyprodukuj:

1. Konfiguracja odczytana. Dla każdej flagi nazwij kontrolowane przez nią zachowanie programu planującego oraz wartość domyślną na rok 2026. Oznacz dowolną flagę ustawioną na wartość inną niż domyślna i wyjaśnij dlaczego.
2. Identyfikacja wąskiego gardła. Sklasyfikuj wąskie gardło jako jedno z: niedostateczna obsługa PagedAttention (głód bloków KV), przeciągnięcie ciągłego przetwarzania wsadowego (wzrost kolejki OCZEKIWANIE), nieprawidłowe rozmiary fragmentarycznego wstępnego wypełnienia (skok ogona TTFT), dekodowanie związane z obliczeniami (minimalny poziom ITL) lub związane z HBM (nie można zmieścić wsadu). Uzasadnij za pomocą zgłoszonych wskaźników.
3. Zalecenia dotyczące pokrętła. Konkretne, uporządkowane działania — którą flagę odwrócić, jaką wartość wypróbować i jakie metryki obserwować. Nie sugeruj „wypróbuj więcej procesorów graficznych” bez uprzedniego wyczerpującego dostrojenia na poziomie harmonogramu.
4. Kontrola kompatybilności. W szczególności dla vLLM v0.18.0: oznacz kombinację `--enable-chunked-prefill` + `--speculative-model` jako twardą niezgodność. Zalecane dekodowanie spekulatywne N-gram GPU w wersji 1 jako udokumentowany wyjątek, jeśli oba są pożądane.
5. Co dalej czytać. W zależności od postawionej diagnozy wskaż jedną z informacji o wydaniu vLLM v0.18.0, artykuł PagedAttention lub przewodnik po programie planującym Aleksa Gordic V1.

Twarde odrzucenia:
- Diagnozowanie bez czterech podstawowych wskaźników (TTFT, ITL, przepustowość, współbieżność). Odmów i poproś o zestaw metryczny.
— Polecanie `--enable-chunked-prefill` bez sprawdzania konfiguracji dekodowania spekulatywnego.
- Traktowanie `DCGM_FI_DEV_GPU_UTIL` jako sygnału skalującego. vLLM wstępnie przydziela KV; liczby cykli pracy wprowadzają w błąd.

Zasady odmowy:
— Jeśli zgłoszona przepustowość jest niższa niż 100 tok/s na H100, wąskim gardłem prawdopodobnie nie jest vLLM — sprawdź tokenizator po stronie klienta, Python GIL lub serializację na poziomie żądania.
- Jeśli wartość `--gpu-memory-utilization` jest ustawiona poniżej 0,7, odmów dalszego dostrajania — operator zdecydował się zostawić HBM na stole, a rozwiązaniem jest podniesienie pułapu przed zmianą flag programu planującego.
- Jeśli operator poprosi o przepis na dekodowanie spekulatywne + wstępne wypełnienie fragmentaryczne na podstawie spekulacji modelu roboczego, odmów i podaj niezgodność z wersją 0.18.0. Zamiast tego wskaż EAGLE-3 w fazie 17 · 05.

Wynik: jednostronicowa diagnoza harmonogramu zawierająca flagi, wąskie gardła, uporządkowane zalecenia, uwagi dotyczące zgodności i wskaźnik następnego przeczytania. Zakończ akapitem „Co dalej mierzyć”, wymieniając jedno z P99 ITL, współczynnik alokacji bloków lub głębokość kolejki OCZEKIWANIE, w zależności od zidentyfikowanego wąskiego gardła.