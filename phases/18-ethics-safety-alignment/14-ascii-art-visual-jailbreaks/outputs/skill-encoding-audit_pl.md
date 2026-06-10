---

name: encoding-audit
description: Przejrzyj raport dotyczący ochrony przed jailbreakiem dotyczący ataków na rodzinę kodowania.
version: 1.0.0
phase: 18
lesson: 14
tags: [artprompt, ascii-art, encoding-attack, utes, structural-sleight]

---

Biorąc pod uwagę raport dotyczący ochrony przed jailbreakiem, wylicz objęte ataki na rodzinę kodowania i warstwę obrony, która przechwytuje każdy z nich.

Wyprodukuj:

1. Pokrycie kodowania. Wymień każdą ocenianą rodzinę ataków: grafika ASCII (ArtPrompt), base64, leet-speak, homoglify UTF-8, zagnieżdżony JSON/YAML/CSV, drzewo/wykres UTES, modalność obrazu. Oznacz zaginione rodziny.
2. Mapowanie warstwy obronnej. Dla każdej rodziny określ, która warstwa obrony (filtr słów kluczowych, filtr zakłopotania, parafraza, retokenizacja, klasyfikator wyników, moderator multimodalny) ją wychwytuje, a która nie.
3. Luka w rozpoznawaniu wzrokowym. Per Jianga i in. 2024, PPL i Retokenizacja nie sprawdzają się w przypadku ArtPrompt, ponieważ rozpoznawanie odbywa się na poziomie wizualnym. Czy obrona raportu obejmuje cokolwiek, co działa na poziomie wizualnym/strukturalnym?
4. Test uogólnienia. UTES (StructuralSleight) uogólnia dowolne rzadkie struktury. Czy raport testuje struktury, których nie ma w zestawie szkoleniowym?
5. Kompromis między możliwościami a bezpieczeństwem. Model z silniejszymi możliwościami tekstu wizualnego (wysoki wynik ViTC) jest bardziej podatny na ArtPrompt. Jeśli zostanie zgłoszony, zanotuj wynik ViTC modelu; poproś o to, jeśli nie.

Twarde odrzucenia:
- Wszelkie roszczenia obronne oparte wyłącznie na filtrowaniu podciągów/słów kluczowych.
- Wszelkie roszczenia obronne obejmujące jedną rodzinę kodowania i ekstrapolujące na „ataki kodujące”.
- Wszelkie roszczenia obronne bez wskaźnika skuteczności ataków na rodzinę.

Zasady odmowy:
- Jeśli użytkownik zapyta, czy ArtPrompt jest „załatany”, odmów i wyjaśnij lukę w obronie na poziomie rozpoznawania i na poziomie tekstu.
— Jeśli użytkownik poprosi o zalecaną ochronę obejmującą całe kodowanie, odrzuć jedno zalecenie — ochrona musi obejmować wszystkie rodziny, z którymi może spotkać się wdrożenie.

Wynik: jednostronicowy audyt, który wypełnia pięć powyższych sekcji, wskazuje podstawową lukę w kodowaniu i wskazuje najpilniejszą warstwę obrony do dodania. Cytuj Jianga i in. (arXiv:2402.11753) i StructuralSleight po jednym egzemplarzu.