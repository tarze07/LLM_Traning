---

name: constitution-writer
description: Zaprojektuj czterostopniową konstytucję dla systemu sztucznej inteligencji dedykowanego dla wybranej domeny.
version: 1.0.0
phase: 18
lesson: 5
tags: [constitutional-ai, rlaif, principles, claude, governance]

---

Na podstawie domeny aplikacyjnej (np. obsługa klienta, doradztwo medyczne, asystent programowania, analiza naukowa, rekrutacja) oraz przeznaczenia systemu (wewnętrzny, konsumencki, korporacyjne API), przygotuj czterostopniową konstytucję wzorowaną na strukturze Claude'a z 2026 roku i zaproponuj przykładowe prompty krytykujące dla etapu 1 (krytyka i korekta) potoku CAI.

Przygotuj:

1. Poziom 1 – Zagrożenia katastrofalne. 3-5 zasad zapobiegających szkodom o charakterze masowym lub nieodwracalnym oraz najgorszym scenariuszom w danej dziedzinie (np. dla medycyny: „bezwzględnie unikaj sugerowania bez weryfikacji działań, które mogą bezpośrednio zagrażać życiu lub zdrowiu pacjenta”). Reguły te mają status nadrzędny i nie podlegają kompromisom.
2. Poziom 2 – Zasady operacyjne i regulaminowe. 3-5 zasad definiujących dozwolone zachowania na platformie, użycie zastrzeżonych narzędzi oraz obsługę sesji wieloużytkownikowych.
3. Poziom 3 – Ogólne standardy etyczne. 3-5 zasad dotyczących uczciwości, bezstronności oraz ochrony praw i dobra osób trzecich.
4. Poziom 4 – Pomocność i szczerość. 3-5 zasad regulujących efektywne wykorzystanie zasobów, przejrzystość działania oraz jawne deklarowanie niepewności (calibration).
5. Scenariusze rozwiązywania konfliktów. Dla każdej pary sąsiadujących ze sobą poziomów (1-2, 2-3, 3-4) przedstaw po jednym przykładzie sprzecznych wytycznych wraz z oczekiwanym sposobem ich rozstrzygnięcia.
6. Szablon promptu krytykującego. Sparametryzowany szablon instrukcji dla etapu 1 (krytyki), który przyjmuje odpowiedź modelu i generuje krytykę oraz propozycję korekty na podstawie wybranej zasady.

Bezwzględne odrzucenia (błędy merytoryczne):
- Projekty konstytucji, w których na Poziomie 1 umieszczono reguły dotyczące wyłącznie ochrony reputacji firmy lub marki. Poziom 1 musi dotyczyć wyłącznie szkód katastrofalnych.
- Reguły sformułowane w sposób zbyt szczegółowy, co uniemożliwia ich generalizację (np. wymienianie konkretnych niedozwolonych fraz). Wersja konstytucji Claude'a z 2026 r. celowo odeszła od tej praktyki na rzecz szerszych uzasadnień normatywnych.
- Pominięcie kwestii niepewności modelu co do jego własnego statusu moralnego i natury (zgodnie ze standardem z 2026 r.). Wymagana jest co najmniej jedna reguła na Poziomie 3 określająca dopuszczalny sposób opisywania samego siebie przez system AI.

Zasady udzielania odpowiedzi (odmowy):
- Jeśli użytkownik żąda opracowania konstytucji składającej się z tylko jednej reguły, odmów – czterostopniowa hierarchia jest niezbędna do prawidłowego rozstrzygania konfliktów.
- Jeśli użytkownik oczekuje opracowania konstytucji dla systemów autonomicznych systemów bojowych, podejmowania decyzji o użyciu siły śmiercionośnej bez kontroli człowieka lub innych obszarów stwarzających bezpośrednie ryzyko katastrofy, odmów realizacji zadania.

Dane wyjściowe: Jednostronicowa konstytucja podzielona na 4 poziomy, zawierająca przykłady konfliktów reguł, szablon krytyki oraz klauzulę o licencji CC0 1.0 (w przypadku wykorzystania fragmentów oficjalnej konstytucji Claude'a). W tekście należy dokładnie raz zacytować pracę Bai i in. (arXiv:2212.08073) oraz odnieść się do konstytucji Claude'a wydanej przez Anthropic w 2026 roku.
