---

name: mtp-planner
description: Zaplanuj integrację przewidywania wielu tokenów dla nowego przebiegu przedtreningowego.
version: 1.0.0
phase: 10
lesson: 18
tags: [mtp, multi-token-prediction, deepseek-v3, pre-training, speculative-decoding]

---

Biorąc pod uwagę specyfikację przebiegu przed szkoleniem (skala modelu, ukryty rozmiar, warstwy, budżet tokenów danych, topologię GPU, wdrożenie docelowe) i określony cel (gęstszy sygnał szkoleniowy vs wersja robocza dekodowania spekulatywnego vs oba), utwórz plan integracji MTP.

Wyprodukuj:

1. Głębokość D. Wybierz 1 lub 2. DeepSeek-V3 używa D=1 i zgłasza akceptację dekodowania spekulatywnego na pierwszej głębokości na poziomie 80%+. D=2 to obszar malejących zwrotów dla większości przebiegów. Uzasadnij wybór względem budżetu obliczeniowego — każda dodatkowa głębokość dodaje mniej więcej jeden blok obliczeniowy transformatora na krok szkolenia.
2. Harmonogram lambda. Domyślnie: 0,3 przez pierwsze 10% treningu, 0,1 później. Dostosuj do 0,5 wcześniej dla małych modeli (poniżej 7B), gdzie gęstszy sygnał ma większe znaczenie; dostosuj w dół, jeśli zauważysz, że strata MTP dominuje nad stratą główną.
3. Budżet parametrów. Raportuj liczbę parametrów dla każdego modułu w porównaniu z modelem głównym. Upewnij się, że obciążenie jest mniejsze niż 5% głównych parametrów (gęste) lub mniejsze niż 3% (MoE).
4. Narzut pamięci i obliczeń. Określ ilościowo dodatkowe FLOPy przejścia w przód na krok (w przybliżeniu `D * transformer_block_cost`), dodatkową pamięć przejścia wstecz (pamięć aktywacji dla modułów D) i dodatkową szczytową pamięć VRAM (współdzielone osadzanie i głowica nie liczą się, lecz projekcja i blok transformatora tak).
5. Okablowanie czasu wnioskowania. Opisz, jak używać modułu MTP jako wersji roboczej dekodowania spekulatywnego przy wnioskowaniu. Nazwij ścieżkę integracji reguł Lewiatana i księgowość przywracania KV. Potwierdź zgodność z docelowym stosem wnioskowania (vLLM, SGLang, TensorRT-LLM).

Twarde odrzucenia:
- Dodanie MTP do gęstego modelu wstępnie przeszkolonego bez niego. Nie można dokonać modernizacji — moduły MTP nie zostały przeszkolone.
- D > 2 dla pierwszego całkowania. Zysk powyżej D=1 jest niewielki; złożoność szybko rośnie.
- MTP na modelu o parametrach aktywnych 1B. Sygnał jest słabszy niż koszty ogólne w tej skali.
- Używanie równoległych głowic (w stylu Gloeckle), gdy celem jest dekodowanie spekulatywne. Nie łączą się przyczynowo.

Zasady odmowy:
- Jeśli w danych przedtreningowych dominują krótkie sekwencje (poniżej 2 tys.), odrzuć. Zyski MTP zakładają, że sekwencje są wystarczająco długie, aby nadzór na głębokości 2 miał znaczenie.
- Jeśli docelowy stos wnioskowania w ogóle nie obsługuje dekodowania spekulatywnego, należy pamiętać, że MTP nadal kupuje gęstszy sygnał uczący i kontynuuje, ale flaguje niedopasowanie.
- Jeśli użytkownik kontynuuje trening wstępny na istniejącym gęstym punkcie kontrolnym bez MTP, odmów i zalecaj dodanie MTP tylko na początku czystego przebiegu treningowego lub podczas czystego resetu granic danych.

Dane wyjściowe: jednostronicowy plan integracji zawierający listę D, harmonogram lambda, narzut parametrów (bezwzględny i procentowy), narzut obliczeniowy (procent na krok uczenia) oraz plan okablowania spekulatywnego dekodowania w czasie wnioskowania. Zakończ akapitem „kryterium sukcesu” wymieniającym mierzoną metrykę, która uzasadnia utrzymanie MTP: współczynnik akceptacji na głębokości 1 po tokenach szkoleniowych 50B musi przekraczać 70%, w przeciwnym razie należy cofnąć architekturę.