---

name: slo-goodput-gate
description: Stwórz recepturę wzorcową gotową do CI/CD, która będzie bramkować wdrożenia LLM pod kątem dobrej przepustowości, a nie przepustowości, z percentylami P50/P90/P99 i udokumentowanym wyborem narzędzi.
version: 1.0.0
phase: 17
lesson: 08
tags: [inference-metrics, goodput, ttft, tpot, itl, slo, benchmarking]

---

Biorąc pod uwagę obciążenie pracą (model, sprzęt, współbieżność docelową, typ interakcji z użytkownikiem — czat strumieniowy / jednorazowy / głos / agent), utwórz bramę SLO opartą na goodput dla CI/CD.

Wyprodukuj:

1. Specyfikacja SLO. Trzy progi: związany z TTFT P99, związany z TPOT P99, związany z E2E P99. Wybierz możliwe do obrony wartości z rodzaju interakcji (czat strumieniowy: TTFT 500 ms, TPOT 25 ms, E2E 3 s; głos: TTFT 300 ms mocniej; agent: E2E 5 s luźniej).
2. Przepis wzorcowy. Wybór narzędzia (LLMPerf lub GenAI-Perf — podaj, które wybierasz i dlaczego). Szybka dystrybucja (średnia + odchylenie standardowe tokenów wejściowych i wyjściowych). Przemiatanie współbieżności (25%, 50%, 100%, 150% wartości docelowej).
3. Obliczenie Goodput. Wzór: część żądań spełniająca jednocześnie wszystkie trzy ograniczenia. Cel >= 99% dla produkcji, >= 95% dla kanarków.
4. Raportowanie percentylowe. Dla każdego wskaźnika należy zgłosić P50, P90, P99 (nigdy nie oznacza to samego). Adnotacja oznacza jedynie sprawdzenie poprawności.
5. Uwaga dotycząca pułapki narzędziowej. Określ, czy narzędzie obejmuje, czy wyklucza TTFT z ITL. Popraw definicję przed porównaniem między zespołami.
6. Logika bramkowania. CI przechodzi, jeśli goodput >= docelowa współbieżność docelowa AT. Flaga, jeśli goodput pogarsza się o więcej niż 5 punktów w zakresie współbieżności od 100% do 150% — wskazuje, że brakuje zapasu w teście obciążenia.

Twarde odrzucenia:
- Bramkowanie wyłącznie na podstawie przepustowości. Odmów i żądaj dobrej opinii.
- Średnia raportowania bez P99. Odmawiać.
- Pomijanie nazwy i wersji narzędzia. Odmawiać.
- Benchmarking tylko przy docelowej współbieżności; zawsze rób zamiatanie.

Zasady odmowy:
- Jeśli użytkownik nie ma zapisanego poziomu SLO, odmów i najpierw zapisz go w oparciu o typ interakcji.
- Jeśli dystrybucja podpowiedzi to „identyczne podpowiedzi w pętli”, odmów — jest to pułapka jednolitości podpowiedzi. Wymagają realistycznego materiału syntetycznego.
- Jeśli benchmark wynosi < 30 przebiegów lub < 100 żądań na przebieg, odrzuć jako statystycznie niewystarczające.

Dane wyjściowe: jednostronicowa specyfikacja bramki SLO zawierająca listę progów, recepturę testu porównawczego, wybór narzędzia, szablon raportu percentylowego oraz regułę CI Pass/Fail. Zakończ akapitem „Co dalej mierzyć”, wymieniając jedną z krzywych dobra wydajność w porównaniu ze współbieżnością, czułość dystrybucji natychmiastowej lub porównanie włączania/wyłączania częściowego wstępnego wypełniania w zależności od znanej słabości.