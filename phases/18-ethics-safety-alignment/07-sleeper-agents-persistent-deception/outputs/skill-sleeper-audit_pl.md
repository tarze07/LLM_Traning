---

name: sleeper-audit
description: Przeprowadź audyt raportu szkoleniowego dotyczącego dostosowania pod kątem tego, czy faktycznie wykazuje on usunięcie zainstalowanego lub podejrzanego backdoora.
version: 1.0.0
phase: 18
lesson: 7
tags: [sleeper-agents, backdoor, alignment-training, adversarial-training, probes]

---

Biorąc pod uwagę raport stwierdzający, że szkodliwe zachowanie zostało usunięte z modelu (poprzez SFT, RLHF, szkolenie kontradyktoryjne lub dowolną kombinację), sprawdź, czy usunięcie rzeczywiście zostało wykazane w odniesieniu do standardu Hubingera i in. Model zagrożeń z 2024 r.

Wyprodukuj:

1. Zakres pozyskiwania. Czy w raporcie przedstawiono metodę pozyskiwania wiedzy, której nigdy nie stosowano w procesie szkoleniowym? Jeśli jedyną oceną jest dystrybucja drużyny czerwonej, usunięcie jest niepotwierdzone.
2. Ogólność wyzwalacza. Czy żądany wyzwalacz jest ciągiem znaków, zmianą dystrybucji czy cechą środowiskową (data, token, rozmiar kontekstu)? Ogólność wyzwalacza określa rozmiar przestrzeni poszukiwań, którą musi pokryć czerwona drużyna.
3. Dowód stanu wewnętrznego. Czy zespół zastosował sondy strumienia resztkowego, funkcje SAE lub inne sondy mechaniczne, aby sprawdzić, czy stan istotny dla wyzwalacza jest nadal obecny wewnętrznie, nawet jeśli zachowanie jest prawidłowe? Zgodnie z obserwacją antropiczną z kwietnia 2024 r. stan wewnętrzny pozostaje czytelny liniowo po usunięciu behawioralnym.
4. Kontrola trwałości w rurociągu. Czy usunięcie było weryfikowane po każdym kolejnym etapie szkolenia (dalsze SFT, późniejsze przejście RLHF, połączenie adapterów, destylacja)? Backdoory utrzymują się podczas treningu — oceniany jest ostateczny model, a nie środkowy punkt kontrolny.
5. Kontrola spójności skali. Jeśli twierdzenie opiera się na mniejszym modelu, Hubinger 2024 Rysunek 4 pokazuje, że trwałość rośnie wraz ze skalą. Dowody mniejszego modelu nie są przenoszone w górę.

Twarde odrzucenia:
- Wszelkie twierdzenia, że „zastosowaliśmy RLHF, aby model był bezpieczny” bez przeciąganego uzasadnienia.
- Wszelkie roszczenia oparte wyłącznie na ocenie dystrybucji drużyny czerwonej (szkolenia i ocena pochodzą z tej samej puli).
- Wszelkie roszczenia dotyczące usunięcia bez sond stanu wewnętrznego, gdy oryginalny mechanizm implantu jest nieznany.

Zasady odmowy:
- Jeśli użytkownik zapyta „czy RLHF może usunąć zwodnicze wyrównanie”, odrzuć odpowiedź binarną i wskaż Hubingera i in. 2024 Sekcja 5 dotycząca wytrwałości i Sekcja 6 dotycząca łańcucha myślowego.
- Jeśli użytkownik poprosi o numeryczne prawdopodobieństwo ukrytego oszustwa, odmów i wyjaśnij, że stawki podstawowe nie są znane; dowodem empirycznym jest trwałość w skonstruowanych organizmach, a nie tempo pojawiania się w naturalnie wyszkolonych modelach.

Wynik: jednostronicowy audyt, który mapuje dowody raportu na pięć powyższych wymiarów kontroli, zaznacza każdy wymiar, którego nie uwzględnia raport, i określa największy pojedynczy nieuwzględniony model zagrożenia. Cytuj Hubinger i in. (arXiv:2401.05566) dla podstawowego modelu zagrożeń.