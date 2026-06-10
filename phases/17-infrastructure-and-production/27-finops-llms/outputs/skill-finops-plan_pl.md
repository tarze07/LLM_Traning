---

name: finops-plan
description: Zaprojektuj program LLM FinOps — schemat atrybucji (użytkownik/zadanie/dzierżawca + cztery warstwy tokenów), trójstopniowa drabina egzekwowania i metryka jednostkowa (koszt na rozwiązany/artefakt).
version: 1.0.0
phase: 17
lesson: 27
tags: [finops, cost-attribution, multi-tenant, kill-switch, unit-economics, rate-limit]

---

Biorąc pod uwagę powierzchnię produktu, poziomy najemców, miesięczne wydatki i bieżący stan atrybucji, utwórz plan FinOps.

Wyprodukuj:

1. Schemat atrybucji. `user_id`, `task_id`, `route`, `tenant_id` wybite w miejscu połączenia. Cztery zliczenia warstwy tokenu (podpowiedź/narzędzie/pamięć/odpowiedź). Preferowany wzór łącznika telemetrycznego.
2. Jednostka metryczna. Zdefiniuj metrykę wyniku produktu — koszt rozwiązanego zgłoszenia, koszt artefaktu, koszt zadania agenta, koszt sesji. Powiąż z modelem rozliczeniowym.
3. Drabina egzekucyjna. Limit stawek na najemcę (2-3x szczyt), dzienny limit wydatków (1,5-3x kontrakt), wyłącznik awaryjny przy z-score > 4.
4. Pulpit nawigacyjny. 5 najważniejszych widoków: dzisiejsze wydatki na dzierżawcę, koszt na wynik na zadanie, dystrybucja na użytkownika, wpływ współczynnika trafień w pamięci podręcznej, podział routingu modelu.
5. Skumulowany audyt optymalizacji. Sprawdź, czy pamięć podręczna (faza 17 · 14), partia (faza 17 · 15), routing (faza 17 · 16), brama (faza 17 · 19) są zaangażowane. Oznacz brakujące dźwignie.
6. Sprawdź rytm. Co tydzień: osoby wydające najwięcej + anomalie. Miesięcznie: ekonomika jednostki na najemcę. Co kwartał: ponowna klasyfikacja obciążeń w trybie interaktywnym/pół/wsadowym.

Twarde odrzucenia:
- Wysyłka bez podania adresu w miejscu połączenia. Odmów – tagowanie z mocą wsteczną powoduje utratę ~10-30% wydatków.
- Rozliczenia z jednego źródła. Odmów — wymaga podziału na cztery warstwy żetonów.
- Przełącznik zabijania bez podstawy Z-score. Odmów — wymagaj statystyk bazowych przed uzbrojeniem.

Zasady odmowy:
- Jeśli produkt ma < 10 najemców, odmów pełnego egzekwowania wielu najemców — najpierw wymagaj podstawowej atrybucji na najemcę.
- Jeśli koszt/wynik jest niezdefiniowany, odmów pulpitu nawigacyjnego — najpierw wybierz metrykę jednostkową.
- Jeśli jakikolwiek pojedynczy najemca generuje > 40% całkowitych wydatków, wymagaj dedykowanego przeglądu ekonomii jednostkowej przed wysyłką planu.

Dane wyjściowe: jednostronicowy plan ze schematem atrybucji, metryką jednostkową, drabiną egzekwowania, pulpitem nawigacyjnym, skumulowanym audytem optymalizacji, częstotliwością przeglądów. Zakończ pojedynczym alertem: dzienne wydatki a prognozy; stronę, gdy delta > 20%.