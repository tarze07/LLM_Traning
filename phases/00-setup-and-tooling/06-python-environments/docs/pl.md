# Środowiska Python

> Dependency hell jest realny. Środowiska wirtualne to lekarstwo.

**Typ:** Build
**Języki:** Shell
**Wymagania wstępne:** Faza 0, Lekcja 01
**Czas:** ~30 minut

## Cele nauki

- Tworzenie izolowanych środowisk wirtualnych przy użyciu `uv`, `venv` lub `conda`
- Pisanie `pyproject.toml` z opcjonalnymi grupami zależności i generowanie lockfiles dla zapewnienia reprodukowalności
- Diagnozowanie i naprawianie typowych pułapek: instalacje globalne, mieszanie pip/conda, niezgodności wersji CUDA
- Wdrożenie strategii środowisk per-faza dla projektów z konfliktującymi zależnościami

## Problem

Instalujesz PyTorch 2.4 do projektu fine-tuningu. W przyszłym tygodniu inny projekt potrzebuje PyTorch 2.1, ponieważ jego build CUDA jest przypięty do konkretnej wersji. Aktualizujesz globalnie i pierwszy projekt się psuje. Cofasz wersję i psuje się drugi.

To jest dependency hell. Zdarza się to nieustannie w pracy z AI/ML, ponieważ:

- PyTorch, JAX i TensorFlow każdy dostarczają własne bindingi CUDA
- Biblioteki modeli przypinają konkretne wersje frameworków
- Globalny `pip install` nadpisuje wszystko, co było wcześniej
- Buildy CUDA 11.8 nie działają ze sterownikami CUDA 12.x (i odwrotnie)

Rozwiązanie: każdy projekt dostaje własne, izolowane środowisko z własnymi pakietami.

## Koncepcja

```mermaid
graph TD
    subgraph without["Without virtual environments"]
        SP[System Python] --> T24["torch 2.4.0 (CUDA 12.4)\nProject A needs this"]
        SP --> T21["torch 2.1.0 (CUDA 11.8)\nProject B needs this"]
        SP --> CONFLICT["CONFLICT: only one\ntorch version can exist"]
    end

    subgraph with["With virtual environments"]
        PA["Project A (.venv/)"] --> PA1["torch 2.4.0 (CUDA 12.4)"]
        PA --> PA2["transformers 4.44"]
        PB["Project B (.venv/)"] --> PB1["torch 2.1.0 (CUDA 11.8)"]
        PB --> PB2["diffusers 0.28"]
    end
```

## Zbuduj to

### Opcja 1: uv venv (zalecane)

`uv` to najszybszy menedżer pakietów Python (10-100x szybszy niż pip). Obsługuje środowiska wirtualne, wersje Pythona i rozwiązywanie zależności w jednym narzędziu.

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh

uv python install 3.12

cd your-project
uv venv
source .venv/bin/activate
```

Instalacja pakietów:

```bash
uv pip install torch numpy
```

Utworzenie projektu z `pyproject.toml` w jednym kroku:

```bash
uv init my-ai-project
cd my-ai-project
uv add torch numpy matplotlib
```

### Opcja 2: venv (wbudowany)

Jeśli nie możesz zainstalować `uv`, Python jest dostarczany razem z `venv`:

```bash
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

pip install torch numpy
```

Wolniejszy niż `uv`, ale działa wszędzie tam, gdzie jest zainstalowany Python.

### Opcja 3: conda (kiedy jest potrzebna)

Conda zarządza zależnościami spoza Pythona, takimi jak toolkity CUDA, cuDNN i biblioteki C. Używaj jej, gdy:

- Potrzebujesz konkretnej wersji toolkitu CUDA bez instalowania go systemowo
- Pracujesz na współdzielonym klastrze, na którym nie możesz instalować pakietów systemowych
- Instrukcje instalacji biblioteki mówią "use conda"

```bash
# Install miniconda (not the full Anaconda)
curl -LsSf https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -o miniconda.sh
bash miniconda.sh -b

conda create -n myproject python=3.12
conda activate myproject

conda install pytorch torchvision torchaudio pytorch-cuda=12.4 -c pytorch -c nvidia
```

Jedna zasada: jeśli używasz conda dla danego środowiska, używaj conda dla wszystkich pakietów w tym środowisku. Mieszanie `pip install` w środowisku conda powoduje konflikty zależności, które są bolesne do debugowania.

### Dla tego kursu: strategia per-faza

Mógłbyś utworzyć jedno środowisko dla całego kursu. Nie rób tego. Różne fazy potrzebują różnych (czasem konfliktujących) zależności.

Strategia:

```
ai-engineering-from-scratch/
├── .venv/                    <-- shared lightweight env for phases 0-3
├── phases/
│   ├── 04-neural-networks/
│   │   └── .venv/            <-- PyTorch env
│   ├── 05-cnns/
│   │   └── .venv/            <-- same PyTorch env (symlink or shared)
│   ├── 08-transformers/
│   │   └── .venv/            <-- might need different transformer versions
│   └── 11-llm-apis/
│       └── .venv/            <-- API SDKs, no torch needed
```

Skrypt w `code/env_setup.sh` tworzy bazowe środowisko dla tego kursu.

## Podstawy pyproject.toml

Każdy projekt Python powinien mieć `pyproject.toml`. Zastępuje on `setup.py`, `setup.cfg` i `requirements.txt` w jednym pliku.

```toml
[project]
name = "ai-engineering-from-scratch"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "numpy>=1.26",
    "matplotlib>=3.8",
    "jupyter>=1.0",
    "scikit-learn>=1.4",
]

[project.optional-dependencies]
torch = ["torch>=2.3", "torchvision>=0.18"]
llm = ["anthropic>=0.39", "openai>=1.50"]
```

Następnie zainstaluj:

```bash
uv pip install -e ".[torch]"    # base + PyTorch
uv pip install -e ".[llm]"     # base + LLM SDKs
uv pip install -e ".[torch,llm]" # everything
```

## Lockfiles

Lockfile przypina każdą zależność (włącznie z zależnościami przechodnimi) do dokładnych wersji. Gwarantuje to reprodukowalność: każdy, kto instaluje z lockfile, otrzymuje dokładnie te same pakiety.

```bash
# uv generates uv.lock automatically when using uv add
uv add numpy

# pip-tools approach
uv pip compile pyproject.toml -o requirements.lock
uv pip install -r requirements.lock
```

Commituj swój lockfile do gita. Gdy ktoś sklonuje repozytorium, instaluje z lockfile i otrzymuje identyczne wersje.

## Typowe błędy

### 1. Instalacja globalna

```bash
pip install torch  # BAD: installs to system Python

source .venv/bin/activate
pip install torch  # GOOD: installs to virtual environment
```

Sprawdź, gdzie trafiają twoje pakiety:

```bash
which python       # should show .venv/bin/python, not /usr/bin/python
which pip           # should show .venv/bin/pip
```

### 2. Mieszanie pip i conda

```bash
conda create -n myenv python=3.12
conda activate myenv
conda install pytorch -c pytorch
pip install some-other-package   # BAD: can break conda's dependency tracking
conda install some-other-package # GOOD: let conda manage everything
```

Jeśli musisz użyć pip wewnątrz conda (niektóre pakiety są dostępne tylko przez pip), zainstaluj najpierw wszystkie pakiety conda, a pakiety pip na końcu.

### 3. Zapomnienie o aktywacji

```bash
python train.py           # uses system Python, missing packages
source .venv/bin/activate
python train.py           # uses project Python, packages found
```

Twój prompt powłoki powinien pokazywać nazwę środowiska:

```
(.venv) $ python train.py
```

### 4. Commitowanie .venv do gita

```bash
echo ".venv/" >> .gitignore
```

Środowiska wirtualne mają 200MB-2GB. Są lokalne, nieprzenośne między maszynami. Zamiast tego commituj `pyproject.toml` i lockfile.

### 5. Niezgodność wersji CUDA

```bash
nvidia-smi                # shows driver CUDA version (e.g., 12.4)
python -c "import torch; print(torch.version.cuda)"  # shows PyTorch CUDA version

# These must be compatible.
# PyTorch CUDA version must be <= driver CUDA version.
```

## Użyj tego

Uruchom skrypt konfiguracyjny, aby utworzyć środowisko kursu:

```bash
bash phases/00-setup-and-tooling/06-python-environments/code/env_setup.sh
```

Tworzy on `.venv` w katalogu głównym repozytorium z zainstalowanymi i zweryfikowanymi podstawowymi zależnościami.

## Ćwiczenia

1. Uruchom `env_setup.sh` i zweryfikuj, że wszystkie sprawdzenia przechodzą
2. Utwórz drugie środowisko wirtualne, zainstaluj w nim inną wersję numpy i potwierdź, że oba środowiska są izolowane
3. Napisz `pyproject.toml` dla projektu, który potrzebuje zarówno PyTorch, jak i Anthropic SDK
4. Celowo zainstaluj pakiet globalnie (bez aktywowania venv), zauważ gdzie trafia, a następnie go odinstaluj

## Kluczowe pojęcia

| Termin | Co się mówi | Co to faktycznie znaczy |
|------|----------------|----------------------|
| Środowisko wirtualne | "Venv" | Izolowany katalog zawierający interpreter Pythona i pakiety, oddzielony od systemowego Pythona |
| Lockfile | "Przypięte zależności" | Plik wymieniający każdy pakiet i jego dokładną wersję, gwarantujący identyczne instalacje na różnych maszynach |
| pyproject.toml | "Nowy setup.py" | Standardowy plik konfiguracyjny projektu Python, zastępujący setup.py/setup.cfg/requirements.txt |
| Zależność przechodnia | "Zależność zależności" | Pakiet B zależy od C; jeśli instalujesz A, które zależy od B, to C jest zależnością przechodnią A |
| Niezgodność CUDA | "Mój GPU nie działa" | PyTorch został skompilowany dla innej wersji CUDA niż ta obsługiwana przez sterownik twojego GPU |
