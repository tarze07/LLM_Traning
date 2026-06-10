---

name: prompt-zero-shot-class-picker
description: Zaprojektuj szablony promptów dla klasyfikacji zero-shot przy użyciu modelu CLIP na podstawie listy klas oraz domeny problemu
phase: 4
lesson: 18

---

Twój cel to optymalne projektowanie promptów dla klasyfikacji zero-shot.

## Dane wejściowe

- `classes`: lista nazw klas
- `domain`: zdjęcia_naturalne (natural_photos) | medyczny (medical) | satelitarny (satellite) | dokumenty (documents) | przemysłowy (industrial) | media_społecznościowe (memes_social)
- `expected_hardness`: łatwy (klasy wizualnie bardzo zróżnicowane) | średni | trudny (drobne, drobnoziarniste różnice)

## Zasady projektowania

### Szablony podstawowe (zawsze uwzględniane)

```
"a photo of a {}"
"a picture of a {}"
"an image of a {}"
```

### Szablony specyficzne dla domeny

- **zdjęcia_naturalne** — dodaj warianty w stylu: „rozmyte zdjęcie {}”, „przycięte zdjęcie {}”, „czarno-białe zdjęcie {}”, „zbliżenie na {}”, „zdjęcie {} o niskiej rozdzielczości”
- **medyczny** — „badanie kliniczne przedstawiające {}”, „zdjęcie RTG przedstawiające {}”, „zdjęcie histopatologiczne {}”
- **satelitarny** — „zdjęcie satelitarne przedstawiające {}”, „zdjęcie lotnicze {}”, „obraz teledetekcyjny przedstawiający {}”
- **dokumenty** — „zeskanowany dokument {}”, „zdjęcie dokumentu {}”, „skan OCR przedstawiający {}”
- **przemysłowy** — „zdjęcie z inspekcji przemysłowej przedstawiające {}”, „obraz przedstawiający defekt {}”
- **media_społecznościowe** — „mem z {}”, „obrazek z internetu przedstawiający {}”

### Szablony drobnoziarniste (dla klas trudnych)

- „zdjęcie {}, typ: <superkategoria>”
- „zdjęcie przedstawiające zbliżenie na {}”
- „zdjęcie przedstawiające kluczowe cechy {}”

## Format danych wyjściowych

```
[classes]
  <list>

[templates used]
  <numbered list>

[per-class prompt counts]
  <class_1>: N prompts
  <class_2>: N prompts

[recommendation]
  - average embeddings across templates: yes
  - alpha-blend with super-category prompts: yes | no
```

## Wskazówki operacyjne

- Zawsze uwzględniaj trzy szablony podstawowe.
- W przypadku `expected_hardness == hard` dodaj szablony uwzględniające superkategorie; bez tego skuteczność klasyfikacji drobnoziarnistej znacząco spada.
- Nie przekraczaj liczby 100 szablonów na jedną klasę; korzyści wydajnościowe drastycznie maleją powyżej 80 szablonów.
- Zwracaj uwagę na wielkość liter w nazwach klas: CLIP poprawnie radzi sobie z formatami typu „dog” czy „Dog”, ale gorzej z zapisem wyłącznie wielkimi literami (np. „DOG”). Sprowadzaj nazwy do małych liter, chyba że są to nazwy własne.
