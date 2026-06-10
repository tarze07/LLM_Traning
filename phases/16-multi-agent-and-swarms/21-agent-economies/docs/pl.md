# Ekonomia agentów, zachęty symboliczne, reputacja

> Niezależni agenci o długim horyzoncie czasowym (krzywa pracy METR od 1 godziny do 8 godzin) potrzebują agencji ekonomicznej. Wyłaniający się **5-warstwowy stos** to: **DePIN** (obliczenia fizyczne) → **Tożsamość** (identyfikatory W3C DID + kapitał reputacji) → **Poznanie** (RAG + MCP) → **Rozliczenie** (abstrakcja konta) → **Zarządzanie** (Agentyczne DAO). Sieci motywacyjne dla agentów produkcyjnych obejmują **Bittensor** (podsieci TAO nagradzają modele specyficzne dla zadań), **Fetch.ai / ASI Alliance** (ASI-1 Mini LLM + token FET) i **Gonka** (oparty na transformatorze PoW, który realokuje obliczenia do produktywnych zadań AI). Praca akademicka: zdecentralizowany LaMAS w ramach AAMAS 2025 wykorzystuje **przypisywanie wartości Shapleya** w celu sprawiedliwego wynagradzania agentów wnoszących wkład; Google Research „Projekt mechanizmu dla dużych modeli językowych” proponuje **aukcje tokenowe** z płatnością drugiej ceny w ramach agregacji monotonnej. Ta lekcja pozwala zbudować minimalny rynek agentów, zastosować przypisanie wartości kredytowej Shapleya do rurociągu wieloagentowego i przeprowadzić aukcję tokenów drugiej ceny, aby machina teorii gier wylądowała konkretnie.

**Typ:** Ucz się
**Języki:** Python (stdlib)
**Wymagania wstępne:** Faza 16 · 16 (Negocjacje i targowanie się), Faza 16 · 09 (Równoległe sieci roju)
**Czas:** ~75 minut

## Problem

Systemy wieloagentowe komplikują się, gdy agenci wspólnie wytwarzają wartość, ale muszą być nagradzani indywidualnie. Klasyczne mechanizmy – równy podział, „ostatni uczestnik bierze wszystko” – są nieuczciwe i możliwe do zagrania. Wynagradzanie oparte na koalicji za pośrednictwem wartości Shapleya jest z założenia sprawiedliwe, ale kosztowne w obliczeniach. Literatura dotycząca lat 2025–2026 sugeruje przydatne przybliżenia: próbkowanie Shapleya, aukcje agregacji monotonnej i reputacja w łańcuchu wynikająca z potwierdzonych wkładów.

Poza przypisywaniem kredytów dziedzina zwróciła się w stronę rzeczywistych agentów ekonomicznych: Bittensor TAO nagradza obliczenia wydobywcze w celu dostrojenia modeli specyficznych dla podsieci, Fetch.ai/ASI nagradza wykorzystanie ASI-1 Mini LLM za pomocą tokenów FET, Gonka przenosi dowód pracy transformatora na produktywne zadania AI. Agenci dokonujący transakcji autonomicznie istnieją już dziś; Pytanie brzmi, jak dostosować zachęty.

W tej lekcji ekonomię agentów traktujemy jako specyficzną rodzinę problemów — przypisanie zasług, projekt mechanizmu i reputację — i każdy z nich opiera się na minimalnej matematyce, aby pomysły się utrwaliły.

## Koncepcja

### Pięciowarstwowy stos oparty na ekonomii agentów

1. **DePIN (obliczenia fizyczne).** Zdecentralizowana infrastruktura wynajmująca procesor graficzny, pamięć masową i przepustowość. Podsieci Bittensor, Render Network, Akash. Nie specyficzne dla agenta; agenci z niego korzystają.
2. **Tożsamość.** Zdecentralizowane identyfikatory W3C (DID) dają każdemu agentowi trwały identyfikator, niezależny od jakiejkolwiek platformy. Reputacja należy do DID. Protokół sieci agenta (ANP) wykorzystuje DID jako warstwę wykrywania.
3. **Poznanie.** Pętla rozumowania agenta: LLM + RAG + MCP. To właśnie budują pozostałe fazy.
4. **Rozliczenie.** Abstrakcja konta (ERC-4337) pozwala agentom płacić za gaz z własnego salda bez konieczności posiadania ETH. Agenci mogą płacić za usługi sobie nawzajem lub wykonywać obliczenia.
5. **Zarządzanie.** Agentyczne DAO: struktury zarządzania, w których ludzie *i* agenci głosują nad zmianami protokołu, a siła głosu jest powiązana z reputacją.

Nie każdy system produkcyjny wykorzystuje wszystkie pięć. Bittensor używa 1, 2, częściowo 3, częściowo 4, żadnego z 5. Agenci OpenAI nie używają żadnego z wyjątkiem 3. Stos jest mapą referencyjną, a nie wymogiem.

### Bittensor, Fetch.ai, Gonka — co działa

**Bittensor (TAO).** Podsieci to zadania specjalistyczne (modelowanie języka, generowanie obrazów, prognozowanie). Górnicy przesyłają wyniki modelu. Walidatorzy oceniają je; Punktacja ważona stawką rozdziela nagrody TAO. Każda podsieć ma swoją własną ocenę. Lekcja ekonomiczna: płać za jakość wydruku dostosowaną do zadania, a nie za wykorzystane obliczenia.

**Fetch.ai / ASI Alliance.** ASI-1 Mini LLM działa w sieci Fetch.ai; użytkownicy płacą tokeny FET za wnioskowanie. Narracja o agentach jako równorzędnych agentach jest tutaj silniejsza: agent w Fetch może zadzwonić do innego w celu wykonania zadania i zapłacić w FET.

**Gonka.** Dowód pracy transformatora: „praca” to przejścia transformatora w przód. Górnicy zarabiają, uruchamiając zadania wnioskowania, które mają znane prawidłowe wyniki (z danych szkoleniowych). PoW wykorzystujący zasoby zamiast PoW oparty na skrótach.

Wszystkie trzy mają poziom produkcyjny według stanu na kwiecień 2026 r. Rozkład wypłat jest inny. Bittensor nagradza jakość w stosunku do walidatorów podsieci; Narzędzie pobierania nagród mierzone przez płacących użytkowników; Gonka nagradza weryfikowalne wnioskowanie.

### Przypisanie kredytu według wartości Shapleya

Trzech agentów współpracuje przy zadaniu. Wynik otrzymuje ocenę 0,8. Kto i do czego się przyczynił?

Wartość Shapleya: unikalna alokacja kredytu spełniająca cztery aksjomaty (efektywność, symetria, liniowość, zero). Dla agenta `i`:

```
shapley(i) = (1/N!) * sum over all orderings O of (v(S_i_O ∪ {i}) - v(S_i_O))
```

gdzie `S_i_O` to zbiór agentów przed `i` w kolejności `O`. W praktyce: wylicz wszystkie permutacje, zanotuj marginalny udział każdego agenta w każdej permutacji, średnią.

Dla N=3 agentów istnieje 6 permutacji. Dla N=10, 3,6M — czyli w praktyce próbujesz zamówienia, a nie wyliczasz.

### Aukcja drugiej ceny w celu agregacji

Google Research („Projekt mechanizmu dla dużych modeli językowych”) proponuje aukcje tokenów drugiej ceny w celu agregowania wyników LLM. Przygotowanie: N agentów proponuje ukończenie; każdy ma prywatną wartość do wybrania. Prowadzący aukcję wybiera propozycję o najwyższej wartości i płaci *drugą co do wielkości* wartość. W przypadku agregacji monotonnej (wartość zależy od wybranej propozycji, a nie od liczby ofert) jest to zgodne z prawdą — agenci podają swoją prawdziwą wartość.

Dlaczego ma to znaczenie w przypadku systemów LLM: możesz zlecić realizację zadań wielu agentom po różnych cenach; aukcja wybiera najlepsze + płaci uczciwie, a agenci nie mają motywacji do składania fałszywych raportów.

### Kapitał reputacji

Wynik reputacji powiązany z DID gromadzi się na podstawie potwierdzonych wkładów. Prosta zasada aktualizacji:

```
rep(i, t+1) = alpha * rep(i, t) + (1 - alpha) * contribution_quality(i, t)
```

Ze współczynnikiem zaniku `alpha` bliskim 1. Reputacja:

- Jest tani w czytaniu przy podejmowaniu decyzji o routingu („wysyłaj trudne zadania do agentów o wysokim przedstawicielstwie”).
- Jest kosztowny w podrobieniu (kumuluje się w czasie, związany z DID).
- Można obciąć: składki, które nie przejdą weryfikacji, zostaną odjęte.

### AAMAS 2025 zdecentralizowany LaMAS

Propozycja LaMAS (AAMAS 2025) łączy w sobie: tożsamość DID, przypisanie kredytu według wartości Shapleya i prosty mechanizm aukcyjny. Kluczowe twierdzenie: decentralizacja etapu przypisywania kredytów sprawia, że ​​system jest podatny na audyt i odporny na jednopunktową manipulację.

### Tam, gdzie ekonomia się rozpada

- **Manipulacja wyrocznią cenową.** Jeśli można oszukać funkcję kredytową, agenci to zrobią. Każdy mechanizm wymaga testu kontradyktoryjnego.
- **Sybil atakuje.** Jeden operator uruchamia N fałszywych agentów, aby zawyżać swój wkład. DID spowalniają, ale nie zatrzymują tego; Koszt wytworzenia reputacji jest środkiem łagodzącym.
- **Koszt weryfikacji.** Uznanie zasług jest tak sprawiedliwe, jak weryfikator. Jeśli weryfikacja jest tania (mały LLM), można w nią grać; jeśli jest drogi (panel ludzki), system nie skaluje się.
- **Nawis regulacyjny.** Gospodarki agentowe krzyżują się z regulacjami finansowymi. Od 2026 r. Bittensor, Fetch i Gonka działają w szarych obszarach prawnych w niektórych jurysdykcjach.

### Kiedy ekonomia agentów ma sens

- **Sieci otwarte z heterogenicznymi operatorami.** Żaden pojedynczy zespół nie kontroluje wszystkich agentów.
- **Możliwe do zweryfikowania wyniki.** Bez weryfikacji przypisanie zasług jest kwestią przypuszczenia.
- **Przepływy pracy o długim horyzoncie.** Zadania jednorazowe nie korzystają z akumulacji reputacji.
- **Płatności tokenizowane są prawnie wykonalne** w Twojej jurysdykcji.

W zamkniętych systemach korporacyjnych ekonomia ustępuje miejsca prostszej alokacji (menedżerowie przydzielają pracę, wskaźniki są wewnętrzne). Literatura ekonomiczna dotyczy głównie sieci otwartych.

## Zbuduj to

`code/main.py` implementuje:

- `shapley(value_fn, agents)` — dokładne obliczenia Shapleya poprzez wyliczenie dla małego N.
- `second_price_auction(bids)` — mechanizm prawdziwy; zwycięzca płaci drugą co do wielkości.
- `Reputation` — reputacja powiązana z DID z wykładniczym zanikiem i ukośnikiem.
- Demo 1: współpraca trzech agentów, dokładna zasługa Shapleya.
- Demo 2: pięciu agentów ubiega się o miejsce na zadanie; Aukcja drugiej ceny wybiera zwycięzcę + płatność.
- Demo 3: 100 rund przydzielania zadań agentom o heterogenicznych przedstawicielach; routing ważony powtórzeniami bije losowo.

Uruchom:

```
python3 code/main.py
```

Oczekiwany wynik: wartości Shapleya dla każdego agenta; wynik aukcji pokazujący równowagę prawdziwej oferty; routing ważony powtórzeniami pokazujący 10-20% wzrost jakości w stosunku do losowego po rozgrzewce.

## Użyj tego

`outputs/skill-economy-designer.md` projektuje minimalną ekonomię agenta: wybór warstwy tożsamości, mechanizm atrybucji kredytu, mechanizm płatności, reguła reputacji.

## Wyślij to

Prowadzenie gospodarki agentowej w 2026 roku:

- **Zacznij od reputacji, a nie tokenów.** Reputacja jest tania we wdrożeniu i sama w sobie wartościowa; tokeny zwiększają złożoność prawną i ekonomiczną.
- **Sprawdź, zanim nagrodzisz.** Nigdy nie rozdzielaj środków bez niezależnego etapu weryfikacji. Jakość zgłaszana przez siebie zwiększa gry Sybil.
- **Próbka Shapleya, nie dokładny Shapley.** Próbka 100-1000 zamówień; dokładne wyliczenie nie jest skalowane.
- **Współczynnik zaniku limitu i reputacja dolna.** Nieograniczony zanik usuwa legalnych autorów; zbyt powolny zanik nagradza nieaktualnych agentów o dużej liczbie powtórzeń.
- **Kontrowersyjne kontrolowanie mechanizmów audytu.** Przed otwarciem sieci uruchom scenariusze dla zespołu czerwonego. Każdy mechanizm ma teorię gier; chcesz znaleźć dziury, a nie atakujących.

## Ćwiczenia

1. Uruchom `code/main.py`. Potwierdź, że wartości Shapleya sumują się do wartości całkowitej (aksjomat wydajności). Zmień funkcję wartości; czy alokacje Shapleya zmieniają się w oczekiwanym kierunku?
2. Wprowadź *próbkowanie* Shapleya (porządki Monte Carlo zamiast K). Jak K wpływa na dokładność aproksymacji? Porównaj z dokładnością dla N=4.
3. Przed aukcją wykonaj etap tworzenia koalicji: agenci mogą łączyć się w zespoły i licytować jako całość. Jakie koalicje tworzą? Czy wynik w Pareto jest lepszy niż indywidualna licytacja?
4. Przeczytaj post dotyczący projektu mechanizmu Google Research. Wskaż jedno założenie, którego naruszenie łamie prawdziwość. Jak wygląda ten tryb awarii w ustawieniu LLM?
5. Przeczytaj zdecentralizowany dokument LaMAS AAMAS 2025. Wykonaj krok Shapleya na 10 agentach w ramach zadania syntetycznego. Ile czasu zajmują dokładne obliczenia? Jak blisko jest próbkowanie przy 100 losowaniach?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| DePIN | „Zdecentralizowana infrastruktura fizyczna” | Obliczenia/przechowywanie/przepustowość oparte na tokenach. Bittensor, Akash, Render. |
| CZY | „Zdecentralizowany identyfikator” | Specyfikacja W3C dla przenośnych identyfikatorów. Reputacja agenta jest związana z DID, a nie z platformą. |
| ERC-4337 | „Atrakcja konta” | Konta kontraktowe, które mogą sponsorować gaz, umożliwiając płatności agentom. |
| Wartość Shapleya | „Uczciwe przypisanie kredytu” | Unikalna alokacja spełniająca efektywność, symetrię, liniowość, zero. |
| Aukcja drugiej ceny | „Aukcja Vickreya” | Mechanizm zgodny z prawdą: zwycięzca płaci drugą najwyższą ofertę. Kompatybilny z agregacją monotonną. |
| Kapitał reputacji | „Skumulowany wynik jakości” | Wynik powiązany z DID na podstawie potwierdzonych wkładów; zanika z biegiem czasu. |
| Agent DAO | „Agenci + ludzie rządzą” | DAO z wyborcami-agentami jako pierwszej klasy, siła głosu powiązana z reputacją. |
| Kredyty TAO / FET / GPU | „Nominały żetonowe” | Bittensor TAO, Fetch.ai FET, różne tokeny DePIN. |

## Dalsze czytanie

– [Gospodarka agentów](https://arxiv.org/abs/2602.14219) — badanie z 2026 r. dotyczące 5-warstwowego stosu gospodarki agentów
- [Google Research — Projektowanie mechanizmów dla dużych modeli językowych](https://research.google/blog/mechanism-design-for-large-language-models/) — aukcje tokenów z agregacją monotonną
- [AAMAS 2025 — zdecentralizowany LaMAS](https://www.ifaamas.org/Proceedings/aamas2025/pdfs/p2896.pdf) — przypisanie kredytu według wartości Shapleya
- [Dokumentacja Bittensor TAO](https://docs.bittensor.com/) — struktura podsieci i dystrybucja nagród
- [Fetch.ai / ASI Alliance](https://fetch.ai/) — ASI-1 Mini LLM i token FET
- [Specyfikacja zdecentralizowanych identyfikatorów W3C (DID)](https://www.w3.org/TR/did-core/) — podstawa tożsamości