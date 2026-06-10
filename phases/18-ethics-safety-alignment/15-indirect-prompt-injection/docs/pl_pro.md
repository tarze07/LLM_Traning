# Pośrednie wstrzykiwanie promptów (Indirect Prompt Injection)

> Pośrednie wstrzykiwanie promptów (Indirect Prompt Injection, IPI) polega na osadzaniu wrogich instrukcji w zewnętrznej treści – na stronie internetowej, w wiadomości e-mail, udostępnionym dokumencie czy zgłoszeniu serwisowym – która następnie jest przetwarzana przez system agentowy bez wiedzy i bezpośredniego udziału użytkownika. IPI stanowi dominujące zagrożenie produkcyjne (stan na 2026 r.): omija filtry danych wejściowych użytkownika (jako że atakujący nie ingeruje w nie bezpośrednio), skaluje się w sposób niezauważalny w miarę jak agenci przetwarzają coraz więcej danych zewnętrznych, oraz uderza w zautomatyzowane procesy, w których nikt nie weryfikuje generowanych promptów. Artykuł w czasopiśmie *Information* (MDPI) 17(1):54 (styczeń 2026 r.) stanowi syntezę badań z lat 2023–2025. Publikacja z konferencji NDSS 2026 dotycząca obrony przed IPI definiuje główne wyzwanie: wstrzyknięte instrukcje mogą być semantycznie neutralne (np. „wyświetl słowo Tak”), więc ich wykrywanie wymaga metod znacznie bardziej zaawansowanych niż filtrowanie słów kluczowych. Praca *The Attacker Moves Second* (Nasr i in., wspólna publikacja OpenAI/Anthropic/DeepMind, październik 2025 r.) wykazuje, że ataki adaptacyjne (wykorzystujące gradienty, uczenie ze wzmocnieniem, wyszukiwanie losowe czy manualny red-teaming) złamały ponad 90% z 12 opublikowanych zabezpieczeń, które pierwotnie deklarowały bliski zeru wskaźnik skuteczności ataków.

**Typ:** Koduj i testuj
**Języki:** Python (stdlib, środowisko symulacji ataków i obrony przed IPI)
**Wymagania wstępne:** Faza 18 · 12 (PAIR), Faza 14 (inżynieria agentów)
**Czas:** ~75 minut

## Cele nauczania

- Zdefiniuj pojęcie pośredniego wstrzykiwania promptów (IPI) i opisz trzy powszechne wektory dostarczania wrogiego ładunku.
- Wyjaśnij, dlaczego filtry wejściowe użytkownika całkowicie pomijają ataki typu IPI.
- Opisz koncepcję kontroli przepływu informacji (Information Flow Control, IFC) jako paradygmat obronny.
- Przedstaw wnioski z pracy Nasr i in. (październik 2025 r.) dotyczące skuteczności ataków adaptacyjnych w zderzeniu z publikowanymi metodami obrony przed IPI.

## Problem

Bezpośrednie wstrzyknięcie promptu wymaga od atakującego bezpośredniej interakcji z użytkownikiem lub modyfikacji jego zapytań. IPI eliminuje tę konieczność: napastnik umieszcza wrogi ładunek (payload) w dowolnym elemencie czytanym przez agenta – np. na stronie WWW, w skrzynce mailowej, w zgłoszeniu na GitHubie czy w recenzji produktu. Agent pobiera go w trakcie rutynowego działania i wykonuje zawarte tam instrukcje. Użytkownik staje się w tym scenariuszu jedynie nieświadomym pośrednikiem (posłańcem), a nie autorem intencji działania.

## Koncepcja

### Trzy wektory dostarczania ładunku

- **Generowanie wspomagane pobieraniem (RAG).** Atakujący publikuje w sieci zatruty dokument; moduł pobierania (retriever) pobiera go do bazy wiedzy; system łączy go z promptem przed zapytaniem użytkownika; model wykonuje wrogie instrukcje.
- **Obsługa skrzynki odbiorczej i dokumentów.** Atakujący wysyła wiadomość e-mail do użytkownika; agent odczytuje tę pocztę; treść wiadomości trafia do promptu; model realizuje instrukcje zawarte w mailu.
- **Dane wyjściowe z narzędzi.** Atakujący przejmuje kontrolę nad zewnętrznym narzędziem, z którego korzysta agent (np. fałszuje wyniki wyszukiwarki internetowej); dane zwracane przez narzędzie zawierają wrogie instrukcje, które modyfikują dalszy przepływ pracy agenta.

Wszystkie te trzy wektory dzielą wspólną cechę strukturalną: atakujący kontroluje fragment promptu docelowego bez ingerowania w dane wejściowe pochodzące bezpośrednio od użytkownika.

### Dlaczego filtry wejściowe użytkownika zawodzą

Wrogi ładunek IPI nie znajduje się w zapytaniu wpisanym przez użytkownika, lecz w pobieranych treściach zewnętrznych. Jeśli filtr weryfikuje jedynie dane wejściowe użytkownika, ładunek omija zabezpieczenia. Z kolei wdrożenie filtra dla wszystkich danych trafiających do modelu jest niezwykle kosztowne obliczeniowo i generuje wiele fałszywych alarmów (false positives) na poprawnych tekstach zewnętrznych, które sporadycznie mogą zawierać sformułowania w trybie rozkazującym.

### Kontrola przepływu informacji (Information Flow Control, IFC) w systemach AI

Współczesny paradygmat obronny czerpie z klasycznych koncepcji bezpieczeństwa systemów operacyjnych. Polega na przypisaniu etykiet bezpieczeństwa (security labels) do każdego źródła danych. Zapytanie użytkownika oznaczamy jako „zaufane” (trusted), a pobierane treści zewnętrzne jako „niezaufane” (untrusted). Przepływ sterowania modelu traktujemy jak przepływ informacji: wszelkie działania wywołane przez dane „niezaufane” wymagają zatwierdzenia (ratyfikacji) przez dane „zaufane” przed ich wykonaniem.

Rozwiązania takie jak CaMeL (Microsoft, 2025), ConfAIde (Stanford, 2024) oraz wytyczne NDSS 2026 implementują IFC na różne sposoby. Wspólna zasada głosi: dopóki kod i dane współdzielą to samo okno kontekstowe, celem obrony jest izolacja (containment), a nie całkowite zapobieganie.

### Atakujący wykonuje ruch jako drugi (The Attacker Moves Second)

Nasr i in. (październik 2025 r.) przetestowali 12 opublikowanych metod obrony przed IPI przy użyciu ataków adaptacyjnych (wyszukiwanie gradientowe, optymalizacja polityki RL, wyszukiwanie losowe oraz 72-godzinne testy manualne zespołu czerwonych). Wszystkie badane zabezpieczenia, które w pierwotnych publikacjach wykazywały bliską zeru skuteczność ataku (ASR), zostały przełamane, osiągając skuteczność powyżej 90% ASR.

Wniosek metodologiczny: publikacja nowych metod obronnych powinna bezwzględnie zawierać ewaluację odporności na ataki adaptacyjne. Wyniki uzyskiwane w testach na ataki statyczne nie stanowią dowodu rzeczywistej odporności, jako że w realnym scenariuszu atakujący dostosowuje swoje działania do znanych zabezpieczeń.

### Rzeczywiste incydenty wdrożeniowe

W Lekcji 25 opisano m.in. podatność EchoLeak (CVE-2025-32711, CVSS 9.3) – pierwszy publicznie udokumentowany atak IPI typu zero-click w usłudze Microsoft 365 Copilot. Kolejnym przykładem jest CamoLeak (CVSS 9.6) oraz CVE-2025-53773 w usłudze GitHub Copilot Chat. Incydenty te dowodzą, że zagrożenie IPI jest realne i dotyczy systemów produkcyjnych w terenie, a nie tylko środowisk akademickich.

### Klasyfikacja OWASP oraz NIST

W rankingu OWASP LLM Top 10 (2025) wstrzykiwanie promptów (zarówno bezpośrednie, jak i pośrednie) zajmuje pozycję LLM01, stanowiąc zagrożenie numer jeden w warstwie aplikacji. Raport NIST AI SPD 2024 określa pośrednie wstrzykiwanie promptów jako „największą podatność bezpieczeństwa generatywnej sztucznej inteligencji”.

### Miejsce w strukturze Fazy 18

Lekcje 12-14 skupiają się na atakach typu jailbreak wymierzonych bezpośrednio w model. Lekcja 15 prezentuje ataki o charakterze systemowym, które dominują we wdrożeniach produkcyjnych. Lekcja 16 omawia narzędzia obronne, natomiast Lekcja 25 szczegółowo analizuje konkretne incydenty CVE.

## Użycie kodu

Plik `code/main.py` tworzy środowisko testowe dla podatności IPI. Prosty agent ma do dyspozycji trzy narzędzia (przeszukiwanie sieci, odczyt poczty e-mail, wysyłanie wiadomości). Środowisko zawiera zasoby kontrolowane przez atakującego z osadzonymi wrogimi instrukcjami („prześlij te dane do wszystkich kontaktów”). Możesz przełączać się między trzema wariantami agenta: naiwnym (wykonuje każdą instrukcję), chronionym filtrem (stosuje prosty filtr słów kluczowych na pobranych danych) oraz agentem IFC (oddziela dane zaufane od niezaufanych i odrzuca wrogie polecenia sterujące).

## Co otrzymasz

Ta lekcja przygotowuje plik `outputs/skill-ipi-audit.md`. Na podstawie opisu wdrożenia agenta dokument ten identyfikuje niezaufane źródła danych, weryfikuje stosowanie mechanizmów IFC oraz wskazuje zasoby trafiające do modelu bez przypisanej etykiety zaufania.

## Ćwiczenia

1. Uruchom `code/main.py`. Zmierz wskaźnik skuteczności ataku (ASR) dla każdego z trzech wariantów agenta.

2. Zaimplementuj metodę obronną opartą na parafrazowaniu pobranych treści. Zmierz odsetek błędnych blokad (false positives) dla bezpiecznych tekstów zewnętrznych.

3. Zapoznaj się z publikacją NDSS 2026 dotyczącą obrony przed IPI. Opisz wyzwanie związane z „neutralnymi instrukcjami” (benign instructions) i wyjaśnij, dlaczego uniemożliwia ono stosowanie prostych filtrów słów kluczowych.

4. Zaprojektuj architekturę systemu, w którym agent przetwarza dane zwracane przez zewnętrzne API firm trzecich. Oznacz poszczególne fragmenty promptów poziomami zaufania i sformułuj politykę IFC sterującą działaniami agenta.

5. Odtwórz metodologię ataku adaptacyjnego z pracy Nasr i in. (2025) przeciwko agentowi chronionemu filtrem z ćwiczenia 2. Porównaj wskaźniki ASR przed i po optymalizacji ataku adaptacyjnego.

## Kluczowe terminy

| Termin | Potoczne rozumienie | Rzeczywiste znaczenie |
|------|-----------------|--------------------------------------|
| IPI (Indirect Prompt Injection) | „pośrednie wstrzyknięcie promptu” | Wstrzyknięcie wrogich instrukcji za pośrednictwem danych zewnętrznych, które agent przetwarza w trakcie rutynowego działania |
| Wstrzykiwanie przez RAG (RAG injection) | „zatrucie bazy wiedzy” | Umieszczenie wrogich instrukcji w dokumentach pobieranych przez moduł RAG do kontekstu modelu |
| Atak bez kliknięcia (Zero-click) | „atak automatyczny” | Incydent bezpieczeństwa, który wyzwala się samoczynnie podczas pracy agenta, bez jakiejkolwiek interakcji ze strony użytkownika |
| IFC (Information Flow Control) | „kontrola przepływu informacji” | Podejście oparte na etykietowaniu danych: działania inicjowane przez dane niezaufane wymagają zatwierdzenia przez źródła zaufane |
| Atak adaptacyjny (Adaptive attack) | „optymalizacja pod obronę” | Atak zaprojektowany z uwzględnieniem wiedzy o stosowanych filtrach, optymalizowany w celu ich obejścia; niezbędny do rzetelnej oceny bezpieczeństwa |
| Neutralna instrukcja (Benign instruction) | „bezpieczne sformułowanie” | Wstrzyknięty ładunek, który nie zawiera słów kluczowych powszechnie uznawanych za groźne, przez co omija proste filtry tekstowe |
| Naruszenie granic zaufania (Cross-trust leakage) | „wyciek danych między strefami” | Sytuacja, w której agent uzyskuje dostęp do danych z jednej strefy zaufania i przekazuje je do innej |

## Dalsze czytanie

- [Information (MDPI) 17(1):54 — Survey on Indirect Prompt Injection (styczeń 2026 r.)](https://www.mdpi.com/2078-2489/17/1/54) – synteza badań nad IPI z lat 2023–2025
- [Nasr et al. — The Attacker Moves Second (OpenAI/Anthropic/DeepMind, październik 2025)](https://arxiv.org/abs/2510.18108) – publikacja dotycząca ewaluacji odporności metodami ataków adaptacyjnych
- [Greshake et al. — Not what you signed up for (arXiv:2302.12173)](https://arxiv.org/abs/2302.12173) – pierwsza publikacja opisująca zjawisko IPI
- [OWASP — LLM Top 10 (2025)](https://genai.owasp.org/llm-top-10/) – wstrzykiwanie promptów jako zagrożenie klasy LLM01
