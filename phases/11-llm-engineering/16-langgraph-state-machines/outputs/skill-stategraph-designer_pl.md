---

name: stategraph-designer
description: Zamień zadanie agenta w LangGraph StateGraph z nazwanymi węzłami, wpisanym stanem, reduktorami, punktem kontrolnym i przerwaniami ludzkimi.
version: 1.0.0
phase: 11
lesson: 16
tags: [langgraph, stategraph, checkpointer, interrupt, time-travel, react-agent, human-in-the-loop]

---

Biorąc pod uwagę zadanie agenta (cel stojący przed użytkownikiem, dostępne narzędzia, oczekiwana liczba tur, skutki uboczne z bezpiecznym promieniem wybuchu, wymagania dotyczące trwałości, docelowy budżet opóźnień), wynik:

1. Lista węzłów. Nazwij każdy odrębny krok: myśliciel LLM, każdy biegacz narzędzi, każdy krok przeglądu przez człowieka, każdy podsumowujący lub krytyk, każdy retriever. Odrzuć projekt, jeśli jakikolwiek węzeł dotyczy więcej niż jednego problemu; podziel to.
2. Schemat stanu. Pola TypedDict (lub Pydantic) z reduktorem dla każdej listy. Zawsze adnotowane [lista, add_messages] w dzienniku wiadomości. Wyciągnij z wiadomości dowolną listę dotyczącą konkretnego zadania (plan, licznik budżetu, listę pobranych dokumentów), aby reduktory pozostały prawidłowe w przypadku równoległych aktualizacji.
3. Mapa krawędzi. Krawędzie statyczne, w których następny krok jest deterministyczny. Krawędzie warunkowe z nazwaną funkcją routera tylko wtedy, gdy model wybiera następny krok. Odrzuć dowolny wykres, którego funkcja routera zależy od nowego wywołania LLM, którego nie wykonałeś jeszcze w poprzednim węźle.
4. Umieszczanie przerwań. przerwanie_przed na każdym węźle z nieodwracalnym skutkiem ubocznym (zapisy, usunięcia, płatności, zewnętrzne wywołania API z kosztami). przerwanie_po w węźle modelu, gdy sprawdzanie poprawności danych wyjściowych przebiega w oddzielnym procesie. Odrzuć przerwanie_po w dowolnym węźle wpływającym na skutki uboczne; do tego czasu wystąpił efekt uboczny.
5. Punkt kontrolny. MemorySaver tylko do testów. Wybierz spośród PostgresSaver, SQLiteSaver, RedisSaver dla dowolnego środowiska, które musi przetrwać ponowne uruchomienie. Potwierdź strategię thread_id (na użytkownika, na sesję, na rozmowę) i TTL punktu kontrolnego.

Odmów wysłania LangGrapha bez punktu kontrolnego. Brak punktu kontrolnego oznacza brak wznowienia, brak podróży w czasie i brak powtarzalności w pętli. Odmów wysłania pola wiadomości bez add_messages; drugi zapis zastępuje pierwszy po cichu i połowa rozmowy znika. Odrzuć graf, którego każde przejście jest krawędzią warunkową wyznaczoną przez planistę LLM; czyli AutoGen z dodatkowymi krokami i spalaniem żetonów na turę.

Przykładowe dane wejściowe: „Agent obsługujący zwroty w Anthropic Claude z trzema narzędziami (lookup_order, Issue_refund, send_email), musi wstrzymać się dla człowieka przed jakimkolwiek zwrotem powyżej 100 dolarów, musi zostać wznowiony po ponownym uruchomieniu serwera, budżet opóźnienia p95 8 sekund”.

Przykładowe wyjście:
- Węzły: agent (wywołanie LLM), narzędzie wyszukiwania, narzędzie_refundacji, narzędzie_e-mail, narzędzie_recenzji.
- Stan: wiadomości z add_messages, Order_context (nadpisanie), refund_amount (nadpisanie), reviewer_decision (nadpisanie).
- Krawędzie: agent powinien_kontynuować router z gałęziami lookup_tool, refund_tool, email_tool, human_review, END. Węzły narzędzi wracają do agenta.
- Przerwania: przerwanie_przed narzędziem refund_tool, gdy kwota_zwrotu > 100. Brak przerwania narzędziem lookup_tool lub email_tool.
- Checkpointer: PostgresSaver z thread_id "user:{user_id}:case:{case_id}" i 30-dniowym TTL.