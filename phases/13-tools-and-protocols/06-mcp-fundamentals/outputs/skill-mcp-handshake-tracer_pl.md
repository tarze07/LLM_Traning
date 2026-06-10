---

name: mcp-handshake-tracer
description: Biorąc pod uwagę transkrypcję rozmowy klient-serwer w stylu pcap, opisz każdą wiadomość wraz z jej pierwotnym etapem cyklu życia i zależnością od możliwości.
version: 1.0.0
phase: 13
lesson: 06
tags: [mcp, json-rpc, lifecycle, capabilities]

---

Biorąc pod uwagę sekwencję kopert JSON-RPC 2.0 przechwyconą z sesji MCP, utwórz opis przejścia, w którym wymieniono element podstawowy, fazę cyklu życia i podstawową flagę możliwości każdej wiadomości.

Wyprodukuj:

1. Adnotacja do wiadomości. Dla każdego `{request, response, notification}` podaj: kierunek (klient-serwer lub serwer-klient), pierwotny (narzędzia / zasoby / podpowiedzi / korzenie / próbkowanie / wywoływanie / cykl życia), faza cyklu życia i flaga możliwości, która musiała zostać wynegocjowana, aby ten komunikat był ważny.
2. Kontrola zdolności. Zrekonstruuj wymianę `initialize` na podstawie transkrypcji i wypisz wszystkie wynegocjowane możliwości. Oflaguj każdą wiadomość, która naruszyłaby nieobecną funkcję.
3. Diagnostyka błędów. Dla każdego błędu JSON-RPC podaj kod i najbardziej prawdopodobną przyczynę, biorąc pod uwagę otaczający kontekst.
4. Audyt kompletności. Oznacz transkrypcję, w której brakuje jednego z: powiadomienia `initialize`, `initialized`, co najmniej jednego `tools/list` lub równoważnego, płynnego zamknięcia.
5. Zgodność ze specyfikacją. Sprawdź parametry każdego żądania względem minimalnego zestawu pól specyfikacji 2025-11-25. Pominięcia flagi.

Twarde odrzucenia:
- Dowolna wiadomość, która wykorzystuje metodę spoza dozwolonego zestawu specyfikacji, bez przedrostka `x-`.
- Dowolny komunikat `sampling/createMessage`, gdy klient nie zadeklarował możliwości `sampling`.
- Każde wywołanie przed przybyciem `notifications/initialized`.

Zasady odmowy:
- Jeśli zostaniesz poproszony o audyt transkrypcji z protokołu innego niż MCP, odmów i wskaż specyfikację A2A (faza 13 · 19) jako alternatywę.
- Jeśli zostaniesz poproszony o „poprawienie” transkrypcji, odmów. Ta umiejętność oznacza; nie przepisuje. Korekty tras poprzez wdrażający SDK.

Dane wyjściowe: jedna linia z adnotacjami na wiadomość w kolejności nadejścia: `[phase/primitive/capability] <method or result shape>`. Zakończ trzyliniowym podsumowaniem wymieniającym wszelkie naruszenia możliwości i wszelkie brakujące etapy cyklu życia.