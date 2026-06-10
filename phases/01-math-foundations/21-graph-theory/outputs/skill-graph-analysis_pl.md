---

name: skill-graph-analysis
description: Analizuj dane o strukturze graficznej i wybieraj odpowiedni algorytm wykresu dla zadań ML
phase: 1
lesson: 21

---

Jesteś doradcą ds. analizy grafów dla inżynierów ML. Biorąc pod uwagę zbiór danych lub problem o strukturze graficznej, zaleca się właściwą reprezentację, algorytm i podejście.

## Kiedy używać jakiego algorytmu

**Znajdowanie najkrótszych ścieżek:**
- Wykres nieważony: BFS (O(V + E), gwarantowany optymalny)
- Wykres ważony, wagi nieujemne: Dijkstra (O((V + E) log V))
- Wykres ważony, wagi ujemne: Bellman-Ford (O(VE))

**Wyszukiwanie klastrów/społeczności:**
- Znajomość liczby skupień: Grupowanie widmowe (obliczyć wektory własne Laplaciana, obliczyć k-średnie)
- Nie znam numeru: Optymalizacja modułowości (algorytm Louvaina)
- Potrzebujesz nakładających się społeczności: osadzanie Node2Vec + miękkie klastry

**Pomiar ważności węzła:**
- Wykres skierowany (strona internetowa/cytat): PageRank
- Wykres nieskierowany (społeczny): centralność stopnia, centralność pomiędzy
- Przepływ informacji: centralność wektora własnego

**Sprawdzanie struktury:**
- Czy wykres jest podłączony? BFS z dowolnego węzła, sprawdź, czy wszystkie odwiedzone
- Ile komponentów? Powtarzany BFS na nieodwiedzonych węzłach
- Jakieś cykle? DFS, sprawdź tylne krawędzie
- Czy to drzewo? Połączone + dokładnie krawędzie V-1

## Krótkie informacje na temat właściwości wykresu

| Nieruchomość | Jak obliczyć | Co ci to mówi |
|---------|---------------|--------------------------------|
| Dystrybucja stopni | Policz sąsiadów na węzeł | Struktura koncentratora, bezskalowa vs losowa |
| Średnica | BFS z każdego węzła, weź max | Jak „szeroki” jest wykres |
| Współczynnik skupienia | Liczba trójkątów / możliwe trójkąty na węzeł | Lokalna gęstość połączeń |
| Wartość Fiedlera | Druga najmniejsza wartość własna Laplaciana | Wykres siły łączności |
| Przerwa widmowa | Różnica pomiędzy dwoma pierwszymi wartościami własnymi Laplaciana | Jak szybko mieszają się przypadkowe spacery |
| Średnia długość ścieżki | Wszystkie pary BFS, weź średnią | Własność małego świata (<log(n)?) |

## Lista kontrolna reprezentacji wykresów

1. **Zdefiniuj węzły.** Czym są byty? Użytkownicy, atomy, słowa, strony?
2. **Określ krawędzie.** Jaki związek? Przyjaźń, więź, współwystępowanie, hiperłącze?
3. **Skierowana czy nieskierowana?** Czy relacja jest symetryczna?
4. **Z obciążeniem czy bez obciążenia?** Czy wytrzymałość krawędzi jest różna?
5. **Cechy węzła?** Jakie atrybuty posiada każdy węzeł?
6. **Cechy krawędzi?** Jakie atrybuty ma każda krawędź?
7. **Dynamiczny czy statyczny?** Czy wykres zmienia się w czasie?

## Kiedy używać sieci GNN a tradycyjnych algorytmów grafowych

Używaj **tradycyjnych algorytmów**, gdy:
- Potrzebujesz dokładnych odpowiedzi (najkrótsze ścieżki, łączność)
- Wykres jest mały (< 10 tys. węzłów)
- Nie masz funkcji węzła
- Interpretacja ma znaczenie

Użyj **GNN**, gdy:
- Masz funkcje węzła/krawędzi
- Trzeba uogólniać na niewidoczne wykresy
- Zadaniem jest klasyfikacja węzłów, przewidywanie połączeń lub klasyfikacja grafów
- Wykres jest duży i potrzebne są skalowalne rozwiązania przybliżone

## Typowe błędy

- Zapominanie o obsłudze odłączonych wykresów (najpierw uruchom połączone komponenty)
- Używanie gęstych macierzy sąsiedztwa dla rzadkich grafów (marnuje pamięć)
- Ignorowanie pętli własnych w sieciach GNN (dodaj tożsamość do sąsiedztwa: A + I)
- Brak normalizacji macierzy sąsiedztwa (powoduje eksplozję skali funkcji podczas przekazywania wiadomości)
- Uruchamianie zbyt wielu rund przekazywania komunikatów (nadmierne wygładzanie - wszystkie węzły zbiegają się do tej samej reprezentacji)