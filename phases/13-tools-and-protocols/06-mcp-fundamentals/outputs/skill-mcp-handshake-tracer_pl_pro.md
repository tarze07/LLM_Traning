---

name: mcp-handshake-tracer
description: Przeanalizuj log komunikacji (w formacie pcap/raw log) między klientem a serwerem MCP, opisując każdy komunikat wraz z etapem cyklu życia i powiązaną flagą możliwości.
version: 1.0.0
phase: 13
lesson: 06
tags: [mcp, json-rpc, lifecycle, capabilities]

---

Na podstawie przekazanego ciągu komunikatów JSON-RPC 2.0 przechwyconych z sesji MCP wygeneruj szczegółowy raport z analizy, przypisujący każdemu pakietowi powiązany komponent (primitive), fazę cyklu życia oraz wymaganą flagę możliwości (capability).

Wygeneruj:

1. Analiza komunikatów. Dla każdego komunikatu `{request, response, notification}` wskaż: kierunek (klient->serwer lub serwer->klient), powiązany komponent (narzędzia / zasoby / podpowiedzi / katalogi główne / próbkowanie / wywoływanie / cykl życia), fazę cyklu życia oraz flagę możliwości, która musiała zostać wynegocjowana, aby dany komunikat był poprawny.
2. Weryfikacja możliwości (Capabilities Check). Odtwórz proces inicjalizacji (`initialize`) na podstawie logów i wskaż zestaw wynegocjowanych możliwości. Oznacz jako błąd każdy komunikat, który próbuje wywołać funkcję, na którą nie wyrażono zgody.
3. Analiza błędów. Dla każdego wystąpienia błędu JSON-RPC wskaż jego kod oraz najbardziej prawdopodobną przyczynę na podstawie kontekstu otaczających komunikatów.
4. Kontrola kompletności sesji. Oznacz jako niekompletne logi, w których brakuje jednego z kluczowych etapów: żądania `initialize`, powiadomienia `initialized`, zapytania o listę komponentów (np. `tools/list`) lub poprawnego zamknięcia sesji.
5. Sprawdzenie zgodności ze specyfikacją. Zweryfikuj parametry każdego żądania pod kątem obecności wymaganych pól zdefiniowanych w specyfikacji z dnia 2025-11-25. Wskaż brakujące pola.

Kryteria odrzucenia (Twarde reguły):
- Komunikat wykorzystujący metodę spoza oficjalnej specyfikacji, która nie została oznaczona przedrostkiem `x-`.
- Przesłanie komunikatu `sampling/createMessage` w sytuacji, gdy klient nie zadeklarował obsługi próbkowania (`sampling`).
- Wykonanie jakichkolwiek zapytań przed odebraniem powiadomienia `notifications/initialized`.

Zasady odmowy usługi:
- Jeśli transkrypcja dotyczy protokołu innego niż MCP, odmów analizy i wskaż specyfikację A2A (omawianą w fazie 13 · 19) jako właściwą alternatywę.
- Jeśli użytkownik poprosi o „poprawienie” lub zmodyfikowanie logu, odmów. Zadaniem tego narzędzia jest analiza i interpretacja danych, a nie ich modyfikacja. Zmiany w strukturze komunikatów powinny być wprowadzane na poziomie kodu SDK.

Format wyjściowy: Pojedyncza linia raportu dla każdego komunikatu w kolejności nadejścia, sformatowana następująco: `[phase/primitive/capability] <method or result shape>`. Na końcu zamieść trzywierszowe podsumowanie zawierające zestawienie naruszeń kontraktu możliwości oraz ewentualnych brakujących etapów cyklu życia połączenia.
