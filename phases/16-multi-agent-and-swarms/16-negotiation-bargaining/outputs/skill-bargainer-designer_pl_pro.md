---

name: bargainer-designer
description: Zaprojektuj protokół negocjacyjny: określ komponenty odpowiedzialne za kalkulację i narrację, rozdziel prywatny obszar roboczy (scratchpad) od wiadomości publicznych, ustal limity rund oraz metryki skuteczności transakcji.
version: 1.0.0
phase: 16
lesson: 16
tags: [multi-agent, negotiation, bargaining, contract-net, OG-Narrator]

---

Na podstawie opisu scenariusza negocjacji lub dynamicznego rynku zadań (negocjacje dwustronne, aukcja wielostronna, alokacja zadań przez Contract Net), zaprojektuj protokół interakcji.

Opracuj:

1. **Mechanizm rynkowy.** Negocjacje dwustronne, aukcja z N oferentami, alokacja typu Contract Net lub koalicja wielostronna. Zdefiniuj strukturę gry.
2. **Generator ofert.** Deterministyczny (np. ustępstwa Zeuthena, równowaga Rubinsteina, harmonogram liniowy) lub sterowany przez LLM. Domyślnie należy stosować generator deterministyczny, chyba że oferta ma charakter jakościowy/strukturalny (np. plany podziału zadań, alokacja ról).
3. **Warstwa narracji (LLM).** Zadania dla modelu LLM: językowa oprawa oferty, taktyki perswazyjne, profil osobowościowy. Wyraźnie zdefiniuj obszary, w których LLM NIE podejmuje decyzji (np. wartości liczbowe).
4. **Separacja kanałów (prywatny vs publiczny).** Mechanizm izolacji procesu wnioskowania od komunikatów wysyłanych do oponenta. Zdefiniuj schemat składający się z pól „prywatny notatnik” (scratchpad) oraz „wiadomość publiczna”. Zgodnie z arXiv:2503.06416 krok ten jest krytyczny dla ochrony strategii.
5. **Limit rund.** Maksymalnie 3-5 rund w negocjacjach dwustronnych. Brak limitu jest niedopuszczalny — sprzyja uleganiu konformizmowi i generowaniu nieprzemyślanych ofert.
6. **Wycena rezerwowa i ochrona BATNA.** Każda ze stron musi znać swoje parametry progowe (BATNA). Jeśli oponent próbuje wyciągnąć te informacje, narrator LLM musi odmówić ich ujawnienia. Wdrażaj reguły walidacji (guardrails) wiadomości wychodzących pod tym kątem.
7. **Monitorowanie skuteczności.** Oczekiwany bazowy wskaźnik sukcesu transakcji (odwołaj się do wyników badań: zakres 27–89% w zależności od przyjmowanej architektury). Określ próg alarmowy sygnalizujący regresję skuteczności.
8. **Ścieżka eskalacji.** Przekazanie sterowania (w przypadku impasu, przekroczenia strefy ZOPA lub naruszenia reguł protokołu przez oponenta) do agenta mediatora lub operatora (człowieka).

Kryteria wykluczające:

- Wyliczanie wartości liczbowych ofert bezpośrednio przez model LLM bez wsparcia ze strony deterministycznych algorytmów (badania w arXiv:2402.15813 wskazują, że obniża to skuteczność do ok. 27%).
- Brak separacji prywatnego obszaru roboczego (scratchpad) od publicznych komunikatów (oponenci odczytają strategię z łańcucha myśli).
- Zezwalanie na nieograniczoną liczbę rund negocjacyjnych (prowadzi to do niekorzystnych ustępstw i konformizmu).
- Uruchamianie jednego agenta w podwójnej roli (kupującego i sprzedającego w ramach jednej sesji) — negocjacje wymagają asymetrii i prywatności informacji, a łączenie ról to uniemożliwia.

Zasady odmowy (Rejection rules):

- Jeśli negocjacje dotyczą kryteriów jakościowych (np. zapisy umowy, warunki współpracy), a nie wartości liczbowych, model OG-Narrator może nie mieć zastosowania. W takich przypadkach zaleć ustrukturyzowany format ofert ze sprawdzaniem schematu JSON.
- Jeśli architektura nie pozwala na separację notatnika (np. pojedyncze wywołanie LLM), wyraźnie wskaż ryzyko ujawnienia ceny rezerwowej i zaleć model oparty na dwóch osobnych wywołaniach.
- W negocjacjach o wysokim poziomie ryzyka (gdzie oponent może manipulować informacjami), zaleć wprowadzenie trzeciej strony (agenta mediatora) oraz rejestrowanie (logowanie) wszystkich ofert do celów audytu.

Format wyjściowy: jednostronicowy brief projektowy. Rozpocznij od jednozdaniowego streszczenia (np. „Negocjacje dwustronne: generator ofert Zeuthena + narrator LLM, limit 5 rund, dedykowany scratchpad, alert przy skuteczności poniżej 85%”), po którym następuje osiem opisanych wyżej sekcji. Zakończ przykładowym komunikatem: przedstaw, co widzi oponent, a co pozostaje wyłącznie w prywatnym notatniku (scratchpad).
