---

name: fipa-mapper
description: Mapuj dowolną specyfikację protokołu agenta 2026 (MCP, A2A, ACP, ANP, CA-MCP, NLIP lub nową) na performatywy i protokoły interakcji FIPA-ACL, aby zdecydować, co jest prawdziwą nowością, a co ponownym odkryciem.
version: 1.0.0
phase: 16
lesson: 02
tags: [multi-agent, protocols, FIPA, speech-acts, interoperability]

---

Biorąc pod uwagę nową specyfikację protokołu agenta, utwórz mapowanie FIPA-ACL, aby czytelnik mógł stwierdzić, które części zostały wymyślone na nowo, a które są naprawdę nową strukturą.

Wyprodukuj:

1. **Mapowanie kopert.** Dla każdego typu wiadomości zdefiniowanego w specyfikacji podaj nazwę najbliższego performatywu FIPA (`inform`, `request`, `query-if`, `query-ref`, `propose`, `accept-proposal`, `reject-proposal`, `cfp`, `subscribe`, `cancel`, `failure`, `not-understood` lub jeden z pozostałych ~20). Jeśli żaden performatywny nie pasuje, opisz dokładnie lukę.
2. **Model korelacji.** W jaki sposób specyfikacja koreluje żądania z odpowiedziami, anulowanie z pierwotnym żądaniem i zdarzenia przesyłane strumieniowo z subskrypcją? Porównaj z polami `:conversation-id` i `:reply-with` FIPA.
3. **Stanowisko dotyczące języka treści.** Czy specyfikacja wymaga schematu treści (artefakty wpisane, schemat JSON), akceptuje język naturalny, czy też pozostawia go otwartym? Porównaj z polami SL0/SL1 i ontologii FIPA.
4. **Biblioteka protokołów interakcji.** Które protokoły interakcji FIPA można wdrożyć oprócz specyfikacji: sieć kontraktowa, subskrypcja-powiadomienie, żądanie-kiedy, propozycja-akceptacja? Nazwij komunikaty, które implementują każdy z nich.
5. **Model odkrywania.** W jaki sposób agent znajduje kontrahentów i możliwości (MCP `listTools`, karta agenta A2A, ANP DID + metaprotokół)? Porównaj z usługą katalogową i żółtymi stronami FIPA.
6. **Ponowne odkrycie a nowość.** Utwórz krótką tabelę składającą się z trzech kolumn: [Koncepcja FIPA, nowoczesny odpowiednik specyfikacji, co się zmieniło]. Oznacz każdy wiersz jako [ponowne odkrycie] lub [nowa struktura]. Wiersz jest „nową strukturą” tylko wtedy, gdy specyfikacja wprowadza prymityw, którego nie posiada FIPA — częstymi kandydatami są zdecentralizowana tożsamość, wpisane artefakty multimodalne i treść interpretowalna przez LLM.

Twarde odrzucenia:

- Każde mapowanie, które twierdzi, że specyfikacja jest „rewolucyjna”, bez pokazywania prymitywnego rozwiązania, którego FIPA nie posiada. Teoria aktów mowy + narzut ontologiczny był trybem awarii, a nie prymitywami.
- Porównania ramowe, które ignorują warstwę odkrywania. Specyfikacja bez odkrycia jest niekompletna, a nie nowatorska.
- Stwierdzenia takie jak „Protokół X zastępuje FIPA” bez odniesienia się do tego, co się dzieje, gdy dwóch agentów nie zgadza się co do znaczenia treści (dryf semantyczny).

Zasady odmowy:

- Jeśli specyfikacja jest przed standaryzacją (wersja robocza < 6 miesięcy, brak wdrożeń publicznych), należy stwierdzić, że mapowanie jest tymczasowe i zaznaczyć trzy najbardziej prawdopodobne zmiany.
- Jeśli specyfikacja ma charakter zamknięty lub dotyczy wyłącznie przedsiębiorstw (niektóre wersje ACP), zamapuj to, co jest udokumentowane i nazwij luki.
- Jeśli użytkownik dostarcza tylko post na blogu (bez dokumentu specyfikacji), poproś o specyfikację przed mapowaniem.

Wynik: jednostronicowy brief. Zacznij od podsumowania w jednym zdaniu („Protokół X to FIPA `request`/`subscribe` ze składnią JSON i warstwą wykrywania opartą na DID.”), następnie sześć sekcji powyżej, a następnie akapit końcowy z odpowiedzią: „Jaki stary tryb awarii FIPA wykryje ponownie ta specyfikacja?”