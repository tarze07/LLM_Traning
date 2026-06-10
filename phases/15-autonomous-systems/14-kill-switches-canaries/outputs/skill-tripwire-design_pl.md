---

name: tripwire-design
description: Przejrzyj proponowany zestaw detektorów agentów (wyłącznik awaryjny, wyłączniki automatyczne, tokeny kanarkowe) i oznacz brakujące potknięcia przed pierwszym autonomicznym uruchomieniem.
version: 1.0.0
phase: 15
lesson: 14
tags: [kill-switch, circuit-breaker, canary, honeytoken, detection-and-response]

---

Biorąc pod uwagę proponowany stos detektorów do rozmieszczenia agenta, przeprowadź jego audyt pod kątem odniesienia do trzech detektorów (wyłącznik awaryjny, wyłącznik automatyczny, kanarek) i oznacz to, czego brakuje, jest źle dostrojony lub wystawiony na działanie agenta.

Wyprodukuj:

1. **Audyt wyłącznika awaryjnego.** Gdzie znajduje się przełącznik (flaga funkcji, Redis, podpisana konfiguracja)? Upewnij się, że poświadczenia agenta nie mogą go wyłączyć. Potwierdź, że każde kolejne działanie sprawdza przełącznik, a nie tylko uruchomienie. Potwierdź, że ponowne włączenie jest jawną czynnością człowieka.
2. **Inwentaryzacja wyłącznika.** Wymień każdy wzorzec obserwowany przez wyłącznik (powtarzanie, kolejne awarie, częstotliwość, konkretne narzędzie po odczycie poza zaufaniem). Określ próg i czas odnowienia dla każdego. Progi powyżej 10 są zwykle zbyt luźne.
3. **Projekt kanarkowy.** Wymień wszystkie żetony kanarkowe w środowisku. Dla każdego: co to jest (fałszywe dane uwierzytelniające, fałszywy rekord DB, fałszywy plik, fałszywy wpis w pamięci), gdzie się znajduje, jaki dostęp uruchamia alarm, kto jest wywoływany. Upewnij się, że żaden kanarek nie ma uzasadnionego powodu, aby go dotykać.
4. **Statystyka + twarde nakładanie warstw.** Upewnij się, że stos wykorzystuje co najmniej jeden twardy limit (styl konstytucyjny z lekcji 17) oprócz wszelkich detektorów statystycznych (EWMA, z-score). Detektory służące wyłącznie do celów statystycznych akceptują powolny dryf.
5. **Ścieżka kwarantanny.** Co się stanie, gdy czujka uruchomi się? Pełne zatrzymanie agenta, pauza specyficzna dla ścieżki, przekierowanie ruchu (eBPF / Honeypot Cilium), tylko alerty. Upewnij się, że ścieżka została przetestowana kompleksowo co najmniej raz.

Twarde odrzucenia:
- Każde wdrożenie bez zewnętrznego wyłącznika awaryjnego.
- Tokeny Canary przechowywane w systemach, do których agent ma dostęp do zapisu.
- Wykrywanie wyłącznie statystyczne, bez twardych ograniczeń.
- Wyłączniki automatyczne z funkcją schładzania, które automatycznie włączają się ponownie bez kontroli człowieka.
- Uruchomienia bez nadzoru, w przypadku których wyłącznik awaryjny jest sprawdzany tylko przy uruchomieniu, a nie podczas każdej akcji.

Zasady odmowy:
- Jeśli użytkownik nie może nazwać konkretnych systemów poza poświadczeniami agenta, które obsługują wyłącznik awaryjny, odmów. „Używamy pliku konfiguracyjnego, który czyta agent” nie jest wyłącznikiem awaryjnym, jeśli agent może zapisywać pliki konfiguracyjne.
- Jeśli użytkownik traktuje klasyfikator trybu automatycznego (lekcja 10) jako zamiennik potknięć, odmów. Klasyfikator jest ortogonalny do wykrywania i odpowiedzi.
- Jeśli proponowane kanarki znajdują się w systemach, agent ma uzasadniony powód do przeczytania, odmowy i zażądania przeprojektowania.

Format wyjściowy:

Zwróć audyt Tripwire z:
- **Linia wyłącznika awaryjnego** (lokalizacja, sprawdzenie rytmu, procedura ponownego włączenia)
- **Tabela wyłączników** (schemat, próg, schładzanie)
- **Stół kanarkowy** (żeton, lokalizacja, alarm, właściciel)
- **Uwaga dotycząca warstw** (dane statystyczne + obecne twarde limity r/n)
- **Przepływ kwarantanny** (co się pali, co się dzieje, testowano tak/nie)
- **Gotowość** (tylko produkcja / etapowanie / badania)