---

name: unified-gen-model-picker
description: Wybierz pomiędzy rodzinami Show-o / Transfusion / Emu3 / Janus-Pro, aby uzyskać produkt, który wymaga zarówno zrozumienia multimodalnego, jak i generowania z otwartymi ciężarami.
version: 1.0.0
phase: 12
lesson: 14
tags: [show-o, masked-diffusion, unified, t2i, inpainting]

---

Biorąc pod uwagę produkt, który wymaga ujednoliconego zrozumienia i generowania (VQA, napisy, T2I, opcjonalnie malowanie) z ograniczeniem otwartych wag i budżetem opóźnień, wybierz rodzinę modeli i wyemituj konfigurację referencyjną.

Wyprodukuj:

1. Wyrok rodzinny. Show-o (maskowana dyskretna dyfuzja), Transfusion / MMDiT (ciągła dyfuzja), Emu3 / Chameleon (autoregresywna dyskretna) lub Janus-Pro (oddzielone enkodery).
2. Budżet kroku wnioskowania. 16 kroków dla Show-o, 20 dla Transfuzji, 1024+ dla Emu3. Uzasadnij wybór budżetem opóźnień użytkownika.
3. Wsparcie przy malowaniu. Show-o jest bezpłatne; Transfuzja dodaje kanał maski; Emu3 wymaga osobnego dostrojenia. Oznacz to dla użytkownika.
4. Wybór tokenizatora. Dla dyskretnych rodzin polecamy IBQ / MAGVIT-v2 / SBER; w przypadku pracy ciągłej polecam VAE SD3.
5. Stabilność treningu. Dwie straty (transfuzja) wymagają dostrojenia wagi; Pojedyncza strata Show-o jest czystsza.
6. Ścieżka migracji w przypadku powiększenia się użytkownika. Od Show-o do Transfuzji, gdy jakość staje się granicą.

Twarde odrzucenia:
- Proponowanie Emu3 / Chameleon, gdy opóźnienie wnioskowania wynosi <10 s na obraz. Autoregresja na ~1024 tokenach jest zbyt wolna.
- Twierdzenie, że Show-o odpowiada Transfuzji w zakresie granicznej jakości obrazu. Tak nie jest. Tokenizatorem jest sufit.
- Zalecanie stabilnej dyfuzji dla produktu wymagającego VQA. SD nie może myśleć o obrazach.

Zasady odmowy:
- Jeśli użytkownik chce <2 s na wygenerowanie obrazu, odrzuć Show-o i zarekomenduj Stable Diffusion + oddzielny VLM do zrozumienia. Zaakceptuj złożoność wielu modeli.
- Jeśli użytkownik chce „najlepszej w swojej klasie jakości” przy otwartych ciężarkach, odrzuć Show-o / Emu3 i poleć rodzinę Transfusion (MMDiT) lub JanusFlow.
- Jeśli użytkownik nie może zaangażować się w tokenizer (boi się licencji, pułapu jakości), odmów dyskretnym rodzinom i zaleć Transfuzję.

Dane wyjściowe: jednostronicowy wybór z werdyktem rodzinnym, budżetem krokowym, wsparciem w zakresie malowania, rekomendacją tokenizatora, planem stabilności i ścieżką migracji. Zakończ za pomocą arXiv 2408.12528 (Show-o), 2408.11039 (Transfuzja), 2501.17811 (Janus-Pro).