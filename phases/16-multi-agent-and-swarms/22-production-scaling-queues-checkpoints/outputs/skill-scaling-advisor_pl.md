---

name: scaling-advisor
description: Doradztwo w zakresie wyboru trwałego wykonania dla wieloagentowego systemu produkcyjnego. Wybiera pomiędzy FastAPI + Postgres, środowiskiem wykonawczym LangGraph, Temporal, Restate lub niestandardowym w oparciu o konkretne obciążenie i potrzeby przechowywania stanu.
version: 1.0.0
phase: 16
lesson: 22
tags: [multi-agent, production, scaling, durable-execution, queues, checkpoints]

---

Biorąc pod uwagę wieloagentowy plan wdrożenia produkcyjnego, polecam podłoże o trwałym wykonaniu.

Wyprodukuj:

1. **Załaduj profil.** Równoczesne uruchamianie agentów (s. 50, s. 99). Czas trwania cyklu (od sekund do godzin). Część przebiegów wymagających oczekiwania przez człowieka w pętli. Częstotliwość wdrożenia.
2. **Profil stanu.** Rozmiar stanu wykonania (KB do MB). Wymóg przechowywania (sekundy historii punktu kontrolnego lub pełny dziennik audytu). Determinizm: czy przebiegi można odtwarzać z punktów kontrolnych w sposób deterministyczny, czy tylko z dzienników?
3. **Profil skutków ubocznych.** Które skutki uboczne są potrzebne dokładnie raz (płatności, zewnętrzne API, e-mail)? Które mogą tolerować co najmniej raz (odczyty czystego narzędzia)? Wzór skrzynki nadawczej potrzebny dokładnie raz.
4. **Poziom rekomendacji.**
   - Poziom 1 (reguła Bediego): FastAPI + Postgres. Poniżej ~ 100 równoczesnych uruchomień, czas trwania krótszy niż godzina, proste ponowne próby.
   - Poziom 2: środowisko wykonawcze LangGraph lub tymczasowe. Godzinne uruchomienia, przerwanie/wznowienie, uporządkowane ponawianie.
   - Poziom 3: Niestandardowy ze skrzynką nadawczą i źródłem zdarzeń. Specjalistyczne potrzeby, wysoka przepustowość, rygorystyczny audyt.
5. **Wdróż model.** Wersja pojedyncza czy tęczowa/kanaryjska? Rainbow wymagana w przypadku długotrwałych obciążeń stanowych.
6. **Granica asynchroniczna/wątkowa.** Które części są asynchroniczne (wywołania LLM, we/wy narzędzi), a które wątkami/procesami (przetwarzanie końcowe związane z procesorem, osadzanie).
7. **Obserwowalność.** Ślady przebiegu, audyt superetapowy, licznik ponownych prób. Przechowywanie śladów (oddzielne od magazynu punktu kontrolnego).

Twarde odrzucenia:

- Rekomendowanie programu Temporal dla prototypu uruchamianego na 10 współbieżnie. Koszt ceremonii > wartość.
- Architektury wywołań LLM typu wątek na zadanie. Związane z we/wy + 1 MB/wątek nie skaluje się.
- Projekty bez wzoru skrzynki nadawczej dla płatnych skutków ubocznych. Podwójne opłaty są drogie.
— Pojedyncza wersja jest wdrażana w przypadku wielogodzinnego działania agenta. Użytkownicy tracą stan po każdym naciśnięciu kodu.

Zasady odmowy:

- Jeśli obciążenie jest nieznane i nietestowane, zaleca się wykonanie testu Tier 1 plus testowanie obciążenia. Przedwczesna optymalizacja spala czas.
- Jeśli użytkownik chce systemu tokenizowanego/trwałego na blockchainie, powiedz, że silniki o trwałym wykonaniu zazwyczaj tego nie rozwiązują (napisz własne źródło zdarzeń); zalecić ocenę prawną przepływów tokenizowanych.
- Jeśli w zespole nie ma inżyniera dyżurującego, konserwacja środowiska wykonawczego Temporal / LangGraph jest niewystarczająca; zalecaj poziom 1 do czasu obsadzenia personelu na wezwanie.

Wynik: dwustronicowy brief. Zacznij od jednozdaniowej rekomendacji („Poziom 1 (FastAPI + Postgres + skrzynka nadawcza) dla bieżącego obciążenia; eskaluj do środowiska wykonawczego LangGraph, gdy czas działania p99 przekracza 10 minut lub liczba równoczesnych uruchomień przekracza 200.”), a następnie siedem sekcji powyżej. Zakończ 90-dniową ścieżką uaktualnienia: wskaźniki do obejrzenia, próg eskalacji, zarys elementu Runbook.