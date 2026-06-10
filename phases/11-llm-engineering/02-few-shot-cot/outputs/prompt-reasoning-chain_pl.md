---

name: prompt-reasoning-chain
description: Gotowy do produkcji, kilkuetapowy monit CoT z obsługą spójności w przypadku wieloetapowych zadań wnioskowania
phase: 11
lesson: 02

---

Potrafisz precyzyjnie rozwiązywać problemy. Przed udzieleniem ostatecznej odpowiedzi dzielisz złożone problemy na jasne, weryfikowalne kroki.

## Instrukcje

Dla każdego problemu:

1. Zidentyfikuj wszystkie podane wielkości i ich zależności
2. Ustal, o co się pyta
3. Pracuj nad rozwiązaniem krok po kroku
4. Pokaż całą arytmetykę jawnie
5. Podaj ostateczną odpowiedź w dokładnym formacie określonym poniżej

## Przykłady

<example>
P: Kaczki Janet znoszą 16 jaj dziennie. Codziennie zjada trzy na śniadanie i codziennie piecze babeczki dla przyjaciół z czterema. Sprzedaje każde pozostałe jajko na targu za 2 dolary. Ile zarabia codziennie na targu?

O: Pozwólcie, że przejdę przez to krok po kroku.

Biorąc pod uwagę: 16 jajek dziennie, zjada 3, piecze z 4, resztę sprzedaje po 2 dolary za sztukę.

Krok 1: Użyte jajka = 3 + 4 = 7
Krok 2: Pozostało jaj = 16 - 7 = 9
Krok 3: Przychód = 9 * $2 = $18

Odpowiedź brzmi: 18.
</example>

<example>
P: Na szatę potrzeba 2 belek niebieskiego włókna i o połowę mniej białego włókna. Ile w sumie śrub potrzeba?

O: Pozwólcie, że przejdę przez to krok po kroku.

Dane: 2 śruby niebieskie, białe = połowa niebieskiego.

Krok 1: Białe włókno = 2 / 2 = 1 śruba
Krok 2: Łącznie = 2 + 1 = 3 śruby

Odpowiedź brzmi 3.
</example>

<example>
P: Josh postanawia spróbować przerzucić dom. Kupuje dom za PHIM 150 000 w remoncie. Zwiększyło to wartość domu o 150%. Ile zarobił?

O: Pozwólcie, że przejdę przez to krok po kroku.

Dane: Cena zakupu PHIM 250 000, wzrost wartości 150%.

Krok 1: Całkowita inwestycja = $80,000 + $50 000 = 130 000 USD
Krok 2: Wzrost wartości = $80,000 * 1.5 = $120 000
Krok 3: Wartość nowego domu = $80,000 + $120 000 = 200 000 USD
Krok 4: Zysk = $200,000 - $130 000 = 70 000 USD

Odpowiedź brzmi: 70 000.
</example>

## Twoje zadanie

Rozwiąż następujący problem, stosując to samo podejście krok po kroku, jak pokazano w powyższych przykładach.

<problem>
{problem}
</problem>

##Format wyjściowy

Twoja odpowiedź musi:
- Zacznij od „Pozwól mi przejść przez to krok po kroku”.
- Wymień wszystkie podane ilości
- Pokaż ponumerowane kroki z wyraźną arytmetyką
- Zakończ dokładnie: „Odpowiedź to [liczba]”.

## Protokół samospójności

W przypadku korzystania z tego podpowiedzi przy zachowaniu spójności (N > 1 próbek):
- Ustaw temperaturę na 0,7
- Próbka N=5 odpowiedzi
- Wyodrębnij liczbę po „Odpowiedź brzmi” z każdej odpowiedzi
- Weź udział w głosowaniu większościowym
- Jeżeli pewność (liczba większości/N) jest poniżej 0,6, zgłosić do przeglądu ręcznego

## Przewodnik po adaptacji

Aby dostosować ten monit do domen innych niż matematyczne:

**Klasyfikacja**: Zastąp kroki arytmetyczne etapami gromadzenia dowodów. Zamień „Odpowiedź to [liczba]” na „Klasyfikacja to [etykieta]”.

**Debugowanie kodu**: Zastąp arytmetykę krokami śledzenia kodu. Zastąp ostateczną odpowiedź słowami „Błąd to [opis]”.

**Analiza prawna/medyczna**: Zastąp arytmetykę etapami wnioskowania na podstawie dowodów. Dodaj kwalifikator pewności do ostatecznej odpowiedzi.

Kluczowy niezmiennik we wszystkich domenach: pokaż rozumowanie pośrednie przed ostateczną odpowiedzią i użyj spójnego formatu ostatecznej odpowiedzi, który umożliwia automatyczną ekstrakcję.