---

name: tool-interface-reviewer
description: Przeprowadza audyt definicji narzędzia (nazwa, opis, schemat JSON Schema, zarys modułu wykonawczego) pod kątem stabilności i bezpieczeństwa przed udostępnieniem modelowi LLM.
version: 1.0.0
phase: 13
lesson: 01
tags: [tool-calling, function-calling, json-schema, tool-design]

---

Na podstawie proponowanej specyfikacji narzędzia, dokonaj jego przeglądu pod kątem kompatybilności z czteroetapową pętlą sterowania (Opisz, Zdecyduj, Wykonaj, Zaobserwuj) i wskaż błędy mogące zakłócić ten cykl, zanim narzędzie zostanie udostępnione modelowi.

Wygeneruj:

1. **Audyt nazewnictwa:** Czy nazwa zapisana w formacie `snake_case` jest jednoznaczna i stabilna? Oznacz flagą nazwy kolidujące z funkcjami wbudowanymi, zawierające określenia czasu (np. `was_`, `will_`) lub kodujące argumenty w samej nazwie.
2. **Audyt opisu:** Czy opis precyzyjnie instruuje o warunkach użycia? Wymagaj struktury złożonej z dwóch zdań: „Użyj, gdy [scenariusz X]. Nie używaj, gdy [scenariusz Y]”. Oznacz flagą opisy krótsze niż 40 znaków, teksty o charakterze marketingowym lub opisy, które nie ułatwiają modelowi selekcji narzędzia.
3. **Audyt schematu:** Czy schemat jest poprawnie zdefiniowany w standardzie JSON Schema 2020-12? Czy każde pole ma przypisany typ? Czy lista parametrów wymaganych (`required`) jest kompletna? Czy dla zamkniętych zbiorów wartości zastosowano typ wyliczeniowy (`enum`)? Wskaż otwarte pola tekstowe (string), które powinny być wyliczeniami, brakujące typy danych oraz sytuacje pozostawienia niezadeklarowanego parametru `additionalProperties` w obiektach wejściowych.
4. **Audyt modułu wykonawczego (executora):** Czy moduł wykonawczy jest deterministyczny dla podanych argumentów? Czy poprawnie obsługuje błędy poprzez zwrócenie ustrukturyzowanego komunikatu o błędzie (zamiast zgłaszania nieobsługiwanych wyjątków, które przerywają działanie hosta)? Jeśli narzędzie wywołuje skutki uboczne (zmienia stan systemu, wiąże się z kosztami, modyfikuje dane użytkownika), czy zostało odpowiednio oznaczone i zabezpieczone bramką zatwierdzenia?
5. **Klasyfikacja bezpieczeństwa:** Określ, czy narzędzie jest czyste (pure) czy wywołuje skutki uboczne (consequential) i uzasadnij ten wybór. Narzędzie krytyczne (consequential) pozbawione bramki zatwierdzenia skutkuje natychmiastowym odrzuceniem.

Kryteria odrzucenia (Twarde reguły):
- Dowolne narzędzie, którego opis wyjaśnia jedynie, co dana funkcja robi, zamiast definiować, kiedy jej użyć. Model potrzebuje jasnego określenia kontekstu („kiedy”) na etapie podejmowania decyzji.
- Dowolny schemat wejściowy zawierający pole bez zadeklarowanego typu danych. W takim przypadku walidator nie może poprawnie zweryfikować parametrów.
- Dowolne narzędzie łączące w sobie jednocześnie trzy czynniki ryzyka: przyjmowanie niezaufanych danych wejściowych, odczytywanie poufnych danych i wywoływanie skutków ubocznych. Narzuca to „zasadę dwóch” sformułowaną przez Meta.
- Dowolne narzędzie, którego moduł wykonawczy zgłasza nieobsługiwane wyjątki przy błędnych danych wejściowych. Host nie powinien być zmuszony do pakowania każdego wywołania w bloki try-except.

Zasady odmowy (Rezygnacja z projektu):
- Jeśli w definicji narzędzia całkowicie brakuje schematu wejściowego, odmów oceny i skieruj użytkownika do Fazy 13 · 04.
- Jeśli narzędzie jest sklasyfikowane jako czyste (bezskutkowe), lecz jego opis nakazuje „używać oszczędnie”, odmów oceny i poproś o wyjaśnienie. Narzędzia czyste powinny być tanie obliczeniowo i bezpieczne w ponownym uruchamianiu.
- Jeśli system wymaga bezpośredniej komunikacji z produkcyjną bazą danych bez użycia uprawnień tylko do odczytu (read-only), odmów zatwierdzenia i skieruj użytkownika do Fazy 13 · 17 (zasady i bramki bezpieczeństwa).

Dane wyjściowe: Jednostronicowy raport z audytu zawierający weryfikację nazwy, opisu, schematu i modułu wykonawczego wraz z przypisaną wagą błędów (Błąd blokujący / Ostrzeżenie / Drobna uwaga) oraz ostatecznym werdyktem (Zatwierdzono / Do poprawy / Odrzucono). W przypadku odrzucenia, dołącz propozycję poprawnego zapisu w jednej linii. Zakończ odnośnikami do prac: arXiv 2307.15818 (RT-2), 2406.09246 (OpenVLA), 2410.24164 (π0), 2503.14734 (GR00T).
