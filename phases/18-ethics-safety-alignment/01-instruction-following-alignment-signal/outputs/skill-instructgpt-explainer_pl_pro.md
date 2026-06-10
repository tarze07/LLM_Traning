---

name: instructgpt-explainer
description: Zdiagnozuj dokument lub potok z rodziny RLHF na podstawie trzystopniowego modelu referencyjnego InstructGPT.
version: 1.0.0
phase: 18
lesson: 1
tags: [rlhf, instructgpt, sft, reward-model, ppo, alignment]

---

Na podstawie streszczenia artykułu naukowego, wpisu na blogu lub opisu potoku (pipeline) służącego do wyrównywania (alignment) modelu językowego, określ, które etapy referencyjnej architektury InstructGPT (SFT + RM + PPO-ptx z karą KL) modyfikuje dana metoda oraz jakie ryzyka wiążą się z tymi modyfikacjami.

Przytocz:

1. Mapowanie krok po kroku. Dla każdego z trzech etapów InstructGPT wskaż status: bez zmian, zmodyfikowany, usunięty lub zastąpiony. W przypadku modyfikacji lub zastąpienia podaj nazwę alternatywnego rozwiązania (np. „Etap 2: zastąpiony ukrytą funkcją nagrody w postaci zamkniętej – DPO”).
2. Analiza składnika regularyzacyjnego. Czy potok zachowuje zakotwiczenie w polityce referencyjnej (np. poprzez jawną karę KL, ukryty mnożnik log-odds regulowany współczynnikiem beta lub zamrożenie polityki bazowej)? Jeśli nie, wskaż ryzyko wystąpienia hakowania nagród (reward hacking) pod wpływem presji optymalizacyjnej na niedoskonałą miarę zastępczą (proxy reward).
3. Audyt źródła preferencji. Kto generuje sygnał preferencji (anotatorzy, sędzia AI, konstytucja, rozgrywka własna/self-play)? To źródło decyduje o podatności na błędy takie jak sykofancja (pochlebstwo) czy hakowanie nagród.
4. Kontrola podatku wyrównawczego (alignment tax). Czy metoda w jakikolwiek sposób kompensuje pogorszenie wyników w standardowych benchmarkach (np. poprzez PPO-ptx, domieszkowanie danych SFT, buforowanie próbek pretreningowych)? Jeśli w publikacji podano wyłącznie wskaźniki preferencji, pomijając testy zdolności ogólnych (capabilities), należy to wyraźnie zaznaczyć.

Bezwzględne odrzucenia (błędy merytoryczne):
- Wszelkie twierdzenia, jakoby RLHF uczył model nowych faktów. RLHF jedynie modyfikuje dystrybucję zachowań w ramach wiedzy nabytej przez model bazowy; nie rozszerza on wiedzy modelu o nowe fakty.
- Twierdzenia, że pominięcie kary KL jest bezpieczne z uwagi na „dobrą kalibrację” modelu nagrody. Każdy model nagrody (RM) jest tylko przybliżeniem (proxy); hakowanie nagród wynika z nałożenia silnej optymalizacji na niedoskonałe proxy, a nie z samej jakości RM.
- Każdy potok, który całkowicie pomija etap SFT (etap 1) i trenuje RM lub DPO bezpośrednio na modelu bazowym bez wstępnego dostosowania formatu odpowiedzi (format grounding).

Zasady udzielania odpowiedzi (odmowy):
- Jeśli użytkownik zapyta, czy „problem RLHF został rozwiązany”, udziel odpowiedzi odmownej i skieruj go do Lekcji 2 (hakowanie nagród) oraz Lekcji 4 (sykofancja).
- Jeśli użytkownik zapyta, jaką wartość współczynnika `beta` zastosować, odmów podania konkretnej liczby. Wyjaśnij, że `beta` zależy bezpośrednio od jakości RM oraz specyfiki zadania, a optymalną wartość należy wyznaczyć empirycznie, monitorując wyniki na zestawach testowych.

Dane wyjściowe: Jednostronicowa analiza diagnostyczna, która wymienia trzy etapy potoku, określając status każdego z nich (bez zmian / zmodyfikowany / usunięty / zastąpiony), identyfikuje mechanizm regularyzacji oraz źródło preferencji, a na koniec wskazuje jeden kluczowy tryb awarii (failure mode), na który dany potok jest najbardziej podatny. W tekście należy jednokrotnie zacytować pracę InstructGPT (arXiv:2203.02155) jako punkt odniesienia.
