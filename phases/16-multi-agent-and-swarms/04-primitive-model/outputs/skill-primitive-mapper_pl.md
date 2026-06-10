---

name: primitive-mapper
description: Mapuj dowolną platformę wieloagentową lub bazę kodu na cztery prymitywne osie (agent, przekazanie, stan współdzielony, orkiestrator).
version: 1.0.0
phase: 16
lesson: 04
tags: [multi-agent, primitives, framework-comparison, architecture]

---

Biorąc pod uwagę strukturę wieloagentową (lub bazę kodu, która z niej korzysta), utwórz czteroprymitywne mapowanie, aby czytelnik mógł zrozumieć strukturę w jednym akapicie.

Wyprodukuj:

1. **Definicja agenta.** Jak zbudowany jest agent? Jakie parametry? Jaki stan nosi? Nazwij dokładną klasę lub fabrykę.
2. **Mechanizm przekazywania.** Który z trzech wzorców przekazywania jest używany — powrót funkcji, krawędź wykresu czy wybór mówcy? Jeśli hybryda, która jest pierwotna? Pokaż minimalny kod, który wyzwala jedno przekazanie.
3. **Model stanu współdzielonego.** Pełna pula komunikatów czy widok rzutowany? W pamięci czy trwały (w punkcie kontrolnym)? Czy jest bezpieczny dla wątków dla współbieżnych autorów? Kto łagodzi konflikty?
4. **Typ orkiestratora.** Statyczny, wybrany przez LLM, sterowany przekazywaniem czy sterowany kolejką? Jeśli wybrano LLM, który model jest domyślny? Jeśli jest statyczny, czy wykres jest cykliczny czy DAG?
5. **Kompromisy między osiami.** Po jednym zdaniu na temat: determinizmu, pułapu skalowalności, debugowalności, typowego trybu awarii.

Twarde odrzucenia:

- Każde mapowanie, które twierdzi, że abstrakcja jest „nowa”, bez pokazywania tego, nie zapada się w jeden z czterech prymitywów. Jeśli nie możesz jej zmniejszyć, nazwij lukę dokładnie, zamiast wymyślać piąty element pierwotny.
- Porównania ramowe, które cytują jedynie dokumenty marketingowe. Zawsze cytuj konkretny przykład kodu z repozytorium frameworka lub oficjalnej książki kucharskiej.
- Stwierdzenia takie jak „Framework X jest lepszy dla agentów” bez określania, który element podstawowy jest optymalizowany przez platformę.

Zasady odmowy:

- Jeśli framework ma zamknięte źródła, a publiczne dokumenty nie ujawniają powierzchni organizatora-przekazania-stanu agenta, należy stwierdzić, że mapowanie nie jest możliwe bez elementów wewnętrznych.
- Jeśli użytkownik dostarcza bazę kodu, ale nie dostarcza frameworka (ręcznie dobierani agenci), zamiast tego zmapuj niestandardową implementację i oznacz, który element podstawowy jest niedostatecznie zaprojektowany.
- Jeśli framework jest starszy niż 2024 (oryginalny AutoGen v0.2, wersja sprzed Swarm) i nie jest już obsługiwany, dołącz jednowierszową informację, czy jego następca zachowuje mapowanie.

Wynik: jednostronicowy opis struktury. Zacznij od podsumowania w jednym zdaniu („Framework X naprawia przekazywanie jako krawędź wykresu i udostępnia stan współdzielony poprzez reduktor.”), następnie pięć sekcji powyżej, a następnie akapit zamykający określający, który projekt produkcyjny najlepiej pasuje do prymitywów tego frameworka.