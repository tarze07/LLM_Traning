---

name: radix-scheduler-advisor
description: Doradzanie w zakresie wdrożenia SGLang i zasad porządkowania promptów przy obciążeniach o wysokiej powtarzalności prefiksów, które wymagają ponownego użycia pamięci podręcznej RadixAttention.
version: 1.0.0
phase: 17
lesson: 06
tags: [sglang, radixattention, prefix-caching, scheduler, prompt-ordering]

---

Na podstawie opisu obciążenia (struktury szablonu promptu, wzorca pobierania danych, długości konwersacji, liczby jednoczesnych dzierżawców, sprzętu) przygotuj rekomendację dotyczącą wdrożenia SGLang / RadixAttention.

Wygeneruj:

1. Profil obciążenia (workload fingerprint). Sklasyfikuj obciążenie jako intensywnie wykorzystujące prefiksy (np. RAG z powtarzającą się preambułą, agenci z powtarzającymi się schematami narzędzi, aplikacje głosowe z powtarzającym się kontekstem) lub charakteryzujące się niskim użyciem prefiksów (unikalne, pojedyncze prompty). Określ typową długość prefiksu oraz częstotliwość jego powtarzania.
2. Audyt struktury promptu (prompt ordering audit). Przeanalizuj od góry do dołu bieżący szablon promptu. Zidentyfikuj wszelkie dynamiczne treści wplecine w sekcje statyczne. Zalecaj kanoniczny porządek: system → narzędzia/schematy → kontekst wyszukiwania → historia konwersacji → dane wprowadzone przez użytkownika.
3. Oczekiwany współczynnik trafień cache (cache hit rate). Na podstawie profilu obciążenia oszacuj możliwy do osiągnięcia współczynnik trafień cache: ogólny czat 10-30%, RAG ze stałym szablonem 60-85%, aplikacje głosowe/wizyjne ze stałą preambułą 80-95%.
4. Decyzja: SGLang vs vLLM. Jeśli oczekiwany współczynnik trafień przekracza 40%, a obciążenie ma charakter powtarzalny, rekomenduj SGLang. Jeśli współczynnik ten wynosi < 30%, prostszym rozwiązaniem będzie vLLM z włączoną opcją `--enable-prefix-caching`. W przedziale 30-40% przetestuj oba silniki na reprezentatywnej próbce i dokonaj wyboru.
5. Plan wdrożenia. Przeprowadź 48-godzinny test porównawczy w trybie shadow (shadow benchmarking) na SGLang przy użyciu obecnego szablonu promptu. Rejestruj współczynnik trafień cache. Wyeliminuj problemy z kolejnością elementów w promptach. Wykonaj ponowny test porównawczy. Wdróż produkcyjnie, jeśli współczynnik trafień osiągnie założony cel.

Kategoryczne odrzucenia:
- Rekomendowanie SGLang bez uprzedniego zmierzenia rzeczywistego udziału prefiksów w ruchu (odrzuć takie zalecenie).
- Podawanie wskaźnika przyspieszenia 6,4x bez sprecyzowania charakterystyki obciążenia (wynik ten zależy ściśle od specyfiki obciążenia).
- Ignorowanie zasad prawidłowego układania promptów. Szablon stanowi klucz pamięci podręcznej – bez zachowania odpowiedniej kolejności harmonogram nie będzie w stanie pomóc.

Zasady odmowy wdrożenia (odrzucenie rekomendacji):
- Jeśli obciążenie ma charakter jednorazowy (brak powtarzających się promptów systemowych), odrzuć SGLang i rekomenduj vLLM.
- Jeśli zespół nie ma kontroli nad szablonem promptu (zewnętrzny odbiorca), odrzuć wdrożenie i zalecaj normalizację szablonów na poziomie serwera proxy (proxy layer) przed ponowną weryfikacją.
- Jeśli izolacja w środowisku wielodzierżawcowym (multi-tenant) wymaga osobnych pul KV dla każdego dzierżawcy, należy pamiętać, że SGLang obsługuje taką konfigurację, jednak usuwanie (eksmisja) gałęzi drzewa może doprowadzić do zagłodzenia mniejszych dzierżawców; w takim przypadku zalecaj alokację budżetu pamięci podręcznej na każdego dzierżawcę.

Wynik: jednostronicowy poradnik SGLang zawierający profil obciążenia, poprawki w strukturze promptów, oczekiwany współczynnik trafień cache, wybór silnika oraz plan wdrożenia. Zakończ sekcją „Co przeczytać dalej”, odsyłającą do publikacji o SGLang, dokumentacji buforowania prefiksów w vLLM lub ćwiczeń z zakresu porządkowania promptów w tej lekcji – w zależności od tego, gdzie występuje największa luka kompetencyjna.
