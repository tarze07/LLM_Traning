# Docker dla AI

> Kontenery sprawiają, że problem „u mnie działa” odchodzi do przeszłości.

**Typ:** Build
**Języki:** Docker
**Wymagania wstępne:** Faza 0, lekcje 01 i 03
**Czas:** ~60 minut

## Cele nauki

- Zbuduj obraz Dockera z obsługą GPU, zawierający CUDA, PyTorch i biblioteki AI, na podstawie Dockerfile
- Montuj katalogi hosta jako wolumeny (volumes), aby przechowywać modele, datasety i kod między przebudowami kontenerów
- Skonfiguruj NVIDIA Container Toolkit, aby udostępnić GPU wewnątrz kontenerów
- Zorkiestruj wieloskładnikową aplikację AI (serwer inferencji + baza wektorowa) za pomocą Docker Compose

## Problem

Wytrenowałeś model na laptopie z PyTorch 2.3, CUDA 12.4 i Python 3.12. Twój kolega ma PyTorch 2.1, CUDA 11.8 i Python 3.10. Twój model crashuje na jego maszynie. Twój Dockerfile działa na obu.

Projekty AI to koszmar zależności. Typowy stos zawiera Pythona, PyTorch, sterowniki CUDA, cuDNN, biblioteki C na poziomie systemu oraz wyspecjalizowane pakiety, takie jak flash-attn, które wymagają dokładnie określonych wersji kompilatora. Docker pakuje to wszystko w jeden obraz, który działa identycznie wszędzie.

## Koncepcja

Docker zamyka twój kod, runtime, biblioteki i narzędzia systemowe w izolowanej jednostce zwanej kontenerem. Pomyśl o tym jak o lekkiej maszynie wirtualnej, z tą różnicą, że dzieli ona kernel systemu operacyjnego hosta zamiast uruchamiać własny, dzięki czemu startuje w sekundy zamiast minut.

```mermaid
graph TD
    subgraph without["Bez Dockera"]
        A1["Twoja maszyna<br/>Python 3.12<br/>CUDA 12.4<br/>PyTorch 2.3"] -->|crash| X1["???"]
        A2["Maszyna kolegi<br/>Python 3.10<br/>CUDA 11.8<br/>PyTorch 2.1"] -->|crash| X2["???"]
        A3["Serwer<br/>Python 3.11<br/>CUDA 12.1<br/>PyTorch 2.2"] -->|crash| X3["???"]
    end

    subgraph with_docker["Z Dockerem — ten sam obraz wszędzie"]
        B1["Twoja maszyna<br/>Python 3.12 | CUDA 12.4<br/>PyTorch 2.3 | Twój kod"]
        B2["Maszyna kolegi<br/>Python 3.12 | CUDA 12.4<br/>PyTorch 2.3 | Twój kod"]
        B3["Serwer<br/>Python 3.12 | CUDA 12.4<br/>PyTorch 2.3 | Twój kod"]
    end
```

### Dlaczego projekty AI potrzebują Dockera bardziej niż większość

1. **Sterowniki GPU są kruche.** Kod CUDA 12.4 nie działa na CUDA 11.8. Docker izoluje toolkit CUDA wewnątrz kontenera, jednocześnie udostępniając sterownik GPU hosta poprzez NVIDIA Container Toolkit.

2. **Wagi modeli są duże.** Model z 7 miliardami parametrów to 14 GB w fp16. Nie chcesz pobierać go ponownie za każdym razem, gdy przebudowujesz obraz. Wolumeny Dockera pozwalają zamontować katalog z modelami z hosta.

3. **Architektury wieloskładnikowe są powszechne.** Prawdziwa aplikacja AI to nie tylko skrypt w Pythonie. To serwer inferencji, baza wektorowa do RAG, może frontend webowy. Docker Compose orkiestruje to wszystko jednym poleceniem.

### Kluczowe słownictwo

| Termin | Co oznacza |
|------|---------------|
| Image (obraz) | Szablon tylko do odczytu. Twój przepis. Zbudowany z Dockerfile. |
| Container (kontener) | Działająca instancja obrazu. Twoja kuchnia. |
| Dockerfile | Instrukcje budowania obrazu. Warstwa po warstwie. |
| Volume (wolumen) | Trwałe przechowywanie danych, które przetrwa restart kontenera. |
| docker-compose | Narzędzie do definiowania aplikacji wielokontenerowych w YAML. |

### Typowe wzorce kontenerów w AI

```
Dev Container
  Pełny zestaw narzędzi. Wsparcie edytora. Jupyter. Narzędzia debugujące.
  Używany podczas rozwoju i eksperymentowania.

Training Container
  Minimalny. Tylko skrypt treningowy i zależności.
  Działa na klastrach GPU. Bez edytora, bez Jupytera.

Inference Container
  Zoptymalizowany do serwowania. Mały obraz. Szybki cold start.
  Działa za load balancerem w produkcji.
```

## Zbuduj to

### Krok 1: Zainstaluj Dockera

```bash
# macOS
brew install --cask docker
open /Applications/Docker.app

# Ubuntu
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
# Wyloguj się i zaloguj ponownie, aby zmiana grupy zaczęła obowiązywać
```

Zweryfikuj:

```bash
docker --version
docker run hello-world
```

### Krok 2: Zainstaluj NVIDIA Container Toolkit (Linux z GPU NVIDIA)

To pozwala kontenerom Docker na dostęp do twojego GPU. Użytkownicy macOS i Windows (WSL2) mogą pominąć ten krok; Docker Desktop obsługuje przekazywanie GPU inaczej na tych platformach.

```bash
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

Przetestuj dostęp do GPU wewnątrz kontenera:

```bash
docker run --rm --gpus all nvidia/cuda:12.4.1-base-ubuntu22.04 nvidia-smi
```

Jeśli widzisz informacje o swoim GPU, toolkit działa poprawnie.

### Krok 3: Zrozum obrazy bazowe

Wybór odpowiedniego obrazu bazowego oszczędza godziny debugowania.

```
nvidia/cuda:12.4.1-devel-ubuntu22.04
  Pełny toolkit CUDA. Kompilatory w zestawie.
  Użyj do: budowania pakietów wymagających nvcc (flash-attn, bitsandbytes)
  Rozmiar: ~4 GB

nvidia/cuda:12.4.1-runtime-ubuntu22.04
  Tylko runtime CUDA. Bez kompilatorów.
  Użyj do: uruchamiania gotowego kodu
  Rozmiar: ~1.5 GB

pytorch/pytorch:2.3.1-cuda12.4-cudnn9-runtime
  PyTorch wstępnie zainstalowany na bazie CUDA.
  Użyj do: pominięcia kroku instalacji PyTorch
  Rozmiar: ~6 GB

python:3.12-slim
  Bez CUDA. Tylko CPU.
  Użyj do: inferencji na CPU, lekkich narzędzi
  Rozmiar: ~150 MB
```

### Krok 4: Napisz Dockerfile dla środowiska deweloperskiego AI

Oto Dockerfile w `code/Dockerfile`. Przejdźmy przez niego krok po kroku:

```dockerfile
FROM nvidia/cuda:12.4.1-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.12 \
    python3.12-venv \
    python3.12-dev \
    python3-pip \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.12 1

RUN python -m pip install --no-cache-dir --upgrade pip setuptools wheel

RUN python -m pip install --no-cache-dir \
    torch==2.3.1 \
    torchvision==0.18.1 \
    torchaudio==2.3.1 \
    --index-url https://download.pytorch.org/whl/cu124

RUN python -m pip install --no-cache-dir \
    numpy \
    pandas \
    scikit-learn \
    matplotlib \
    jupyter \
    transformers \
    datasets \
    accelerate \
    safetensors

WORKDIR /workspace

VOLUME ["/workspace", "/models"]

EXPOSE 8888

CMD ["python"]
```

Zbuduj go:

```bash
docker build -t ai-dev -f phases/00-setup-and-tooling/07-docker-for-ai/code/Dockerfile .
```

Za pierwszym razem zajmuje to chwilę (pobieranie obrazu bazowego CUDA + PyTorch). Kolejne buildy korzystają z cache'owanych warstw.

Uruchom go:

```bash
docker run --rm -it --gpus all \
    -v $(pwd):/workspace \
    -v ~/models:/models \
    ai-dev python -c "import torch; print(f'PyTorch {torch.__version__}, CUDA: {torch.cuda.is_available()}')"
```

Uruchom Jupyter wewnątrz kontenera:

```bash
docker run --rm -it --gpus all \
    -v $(pwd):/workspace \
    -v ~/models:/models \
    -p 8888:8888 \
    ai-dev jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root
```

### Krok 5: Montowanie wolumenów dla danych i modeli

Montowanie wolumenów jest krytyczne dla pracy z AI. Bez nich pobrany model o rozmiarze 14 GB znika, gdy kontener zostaje zatrzymany.

```bash
# Zamontuj swój kod
-v $(pwd):/workspace

# Zamontuj wspólny katalog z modelami
-v ~/models:/models

# Zamontuj datasety
-v ~/datasets:/data
```

Wewnątrz skryptu treningowego, ładuj dane ze zamontowanej ścieżki:

```python
from transformers import AutoModel

model = AutoModel.from_pretrained("/models/llama-7b")
```

Model znajduje się w systemie plików hosta. Przebudowuj kontener tak często, jak chcesz, bez ponownego pobierania.

### Krok 6: Docker Compose dla wieloskładnikowych aplikacji AI

Prawdziwa aplikacja RAG potrzebuje serwera inferencji oraz bazy wektorowej. Docker Compose uruchamia oba jednym poleceniem.

Zobacz `code/docker-compose.yml`:

```yaml
services:
  ai-dev:
    build:
      context: .
      dockerfile: Dockerfile
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
    volumes:
      - ../../../:/workspace
      - ~/models:/models
      - ~/datasets:/data
    ports:
      - "8888:8888"
    stdin_open: true
    tty: true
    command: jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root

  qdrant:
    image: qdrant/qdrant:v1.12.5
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - qdrant_data:/qdrant/storage

volumes:
  qdrant_data:
```

Uruchom wszystko:

```bash
cd phases/00-setup-and-tooling/07-docker-for-ai/code
docker compose up -d
```

Teraz twój kontener deweloperski AI może komunikować się z bazą wektorową pod adresem `http://qdrant:6333` poprzez nazwę usługi. Docker Compose automatycznie tworzy współdzieloną sieć.

Przetestuj połączenie z wnętrza kontenera AI:

```python
from qdrant_client import QdrantClient

client = QdrantClient(host="qdrant", port=6333)
print(client.get_collections())
```

Zatrzymaj wszystko:

```bash
docker compose down
```

Dodaj `-v`, aby usunąć również wolumen qdrant:

```bash
docker compose down -v
```

### Krok 7: Przydatne polecenia Dockera w pracy z AI

```bash
# Wyświetl listę działających kontenerów
docker ps

# Wyświetl listę wszystkich obrazów i ich rozmiarów
docker images

# Usuń nieużywane obrazy (odzyskaj miejsce na dysku)
docker system prune -a

# Sprawdź użycie GPU wewnątrz działającego kontenera
docker exec -it <container_id> nvidia-smi

# Skopiuj plik z kontenera na hosta
docker cp <container_id>:/workspace/results.csv ./results.csv

# Wyświetl logi kontenera
docker logs -f <container_id>
```

## Wykorzystaj to

Masz teraz odtwarzalne środowisko deweloperskie AI. Przez resztę tego kursu:

- Używaj `docker compose up`, aby uruchomić środowisko deweloperskie razem z bazą wektorową
- Montuj swój kod, modele i dane jako wolumeny, aby nic nie zostało utracone między przebudowami
- Gdy lekcja wymaga nowego pakietu Python, dodaj go do Dockerfile i przebuduj obraz
- Udostępnij swój Dockerfile członkom zespołu. Otrzymają dokładnie to samo środowisko.

### Brak GPU?

Usuń flagę `--gpus all` oraz blok deploy NVIDIA. Kontener nadal będzie działał dla lekcji opartych na CPU. PyTorch wykrywa brak CUDA i automatycznie przełącza się na CPU.

## Ćwiczenia

1. Zbuduj Dockerfile i uruchom `python -c "import torch; print(torch.__version__)"` wewnątrz kontenera
2. Uruchom stos docker-compose i zweryfikuj, że Qdrant jest dostępny z kontenera AI pod adresem `http://qdrant:6333/collections`
3. Dodaj `flask` do Dockerfile, przebuduj obraz i uruchom prosty serwer API na porcie 5000. Zmapuj port za pomocą `-p 5000:5000`
4. Zmierz rozmiar obrazu za pomocą `docker images`. Spróbuj zmienić obraz bazowy z `devel` na `runtime` i porównaj rozmiary

## Kluczowe pojęcia

| Termin | Co mówią ludzie | Co to faktycznie oznacza |
|------|----------------|----------------------|
| Container (kontener) | "Lekka VM" | Izolowany proces korzystający z kernela hosta, z własnym systemem plików i siecią |
| Image layer (warstwa obrazu) | "Cache'owany krok" | Każda instrukcja Dockerfile tworzy warstwę. Niezmienione warstwy są cache'owane, dzięki czemu rebuildy są szybkie. |
| NVIDIA Container Toolkit | "GPU w Dockerze" | Hook runtime, który udostępnia GPU hosta kontenerom poprzez flagę `--gpus` |
| Volume mount (montowanie wolumenu) | "Współdzielony folder" | Katalog na hoście zmapowany do kontenera. Zmiany przetrwają zatrzymanie kontenera. |
| Base image (obraz bazowy) | "Punkt startowy" | Obraz `FROM`, na bazie którego budowany jest twój Dockerfile. Determinuje, co jest wstępnie zainstalowane. |
