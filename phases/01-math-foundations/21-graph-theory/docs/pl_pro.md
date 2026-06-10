# Teoria Grafów

> Grafy to nic innego, jak uniwersalny matematyczny zapis relacji. Jeśli w Twoich danych najważniejsze są same połączenia pomiędzy obiektami, to struktura grafowa jest wszystkim, czego potrzebujesz.

**Typ:** Praktyka (Zbuduj to)
**Język:** Python
**Wymagania wstępne:** Faza 1, Lekcje 01-03 (Algebra Liniowa, Macierze)
**Czas:** ~90 minut

## Cele nauczania

- Budowa własnej, samodzielnej klasy reprezentującej Graf, operującej na wydajnej liście sąsiedztwa i implementującej algorytmy przeszukiwania: Wszerz (BFS) oraz W Głąb (DFS).
- Wyliczenie i zrozumienie macierzy Laplasjanu grafu, oraz tego, jak jej wartości własne pozwalają na wyodrębnienie spójnych składowych.
- Implementacja procesu przekazywania wiadomości (Message Passing), będącego odpowiednikiem propagacji w Sieciach Grafowych (GNN), poprzez znormalizowane mnożenie przez macierz sąsiedztwa.
- Zrozumienie zasady działania Klastrowania Widmowego (Spectral Clustering) i zastosowanie wektora Fiedlera do dzielenia grafu na klastry.

## Problem

Większość tradycyjnego uczenia maszynowego przyjmuje ustrukturyzowane, płaskie dane w formie tabelarycznej (np. tabele z bazy danych lub pliki CSV). W takim modelu każdy wiersz jest traktowany niezależnie. Jest to jednak wysoce nieefektywne, gdy najcenniejsza informacja i sygnał ukryte są w tym, jak poszczególne obiekty łączą się ze sobą. 

Gdy analizujemy sieci społeczne, rekomendujemy produkty, modelujemy ruch miejski lub próbujemy przewidzieć zachowanie skomplikowanych cząsteczek chemicznych czy białek, tradycyjne tabele zawodzą. Teoria Grafów pozwala uchwycić samą architekturę powiązań i relacji. To na niej bezpośrednio opierają się Grafowe Sieci Neuronowe (GNN), używane obecnie od Google Maps po odkrywanie nowych leków.

## Koncepcja

### Węzły i Krawędzie (Nodes i Edges)

Graf $G$ to para zbiorów $G = (V, E)$. 
$V$ to zbiór węzłów (wierzchołków - z ang. Vertices / Nodes). Węzły reprezentują obiekty, na przykład ludzi w sieci społecznej, atomy w cząsteczce lub stacje metra w mieście.
$E$ to zbiór krawędzi (Edges). Reprezentują one powiązania między dwoma węzłami $(u, v)$. 

W zależności od charakterystyki relacji, grafy dzielimy na:
1. **Nieskierowane:** Krawędź ma charakter dwukierunkowy. Znajomość na Facebooku działa w obie strony. Z węzła A można przejść do węzła B i vice versa.
2. **Skierowane:** Krawędź ma określony zwrot i działa w jedną stronę, jak śledzenie kogoś na Twitterze lub hiperłącze z jednej strony WWW do innej (PageRank).
3. **Nieważone:** Relacja po prostu istnieje (wartość 1) lub nie (wartość 0). 
4. **Ważone:** Krawędź posiada określoną wagę, na przykład odległość w kilometrach między dwoma stacjami czy "siłę" więzi.

### Macierz Sąsiedztwa (Adjacency Matrix)

Grafy można wyrazić za pomocą macierzy, co pozwala analizować je z wykorzystaniem algebry liniowej i mnożyć je w pamięci GPU w uczeniu maszynowym.

Macierz Sąsiedztwa $A$ wymiaru $N \times N$ (gdzie $N$ to liczba węzłów) jest zdefiniowana w taki sposób, że:
$A[i][j] = 1$ (lub wartość wagi krawędzi), jeśli pomiędzy węzłem $i$ a $j$ istnieje połączenie, oraz $0$ w przeciwnym razie. W przypadku grafów nieskierowanych macierz ta jest zawsze symetryczna.

```
Przykładowy graf trójkąta (węzły 0, 1, 2 powiązane wzajemnie):
A = [ [0, 1, 1],
      [1, 0, 1],
      [1, 1, 0] ]
```

### Stopień węzła (Degree) i Macierz Stopni

Stopień (Degree) to po prostu liczba sąsiadów danego węzła (ile krawędzi jest do niego podłączonych). Dla węzłów charakteryzujących się masową ilością powiązań, mówi się o nich jako o "Hubach" w sieci (np. konto influencera na Twitterze). Macierz Stopni (Degree Matrix, oznaczana jako $D$) to macierz diagonalna, gdzie na przekątnej wpisany jest stopień każdego węzła, a pozostałe pola wynoszą zero.

```
D = [ [2, 0, 0],
      [0, 2, 0],
      [0, 0, 2] ]
```

### Przeszukiwanie Grafów: BFS vs DFS

Najstarsze i fundamentalne algorytmy wędrówki po grafach:
- **BFS (Breadth-First Search) - Przeszukiwanie wszerz:** Wykorzystuje kolejkę (FIFO). Najpierw odwiedza wszystkich najbliższych (bezpośrednich) sąsiadów przed wędrówką w głąb struktury. Świetnie sprawdza się w wyliczaniu najkrótszych ścieżek bez uwzględnienia wag.
- **DFS (Depth-First Search) - Przeszukiwanie w głąb:** Wykorzystuje stos (LIFO). Podąża pojedynczą ścieżką w dół tak daleko, jak to możliwe, i dopiero przy napotkaniu ślepego zaułka cofa się i sprawdza sąsiednie odnogi. Idealnie nadaje się do odnajdywania spójnych składowych i cykli w grafie.

### Macierz Laplasjanu i jej Właściwości

Laplasjan Grafu to macierz $L = D - A$ (Macierz Stopni minus Macierz Sąsiedztwa). Stanowi ona centralny obiekt Teorii Grafów Spektralnych (Spectral Graph Theory).

```
Dla naszego Trójkąta:
L = [ [ 2, -1, -1],
      [-1,  2, -1],
      [-1, -1,  2] ]
```

Laplasjan ma genialne właściwości matematyczne:
- Zawsze jest dodatnio półokreślony (PSD), a jego wartości własne są nieujemne ($\ge 0$).
- Liczba zerowych wartości własnych w tej macierzy jest równa dokładnej liczbie rozłącznych, niepołączonych w żaden sposób Składowych Spójnych (Komponentów) grafu.
- Pierwsza niezerowa wartość własna nazywana jest **Łącznością Algebraiczną** (Algebraic Connectivity), a powiązany z nią **Wektor Własny Fiedlera** (Fiedler Vector) można z powodzeniem zastosować do podzielenia grafu na równe i mocno odseparowane od siebie klastry (technika Klastrowania Widmowego - Spectral Clustering).

### Przekazywanie Wiadomości (Message Passing) w GNN

Modele GNN działają na prostej koncepcji zwanej Propagacją Komunikatów (Message Passing). Każdy węzeł tworzy swój nowy stan / ukrytą reprezentację poprzez zsumowanie (lub uśrednienie) cech swoich bezpośednich sąsiadów. 

W podstawowej sieci GCN (Graph Convolutional Network) zapisuje się to macierzowo jako znormalizowane mnożenie:

$H^{(k+1)} = \sigma(D^{-1} A \cdot H^{(k)} W)$

Mnożenie przez $A$ zbiera komunikaty od wszystkich sąsiadów. Mnożenie z przodu przez odwrotność macierzy $D$ uśrednia i normalizuje siłę wiadomości, a $W$ to wyuczalne wagi w modelu. Jedna runda takiej wymiany poszerza "pole widzenia" każdego węzła na swoich sąsiadów o odległość jednego kroku (1-hop).

## Zbuduj To (Implementacja z wykorzystaniem NumPy i Python)

```python
import numpy as np
from collections import deque

class Graph:
    def __init__(self, n_nodes, directed=False):
        self.n = n_nodes
        self.directed = directed
        self.adj = {i: {} for i in range(n_nodes)} 

    def add_edge(self, u, v, weight=1.0):
        self.adj[u][v] = weight
        if not self.directed:
            self.adj[v][u] = weight

    def neighbors(self, node):
        return list(self.adj[node].keys())

    def degree(self, node):
        return len(self.adj[node])

    def adjacency_matrix(self):
        A = np.zeros((self.n, self.n))
        for u in range(self.n):
            for v, w in self.adj[u].items():
                A[u][v] = w
        return A

    def degree_matrix(self):
        D = np.zeros((self.n, self.n))
        for i in range(self.n):
            D[i][i] = self.degree(i)
        return D

    def laplacian(self):
        return self.degree_matrix() - self.adjacency_matrix()


# Wyszukiwanie Wszerz (Breadth-First Search)
def bfs(graph, start):
    visited = set([start])
    order = []
    distances = {start: 0}
    queue = deque([(start, 0)]) 

    while queue:
        node, dist = queue.popleft() 
        order.append(node)
        for neighbor in graph.neighbors(node):
            if neighbor not in visited:
                visited.add(neighbor)
                distances[neighbor] = dist + 1
                queue.append((neighbor, dist + 1))
    return order, distances


# Spektralne badanie Spójnych Składowych Grafu (Laplasjan)
def laplacian_eigenvalues(graph):
    L = graph.laplacian()
    # eigvalsh jest przeznaczone dla symetrycznych (hermitowskich) macierzy
    eigenvalues = np.linalg.eigvalsh(L) 
    return eigenvalues

# Spectral Clustering (Klastrowanie Widmowe Oparte na Wektorze Fiedlera)
def spectral_clustering(graph, k=2):
    L = graph.laplacian()
    eigenvalues, eigenvectors = np.linalg.eigh(L)
    # Wybieramy pierwsze istotne wektory (odrzucamy zerowy)
    features = eigenvectors[:, 1:k+1] 

    labels = np.zeros(graph.n, dtype=int)
    for i in range(graph.n):
        # Partycjonowanie w oparciu o wektor Fiedlera
        if features[i, 0] >= 0:
            labels[i] = 0
        else:
            labels[i] = 1
    return labels

# Symulacja pojedynczej rundy Message Passing (GNN / GCN)
def message_passing(graph, features, weight_matrix):
    A = graph.adjacency_matrix()
    row_sums = A.sum(axis=1, keepdims=True)
    # Unikamy dzielenia przez 0
    row_sums[row_sums == 0] = 1 
    A_norm = A / row_sums
    
    # Agregacja od sąsiadów
    aggregated = A_norm @ features
    
    # Przejście przez macierz uczących się Wag modelu (Update step)
    output = aggregated @ weight_matrix
    return output
```

## Dalsza nauka

- **Grafowe Sieci Neuronowe i Mnożenie Macierzy:** W rzeczywistości GNNy bazują na tej samej koncepcji co powyżej. Modele PyTorch Geometric (PyG) opierają się na wdrożeniu `MessagePassing`.
- **Klastrowanie Widmowe w sklearn:** Gotową implementację można znaleźć z pakietu `sklearn.cluster.SpectralClustering`, która pod spodem używa powyższej logiki opierającej się o obliczenia na Macierzy Laplasjanu i wektorach własnych.
