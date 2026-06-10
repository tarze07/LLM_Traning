---

name: fipa-mapper
description: Mapuj dowolną specyfikację protokołu agentowego z 2026 roku (MCP, A2A, ACP, ANP, CA-MCP, NLIP lub nową) na performatywy i protokoły interakcji FIPA-ACL, aby ocenić, co stanowi rzeczywistą nowość, a co jest powtórzeniem znanych koncepcji.
version: 1.0.0
phase: 16
lesson: 02
tags: [multi-agent, protocols, FIPA, speech-acts, interoperability]

---

Na podstawie nowej specyfikacji protokołu agentowego utwórz mapowanie na standard FIPA-ACL, aby czytelnik mógł łatwo ocenić, które elementy zostały odtworzone na nowo, a które stanowią unikalne innowacje strukturalne.

Wygeneruj:

1. **Mapowanie kopert.** Dla każdego typu komunikatu zdefiniowanego w specyfikacji przyporządkuj najbliższy performatyw FIPA (`inform`, `request`, `query-if`, `query-ref`, `propose`, `accept-proposal`, `reject-proposal`, `cfp`, `subscribe`, `cancel`, `failure`, `not-understood` lub jeden z pozostałych około 20). Jeśli żaden performatyw nie pasuje, opisz precyzyjnie tę lukę.
2. **Model korelacji.** W jaki sposób specyfikacja łączy żądania z odpowiedziami, żądania anulowania z pierwotnymi zapytaniami oraz zdarzenia strumieniowe z subskrypcjami? Porównaj to z polami `:conversation-id` i `:reply-with` w FIPA.
3. **Podejście do języka treści.** Czy specyfikacja wymaga określonego schematu danych (np. typowane artefakty, schemat JSON), akceptuje język naturalny, czy też pozostawia tę kwestię otwartą? Porównaj z polami SL0/SL1 i ontologii w FIPA.
4. **Biblioteka protokołów interakcji.** Które z protokołów interakcji FIPA można zaimplementować na bazie danej specyfikacji (np. sieć kontraktowa, subskrypcja-powiadomienie, żądanie-kiedy, propozycja-akceptacja)? Wskaż komunikaty realizujące każdy z nich.
5. **Model wykrywania (Discovery).** W jaki sposób agent odnajduje partnerów komunikacji i ich możliwości (np. MCP `listTools`, karta agenta A2A, ANP DID + metaprotokół)? Porównaj to z usługą katalogową (Directory Facilitator) i tzw. żółtymi stronami w FIPA.
6. **Powtórzenie a rzeczywista nowość.** Utwórz zwięzłą tabelę składającą się z trzech kolumn: [Koncepcja FIPA, nowoczesny odpowiednik w specyfikacji, co się zmieniło]. Oznacz każdy wiersz jako [powtórzenie koncepcji] lub [nowa struktura]. Wiersz może być oznaczony jako „nowa struktura” tylko wtedy, gdy specyfikacja wprowadza prymityw, którego nie było w FIPA — częstymi kandydatami są zdecentralizowana tożsamość, typowane artefakty multimodalne oraz treści interpretowalne bezpośrednio przez LLM.

Twarde kryteria odrzucenia:

- Odrzuć analizy sugerujące, że specyfikacja jest „rewolucyjna”, jeśli nie wykazano w niej prymitywów nieobecnych w FIPA. Narzut ontologiczny i teoria aktów mowy były elementami implementacji/awarii, a nie samymi prymitywami.
- Odrzuć porównania architektury, które ignorują warstwę wykrywania (discovery). Specyfikacja bez mechanizmu wykrywania jest niekompletna, a nie innowacyjna.
- Odrzuć stwierdzenia typu „Protokół X zastępuje FIPA”, które nie wyjaśniają, jak system radzi sobie z sytuacją, gdy dwaj agenci różnie interpretują treść komunikatu (dryf semantyczny).

Zasady obsługi przypadków szczególnych:

- Jeśli specyfikacja nie jest jeszcze w pełni standaryzowana (wersja robocza powstała mniej niż 6 miesięcy temu, brak publicznych wdrożeń), zaznacz, że mapowanie ma charakter tymczasowy i wskaż trzy najbardziej prawdopodobne kierunki zmian.
- Jeśli specyfikacja ma charakter zamknięty lub dotyczy wyłącznie systemów zamkniętych (jak niektóre wersje ACP), zamapuj udokumentowane elementy i wyraźnie wskaż luki.
- Jeśli użytkownik dostarcza jedynie artykuł na blogu zamiast pełnego dokumentu specyfikacji, poproś o dostarczenie specyfikacji przed przystąpieniem do mapowania.

Wynik: jednostronicowy raport syntetyczny. Rozpocznij od jednozdaniowego podsumowania (np. „Protokół X to w istocie FIPA `request`/`subscribe` z zapisem JSON i warstwą wykrywania opartą na standardzie DID.”), następnie przedstaw sześć wymaganych sekcji i zakończ akapitem odpowiadającym na pytanie: „Jaki znany z FIPA tryb awarii ujawni się na nowo w tej specyfikacji?”.
