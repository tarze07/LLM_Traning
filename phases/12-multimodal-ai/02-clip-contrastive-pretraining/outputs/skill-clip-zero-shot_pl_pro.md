---

name: clip-zero-shot
description: Przeprowadź klasyfikację obrazów zero-shot za pomocą checkpointu CLIP/SigLIP, tworząc ranking predykcji wraz z wartościami podobieństwa.
version: 1.0.0
phase: 12
lesson: 02
tags: [clip, siglip, zero-shot, vision-language]

---

Na podstawie listy obrazów (ścieżek do plików lub adresów URL) oraz listy klas kandydatów, przeprowadź klasyfikację zero-shot z użyciem wybranego punktu kontrolnego (checkpointu) CLIP lub SigLIP. Ta umiejętność służy wyłącznie do wnioskowania (predykcji); nie obejmuje trenowania ani dostrajania modelu.

Wymagane kroki:

1. Konstruowanie promptów. Dla każdej klasy utwórz N szablonów tekstowych (domyślnie: `a photo of a {class}`, `a picture of a {class}`, `an image of a {class}`). Wygeneruj embeddingi dla każdego promptu za pomocą encodera tekstu i uśrednij je, aby stworzyć prototyp klasy.
2. Generowanie embeddingów obrazu. Wygeneruj embeddingi każdego obrazu wejściowego za pomocą dostarczonego encodera wizyjnego. Znormalizuj wektory z obu stron do długości jednostkowej.
3. Ranking predykcji. Oblicz podobieństwo cosinusowe pomiędzy embeddingiem każdego obrazu a prototypem każdej klasy. Zwróć predykcje top-1 oraz top-5 wraz z ich wynikami.
4. Metadane checkpointu. Podaj dokładną nazwę punktu kontrolnego (checkpointu) w serwisie Hugging Face (np. `openai/clip-vit-large-patch14` lub `google/siglip2-so400m-patch14-384`) oraz oczekiwaną rozdzielczość.
5. Ostrzeżenie o wiarygodności. Zwróć uwagę, że klasyfikacja zero-shot dla klas spoza rozkładu danych treningowych (OOD) jest niewiarygodna; podaj najwyższy wynik jako wskaźnik pewności (confidence score) i wygeneruj ostrzeżenie, gdy spadnie on poniżej 0,2.

Bezwzględne odrzucenia:
- Wszelkie próby przypisania etykiet klas niewymienionych na liście dostarczonej przez użytkownika (wywołującego).
- Porównywanie bezpośrednich wartości wyników (scores) pomiędzy różnymi punktami kontrolnymi; wyniki SigLIP i CLIP są w innych skalach.
- Przetwarzanie obrazów przedstawiających ludzi bez wdrożonej polityki dotyczącej ochrony prywatności i zgody na przetwarzanie danych osobowych.

Zasady odmowy wykonania usługi:
- Jeśli użytkownik (wywołujący) poprosi o klasyfikację w obszarach medycznych, prawnych lub kluczowych dla bezpieczeństwa (diagnoza, tożsamość, cechy prawnie chronione), odmów i zalecaj użycie modeli trenowanych pod nadzorem (supervised) wraz ze ścieżkami audytowymi.
- Jeśli podano tylko jedną klasę (klasyfikacja jednoklasowa bez alternatyw), odmów – klasyfikacja zero-shot wymaga co najmniej dwóch kandydatów, aby miała sens.
- Jeśli punkt kontrolny nie został określony, odmów i zapytaj o wybór modelu (CLIP, OpenCLIP, SigLIP, SigLIP 2) oraz jego skalę.

Dane wyjściowe: rankingowa lista top-5 predykcji dla każdego obrazu wraz z wartościami podobieństwa cosinusowego, nazwą checkpointu, użytymi szablonami promptów oraz flagą ufności (confidence flag). Na końcu umieść sekcję „Sugerowane lektury” odsyłającą do lekcji 12.06 o NaFlex (obsłudze zmiennych proporcji obrazu) lub do publikacji o SigLIP 2 w celu pogłębienia wiedzy.
