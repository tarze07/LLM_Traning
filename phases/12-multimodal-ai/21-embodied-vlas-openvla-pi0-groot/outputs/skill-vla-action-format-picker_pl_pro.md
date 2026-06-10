---

name: vla-action-format-picker
description: Ułatwia dobór formatu reprezentacji akcji (dyskretne kubełkowanie, FAST, Flow Matching, dwupoziomowy system) oraz rodziny modeli VLA (RT-2, OpenVLA, π0, GR00T) do zadania robotycznego.
version: 1.0.0
phase: 12
lesson: 21
tags: [vla, rt-2, openvla, pi0, groot, action-tokenization]

---

Na podstawie zadania robotycznego (manipulacja, nawigacja, humanoidalna kontrola całego ciała), liczby stopni swobody (DOF), wymaganej częstotliwości sterowania oraz ograniczeń obliczeniowych, dobierz format zapisu akcji i rodzinę modeli VLA.

Wygeneruj:

1. **Format reprezentacji akcji:** Dyskretne kubełkowanie (discrete bins) dla prostych zadań jedno-ramiennych, tokenizer FAST dla trajektorii wrażliwych na opóźnienia, Flow Matching dla płynnego sterowania ciągłego, lub dwupoziomowy system dla robotów humanoidalnych.
2. **Rodzina modeli VLA:** RT-2 (model komercyjny/zamknięty), OpenVLA (otwarty model 7B), π0 (otwarty model z Flow Matching), GR00T N1 (otwarty system dwupoziomowy dla humanoidów).
3. **Analiza częstotliwości sterowania:** Dopasowanie przepustowości wybranego formatu do wymaganej częstotliwości pętli sprzężenia zwrotnego. Dyskretne kubełkowanie nie pozwala na pracę z częstotliwością >10 Hz na modelu 7B.
4. **Proporcje danych treningowych:** Określenie stosunku danych internetowych do robotycznych w procesie co-fine-tuningu (np. VQA z sieci : trajektorie robota). Rekomendowany punkt startowy to 0,5:1.
5. **Plan dostrajania (Finetuning):** Wykorzystanie LoRA na małej próbie (~500-1000 demonstracji zadania) lub pełne dostrojenie przy posiadaniu ~10 tys. demonstracji.
6. **Filtry bezpieczeństwa:** Wykaz niezbędnych fizycznych zabezpieczeń pętli sprzężenia realizowanych w warstwie sterownika (poza modelem VLA).

Kryteria odrzucenia (Twarde reguły):
- Rekomendowanie wdrożenia modelu VLA bez specyfikacji zewnętrznej warstwy filtrów bezpieczeństwa (ograniczeń kątowych stawów oraz limitów prędkości).
- Zakładanie, że klasyczna tokenizacja dyskretna (autoregresywna) jest wystarczająco szybka do sterowania w czasie rzeczywistym przy 30 Hz. W praktyce jest to niemożliwe bez dodatkowych optymalizacji.
- Proponowanie mechanizmu Flow Matching bez odpowiednich ograniczeń (clipping/filtering), co wciąż może generować akcje spoza bezpiecznego rozkładu.

Zasady odmowy (Rezygnacja z projektu):
- Jeśli wymagana częstotliwość sterowania wynosi >50 Hz dla modelu o skali <=7B z dyskretnym formatem akcji, odrzuć projekt i zarekomenduj π0 lub dedykowaną głowicę sterującą.
- Jeśli platforma robotyczna posiada >30 stopni swobody (robot humanoidalny), odrzuć proste architektury jednostopniowe i wymagaj wdrożenia systemu dwupoziomowego (klasy GR00T).
- Jeśli budżet obliczeniowy nie pozwala na bazowy trening w skali Open X-Embodiment, odrzuć pomysł trenowania VLA od zera i zalecaj dostrajanie OpenVLA.

Dane wyjściowe: Jednostronicowy raport zawierający format zapisu akcji, wybór modelu VLA, analizę częstotliwości sterowania, proporcje danych do dostrojenia oraz specyfikację filtrów bezpieczeństwa. Na końcu dodaj odnośniki do prac: arXiv 2307.15818 (RT-2), 2406.09246 (OpenVLA), 2410.24164 (π0), 2503.14734 (GR00T).
