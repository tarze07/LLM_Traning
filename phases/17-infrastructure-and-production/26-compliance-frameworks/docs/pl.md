# Zgodność — SOC 2, HIPAA, RODO, PCI-DSS, ustawa UE o sztucznej inteligencji, ISO 42001

> Zasięg wielu platform to stawka w tabeli transakcji dla przedsiębiorstw na rok 2026. **Ustawa EU AI**: obowiązuje od 1 sierpnia 2024 r. Większość wymogów wysokiego ryzyka obowiązuje od 2 sierpnia 2026 r. Kary do 15 mln euro lub 3% całkowitego rocznego obrotu za zobowiązania systemowe wysokiego ryzyka (art. 99 ust. 4); do 35 mln euro lub 7% za zabronione praktyki AI (art. 99 ust. 3). Ma zastosowanie globalnie, jeśli obsługuje użytkowników z UE. **Ustawa Colorado AI**: obowiązuje od 30 czerwca 2026 r. (opóźniona z lutego 2026 r. przez SB25B-004) – oceny skutków dla systemów wysokiego ryzyka, prawo do odwołania się od decyzji AI. Virginia podobnie pod względem kredytów/zatrudnienia/mieszkania/edukacji. **SOC 2 Typ II**: de facto wymóg B2B AI (typ II, a nie typ I, dla fintech). **RODO**: największa udokumentowana kara za sztuczną inteligencję wynosi 30,5 mln euro nałożona na Clearview AI (holenderski DPA, wrzesień 2024 r.); Włoska firma Garante wydała 15 mln euro przeciwko OpenAI w grudniu 2024 r. (później unieważniona w wyniku odwołania w marcu 2026 r.). Redakcja informacji umożliwiających identyfikację w czasie rzeczywistym przy wnioskowaniu jest standardem, którego można obronić; czyszczenie po przetwarzaniu nie wystarczy. **HIPAA**: związana z opieką zdrowotną — nie można wysyłać PHI do zewnętrznych usług AI bez BAA. **PCI-DSS**: pokrycie warstwy interakcji AI wymaga konfiguracji + ustaleń umownych, a nie automatycznego. **ISO 42001**: powstający standard zarządzania sztuczną inteligencją, rosnące wymagania dotyczące zamówień zgodnie z ISO 27001. Profil referencyjny: OpenAI utrzymuje SOC 2 typ 2, ISO/IEC 27001:2022, ISO/IEC 27701:2019, RODO/CCPA/HIPAA (BAA)/FERPA, PCI-DSS dla komponentów płatniczych ChatGPT. Mapowanie międzyplatformowe zmniejsza zmęczenie audytem: mapa kontroli dostępu w ramach ISO 27001 A.5.15-5.18, art. 32, HIPAA §164.312(a).

**Typ:** Ucz się
**Języki:** (opcjonalnie Python — zgodność to polityka + proces, a nie kod)
**Wymagania wstępne:** Faza 17 · 25 (Bezpieczeństwo), Faza 17 · 13 (Obserwowalność)
**Czas:** ~60 minut

## Cele nauczania

- Wymień siedem ram na rok 2026 istotnych dla produktów LLM i dopasuj każdy do segmentu klienta.
– Należy podać harmonogram egzekwowania unijnej ustawy o sztucznej inteligencji (obowiązujący od sierpnia 2024 r.; egzekwowanie przepisów wysokiego ryzyka od sierpnia 2026 r.) i dwupoziomowy pułap kar (15 mln EUR / 3% w przypadku zobowiązań wysokiego ryzyka, 35 mln EUR / 7% w przypadku zabronionych praktyk).
- Wyjaśnij, dlaczego czyszczenie danych osobowych po przetwarzaniu końcowym nie wystarczy w przypadku RODO i wskaż redakcję warstwy wnioskowania w czasie rzeczywistym jako możliwy do obrony standard.
- Opisać międzyplatformowe mapowanie kontroli (np. mapy kontroli dostępu zgodnie z ISO 27001 A.5.15-5.18 + RODO art. 32 + HIPAA §164.312(a)).

## Problem

Zamówienie klienta korporacyjnego wymaga SOC 2 typu II, RODO, HIPAA BAA, ISO 27001 i „Oświadczenia o zgodności z ustawą UE o sztucznej inteligencji”. Twój zespół ma SOC 2 typu I. Minęło sześć miesięcy od typu II i nie rozpocząłeś jeszcze rejestracji na podstawie art. 30 RODO.

Zasięg wielu platform nie jest problemem LLM — jest to problem SaaS dla przedsiębiorstw z nakładkami specyficznymi dla LLM. Zespoły ds. zakupów w 2026 r. będą chciały macierzy z wierszem na platformę i kolumną na kontrolkę, a nie pliku PDF.

## Koncepcja

### Siedem struktur

| Ramy | Zakres | Wymagania specyficzne dla LLM |
|----------|-------|---------------|
| SOC 2 Typ II | Bazowy model B2B SaaS | Kontrole procesów audytowane przez 6-12 miesięcy |
| HIPAA | Opieka zdrowotna w USA | wymagane BAA; PHI nie może opuścić infrastruktury bez podpisanej umowy |
| RODO | Użytkownicy z UE | Redagowanie informacji umożliwiających identyfikację w czasie rzeczywistym; prawa osób, których dane dotyczą; Artykuł 30 rejestruje |
| PCI-DSS | Dane dotyczące płatności | Konfiguracja + umowy na AI dotykające płatności |
| Ustawa UE o sztucznej inteligencji | Obsługa użytkowników z UE | Klasyfikacja poziomów ryzyka; systemy wysokiego ryzyka: ocena zgodności, dokumentacja, logowanie |
| Ustawa o sztucznej inteligencji stanu Kolorado | Obsługa mieszkańców CO | oceny skutków; prawo do odwołania |
| ISO 42001 | Zarządzanie sztuczną inteligencją | Pojawiające się; pary z ISO 27001 |

### Harmonogram unijnej ustawy o sztucznej inteligencji

- 1 sierpnia 2024 r.: obowiązuje.
- 2 lutego 2025 r.: egzekwowanie zakazanych praktyk związanych ze sztuczną inteligencją.
- 2 sierpnia 2026 r.: wdrożono systemy wysokiego ryzyka (ocena zgodności, dokumentacja, logowanie).
- sierpień 2027 r.: systemy wysokiego ryzyka w produktach objętych zharmonizowanym prawodawstwem.

Poziomy ryzyka: Niedopuszczalne (zakazane), Wysokie ryzyko (zgodność + rejestrowanie), Ograniczone ryzyko (przejrzystość), Minimalne ryzyko (brak ograniczeń). Większość usług B2B LLM SaaS wiąże się z ograniczonym ryzykiem; Wysokie ryzyko pojawia się w przypadku zatrudnienia, kredytów, edukacji, egzekwowania prawa, migracji i podstawowych usług.

Kary (art. 99): do 15 mln euro lub 3% całkowitego rocznego obrotu za naruszenie obowiązków systemowych wysokiego ryzyka (art. 99 ust. 4); do 35 mln euro lub 7% za zabronione praktyki AI (art. 99 ust. 3); w zależności od tego, która wyższa wartość ma zastosowanie.

### RODO — redakcja w czasie rzeczywistym to standard

Oczyszczanie po przetwarzaniu (redagowanie danych osobowych po zobaczeniu ich przez LLM) nie jest postawą, której można obronić — model już widział dane. Redakcja warstwy wnioskowania w czasie rzeczywistym to standard na rok 2026:

- Rozpoznawanie podmiotu przed wywołaniem LLM.
- Spójna tokenizacja (podejście Mesh) pozwala zachować semantykę.
- Przechowuj tylko zredagowane podpowiedzi i zgodę na surową zgodę.

Niedawne egzekwowanie prawa: 30,5 mln euro przeciwko Clearview AI (holenderski DPA, wrzesień 2024 r.) to największa jak dotąd udokumentowana kara za RODO dotycząca sztucznej inteligencji; 15 mln euro nałożone na OpenAI (włoska Garante, grudzień 2024 r.) to największa kara nałożona na LLM, chociaż została uchylona w wyniku odwołania w marcu 2026 r., a orzeczenie pozostaje w trakcie dalszego przeglądu. Roszczenia po przetworzeniu nie powiodły się podczas audytu.

### HIPAA — BAA nie jest opcjonalne

Nie można wysyłać PHI do zewnętrznych usług AI bez podpisanej umowy o partnerstwie biznesowym. Wszystkie trzy hiperskalowalne platformy LLM (Bedrock, Azure OpenAI, Vertex) oferują BAA. Bezpośrednie API OpenAI oferuje BAA. Anthropic direct API oferuje BAA. Potwierdź przed wysłaniem PHI.

### SOC 2 Typ II

Typ I: kontrole zaprojektowane i udokumentowane.
Typ II: kontrole działają skutecznie przez 6-12 miesięcy.

Zamówienia B2B w 2026 r. domyślnie będą typu II. Typ I to starter; Typ II to brama.

Typowe czynniki audytu: dzienniki dostępu (kto co widział), zarządzanie zmianami (w jaki sposób zostało wdrożone), ocena ryzyka (co kwartał), reakcja na incydenty (przetestowana?). Dziennik audytu z fazy 17 · 25 można bezpośrednio wykorzystać ponownie.

### Mapowanie między platformami

Jedna polityka kontroli dostępu spełnia wiele kontroli struktury:

| Kontrola | Ramy |
|--------|-----------|
| Rejestrowanie dostępu | ISO 27001 A.5.15-5.18, RODO art. 32, HIPAA §164.312(a) |
| Zarządzanie zmianami | ISO 27001 A.8.32, wymagania PCI DSS 6, Zakres powiadomień o naruszeniu ustawy HIPAA |
| Szyfrowanie w transporcie | ISO 27001 A.8.24, RODO art. 32, HIPAA §164.312(e) |
| Zarządzanie tajemnicami | ISO 27001 A.8.19, wymagania PCI DSS 8, SOC 2 CC6.1 |

Narzędzia zgodności (Drata, Vanta, Secureframe) automatyzują to mapowanie. Warte swojej ceny w skali.

### ISO 42001 — wschodzące

Opublikowano pod koniec 2023 r. Rosnące wymagania dotyczące zamówień zgodnie z normą ISO 27001. Ramy zarządzania sztuczną inteligencją, w tym zarządzanie ryzykiem, jakość danych, przejrzystość i nadzór ludzki.

### Profil referencyjny OpenAI

OpenAI utrzymuje SOC 2 typ 2, ISO/IEC 27001:2022, ISO/IEC 27701:2019, RODO/CCPA/HIPAA (BAA)/FERPA, PCI-DSS dla komponentów płatniczych ChatGPT. To mniej więcej stawka dla przedsiębiorstw w 2026 r.

### Liczby, które powinieneś zapamiętać

- Kary wynikające z ustawy UE o sztucznej inteligencji: do 15 mln euro / 3% (obowiązki wysokiego ryzyka, art. 99 ust. 4); do 35 mln € / 7% (praktyki zabronione, art. 99 ust. 3).
- Egzekwowanie przepisów UE o wysokim ryzyku związanych z ustawą o sztucznej inteligencji: 2 sierpnia 2026 r.
– Największa udokumentowana kara za RODO dotycząca sztucznej inteligencji: 30,5 mln euro, Clearview AI (holenderski DPA, wrzesień 2024 r.).
– Największa kara za RODO za LLM: 15 mln euro, OpenAI (Włoska Garante, grudzień 2024 r.; unieważniona w wyniku odwołania w marcu 2026 r.).
- Okno SOC 2 Typ II: 6-12 miesięcy obsługi sterowań.
- Data wejścia w życie ustawy Colorado AI Act: 30 czerwca 2026 r. (opóźniona z lutego 2026 r. przez SB25B-004).

## Użyj tego

`code/main.py` to arkusz kalkulacyjny mapujący zgodność w Pythonie — po uzyskaniu kontroli wyświetla listę platform, które spełnia.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-compliance-matrix.md`. Biorąc pod uwagę segment klientów i lokalizację geograficzną, określa wymagane ramy i kontrole.

## Ćwiczenia

1. Twój pierwszy klient korporacyjny wymaga oświadczenia SOC 2 typu II, HIPAA BAA, EU AI Act. Jaki jest minimalny możliwy poziom zgodności, aby wygrać transakcję?
2. Sklasyfikuj trzy hipotetyczne produkty LLM według poziomów ryzyka wynikających z ustawy UE o sztucznej inteligencji. Jakie zmiany przy wysokim ryzyku?
3. Przypadkowo wysłałeś PHI do dostawcy bez BAA. Zapoznaj się z reakcją na incydent.
4. Uzasadnij, czy norma ISO 42001 jest „konieczna w 2026 r.” dla dostawcy sztucznej inteligencji średniej wielkości.
5. Zmapuj pola dziennika audytu LLM (faza 17 · 25) na co najmniej trzy kontrole struktury.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| SOC 2 Typ II | „kontrole skontrolowane” | Kontrole działające przez okres 6-12 miesięcy, niezależnie poświadczone |
| HIPAA BAA | „umowa o opiekę zdrowotną” | Umowa o współpracy biznesowej; wymagane dla PHI |
| RODO | „Prywatność UE” | Redagowanie informacji umożliwiających identyfikację w czasie rzeczywistym to możliwy do obrony standard na rok 2026 |
| Ustawa UE o sztucznej inteligencji | „Przepisy UE dotyczące sztucznej inteligencji” | Egzekwowanie przepisów o wysokim ryzyku, sierpień 2026 r.; 15 mln euro / 3% (obowiązki wysokiego ryzyka) — 35 mln euro / 7% (praktyki zabronione) |
| Ustawa o sztucznej inteligencji stanu Kolorado | „Prawo stanowe USA dotyczące AI” | Obowiązuje od 30 czerwca 2026 r. (opóźnienie przez SB25B-004); oceny skutków |
| ISO 42001 | „Zarządzanie sztuczną inteligencją” | Powstające ramy dotyczące ryzyka związanego ze sztuczną inteligencją + przejrzystość |
| ISO 27001 | „SZBI bezpieczeństwa” | Podstawowe informacje o Systemie Zarządzania Bezpieczeństwem Informacji |
| Ocena zgodności | „Pakiet dokumentów UE dotyczących sztucznej inteligencji” | Wymóg wysokiego ryzyka: dokumentacja, testowanie, rejestrowanie |
| Mapowanie między platformami | „jedna kontrola, wiele klatek” | Pojedyncza polityka spełnia wiele kontroli ramowych |

## Dalsze czytanie

- [OpenAI Security and Privacy](https://openai.com/security-and-privacy/) — referencyjny profil zgodności.
- [GuardionAI — zgodność LLM 2026: ISO 42001, ustawa UE o sztucznej inteligencji, SOC 2, RODO](https://guardion.ai/blog/llm-compliance-guide-iso-42001-eu-ai-act-soc2-gdpr-2026)
– [Dsalta — Przewodnik audytu typu 2 SOC 2 2026: 10 kontroli AI](https://www.dsalta.com/resources/ai-compliance/soc-2-type-2-audit-guide-2026-10-ai-powered-controls-every-saas-team-needs)
– [oficjalny tekst unijnego aktu o sztucznej inteligencji](https://eur-lex.europa.eu/eli/reg/2024/1689/oj) – źródło pierwotne.
– [Ustawa Kolorado o sztucznej inteligencji](https://leg.colorado.gov/bills/sb24-205) – źródło główne.
- [ISO/IEC 42001:2023](https://www.iso.org/standard/81230.html) – norma dotycząca systemu zarządzania sztuczną inteligencją.