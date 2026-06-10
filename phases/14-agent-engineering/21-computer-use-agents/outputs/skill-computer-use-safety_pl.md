---

name: computer-use-safety
description: Zbuduj klasyfikator bezpieczeństwa krokowy + bramkę potwierdzającą dla agenta korzystającego z komputera, z nawigacją na liście dozwolonych i filtrowaniem znaczników wtrysku.
version: 1.0.0
phase: 14
lesson: 21
tags: [computer-use, safety, claude, openai-cua, gemini]

---

Mając agenta obsługującego komputer i listę aplikacji docelowych, utwórz warstwę bezpieczeństwa, która klasyfikuje każdą akcję przed jej wykonaniem.

Wyprodukuj:

1. `SafetyClassifier.assess(action, screen) -> SafetyVerdict` z polami `allow`, `reason`, `needs_confirmation`.
2. Lista dozwolonych etykiet elementów, które agent może kliknąć; odmówić inaczej.
3. Lista dozwolonych adresów URL, do których agent może przejść; odmowa przekierowań z listy.
4. Filtr znaczników wtrysku dla tekstu DOM, pobranej treści i wpisanego tekstu. Każde dopasowanie blokuje akcję.
5. Bramka potwierdzenia dla wrażliwych działań (logowanie, zakup, usuwanie, publikowanie). Interfejs wywołania zwrotnego typu „człowiek w pętli”.
6. Emiter śledzenia: każda zarejestrowana decyzja (działanie, werdykt, powód).

Twarde odrzucenia:

- Klasyfikator bezpieczeństwa, który działa tylko przy pierwszej akcji. Każde działanie musi być sklasyfikowane.
- Lista dozwolonych formularzy `*`. Lista dozwolonych, która pozwala na wszystko, nie jest listą dozwolonych.
- Pomijanie potwierdzenia, ponieważ model „wydaje się pewny siebie”. Zaufanie to nie bezpieczeństwo.

Zasady odmowy:

- Jeśli agent ma dostęp do komputera bez zabezpieczeń na każdym kroku, odmów wysyłki.
- Jeśli agent może przejść do dowolnych adresów URL, odmów. Wymagaj listy dozwolonych lub blokowanych.
- Jeśli wrażliwe działania ominą bramkę potwierdzenia w jakimkolwiek trybie, odmów.

Dane wyjściowe: `classifier.py`, `allowlist.py`, `confirmation.py`, `trace.py`, `README.md` wyjaśniające zasady dotyczące bramek, znaczniki wstrzykiwania i proces konserwacji listy dozwolonych. Zakończ słowami „co dalej czytać”, wskazując na Lekcję 27 (wstrzyknięcie natychmiastowe) i Lekcję 23 (Przypisywanie zakresu Otel w przypadku decyzji dotyczących bezpieczeństwa).