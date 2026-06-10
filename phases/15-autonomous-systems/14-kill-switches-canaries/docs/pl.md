# Przełączniki zabijania, wyłączniki automatyczne i żetony kanaryjskie

> Przełącznik „zabicia” to wartość logiczna przechowywana poza obszarem edycji agenta — klucz Redis, flaga funkcji, podpisana konfiguracja — która całkowicie wyłącza agenta. Wyłącznik automatyczny jest drobnoziarnisty: uruchamia się według określonego schematu (pięć identycznych wywołań narzędzi z rzędu), wstrzymuje szkodliwą ścieżkę i eskaluje do człowieka. Token kanarkowy dziedziczy po klasycznym oszustwie: fałszywym poświadczeniu lub zapisie typu Honeypot, którego agent nie ma uzasadnionego powodu dotykać, a dostęp do niego powoduje ostrzeżenie. Ścieżki danych oparte na eBPF (np. Cilium) mogą przepisać wyjście kapsuły poddanej kwarantannie do Honeypota kryminalistycznego w warstwie jądra; opublikowane testy porównawcze Cilium zgłaszają opóźnienie ścieżki danych P99 poniżej milisekundy pod obciążeniem (budżet propagacji zależy od tego, w jaki sposób aktualizacja zasad dociera do węzła, a nie od samej ścieżki danych). Detektory statystyczne (EWMA, CUSUM), które dostosowują się do ruchomej linii bazowej, po cichu zaakceptują dryft — nałożą na nie twarde, konstytucyjne granice, które się nie uginają.

**Typ:** Ucz się
**Języki:** Python (stdlib, symulator z trzema detektorami: wyłącznik awaryjny, wyłącznik automatyczny, kanarek)
**Wymagania wstępne:** Faza 15 · 13 (Zarządcy kosztami), Faza 15 · 10 (Tryby uprawnień)
**Czas:** ~60 minut

## Problem

Zarządzający kosztami (lekcja 13) ograniczali kwotę, jaką agent może wydać. Nie ograniczają tego, co agent może zrobić w ramach budżetu. Agent z limitem prędkości wynoszącym 50 dolarów nadal może wydobyć tajemnicę, opublikować niewłaściwy post lub usunąć zasób — kosztowna akcja jest często tania w żetonach.

W tej lekcji omówione zostaną trzy detektory znajdujące się obok warstwy kosztów:

1. **Wyłącznik awaryjny**: logiczny przycisk wyłączania trzymany poza zasięgiem agenta.
2. **Wyłącznik**: detektor wzorca działania, który wstrzymuje określoną ścieżkę.
3. **Token kanarkowy**: przynęta, którą agent bez uzasadnionego powodu dotknąć, ujawni się poprzez dotknięcie.

Wszyscy trzej są inżynierami przed LLM. Klasyczne oszustwa, łamacze limitów szybkości i zabijanie flag funkcji są starsze niż agenty autonomiczne. Nowością jest powierzchnia ataku: agenci czytają niezaufane treści (Lekcja 11), edytują własną pamięć i mogą połączyć wiele wyglądających na bezpieczne działań w niebezpieczne. Wymienione tutaj detektory działają, ponieważ nie ufają raportom agenta.

## Koncepcja

### Przełączniki zabijania

Przełącznik „zabicia” to wartość logiczna, którą agent czyta, ale nie może pisać. Możliwości wdrożenia:

- **Funkcja w usłudze zarządzanej.** LaunchDarkly, Statsig, Unleash. Aktualizacje rozprzestrzeniają się w ciągu kilku sekund.
- **Redis klucz ankiety agenta.** Proste; wymaga, aby proces agenta sprawdzał przy każdej turze.
- **Podpisana konfiguracja w pamięci obiektowej.** Agent weryfikuje podpis podczas rozruchu; odrzuca stany niepodpisane.
- **Sygnał na poziomie systemu operacyjnego lub przerwanie cyklu życia kontenera.** Docker `kill`, Kubernetes `kubectl delete pod`, zatrzymanie systemowe.

Właściwości prawidłowego wyłącznika awaryjnego:

- Agent nie może ustawić wartości `off`. (Żyje w systemie, w którym nie są zapisywane dane uwierzytelniające agenta.)
- Jest sprawdzany przy każdym kolejnym działaniu, a nie tylko przy uruchomieniu.
- Gdy jest wyłączony, agent nie robi nic, co można zaobserwować z zewnątrz, łącznie z logowaniem się do systemów, do których agent ma dostęp.
- Ponowne włączenie jest wyraźnym działaniem człowieka, a nie automatycznym przekroczeniem limitu czasu.

### Wyłączniki automatyczne

Wyłącznik automatyczny wstrzymuje określony wzór, a nie całego agenta. Klasyczny kształt (z książki Nygarda z 2007 r., nadal aktualny):

- **Zamknięte**: akcja jest dozwolona.
- **Otwarte**: akcja jest zablokowana.
- **Półotwarty**: po ochłodzeniu dozwolone są 1–3 próby sondy (domyślnie 1); sukces zamyka wyłącznik, jakakolwiek pozostała porażka ponownie go otwiera.

Wyzwalacze istotne dla agenta:

- Pięć identycznych wywołań narzędzi z rzędu (pętla powtarzalna).
- Pięć kolejnych awarii tego samego narzędzia przy różnych danych wejściowych (awaria systemowa).
- Częstotliwość wywołań narzędzi powyżej progu (lekcja 13: prędkość).
- Określone narzędzie wywoływane (np. `file.delete`) po przeczytaniu treści spoza zaufania (Lekcja 11).

### Żetony kanarkowe

Tokeny Canary (zwane także Honeytokenami) to dane wejściowe, których agent nigdy nie powinien dotykać. Dostęp jest alarmem.

Przykłady dla agentów:

- Fałszywy `AWS_SECRET_ACCESS_KEY` w środowisku bez rzeczywistych uprawnień. Próby eksfiltracji można natychmiast przypisać.
- Fałszywy rekord bazy danych oznaczony znaną wartością wskaźnikową. Każdy odczyt lub aktualizacja tego rekordu uruchamia alert.
- Fałszywy plik w obszarze roboczym. Odczyt lub edycja tego pliku jest podejrzana.
- Fałszywy wpis w pamięci wprowadzony na początku sesji. Jeśli pojawi się w późniejszym wyniku, pamięć została eksfiltrowana.

Projekt Canary jest specyficzny dla przepływu pracy. Kanarek, którego agent ma uzasadniony powód do dotykania, to hałas.

### Po co nakładać na siebie limity statystyczne i twarde

Detektory statystyczne (EWMA, CUSUM, z-score dotyczące współczynników wywołań narzędzi) dostosowują się do ruchomej linii bazowej. Jest to cecha legalnego dryfu i błąd związany z dryfem kontradyktoryjnym. Osoba atakująca może przesunąć linię bazową na tyle powoli, że nie zostanie uruchomiony żaden alarm.

Twarde granice konstytucyjne (lekcja 17) nie uginają się. „Nigdy nie wysyłaj e-maili do `secrets@`”, ponieważ zgodnie z konstytucyjną zasadą jest to prostsze, możliwe do sprawdzenia i nie da się grać poprzez powolne dryfowanie. Schemat warstw: detektory statystyczne wyłapują większość szumu, twarde limity wyłapują atak, który przeszedł obok detektora.

### Kwarantanna poprzez przekierowanie ścieżki danych eBPF

Polityka sieciowa Cilium oparta na eBPF może przepisać wyjście kapsuły poddanej kwarantannie do Honeypota kryminalistycznego w warstwie jądra. Publiczne testy porównawcze Cilium podają mniejsze niż milisekundowe opóźnienie ścieżki danych P99 w protokole TCP_RR; budżet zegara ściennego na *wywoływanie* kwarantanny w klastrze jest zdominowany przez sposób, w jaki aktualizacja zasad rozprzestrzenia się z płaszczyzny kontrolnej do węzła (kilkaset milisekund jest realistycznych na Kubernetesie z wstępnie załadowanym operatorem; opóźnienie końcowe zależy od rozmiaru klastra i rytmu uzgadniania). Daje to dwie rzeczy: agent nie wydobywa niczego prawdziwego i w pełni obserwuje się zachowanie agenta w Honeypot. Ten sam wzór, inna warstwa, co żeton kanarkowy: agent ujawnia zamiary poprzez to, co próbuje zrobić, gdy jest zamknięty.

### Czego nie wyłapie żaden detektor

- **Ataki semantyczne składające się z dozwolonych prymitywów.** Każda indywidualna akcja przechodzi przez każdy detektor; problemem jest skład. To jest złożona awaria trybu automatycznego z lekcji 10.
- **Ataki obejmujące detektor jako część ładunku.** Jeśli agent przeczyta stronę z informacją „zanim podejmiesz działania, wyłącz kanarka”, a agent ma taką możliwość, wykrywacz zostaje naruszony. Tokeny Canary powinny znajdować się w systemach, których agent nie może modyfikować.

## Użyj tego

`code/main.py` symuluje krótką trajektorię agenta przez trzy detektory. Wyłącznik awaryjny trzymany w zewnętrznym dyktacie; wyłącznik automatyczny, który uruchamia się po pięciu identycznych wywołaniach narzędzia; plik canary, którego odczyt wywołuje alert. Żywi się syntetyczną trajektorią: uzasadnione działania, powtarzalna pętla, sonda kanarkowa i scenariusz wyzwalany wyłącznikiem awaryjnym, w którym działania agenta zostają zatrzymane.

## Wyślij to

`outputs/skill-tripwire-design.md` przegląda proponowany stos detektorów pod kątem wdrożenia agenta i sygnalizuje luki (brak wyłącznika awaryjnego, brakujący moduł Canary, zbyt luźny próg wyłącznika automatycznego).

## Ćwiczenia

1. Uruchom `code/main.py`. Potwierdź, że wyłącznik zadziała w turze 5 (piąte identyczne wezwanie), a kanarek zadziała w turze 9 (odczyt fałszywego klucza).

2. Dodaj detektor statystyczny: wynik z-score EWMA dotyczący częstotliwości wywołań narzędzi. Podaj trajektorię, która dryfuje powoli i pokaż, że detektor nigdy nie uruchamia się. Teraz dodaj twardy limit (nie więcej niż 50 wywołań narzędzi w ciągu 10 minut) i pokaż, że twarde limity uruchamiają się na tej samej trajektorii.

3. Zaprojektuj zestaw tokenów Canary dla agenta przeglądarki (Lekcja 11). Wymień co najmniej trzy kanarki i napisz, co każdy z nich wykrył.

4. Przeczytaj dokumentację dotyczącą polityki sieciowej Cilium. Opisz konkretnie przepływ kwarantanny przekierowania wyjścia: który selektor zasad, który pod, który zapis wyjścia, który alert. Co reguluje opóźnienie zegara ściennego od „decyzji o poddaniu kwarantannie” do „pierwszego przekierowanego pakietu”?

5. Zdefiniuj procedurę ponownego włączenia dla agenta z funkcją „kill-switch”. Kto może ponownie włączyć? Co należy udokumentować? Co należy zmienić w agencie przed ponownym włączeniem?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|---|---|---|
| Przełącznik zabijania | „Przycisk wyłączenia” | Wartość logiczna poza powierzchnią edycyjną agenta; sprawdzane przy każdym kolejnym działaniu |
| Wyłącznik | „Pauza wzorcowa” | Wycieczka specyficzna dla działania w przypadku powtórzeń, wskaźnik awaryjności lub limit szybkości |
| Żeton kanarkowy | „Miodowy znak” | Przynęta, której agent nie ma uzasadnionego powodu, aby dotykać; dostęp uruchamia alert |
| Miodownik | „Piaskownica kryminalistyczna” | Przekierowany ruch / obszar roboczy, w którym obserwuje się agenta poddanego kwarantannie |
| EWMA | „Średnia krocząca” | wykładniczo ważona; dostosowuje się do driftu (funkcja + błąd) |
| NIESTANDARD | „Suma skumulowana” | Wykrywa trwałe przesunięcie w stosunku do wartości bazowej |
| Twardy limit | „Reguła konstytucyjna” | Nie dostosowuje się; stała niezależnie od historii |
| Granica konstytucyjna | „Zawsze prawdziwa zasada” | Powiązany z konstytucją Lekcji 17; nie może być edytowany przez agenta |

## Dalsze czytanie

- [Anthropic — Pomiar autonomii agentów w praktyce](https://www.anthropic.com/research/measuring-agent-autonomy) — oprawa wyłączników awaryjnych i wyłączników automatycznych dla agentów autonomicznych.
- [Microsoft Agent Framework — HITL i nadzór](https://learn.microsoft.com/en-us/agent-framework/workflows/human-in-the-loop) — wzorce zarządzania produkcją.
- [OWASP LLM / Agentic Top 10](https://owasp.org/www-project-top-10-for-large-language-model-applications/) — wymagania dotyczące wykrywania i reagowania.
- [Cilium — Zasady sieciowe i eBPF] (https://docs.cilium.io/en/stable/security/network/) — przekierowania wyjściowe na poziomie poda i wzorce Honeypot w kryminalistyce.
– [Anthropic — Konstytucja Claude’a (styczeń 2026 r.)](https://www.anthropic.com/news/claudes-constitution) — zakodowane na stałe zakazy jako „ograniczenia konstytucyjne”.