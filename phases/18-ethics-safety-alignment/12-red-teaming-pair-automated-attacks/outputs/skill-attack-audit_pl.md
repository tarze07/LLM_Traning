---

name: attack-audit
description: Przeprowadź audyt raportu z oceny zespołu czerwonego pod kątem zasięgu ataków, budżetu, tożsamości sędziego i zestawu zachowań.
version: 1.0.0
phase: 18
lesson: 12
tags: [red-teaming, jailbreak, pair, harmbench, jailbreakbench, asr]

---

Mając raport z oceny zespołu czerwonego, sprawdź, czy ocena jest porównywalna z opublikowanymi wartościami bazowymi i czy potwierdza zawarte w niej wnioski.

Wyprodukuj:

1. Pokrycie ataku. Wypisz każdy przebieg ataku: PAIR, GCG, AutoDAN, TAP, PAP, ręczny. Oznacz brakującą klasę ataku. Raport, który obsługuje tylko jedną rodzinę ataków, nie może pochwalić się solidnością.
2. Budżet na atak. Zgłoś budżet zapytań na monit dla każdego ataku. Oświadczenia o sukcesie PAIR przy 20 zapytaniach nie są porównywalne z oświadczeniami o sukcesie GCG przy 500 krokach.
3. Tożsamość sędziego. Którego sędziego LLM użyto (GPT-4-turbo, Llama Guard, StrongREJECT, klasyfikator wewnętrzny)? Kalibracja sędziego wpływa na wariancję ASR.
4. Zestaw zachowań. JailbreakBench (100 zachowań, 10 kategorii), HarmBench (510 zachowań, 7 kategorii), wewnętrzny czy inny? Określ, czy zbiór jest publiczny i odtwarzalny.
5. Kontrola transferu. Jeśli zespół czerwonych zoptymalizowano w oparciu o jeden model, czy zgłoszono ASR transferu w odniesieniu do innych modeli? ASR dla jednego modelu to górna granica solidności rodziny modeli, a nie dolna granica.

Twarde odrzucenia:
- Każde twierdzenie „nasz model jest solidny” oparte na pojedynczej rodzinie ataków.
- Wszelkie raporty ASR bez budżetu zapytań.
- Dowolny ASR wykorzystujący sędziego innego niż opublikowany benchmark bez kalibracji względem sędziego wzorcowego.

Zasady odmowy:
- Jeśli użytkownik zapyta „czy nasz model jest odporny na jailbreak”, odrzuć odpowiedź binarną i wskaż powyższą strukturę obejmującą wiele ataków, wielu sędziów i kontrolę transferu.
- Jeśli użytkownik poprosi o zalecany zestaw narzędzi do ataku, odrzuć jedno zalecenie i wskaż empiryczną rozbieżność w HarmBench na rok 2024.

Wynik: jednostronicowy audyt, który wypełnia pięć powyższych sekcji, wskazuje brakujące klasy ataków i szacuje, czy ASR jest zaniżony, czy zawyżony w stosunku do powtarzalnych wzorców. Cytuj Chao i in. (arXiv:2310.08419) i po jednym odpowiednim dokumencie referencyjnym.