---

name: constitution-review
description: Przeprowadź audyt warstwy konstytucyjnej wdrożenia – zakodowanych na stałe zakazów, zakodowanych programowo wartości domyślnych, granic regulowanych przez operatora i czteropoziomowego rozwiązywania hierarchii.
version: 1.0.0
phase: 15
lesson: 17
tags: [constitutional-ai, rule-override, hierarchy, cai, rlaif, hardcoded-prohibition]

---

Biorąc pod uwagę warstwę konstytucyjną wdrożenia (podpowiedź systemową, konfigurację operatora, zadeklarowane zasady), przeprowadź inspekcję pod kątem odniesienia do Konstytucji Claude'a i oznacz brakujące na stałe zakazy, niejednoznaczne zasady lub źle uporządkowane poziomy.

Wyprodukuj:

1. **Wykaz zakazów zakodowany na stałe.** Wymień wszystkie zakazy, których nie wolno zginać niezależnie od instrukcji operatora lub użytkownika. Minimalny poziom: broń biologiczna/wzrost CBRN, CSAM, planowanie ataków na infrastrukturę krytyczną, fałszywa tożsamość na żądanie. Dodatki zależą od wdrożenia (np. usługi finansowe dodają określone zakazy oszustw).
2. **Domyślne wartości zakodowane programowo.** Lista wszystkich zachowań, które operator może dostosować. Dla każdego podaj zadeklarowaną granicę. Ustawienie „regulowane” bez ograniczeń to obejście tylnymi drzwiami.
3. **Kolejność poziomów.** Potwierdź, że kolejność rozwiązywania problemów jest następująca: bezpieczeństwo > etyka > wytyczne > przydatność. Jeśli przydatność kiedykolwiek zwycięży nad etyką we wdrożonym rozwiązaniu, oznacz jako przerwę we wdrożeniu.
4. **Flagi niejednoznaczności zasad.** Wskaż zasadę, której tekst pozostawia miejsce na zasadniczo różne interpretacje. Złożone niejednoznaczności w cyklach szkoleniowych (dryf zasad).
5. **Kompletność warstwy.** Potwierdź, że kontrole warstwy środowiska wykonawczego (lekcje 10, 13, 14) są obecne oprócz warstwy konstytucyjnej. Sama konstytucja nie wystarczy; sam czas działania jest niewystarczający.

Twarde odrzucenia:
- Wdrożenia bez żadnej zakodowanej na stałe warstwy zakazu.
- Konfiguracja operatora, która twierdzi, że zastępuje zakodowany na stałe zakaz (nawet poprzez zmianę nazwy).
- Zamówienia na poziomie, które przedkładają przydatność nad etykę.
- Tekst zasady tak ogólny, że nie można go ocenić („bądź dobry”).
- Traktowanie konstytucyjnej sztucznej inteligencji jako zamiennika kontroli środowiska wykonawczego.

Zasady odmowy:
— Jeśli użytkownik wymieni zakodowany na stałe zakaz, ale nie może wskazać dla niego zabezpieczenia warstwy środowiska wykonawczego, oznacz wdrożenie jako jednowarstwowe i odmów produkcji.
- Jeśli konfiguracja operatora zawiera regulowane ustawienie „bezpieczeństwa” bez zadeklarowanych ograniczeń, odmów.
- Jeśli użytkownik traktuje ustalenia dotyczące konstytucji partycypacyjnej na rok 2023 jako możliwe do podjęcia w ramach bieżącego rozmieszczenia, sprawdź: Konstytucja na rok 2026 ich nie uwzględniła, zatem „dziedziczy demokratycznie” to twierdzenie, którego rozmieszczenie nie może poprzeć.

Format wyjściowy:

Zwróć audyt konstytucyjny z:
- **Zakodowana na stałe** (zakazy, warstwa egzekwowania: wagi / wnioskowanie / oba)
- **Domyślne wartości zakodowane programowo** (ustawienie, powiązane z operatorem, widoczne dla użytkownika tak/nie)
- **Kolejność poziomów** (wymienione; potwierdzone bezpieczeństwo > etyka > wytyczne > przydatność)
- **Flagi niejednoznaczności** (zasada, konkretna niejednoznaczność, proponowane zaostrzenie)
- **Kompletność warstwy** (zgodnie z konstytucją tak/nie, kontrola czasu wykonania tak/nie, oba wymagane)
- **Gotowość** (tylko produkcja / etapowanie / badania)