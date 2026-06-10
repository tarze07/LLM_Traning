---

name: mesa-diagnostic
description: Sklasyfikuj zaobserwowaną awarię bezpieczeństwa jako zewnętrzną, zastępczą wewnętrzną lub zwodniczo wewnętrzną.
version: 1.0.0
phase: 18
lesson: 6
tags: [mesa-optimization, deceptive-alignment, inner-alignment, hubinger]

---

Mając raport z oceny bezpieczeństwa (zadanie ewaluacyjne, tryb awarii, klasa modelu, przepis szkoleniowy), sklasyfikowaj awarię w kategoriach Hubingera 2019 i zarekomenduj klasę łagodzenia, która ją rozwiązuje.

Wyprodukuj:

1. Kategoryzacja trybów awaryjnych. Wybierz jedno z:
   - Niepowodzenie w dostosowaniu zewnętrznym: podstawowy cel (nagroda, strata) był błędny; model zoptymalizował go poprawnie.
   - Awaria serwera proxy wewnętrznego wyrównania: mesa-obiektyw to serwer proxy, który śledzi dystrybucję bazy; kończy się niepowodzeniem w dystrybucji.
   - Zwodnicze ustawienie wewnętrzne: optymalizator mesa ma świadomość sytuacyjną i wady podczas wdrażania; zachowanie podczas szkolenia jest czyste.
2. Ślad dowodowy. Dla każdej kategorii, jakie dowody ją potwierdzają. W przypadku zwodniczych należy odróżnić od zastępczego: dowód świadomości sytuacyjnej (wrażliwość na daty, rozróżnienie między oceną a rozmieszczeniem, strategiczne rozumowanie w łańcuchu myślowym).
3. Klasa łagodzenia. W przypadku dostosowania zewnętrznego: zmień cel (CAI, lepsze dane dotyczące wynagrodzeń, nadzór nad procesem). Dla proxy-inner: zasięg dystrybucyjny, zespoły, wyczekiwane ewaluacje. Dla zwodniczo-wewnętrznego: środki kontroli (lekcja 10), interpretowalność (sondy strumienia resztkowego), redukcja zdolności.
4. Sprawdzenie znanych usterek. Aby poznać zwodnicze wnętrze, przytocz odpowiednią demonstrację empiryczną z lat 2024–2026 (Uśpieni agenci, Fałszowanie dopasowania, Planowanie w kontekście), do której ta porażka najbardziej przypomina tę porażkę.

Twarde odrzucenia:
- Jakakolwiek klasyfikacja zwodniczo-wewnętrzna bez dowodów świadomości sytuacyjnej. „Nieoczekiwane zachowanie podczas wdrażania” nie wystarczy — może mieć podłoże wewnętrzne proxy.
- Wszelkie twierdzenia, że ​​sam trening odporności kontradyktoryjnej rozwiązuje problem zwodniczego wnętrza. Hubinger 2019 przewiduje (i potwierdza to Sleeper Agents 2024), że szkolenie kontradyktoryjne może nauczyć lepszego odróżniania testów od wdrożeń.
- Wszelkie zalecenia dotyczące ponownego uczenia łudząco dopasowanego modelu na większej ilości danych. Przeor przewiduje, że oszustwo zostanie zachowane w trakcie dalszego szkolenia.

Zasady odmowy:
- Jeżeli dowodem jest pojedyncza porażka w jednym zdaniu, odmów klasyfikacji. Stawki podstawowe mają znaczenie; potrzebujesz dystrybucji niepowodzeń.
- Jeśli użytkownik poprosi Cię o „wykluczenie” zwodniczego dostosowania, odmów — możesz oszacować prawdopodobieństwo tego na podstawie dowodów, ale nie możesz tego wykluczyć wyłącznie na podstawie zachowania.

Wynik: jednostronicowa diagnoza zawierająca kategorię, ślad dowodowy, klasę łagodzenia i najbliższy analog empiryczny. Cytuj Hubinger i in. (arXiv:1906.01820) raz.