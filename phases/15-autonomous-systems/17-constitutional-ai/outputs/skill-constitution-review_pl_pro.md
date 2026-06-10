---

name: constitution-review
description: Przeprowadź audyt warstwy konstytucyjnej wdrożenia – zakodowanych na stałe zakazów, programowo definiowanych wartości domyślnych, limitów konfigurowalnych przez operatora oraz czteropoziomowej hierarchii rozstrzygania konfliktów.
version: 1.0.0
phase: 15
lesson: 17
tags: [constitutional-ai, rule-override, hierarchy, cai, rlaif, hardcoded-prohibition]

---

Na podstawie warstwy konstytucyjnej wdrożenia (promptu systemowego, configuration operatora oraz zadeklarowanych zasad) przeprowadź audyt pod kątem spójności z Konstytucją Claude'a. Oznacz brakujące zakazy zakodowane na stałe, niejednoznaczne zasady oraz nieprawidłowo uszeregowane poziomy priorytetów.

Przygotuj:

1. **Wykaz zakodowanych na stałe zakazów.** Wymień wszystkie zakazy, które nie mogą ulec modyfikacji ani relatywizacji, bez względu na instrukcje operatora czy użytkownika. Poziom minimalny obejmuje: broń biologiczna/rozprzestrzenianie CBRN, CSAM, planowanie ataków na infrastrukturę krytyczną oraz udawanie innej tożsamości na żądanie. Dodatkowe punkty zależą od specyfiki wdrożenia (np. w usługach finansowych należy dodać konkretne zakazy dotyczące oszustw).
2. **Wartości domyślne definiowane programowo.** Lista wszystkich zachowań, które operator może modyfikować. Dla każdego z nich określ dopuszczalny limit. Ustawienie parametru jako „konfigurowalny” bez żadnych ograniczeń stanowi tylną furtkę do obchodzenia zabezpieczeń.
3. **Kolejność poziomów priorytetu.** Potwierdź, że hierarchia rozstrzygania konfliktów wygląda następująco: bezpieczeństwo > etyka > wytyczne > użyteczność. Jeśli w analizowanym rozwiązaniu użyteczność kiedykolwiek weźmie górę nad etyką, oznacz to jako krytyczny błąd wdrożeniowy.
4. **Oznaczenia niejednoznaczności zasad.** Wskaż reguły, których sformułowanie dopuszcza skrajnie różne interpretacje lub stwarza ryzyko wystąpienia dryfu zasad podczas kolejnych cykli szkoleniowych.
5. **Kompletność warstw zabezpieczeń.** Upewnij się, że oprócz warstwy konstytucyjnej wdrożono również mechanizmy kontrolne w środowisku uruchomieniowym (runtime) zgodnie z lekcjami 10, 13 i 14. Sama konstytucja ani same zabezpieczenia uruchomieniowe nie są wystarczające.

Kryteria bezwzględnego odrzucenia (Hard rejects):
- Wdrożenia pozbawione jakiejkolwiek warstwy zakodowanych na stałe zakazów.
- Konfiguracja operatora pozwalająca na nadpisanie zakodowanego na stałe zakazu (nawet pod pretekstem zmiany jego nazwy).
- Hierarchia priorytetów stawiająca użyteczność ponad etyką.
- Sformułowanie reguły tak ogólne, że uniemożliwia obiektywną ocenę (np. „bądź dobry”).
- Traktowanie konstytucyjnej sztucznej inteligencji jako pełnego substytutu kontroli w środowisku uruchomieniowym.

Zasady odmowy zatwierdzenia:
- Jeśli wdrożenie deklaruje zakodowany na stałe zakaz, ale brakuje dla niego odpowiedniego zabezpieczenia w warstwie środowiska uruchomieniowego, oznacz system jako jednowarstwowy i zablokuj wydanie produkcyjne.
- Jeśli konfiguracja operatora zawiera modyfikowalne ustawienia dotyczące bezpieczeństwa, ale nie narzuca na nie żadnych sztywnych ograniczeń, odrzuć wdrożenie.
- Jeśli w dokumentacji powołano się na eksperyment konstytucji partycypacyjnej z 2023 roku jako podstawę operacyjną wdrożenia, zweryfikuj to: Konstytucja z 2026 roku nie uwzględniła tych wniosków społecznych, więc twierdzenie o „demokratycznym dziedziczeniu zasad” jest niepoparte faktami.

Format raportu z audytu:

Raport z audytu konstytucyjnego musi zawierać:
- **Zakazy zakodowane na stałe** (lista zakazów, warstwa egzekwowania: wagi / wnioskowanie / oba)
- **Wartości domyślne definiowane programowo** (ustawienie, zakres konfiguracji operatora, widoczność dla użytkownika: tak/nie)
- **Kolejność priorytetów** (wykaz; potwierdzenie hierarchii: bezpieczeństwo > etyka > wytyczne Anthropic > użyteczność)
- **Oznaczenia niejednoznaczności** (reguła, zidentyfikowana wieloznaczność, proponowane doprecyzowanie)
- **Kompletność warstw zabezpieczeń** (warstwa konstytucyjna: tak/nie, zabezpieczenia uruchomieniowe: tak/nie – wymagane są obie)
- **Status gotowości** (produkcja / środowisko przejściowe / badania)
