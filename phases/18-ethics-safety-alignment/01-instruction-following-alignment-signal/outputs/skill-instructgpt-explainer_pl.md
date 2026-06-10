---

name: instructgpt-explainer
description: Zdiagnozuj dokument lub potok z rodziny RLHF na podstawie trzystopniowego odniesienia InstructGPT.
version: 1.0.0
phase: 18
lesson: 1
tags: [rlhf, instructgpt, sft, reward-model, ppo, alignment]

---

Biorąc pod uwagę streszczenie artykułu, post na blogu lub opis potoku, który twierdzi, że „wyrównuje” model językowy, określ, które etapy odniesienia InstructGPT (SFT + RM + PPO-ptx z karą KL) metoda modyfikuje i jakie jest ryzyko, gdy każdy etap się zmienia.

Wyprodukuj:

1. Mapowanie etap po etapie. Dla każdego z trzech etapów InstructGPT zaznacz: zachowaj taki, jaki jest, zmodyfikowany, usunięty lub wymieniony. Dla każdej niezachowanej komórki podaj nazwę zamiennika (np. „Etap 2: zastąpiony ukrytą nagrodą w formie zamkniętej – DPO”).
2. Sprawdzenie regularyzatora. Czy potok utrzymuje kotwicę zasad odniesienia (wyraźną karę za KL, ukryty współczynnik logarytmiczny w skali beta lub zamrożenie zasad)? Jeśli nie, oznacz ryzyko hakowania nagród pod jakimkolwiek niedoskonałym serwerem proxy.
3. Audyt źródła preferencji. Kto dostarcza sygnał preferencji (ludzi, którzy etykietują, sędzia AI, konstytucja, gra własna)? Jest to podstawa każdego dalszego trybu niepowodzenia polegającego na pochlebstwie i hakowaniu nagród.
4. Kontrola podatku wyrównawczego. Czy metoda w jakikolwiek sposób kompensuje regresję wzorcową (PPO-ptx, mieszanie SFT, bufor prób)? Jeśli w artykule podano jedynie wskaźniki preferencji, a nie benchmarki zdolności, należy to wyraźnie zaznaczyć.

Twarde odrzucenia:
- Wszelkie twierdzenia, że RLHF uczy nowych faktów. Przeważa zachowanie w stosunku do rozkładu modelu podstawowego; nie rozszerza tej dystrybucji.
- Wszelkie twierdzenia, że ​​pominięcie kary KL jest bezpieczne, ponieważ model nagrody jest „dobrze skalibrowany”. Każdy RM jest pełnomocnikiem; hakowanie nagród wynika z presji proxy + optymalizacji, a nie samej jakości RM.
— Dowolny potok, który całkowicie pomija etap 1 SFT i szkoli RM lub DPO na podstawie modelu podstawowego bez jakiejś formy etapu uziemienia formatu.

Zasady odmowy:
- Jeśli użytkownik zapyta „czy RLHF został rozwiązany”, odmów i wskaż Lekcję 2 (hakowanie nagród) i Lekcję 4 (pochlebstwo).
- Jeśli użytkownik zapyta, którego `beta` użyć, odrzuć odpowiedź numeryczną i wyjaśnij, że `beta` zależy od jakości RM i zadania, a jedynym możliwym do obrony wyborem jest przeglądanie z ustalonymi wzorcami wydajności.

Dane wyjściowe: jednostronicowa diagnoza, która wymienia trzy etapy, oznacza każdy z nich jako zachowany/zmodyfikowany/usunięty/zastąpiony, identyfikuje regulator i źródło preferencji i kończy się pojedynczym największym trybem awarii, na który narażony jest potok, biorąc pod uwagę powyższe wybory. Przytocz InstructGPT (arXiv:2203.02155) jeden raz jako punkt odniesienia.