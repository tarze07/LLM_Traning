---

name: elicitation-form-designer
description: Zaprojektuj schemat formularza elicitation oraz treść komunikatów dla narzędzia wymagającego weryfikacji lub ujednoznacznienia danych przez użytkownika w czasie rzeczywistym.
version: 1.0.0
phase: 13
lesson: 12
tags: [mcp, elicitation, user-input, forms]

---

Na podstawie specyfikacji narzędzia wymagającego weryfikacji danych przez użytkownika w locie zaprojektuj schemat wywołania formularza (elicitation) oraz komunikaty.

Wygeneruj:

1. Warunki wyzwalania. Określ dokładnie dane wejściowe lub sytuacje niejednoznaczności, które powinny skutkować wysłaniem żądania `elicitation/create`.
2. Treść komunikatu. Przygotuj proste, jednozdaniowe powiadomienie prezentowane użytkownikowi przez hosta. Komunikat powinien być konkretny i pozbawiony technicznego żargonu.
3. Schemat parametrów (JSON Schema). Zdefiniuj płaską strukturę JSON Schema z polami o określonych typach (np. `enum` do wyboru opcji lub `boolean` do potwierdzenia). Zabrania się zagnieżdżania obiektów.
4. Obsługa decyzji. Zaprojektuj reakcję kodu narzędzia na poszczególne statusy odpowiedzi użytkownika: `accept`, `decline` oraz `cancel`.
5. Limit zapytań (Rate limit). Określ limit wyświetleń formularza (wywoływanie nie może być uruchamiane w pętli).

Kryteria odrzucenia (Twarde reguły):
- Zdefiniowanie schematu zawierającego zagnieżdżone obiekty (formularze elicitation w wersji v1 muszą być płaskie).
- Stosowanie formularzy do pobrania brakujących parametrów, o które model mógłby samodzielnie zapytać użytkownika w toku rozmowy tekstowej.
- Wywoływanie formularzy z wysoką częstotliwością (np. więcej niż raz w ramach jednego uruchomienia narzędzia).

Zasady odmowy usługi:
- Jeśli narzędzie wykonuje operacje wyłącznie do odczytu (read-only) o niskim poziomie ryzyka, odmów projektowania formularza i zwróć dane bezpośrednio.
- Jeśli narzędzie wykonuje operacje niszczące, a host obsługuje adnotację `destructiveHint`, zaleć użycie adnotacji i pozostawienie obsługi potwierdzenia klientowi.
- Jeśli wymagane jest przeprowadzenie autoryzacji OAuth, zaleć wywoływanie w trybie adresu URL i oznacz ryzyko związane z eksperymentalnym statusem SEP-1036.

Format wyjściowy: Jednostronicowa specyfikacja zawierająca warunki wyzwolenia, treść komunikatu, schemat parametrów, obsługę gałęzi decyzyjnych, limit wyświetleń oraz wskazanie, czy w danym scenariuszu lepiej sprawdzi się tryb formularza, czy tryb adresu URL.
