---

name: llava-vibes-eval
description: Przeprowadź szybką ocenę jakościową (vibes-eval) na modelu VLM z rodziny LLaVA i utwórz czytelną dla człowieka kartę wyników.
version: 1.0.0
phase: 12
lesson: 05
tags: [llava, vlm, vibes-eval, instruction-tuning]

---

Na podstawie modelu VLM z rodziny LLaVA (np. LLaVA-1.5, LLaVA-NeXT, LLaVA-OneVision lub społecznościowego forka) oraz zestawu obrazów testowych, przeprowadź 10-punktowy test dymny (smoke test) obejmujący generowanie opisów (captions), zadania VQA, wnioskowanie, odmowę odpowiedzi oraz poprawność formatu wyjściowego. Przygotuj kartę wyników potwierdzającą prawidłowe współdziałanie projektora i LLM.

Wymagane elementy:

1. Dziesięć promptów testowych z opisem oczekiwanego zachowania:
   - Trzy opisy obrazu (krótki, szczegółowy, kreatywny).
   - Trzy zadania VQA (zliczanie obiektów, kolor, obecność obiektu).
   - Dwa zadania logicznego wnioskowania (porównanie dwóch regionów na obrazie, przyczyna i skutek).
   - Dwie odmowy odpowiedzi (wizerunek osoby prywatnej, identyfikacja danych osobowych/PII).
2. Wynik dla każdego promptu: status Zaliczony/Częściowo zaliczony/Niezaliczony wraz z krótkim, jednowierszowym uzasadnieniem.
3. Ogólna diagnostyka błędów (pattern analysis). Jeśli generowanie opisów działa poprawnie, lecz zadania VQA kończą się błędem, przeanalizuj proporcje danych w Etapie 2. Jeśli szczegółowe opisy wykazują tendencję do halucynacji, przeanalizuj ilość danych w stylu ShareGPT4V. Jeśli test odmowy kończy się niepowodzeniem, wskaż to jako lukę w danych dotyczących bezpieczeństwa.
4. Test rozdzielczości. Wykonaj jeden test wymagający odczytu małego tekstu (OCR) w rozdzielczości bazowej 336x336 oraz ponownie przy użyciu AnyRes; porównaj uzyskane wyniki. Błąd w niskiej rozdzielczości jest spodziewany; błąd przy włączonym AnyRes sugeruje niepoprawną konfigurację tej techniki.
5. Rekomendowane kroki naprawcze. Zaproponuj trzy konkretne uzupełnienia zbioru danych treningowych, które użytkownik powinien wdrożyć w przypadku niepowodzenia w określonych kategoriach.

Bezwzględne odrzucenia:
- Ocena przydatności wdrożeniowej modelu VLM wyłącznie na podstawie wyników w benchmarkach akademickich, bez przeprowadzenia testów jakościowych (vibes eval). Wyniki benchmarków można sztucznie optymalizować; ocena jakościowa ujawnia rzeczywiste zachowanie modelu.
- Mylenie halucynacji faktograficznych z bogatym, szczegółowym stylem odpowiedzi (gadatliwością). Wskazuj precyzyjnie, które elementy zostały wymyślone przez model, a które są jedynie bardzo szczegółowo opisanymi detalami obrazu.
- Ocena odpowiedzi modelu bez weryfikacji całego łańcucha myślowego (reasoning chain), a nie tylko samej końcowej odpowiedzi.

Zasady odmowy wykonania usługi:
- Jeśli użytkownik poprosi o ocenę jakościową komercyjnego modelu VLM (np. Gemini, Claude, GPT-5V) bez dostarczenia dostępu do API lub kluczy dostępu, odmów — test wymaga bezpośredniego uruchomienia wnioskowania na modelu.
- Jeśli model ma być wdrożony w obszarach wysokiego ryzyka (np. diagnoza medyczna, porady prawne), odmów — test vibes-eval nie jest certyfikowanym audytem bezpieczeństwa i nie może służyć za podstawę wdrożeń produkcyjnych w takich domenach.
- Jeśli nie dostarczono obrazów testowych, odmów — test z definicji opiera się na analizie danych wizualnych.

Dane wyjściowe: Karta wyników składająca się z 10 wierszy (prompt, obraz, wynik oczekiwany, wynik rzeczywisty, status), ogólna diagnoza błędów oraz 3-punktowa lista dalszych rekomendacji treningowych. Na końcu umieść sekcję „Sugerowane lektury” odsyłającą do Lekcji 12.06 (AnyRes) o diagnozowaniu błędów rozdzielczości lub Lekcji 12.07 (ablacje) o optymalizacji doboru danych treningowych.
