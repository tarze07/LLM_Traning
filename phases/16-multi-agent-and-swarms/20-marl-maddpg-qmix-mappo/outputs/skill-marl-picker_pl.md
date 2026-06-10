---

name: marl-picker
description: Wybierz algorytm MARL (MADDPG, QMIX, MAPPO, IQL lub rozszerzenia) dla danego zadania wieloagentowego. Rozważ współpracę i rywalizację, typ przestrzeni działania, heterogeniczność, strukturę nagród i skalę.
version: 1.0.0
phase: 16
lesson: 20
tags: [multi-agent, MARL, MADDPG, QMIX, MAPPO, CTDE]

---

Mając opis zadania wieloagentowego, wybierz algorytm MARL.

Wyprodukuj:

1. **Taksonomia zadań.** W pełni współpracujący (wspólna nagroda), w pełni konkurencyjny (o sumie zerowej), mieszany, o sumie ogólnej. Liczba agentów. Homogeniczne vs heterogeniczne.
2. **Obserwowalność.** Pełna (każdy agent widzi stan globalny), częściowa (każdy widzi tylko własną obserwację) lub z możliwością komunikacji.
3. **Przestrzeń akcji.** Dyskretna (podobna do Atari, SMAC) lub ciągła (świat cząstek, MuJoCo). Wpływa na wybór algorytmu.
4. **Struktura nagród.** Gęsta (w kształcie każdego kroku) vs rzadka (tylko terminal). Gęsty sprawia, że ​​MAPPO jest praktyczny; sparse potrzebuje pomocy przy przypisywaniu kredytów (dekompozycja wartości QMIX).
5. **Zalecenie dotyczące algorytmu.** Zacznij od MAPPO jako punktu odniesienia według Yu i in. 2022. Przełącz na:
   - QMIX, gdy potrzebne jest przypisanie kredytu opartego na współpracy + jednorodności + silnego i rzadkiego wynagrodzenia
   - MADDPG w przypadku mieszania (współpraca + rywalizacja) + działania ciągłe
   - Rozszerzenia (QTRAN, QPLEX, FACMAC), gdy ograniczenie monotoniczności jest zbyt restrykcyjne
6. **Infrastruktura szkoleniowa.** Czy masz wystarczającą ilość danych dotyczących interakcji, obliczony budżet, wiedzę specjalistyczną w zakresie kształtowania nagród, budżet stabilności (5-10 nasion na eksperyment)? Jeśli nie, zarekomenduj zasady na poziomie podpowiedzi dla agentów LLM.
7. **Umowa wdrożeniowa.** CTDE: w czasie wdrażania każdy agent widzi tylko lokalną obserwację. Napisz umowę jawnie, aby kod wykonawczy ją szanował.

Twarde odrzucenia:

- Wybór linii bazowej innej niż MAPPO do pierwszego uruchomienia. MAPPO to poziom bazowy na 2026 r.; zacznij tam.
- Używanie QMIX do mieszanych zadań opartych na współpracy i rywalizacji. Rozkład wartości zakłada agregację monotoniczną.
- Zalecanie szkolenia MARL dla systemów agentów LLM, którym brakuje danych dotyczących interakcji lub sygnału nagrody. Zasady na poziomie podpowiedzi będą działać lepiej, dopóki dane nie będą dostępne.
- Szkolenie bez rejestrowania obserwacji i działań poszczególnych agentów. Debugowanie jest niemożliwe.

Zasady odmowy:

— Jeśli zadanie zawiera mniej niż ~1000 epizodów danych dotyczących interakcji, zarekomenduj zasady na poziomie podpowiedzi lub nadzorowane dostrajanie.
- Jeśli zadanie nie jest markowskie (wymaga pamięci), ale zalecenie nie uwzględnia powtarzających się krytyków, zaznacz lukę.
- Jeśli zadanie ma charakter konkurencyjny o sumie ogólnej (wiele równowag), MARL sam nie wybiera żadnego; zalecić projekt mechanizmu lub wybór równowagi.

Wynik: jednostronicowy brief. Zacznij od jednozdaniowego zalecenia („Linia bazowa MAPPO ze scentralizowaną funkcją wartości; dyskretny aktor dla każdego agenta; CTDE przy wdrożeniu; 5 nasion na eksperyment”), a następnie siedem sekcji powyżej. Zakończ etapem szkolenia do wdrożenia: gromadzenie danych, szkolenie, ocena, wdrożenie.