---

name: framework-diff
description: Porównaj nowe ramy bezpieczeństwa lub informacje o wersji z RSP v3.0, PF v2, FSF v3.0.
version: 1.0.0
phase: 18
lesson: 18
tags: [rsp, pf, fsf, frontier-safety, safety-case]

---

Biorąc pod uwagę nowe ramy bezpieczeństwa, zasady lub informacje o wersji, porównaj je z Anthropic RSP v3.0, OpenAI PF v2, DeepMind FSF v3.0 wzdłuż pięciu osi strukturalnych.

Wyprodukuj:

1. Struktura poziomów. Czy struktura definiuje dyskretne progi możliwości? Czy są one zależne od domeny (w stylu FSF) czy globalne (w stylu RSP)?
2. Próg CBRN. Jaka ocena CBRN jest wymagana? Czy odnosi się do WMDP (lekcja 17) lub jego odpowiednika? Czy obejmuje badanie pobudzające?
3. Próg badań i rozwoju sztucznej inteligencji. Czy istnieje próg badań modelowych autonomicznych? Czy pasek oznacza „początkujący badacz” (Anthropic AI R&D-2) czy „znacznie przyspiesza skalowanie” (Anthropic AI R&D-4)?
4. Dopasowanie do konkurencji. Czy ramy umożliwiają zmniejszenie wymogów, jeśli konkurenci dostarczają towary bez porównywalnych zabezpieczeń? Rama dostosowana do dynamiki wyścigu lub zgodna z motywacją, stosownie do przypadku.
5. Konstrukcja obudowy bezpieczeństwa. Czy wymagane jest pisemne uzasadnienie bezpieczeństwa? Czy chodzi o monitorowanie, nieczytelność lub niemożność działania? Co to jest pasek dowodów?

Twarde odrzucenia:
- Dowolne ramy bezpieczeństwa bez progów zdolności poszczególnych poziomów.
- Wszelkie ramy, w których pominięto odniesienie do zarządzania zewnętrznego (brytyjska AISI, amerykańska CAISI, EU AI Office).
- Wszelkie ramy, które twierdzą, że „dostosowujemy się do wszystkich opublikowanych ram” bez określonych liczb progowych.

Zasady odmowy:
- Jeśli użytkownik zapyta, który framework jest „najlepszy”, odrzuć ranking i wskaż dopasowanie strukturalne.
- Jeśli użytkownik poprosi o liczbowe zalecenie dotyczące progu, odmów — progi są specyficzne dla laboratorium i zależą od jego infrastruktury pomiarowej.

Wynik: jednostronicowe porównanie trzech platform, oznaczone luki i jedno konkretne zalecenie dotyczące progu do dodania. Przytocz RSP v3.0, PF v2, FSF v3.0 jeden raz.