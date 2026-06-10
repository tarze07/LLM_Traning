---

name: router-plan
description: Zaprojektuj plan trasowania modelu LLM — wzór wyboru (przed trasą, kaskada, zespół), sygnały (zadanie, długość, osadzanie, pewność) i bramki jakości online.
version: 1.0.0
phase: 17
lesson: 16
tags: [routing, cascade, model-cascade, routellm, notdiamond, cost-reduction]

---

Biorąc pod uwagę mieszankę obciążeń (próbka klasyfikacji zadań), minimalną jakość, tolerancję opóźnień i bieżące miesięczne wydatki, utwórz plan routingu.

Wyprodukuj:

1. Wzór. Trasa wstępna (najszybsza, zależna od klasyfikatora), kaskada (podłoga najlepszej jakości) lub zespół (tylko próbka A/B). Uzasadnij tolerancją jakości + budżetem opóźnień.
2. Sygnały. Wybierz spośród: klasyfikacji zadań, długości podpowiedzi, osadzania podobieństwa do znanych-trudnych, pewności siebie. Podaj, które kombinacje (zwykle 2-3) i regułę kompozycji.
3. Para tania/graniczna. Podaj nazwy konkretnych modeli. Przykład: Claude Haiku 3.5 + GPT-5. Uzasadnij krzywą kosztów + możliwości.
4. Oczekiwane oszczędności. Oblicz koszt mieszany przy zalecanym podziale; stan oczekiwany miesięczny $ vs bieżący.
5. Bramy jakości online. Określ sędziego ruchu na żywo: pobrano próbkę 5% na trasę ocenianą przez sędziego granicznego; alarmuj, jeśli Δ jakość > 2%. Śledź tempo eskalacji; ostrzegaj, jeśli w ciągu miesiąca wzrośnie o ponad 10 punktów.
6. Wdrożenie. Cień (trasa, ale ignorowana; porównaj offline), kanarek 10% według kohorty użytkowników, rozwiń przy mijającej bramie.

Twarde odrzucenia:
- Routing bez bramek jakości online. Odmów — dryfowanie jest porażką nr 1.
- Używanie wyłącznie klasyfikacji zadań jako sygnału. Odmów — pomija trudności w zadaniach.
- Przekierowywanie zadań spełniających kryteria graniczne (kod, matematyka, wieloetapowe) do tanich bez kaskadowego powrotu. Odmów — jakość podłogi zostanie naruszona.

Zasady odmowy:
- Jeśli tolerancja jakości jest określona jako „regresja zerowa”, odrzuć opcję wstępnej trasy i zaproponuj kaskadę z wysokim współczynnikiem eskalacji.
- Jeśli tani model nie jest antropiczny/nie-OpenAI/niegraniczny i ma znane wzorce odmowy (np. nieocenzurowane modele do użycia narzędzi przez agenta), odrzuć tę parę — spowoduje to ciche przerwanie wywołań narzędzi.
- Jeśli routing jest tani do innego dostawcy (kaskada między dostawcami), wymagaj warstwy bramy AI (faza 17 · 19) w celu ujednolicenia interfejsów API.

Dane wyjściowe: jednostronicowy wzór nazewnictwa planu, sygnały, para modeli, oczekiwane oszczędności, bramki online, plan wdrożenia. Zakończ pojedynczym wskaźnikiem: współczynnik eskalacji w ciągu 7 dni; wyzwalacz dryfu, jeśli zmiana > 10 punktów procentowych.