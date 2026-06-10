---

name: finops-plan
description: Zaprojektuj program FinOps dla LLM – schemat alokacji kosztów (użytkownik/zadanie/najemca + cztery warstwy tokenów), trzystopniowy system limitów (rate limit -> limit wydatków -> kill switch) oraz biznesową metrykę jednostkową (koszt per rozwiązana sprawa / wygenerowany zasób).
version: 1.0.0
phase: 17
lesson: 27
tags: [finops, cost-attribution, multi-tenant, kill-switch, unit-economics, rate-limit]

---

Na podstawie specyfiki produktu, poziomów abonamentowych najemców, miesięcznych wydatków oraz obecnego statusu alokacji kosztów, przygotuj plan FinOps.

Wygeneruj:

1. Schemat alokacji kosztów: Identyfikatory `user_id`, `task_id`, `route`, `tenant_id` przekazywane w punkcie wywołania API. Rozbicie kosztów na cztery warstwy tokenów (prompt / narzędzia / pamięć / odpowiedź). Zaimplementuj wzorzec integracji z telemetrią (Telemetry Linker).
2. Biznesowa metryka jednostkowa: Zdefiniuj wskaźnik powiązany z wartością produktu (np. koszt obsługi zgłoszenia, koszt wygenerowanego raportu/zasobu, koszt wykonania misji przez agenta, koszt sesji użytkownika). Powiąż te dane z modelom rozliczeń z klientem.
3. System limitów (Enforcement Ladder): Limit częstotliwości zapytań na najemcę (2-3x średniego szczytu), dzienny limit budżetu (1,5-3x limitu kontraktowego), wyłącznik awaryjny (kill switch) aktywowany przy nagłym skoku kosztów o Z-score > 4.
4. Panel kontrolny (Dashboard): Pięć kluczowych wykresów (dzisiejsze wydatki na najemcę, koszt jednostkowy na zadanie, rozkład kosztów na użytkownika, wpływ buforowania promptów na oszczędności, podział zapytań według modeli).
5. Audyt optymalizacji (Stacked Optimization): Zweryfikuj wdrożenie buforowania (Faza 17 · Lekcja 14), przetwarzania wsadowego (Faza 17 · Lekcja 15), dynamicznego routingu (Faza 17 · Lekcja 16) oraz bramki AI (Faza 17 · Lekcja 19). Wskaż brakujące mechanizmy.
6. Harmonogram przeglądów: Co tydzień (analiza największych wydatków i anomalii), co miesiąc (marża jednostkowa per najemca), co kwartał (ponowna klasyfikacja ruchu na interaktywny, pół-interaktywny i asynchroniczny/wsadowy).

Kryteria odrzucenia planu (Hard rejects):
- Wdrożenie bez zaimplementowanego oznaczania żądań w kodzie (atrybucja przy wywołaniu): Odrzuć – wsteczna alokacja powoduje utratę i błędne przypisanie ok. 10-30% wydatków.
- Agregowanie rozliczeń do jednej ogólnej kwoty: Odrzuć – wymagaj rozbicia kosztów na cztery warstwy zużycia tokenów.
- Konfiguracja wyłącznika awaryjnego (kill switch) bez zdefiniowania bazowej linii statystycznej Z-score: Odrzuć – przed uzbrojeniem zabezpieczeń konieczne jest określenie stabilnego profilu obciążenia.

Zasady odrzucenia:
- Jeśli aplikacja obsługuje < 10 najemców, odrzuć wdrażanie zaawansowanych systemów limitów wielodostępnych – w pierwszej kolejności wymagaj prostej alokacji kosztów per klient.
- Jeśli wskaźnik kosztu per wynik biznesowy (metryka jednostkowa) jest niezdefiniowany, odrzuć projekt panelu kontrolnego – najpierw należy precyzyjnie ustalić metrykę jednostkową.
- Jeśli jakikolwiek pojedynczy najemca (klient) odpowiada za > 40% całkowitych wydatków, wymagaj przeprowadzenia szczegółowej analizy marży i ekonomii jednostkowej przed zatwierdzeniem planu.

Wynik: Jednostronicowy plan zawierający schemat alokacji kosztów, metryki jednostkowe, system limitów, strukturę panelu kontrolnego, audyt optymalizacji warstwowej oraz harmonogram przeglądów. Na końcu umieść regułę alertu: monitorowanie dobowego zużycia względem prognoz i natychmiastowe powiadomienie (page/alert) w przypadku odchylenia > 20%.
