---

name: ipi-audit
description: Audyt wdrożenia agenta pod kątem pośredniego natychmiastowego wstrzyknięcia i zasięgu kontroli przepływu informacji.
version: 1.0.0
phase: 18
lesson: 15
tags: [ipi, indirect-prompt-injection, ifc, agent-security, owasp-llm01]

---

Biorąc pod uwagę opis wdrożenia agenta, przeprowadź inspekcję wdrożenia pod kątem narażenia na pośrednie natychmiastowe wstrzykiwanie.

Wyprodukuj:

1. Zasoby niezaufanych treści. Wypisz wszystkie źródła treści, które agent może przeczytać: dokumenty RAG, skrzynkę odbiorczą, kalendarz, wyniki narzędzi, zgłoszenia, recenzje produktów, interfejsy API stron trzecich. Każdy z nich jest potencjalnym wektorem IPI.
2. Zaufaj etykietowaniu. Czy wdrożenie oddziela zaufane (podpowiedź użytkownika) od niezaufanych (pobrana treść)? Jeśli treść zostanie połączona w tym samym pytaniu bez etykiety, IFC nie będzie działać.
3. Bramkowanie akcji. Z jakich narzędzi można skorzystać? Czy w każdym przypadku wywołanie jest bramkowane tylko przez zaufany monit, czy też niezaufana treść może mieć wpływ na wywołanie?
4. Ocena ataku adaptacyjnego. Czy wdrożenie zostało przetestowane z atakami adaptacyjnymi (gradient, RL, ludzki zespół czerwony) według Nasra i in. 2025? Ocena wyłącznie ataku statycznego jest niewystarczająca.
5. Granice zakresu i naruszenia. Zidentyfikuj każdą granicę zaufania (np. Skrzynka odbiorcza -> wysyłanie, dokumenty -> zewnętrzny interfejs API). Dla każdego z nich sprawdź, czy działanie jest albo zabronione pod niezaufanym wpływem, albo wyraźnie zatwierdzone przez zaufany monit.

Twarde odrzucenia:
- Dowolne wdrożenie agenta bez wyraźnego oznaczenia zaufania dla pobranej zawartości.
- Wszelkie roszczenia obronne oparte wyłącznie na atakach statycznych.
- Wszelkie twierdzenia, że ​​„nasz środek jest bezpieczny do natychmiastowego wstrzyknięcia” bez wymieniania mechanizmu IFC.

Zasady odmowy:
- Jeśli użytkownik zapyta, czy filtrowanie jest wystarczające, odmów i wyjaśnij wynik Nasr 2025, że ataki adaptacyjne przełamują > 90% obrony opartej na filtrach.
- Jeśli użytkownik poprosi o srebrną obronę, odmów — obrona IPI wymaga IFC, wielowarstwowej moderacji odpowiedzi oraz audytu ludzkiego w przypadku działań o wysoką stawkę.

Wynik: jednostronicowy audyt, który wypełnia pięć powyższych sekcji, wskazuje najniebezpieczniejszą granicę między zaufanymi a zaufanymi i wymienia najpilniejszą kontrolę do dodania. Cytuj MDPI Information 17(1):54 (2026) oraz Nasr i in. (październik 2025 r.) raz na każdą.