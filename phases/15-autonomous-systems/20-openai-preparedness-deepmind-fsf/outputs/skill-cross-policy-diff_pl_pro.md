---

name: cross-policy-diff
description: Dokonaj porównania zasad bezpieczeństwa dla określonej zdolności modelu, korzystając jako odniesienia z OpenAI Preparedness Framework v2, Anthropic RSP v3.0 oraz DeepMind FSF v3.
version: 1.0.0
phase: 15
lesson: 20
tags: [preparedness-framework, fsf, rsp, cross-policy, scaling-policy]

---

Na podstawie wskazanej zaawansowanej zdolności modelu (np. autonomii dalekiego zasięgu, ARA, automatyzacji prac badawczo-rozwojowych) przygotuj zestawienie różnic w politykach bezpieczeństwa, wskazując sposób klasyfikacji tej zdolności przez poszczególne laboratoria oraz wyzwalane procedury ochronne.

Przygotuj:

1. **Klasyfikacja według OpenAI PF v2.** Wskaż, czy zdolność należy do kategorii monitorowanych (tracked), czy badawczych (research). Jeśli jest monitorowana, określ warunki wygenerowania raportów o możliwościach i zabezpieczeniach. Jeśli należy do kategorii badawczych, zaznacz, że dokument przewiduje jedynie „potencjalne” środki zaradcze.
2. **Klasyfikacja według Anthropic RSP v3.0.** Określ przypisany próg (np. ASL-3, AI R&D-4, zakodowany na stałe zakaz) oraz przewidziane środki zaradcze (np. przygotowanie uzasadnienia bezpieczeństwa, procedury wdrożeniowe). Potwierdź, czy zobowiązanie ma charakter jednostronny ze strony Anthropic, czy jest jedynie rekomendacją dla branży.
3. **Klasyfikacja według DeepMind FSF v3.** Wskaż domenę (Cyber, Bio, ML R&D, CBRN), krytyczny poziom zdolności (CCL) lub poziom monitorowany (TCL). Określ, czy uruchamiane jest automatyczne wykrywanie zwodniczego dopasowania.
4. **Podsumowanie spójności.** Przeanalizuj, czy laboratoria są zgodne co do znaczenia danej zdolności, czy też istnieją poważne rozbieżności. Wskaż, która klasyfikacja jest najbardziej restrykcyjna, a która najbardziej liberalna.
5. **Metodologia i realizacja pomiaru.** Każda klasyfikacja opiera się na konkretnych testach. Określ sposób pomiaru danej zdolności oraz podmiot odpowiedzialny za ewaluację (np. METR, Apollo, testy wewnętrzne czy zewnętrzne).

Kryteria bezwzględnego odrzucenia (Hard rejects):
- Deklarowanie spójności między politykami na podstawie ogólnych komunikatów prasowych bez poparcia ich zapisami z oficjalnych dokumentów.
- Przypisywanie klasyfikacji bez powołania się na konkretną sekcję lub klauzulę w dokumencie źródłowym.
- Utożsamianie kategorii badawczej (research) z monitorowaną (tracked) w OpenAI, ze względu na odmienne skutki operacyjne.

Zasady odmowy zatwierdzenia:
- Jeśli użytkownik nie podaje fragmentów z oficjalnych dokumentów dla każdej klasyfikacji, zablokuj proces i zażądaj najpierw cytatów źródłowych.
- Jeśli użytkownik zakłada, że samo istnienie polityki bezpieczeństwa gwarantuje jej realizację, odrzuć wniosek i zażądaj dowodów wdrożenia konkretnych środków ochrony.
- Jeśli twierdzi się, że dana zdolność jest objęta strukturą zabezpieczeń, ale brakuje dla niej jasnego odniesienia w tekście, odrzuć zgłoszenie.

Format raportu z analizy porównawczej:

Raport musi zawierać:
- **Definicja zdolności** (jedno zdanie)
- **Wiersz OpenAI PF v2** (klasyfikacja, kryterium wyzwalające, klauzula źródłowa)
- **Wiersz Anthropic RSP v3.0** (klasyfikacja, warunek wyzwalający, charakter zobowiązania: jednostronne vs zalecenie branżowe)
- **Wiersz DeepMind FSF v3** (domena, CCL/TCL, weryfikacja pod kątem zwodniczego dopasowania)
- **Podsumowanie spójności** (obszary zgodności i istotne rozbieżności)
- **Realizacja pomiaru** (podmiot wykonujący testy, częstotliwość ewaluacji)
- **Rekomendacja analityka** (wskazanie podejścia najbardziej i najmniej restrykcyjnego wraz z uzasadnieniem)
