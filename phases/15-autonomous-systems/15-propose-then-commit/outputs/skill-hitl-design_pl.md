---

name: hitl-design
description: Przejrzyj proponowany przepływ pracy typu Human-in-the-Loop dla warstw typu „zaproponuj, a następnie zatwierdź” kształt i oznacz brakujące metadane, idempotencję, weryfikację lub warstwy wyzwania i odpowiedzi.
version: 1.0.0
phase: 15
lesson: 15
tags: [hitl, propose-then-commit, idempotency, langgraph, cloudflare, agent-framework, eu-ai-act]

---

Biorąc pod uwagę proponowany przepływ pracy HITL, przeprowadź jego audyt pod kątem odniesienia „zaproponuj, a następnie zatwierdź” i oznacz, czego brakuje, jest niedookreślony lub jest niezgodny z przepisami.

Wyprodukuj:

1. **Metadane propozycji.** Potwierdź każdą propozycję, która się pojawia: zamiar (dlaczego), pochodzenie danych (treść źródłowa), naruszone uprawnienia, promień wybuchu (najgorszy przypadek), plan wycofywania. Brakujące pola są blokerami; „Agent chce X” nie jest propozycją.
2. **Idempotencja.** Nazwij kompozycję klucza idempotencji. Musi wynikać z treści propozycji, więc ponowne próby zwracają ten sam rekord. Klucze zawierające czas zegara ściennego nie są kluczami idempotencji; rejestrują znaczniki czasu.
3. **Trwałość.** Nazwij magazyn (PostgreSQL, Redis, Durable Object, pamięć obiektowa z kontrolą integralności). Potwierdź, że zatwierdzenia przetrwają ponowne uruchomienie agenta, ponowne uruchomienie hosta i wdrożenie. Kolejki w pamięci nie kwalifikują się.
4. **Powierzchnia zatwierdzenia.** Zatwierdzenie pieczątką (pojedynczy przycisk Zatwierdź) nie przechodzi audytu. Wymagane: lista kontrolna wyzwań i odpowiedzi z pozytywnym potwierdzeniem zrozumienia zamiarów, weryfikacji promienia wybuchu i gotowości do wycofania. Upewnij się, że lista kontrolna jest dostosowana do konkretnej klasy działań, a nie ogólna.
5. **Weryfikacja po zatwierdzeniu.** Potwierdź, że przepływ pracy ponownie odczytuje zasób docelowy po wykonaniu i wyświetla alerty w przypadku niepowodzenia weryfikacji. „Narzędzie zwróciło 200” nie zostało zweryfikowane.

Twarde odrzucenia:
- Powierzchnie HITL, które nie utrzymują trwale propozycji.
- Przepływy zatwierdzania, w przypadku których recenzentem jest sam agent.
- Wszelkie nieodwracalne działania produkcyjne bez wyzwań i odpowiedzi.
- Klucze idempotencji z komponentami zegara ściennego.
- Przepływy pracy, w których nie ma weryfikacji działań następczych po zatwierdzeniu.

Zasady odmowy:
- Jeśli użytkownik wymieni interfejs użytkownika zatwierdzający, ale nie może podać nazwy trwałego magazynu, który się za nim kryje, odmów i najpierw zażądaj sklepu.
- Jeśli użytkownik traktuje "max_budget_usd i okno potwierdzenia" jako wystarczające HITL, odmów. Budżety ograniczają koszty, a nie poprawność.
- Jeżeli rozmieszczenie dotyczy zakresu UE wysokiego ryzyka i nadal występują pieczątki, należy odmówić na podstawie art. 14.

Format wyjściowy:

Zwróć audyt typu „zaproponuj, a następnie zatwierdź” zawierający:
- **Tabela pól propozycji** (zamiar/pochodzenie/wybuch/wycofanie/pozwolenia — wymagane wszystkie pięć)
- **Notatka o idempotencji** (skład klucza, wynik testu ponownej próby)
- **Linia trwałości** (przechowuj, przetrwa-zrestartuj t/n)
- **Powierzchnia zatwierdzenia** (pieczątka/lista kontrolna; w przypadku listy kontrolnej należy podać pytania)
- **Weryfikacja po zatwierdzeniu** (podaj tak/nie, co ponownie odczytano)
- **Gotowość** (tylko produkcja / etapowanie / badania)