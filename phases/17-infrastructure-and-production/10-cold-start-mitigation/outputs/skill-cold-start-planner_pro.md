---

name: cold-start-planner
description: Zaprojektuj plan ograniczania skutków zimnego startu dla bezserwerowych wdrożeń LLM. Zaplanuj budżet czasowy dla poszczególnych faz (inicjalizacja węzła, pobieranie obrazu, wagi, silnik, pierwsza faza forward) i dobierz metody optymalizacji pod kątem wymogów SLA.
version: 1.0.0
phase: 17
lesson: 10
tags: [cold-start, serverless, bottlerocket, model-streamer, gpu-snapshot, warm-pool, serverlessllm]

---

Na podstawie rozmiaru modelu, wymagań SLA (P99 TTFT), profilu ruchu (stabilny vs nagłe skoki) oraz budżetu, przygotuj plan ograniczania skutków zimnego startu.

Wygeneruj:

1. Budżet czasowy zimnego startu. Przedstaw szczegółowy podział czasu trwania dla nieoptymalizowanej ścieżki (inicjalizacja węzła, pobieranie obrazu kontenera, ładowanie wag do HBM, inicjalizacja silnika, pierwsza faza forward). Użyj nominalnych szacunków czasowych dla roku 2026 w odniesieniu do podanego rozmiaru modelu.
2. Wybór metod optymalizacji (warstw). Dobierz minimalny zestaw rozwiązań, który pozwoli obniżyć całkowity czas poniżej progu SLA: wstępnie przygotowany obraz (L1), streamer modelu (L2), migawka GPU (L3), ciepła pula (L4), ładowanie wielopoziomowe (L5). Uzasadnij wybór każdego z nich, wskazując konkretną fazę opóźnienia, na którą wpływa.
3. Rozmiar ciepłej puli. Określ wartość parametru `min_workers` dla ścieżki podstawowej. Jeśli umowa SLA wymaga opóźnienia P99 TTFT < 60 s dla modelu klasy 70B+, nałóż obowiązek utrzymywania ciepłej puli bez względu na koszty.
4. Szacunek kosztów. Przedstaw miesięczny koszt utrzymania GPU dla wybranej ciepłej puli oraz prognozowaną liczbę zimnych startów w ciągu doby.
5. Polityka obsługi zapytań skrajnych (Tail policy). Co dzieje się z zapytaniem użytkownika, które wywołuje uruchomienie nowej repliki – czy zostaje zakolejkowane do działającej ciepłej instancji, czy też ponosi pełny koszt czasowy zimnego startu? Zdefiniuj precyzyjną regułę (np. „przekieruj zapytanie do dowolnej ciepłej repliki, jeśli zwolni się w ciągu 10 s; w przeciwnym razie zainicjuj nową instancję i zaakceptuj zimny start”).
6. Obsługa awarii (Failover). Co dzieje się w sytuacji, gdy ciepła replika ulegnie awarii w trakcie trwania sesji? Czy proces odzyskiwania sprawności przebiega automatycznie (np. poprzez migrację na żywo), czy też kolejne zapytanie wywoła klasyczny zimny start?

Kategoryczne odrzucenia:
- Proponowanie rozwiązania typu „po prostu dodaj ciepłą pulę” bez dokładnego obliczenia miesięcznych kosztów takiego kroku.
- Rekomendowanie metod optymalizacji bez precyzyjnego wskazania fazy opóźnienia, którą dane rozwiązanie ma skrócić (np. zalecenie użycia Bottlerocket bez wyjaśnienia, że eliminuje ono czas pobierania obrazu kontenera trwający typowo ok. 180 s).
- Ignorowanie ograniczeń związanych z topologią procesorów graficznych przy stosowaniu migawek GPU (jeśli chmura zmieni wersję sprzętową SKU przypisaną do instancji, migawka pamięci utraci ważność).

Zasady odmowy wdrożenia (odrzucenie rekomendacji):
- Jeśli wymaganie SLA zakłada opóźnienie P99 TTFT < 5 s przy uruchamianiu modelu klasy 70B ze stanu pełnego zimnego startu (skala do zera) bez użycia ciepłej puli, odrzuć projekt jako matematycznie i technicznie niewykonalny przy możliwościach chmurowych z roku 2026.
- Jeśli budżet projektu nie pozwala na utrzymywanie ciepłej puli, a umowa SLA wymaga uruchomienia w czasie poniżej 30 sekund, zaproponuj specyficzne dla dostawcy chmurowego rozwiązania (np. migawki GPU na platformie Modal, wstępne podgrzewanie na Baseten) i nie gwarantuj spełnienia SLA na innych platformach pozbawionych tych technologii.
- Jeśli użytkownik oczekuje skalowania do zera (zero-scaling) przy dużym natężeniu ruchu na modelu klasy 70B, odrzuć próbę zagwarantowania SLA – bez migawek lub ciepłych pul takie wymaganie jest technicznie niemożliwe do spełnienia.

Wynik: jednostronicowy plan wdrożenia zawierający analizę faz opóźnień, dobór metod optymalizacji, wartość `min_workers`, wyliczenie kosztów miesięcznych, politykę zapytań skrajnych (tail policy) oraz plan obsługi awarii. Na końcu umieść pojedynczy kluczowy wskaźnik do monitorowania i ustawienia alertu: maksymalny czas zimnego startu P99 w ciągu ostatniej godziny.
