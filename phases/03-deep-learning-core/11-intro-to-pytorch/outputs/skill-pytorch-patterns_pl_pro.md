---

name: skill-pytorch-patterns
description: Wzorce referencyjne dotyczące treningu, oceny i wdrażania modeli w PyTorch
version: 1.0.0
phase: 03
lesson: 11
tags: [pytorch, training, deep-learning, gpu, patterns]

---

## Kanoniczna pętla treningowa

Standardowy, poprawny schemat prowadzenia treningu i ewaluacji.

```python
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = Model().to(device)
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=0.01)

for epoch in range(num_epochs):
    # Faza treningowa
    model.train()
    for inputs, targets in train_loader:
        inputs, targets = inputs.to(device), targets.to(device)
        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, targets)
        loss.backward()
        
        # Opcjonalnie: przycinanie gradientu w celu stabilizacji
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optimizer.step()

    # Faza ewaluacji
    model.eval()
    with torch.no_grad():
        for inputs, targets in val_loader:
            inputs, targets = inputs.to(device), targets.to(device)
            outputs = model(inputs)
            # Metryki oblicza się w tym miejscu...
```

## Trening z mieszaną precyzją (Mixed Precision)

Przyspiesza obliczenia poprzez zastosowanie mniejszych typów zmiennoprzecinkowych na karcie graficznej.

```python
from torch.amp import autocast, GradScaler

scaler = GradScaler()
for inputs, targets in train_loader:
    inputs, targets = inputs.to(device), targets.to(device)
    optimizer.zero_grad()
    
    # Przebieg wprzód (forward) jest wykonywany z użyciem typu float16 w środowisku autocast
    with autocast(device_type="cuda"):
        outputs = model(inputs)
        loss = criterion(outputs, targets)
        
    scaler.scale(loss).backward()
    scaler.step(optimizer)
    scaler.update()
```

**Kiedy stosować:** Podczas treningu na platformach wyposażonych w procesory GPU obsługujące format float16 (rodzina V100, A100, H100, RTX 3090 i nowsze). Z reguły umożliwia to ok. 1,5-2x przyspieszenie uczenia oraz niemal 50% redukcję zużycia pamięci.

## Akumulacja gradientu (Gradient Accumulation)

Technika omijająca ograniczenia narzucone przez pamięć graficzną dla ulepszonego treningu bardzo dużych modeli (takich jak Transformer, modele LLM), kiedy rzeczywista wielkość partii przekracza możliwości.

```python
accumulation_steps = 4
optimizer.zero_grad()

for i, (inputs, targets) in enumerate(train_loader):
    inputs, targets = inputs.to(device), targets.to(device)
    outputs = model(inputs)
    
    # Skalujemy wartość funkcji straty tak by zniwelować wpływ akumulacji po kroku
    loss = criterion(outputs, targets) / accumulation_steps
    loss.backward()
    
    # Aktualizacja gradientów i wykonanie kroku optymalizatora po przebyciu wszystkich kroków w pętli 
    if (i + 1) % accumulation_steps == 0:
        optimizer.step()
        optimizer.zero_grad()
```

**Kiedy stosować:** W sytuacji, gdy wymagany, efektywny "batch size" jest znacząco wyższy od przydziału pamięci dla GPU. Pamiętaj, aby koniecznie podzielić stratę (`loss`) przez stałą wartość `accumulation_steps`, zachowując spójność matematyczną wartości skali u wszystkich zsumowanych na gradientach parametrów.

## Zapisywanie i wczytywanie modeli w Pythonie (Save / Load)

Najbezpieczniejsze formy przywracania stanu z zabezpieczeniem pod wznowienie.

```python
# Najlepsza praktyka zachowania checkpointów do uczenia i ponowień w przyszłości
torch.save({
    "epoch": epoch,
    "model_state_dict": model.state_dict(),
    "optimizer_state_dict": optimizer.state_dict(),
    "loss": loss.item(),
}, "checkpoint.pt")

# Przywrócenie starych punktów wejścia z bezpiecznym wczytywaniem po state_dict
checkpoint = torch.load("checkpoint.pt", weights_only=True)
model.load_state_dict(checkpoint["model_state_dict"])
optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
```

**Najważniejsza zasada:** By móc bez problemów dokończyć i wznowić etap sieci, staraj się uwzględniać stałą formę zapisu do stanu obiektów także dla wywołania optymalizatora na etapie trenowania (po `optimizer.state_dict()`). Jeżeli używasz eksportu wyłączne do celów wnioskowania wyników i inferencji (np. tzw "produkcji"), możesz pominąć ten fragment w słowniku zapisu i zachować wyłącznie samo klasyczne podanie pliku słownika jako wartości z `model.state_dict()`.

## Implementowanie Własnych Zbiorów (Custom Dataset)

Budowa uniwersalnego interfejsu pod pliki dla DataLoadera. 

```python
class CustomDataset(torch.utils.data.Dataset):
    def __init__(self, data_dir, transform=None):
        self.samples = self._load_samples(data_dir)
        self.transform = transform

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        x, y = self.samples[idx]
        if self.transform:
            x = self.transform(x)
        return x, y

    def _load_samples(self, data_dir):
        # ... Wczytywanie ścieżek z katalogów 
        pass
```

## Poprawna Konfiguracja Modułu DataLoader

Szczegółowe konfiguracje potoku przetwarzania paczek dla najwyższej wydajności.

```python
train_loader = torch.utils.data.DataLoader(
    dataset,
    batch_size=64,
    shuffle=True,
    num_workers=4,
    pin_memory=True,
    drop_last=True,
    persistent_workers=True,
)
```

| Parametr dla klasy | Co robi ten wskaźnik | Kiedy optymalnie używać |
|----------|------------|------------|
| `num_workers=4` | Równoległe procedury z ładowaniem danych w tle | Najlepiej zawsze, gdy korzysta się z maszyn z systemami na procesorach posiadających odpowiednią ilość rdzeni |
| `pin_memory=True` | Umieszcza ładowane instancje w specjalnie przygotowanej, pamięci systemu z przydziałami "locked memory" | Zawsze do polepszenia transmisji podczas używania na układach po GPU |
| `drop_last=True` | Opuszcza lub też wyrzuca, końcową niekompletną małą partię w danych na zakończenie ładowania całej jednej sekwencji przy epokach | Bezwzględnie zalecone dla stosowania w momencie aktywnego korzystania ze stosowanego `BatchNorm` |
| `persistent_workers=True` | Podtrzymuje aktywnie zasoby środowisk procesów ładujących roboczych uśpione pomiędzy odczekaniem powrotu epok przy operacji | Rekomendowane zjawisko gdy przydział do zmiennej procesów wynosi więcej jak jeden proces (`num_workers > 0`) |

## Harmonogramy współczynnika uczenia się (Learning Rate Schedulers)

Pozwalają na dynamiczną modyfikację wielkości kroków aktualizacji w optymalizatorze na przestrzeni procesu treningowego.

```python
scheduler = torch.optim.lr_scheduler.OneCycleLR(
    optimizer,
    max_lr=1e-3,
    total_steps=num_epochs * len(train_loader),
    pct_start=0.1,
)

for epoch in range(num_epochs):
    for inputs, targets in train_loader:
        # Obliczenia straty, zerowanie na modelu itp...
        optimizer.step()
        scheduler.step() # Zwróć uwagę - w tym podejściu to na ten punkt należy rzutować odwołanie!
```

**OneCycleLR:** to często stosowane, uważane za najlepsze ustawienie po domyślnym podziale konfiguracyjnym w standardowych operacjach wyjściowych u głębokiego uczenia w dużej rzeszy modeli klasyfikacyjnych. Skutecznie, a po początku wolnym "rozgrzewa" sieć z tzw. *warmup* aż docierając do zadanego docelowego wielkiego *max_lr*, po czy zaczyna wyciszać gładko w locie krzywe od łagodnie łukowatego opadającego gładko współczynnika dla postaci cosinusa na zakończenie treningów. **Uwaga:** Należy bezwzględnie dopilnować wezwania instrukcji po wywołanej komendzie do optymalizatora jako wywołanie nowej kalkulacji modyfikatora `scheduler.step()` w bezpośrednim użyciu zaraz **po zakończeniu każdego ułożonego batcha krok po kroku**, a nie jak dawniej robiono to po przeskoczeniu każdej całej epoki.

## Automatyczna Inicjalizacja Wag (Weight Initialization)

Wprowadzanie zaawansowanych założeń startowych. 

```python
def init_weights(module):
    if isinstance(module, nn.Linear):
        # Dla warstw nieliniowych u ReLU stosujemy znany inicjalizator He (Kaiming) 
        nn.init.kaiming_normal_(module.weight, nonlinearity="relu")
        if module.bias is not None:
            nn.init.zeros_(module.bias)
            
    elif isinstance(module, nn.Conv2d):
        nn.init.kaiming_normal_(module.weight, mode="fan_out", nonlinearity="relu")

# Wpinamy instrukcje do wdrożenia wywołania
model.apply(init_weights)
```

## Optymalny tryb dla wnioskowania na wyprodukowanych modelach (Inference Mode)

Ustawianie sieci wyuczonej po zakończonych fazach prac gotowej z zadanym parametrem pod produkcje wnioskowań do systemu operacyjnego.

```python
model.eval()

with torch.inference_mode():
    outputs = model(inputs)
```

**Co musisz wiedzieć:** Interfejs ze sterownikiem do metody z wywołaniem jako kontekst operacyjny o ulepszonej właściwości: `torch.inference_mode()` potrafi z jeszcze większą poprawą wyprzedzać użycia od używanych i tradycyjnych starszych sposobów poprzez np zablokowywanie standardowego formy bloku przez zapytanie z rzutem po poleceniu `torch.no_grad()`. Poprawa optymalizacji przy parametrze inference wynika nie w stopniu minimalnym by jedynie blokować na bieżąco stany i ukrywać i redukować ślady oraz odcięcia rzutowań liczenia w grafiki z tyłu u mechanizmu budowy, jednak robiąc to absolutnie nie uaktywniając pod spodem samego z procesów systemu po module *autograd* w trakcie tego działania dla samej procedury, za co zwraca czas. 

## Podręczna i szybka lista kontrolna najpopularniejszych błędów dla treningu PyTorch w pigułce

1. Aktywna próba nałożenia na model lub przed wynik transformacji `softmax` tuż przed modułem straty logarytmicznej: `CrossEntropyLoss` (zauważ i pamiętaj, iż to to polecenie posiada w swoich bibliotekach zintegrowane mechanizmy wykonania kroku o nazwie `log_softmax` jako swoista hybryda) 
2. Przypadkowe zaniedbanie z wywołaniem procedury do wejścia w fazę trybu pod model jako metody poleceniem pod testowe wywołanie użycia rzutującego po komendzie testu: `model.eval()`, zwłaszcza w trakcjach przy sprawdzaniu użytych zbiorów w testach (błędy walidacji na normach partii i mechanizmu w zrzutach u drop out dla modelu).
3. Niedopatrzenie, skutkiem którego rzut na przeniesieniu obiektów klasy na format tensorowy oraz w wywołaniach sieci trafiał i bywał nieumiejętnie pomijany tak jak reszta modelu aby wszystkie na pewniaka i ze 100 procentowym dopięciem umieszczane ze wskazaniami operacyjnie na jedno równe wskazanie operacji docelowego podmiotu obliczającego po sprzętach na procesory dla komputera - dla układów czy CPU czy procesor CUDA tożsamych dla akceleratora w architekturze.  
4. Zignorowanie faktu rzutowania operacją o wezwaniu kasowania procedury i pamięci w zerowaniu pod interfejsy `optimizer.zero_grad()` na początkach iteracji przebiegów dla fazy pętlowej. Skutek? Prowadzenie od zaplecza domyślnych błędów z nawarstwiającym problemem o mechanizmie pod nazwą skrótu dla gradientów: "Akumulacja", po czym doprowadzających stopniowo pod błędne nachylenia optymalizatora na przestrzeni sieci i epok dla całej reszty strukturalnego wyniku szkolonego zadania.
5. Zamieszanie i ujęcie kontekstu operacyjnego po `torch.no_grad()` podczas cyklu zapisu modyfikatora sieci (zostaje wówczas odrzucony ubytek do wstecz po mechanizmie gradientowym propagowanym we wnioskującym silniku, stąd absolutnie odcięta dla modelu na nim od podstaw droga ulepszania uczenia w sieci!) - w rezultacie brak jakichkolwiek modyfikacji przy współczynnikach w wektorach a strata stale i niezłomnie potrafi "płasko stać od początku od zerowych i wejściowych danych".
6. Brak odpowiedniej świadomości dotyczący narzucania "z zapasami" dużej przesadzonej oraz maksymalistycznej parametryzacji stałej na wywoływania po liczbach obciążeniowych poprzez wartość: `num_workers`. Powoduje narzuty bez nadmiernej proporcji generowania ilości śmieci w otwieranych w obrębie zaplecza procesach pod zasoby - a tak duża bezcelowo ilość bezpowrotnie zżera, marnując cenne pamięci w ramy u procesora systemowego podczas operowania zadaniami na stacjach sprzętów dla badacza!
7. Totalny zanik i brak wykorzystania zbawiennych modyfikatorów na pętlach o ulepszaniu zapytania parametrów przy użyciu flag modyfikacji jako form atrybutów dla przypisywanej operacyjnie na True po nazwie wartości u wiersza `pin_memory=True` - przy stosowania na architekturach przy docelowym potoku zrzucanym u procesora po transferowanych pętlach szkolenia bezpośrednio procesując po zrzucie akceleracyjnym przy wykorzystywaniu rdzenia po GPU podczas nauki i trenowania w badaniach w sztucznych inteligencjach z użyciami paczki PyTorch!
8. Utworzenie z wyjściem we formacie i formach całości w obiekt z plikiem "na żywo" na zrzucie całego w formacie modelu obiektowym od klasy we frameworku jako użyta domyślnie u Pythona, co psuje na zapleczu architekturze elastyczne modyfikowanie klas ze state form poprzez odniesienia po `state_dict` — co często i nader mocno potrafi psuć z serializowane skrypty kiedy to pękają bez zapowiedzi często już w nowych przebudowanych we repozytoriach struktur lub pakietach wydawanych i po zwykłej domyślnej po czasie formach do operacji odtwórczych na refaktoryzacji kodu - od nowszych u systemów! Używaj plików opartych i stosowanych jak słowniki stanu z `state_dict()`!
