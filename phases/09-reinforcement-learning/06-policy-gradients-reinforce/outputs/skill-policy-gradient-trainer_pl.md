---

name: policy-gradient-trainer
description: Utwórz konfigurację szkoleniową REINFORCE / aktor-krytyk / PPO dla danego zadania i zdiagnozuj problemy z wariancją.
version: 1.0.0
phase: 9
lesson: 6
tags: [rl, policy-gradient, reinforce]

---

Biorąc pod uwagę środowisko (działania dyskretne/ciągłe, horyzont, statystyki nagród), wynik:

1. Szef polityki. Softmax (dyskretny) lub Gaussian (ciągły) ze zliczaniem parametrów.
2. Linia bazowa. Brak (waniliowy), bieżący średni, wyuczony krytyk `V̂(s)` lub A2C.
3. Kontrole wariancji. Domyślnie włączona nagroda, normalizacja powrotu, wartość klipu gradientu.
4. Premia za entropię. Współczynnik β i harmonogram zaniku.
5. Wielkość partii. Odcinki na aktualizację; umowa dotycząca świeżości danych dotycząca zasad.

Odmów WZMOCNIENIA bez linii bazowej na horyzoncie > 500 kroków. Zrezygnuj z ciągłego sterowania za pomocą głowicy softmax. Oznacz dowolny przebieg z `β = 0` i zaobserwowaną entropią zasad < 0,1 jako załamanie entropii.