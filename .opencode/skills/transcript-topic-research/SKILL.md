---
name: Transcript Topic Research
description: Przeszukuje lokalne transkrypcje YouTube pod kątem tematu (najpierw deterministycznie, bez LLM), tworzy indeks tematyczny i opracowuje trzy raporty o różnej długości z odnośnikami do źródeł.
---

# Badanie tematyczne transkrypcji YouTube

Użyj tego skilla, gdy użytkownik chce znaleźć w lokalnych transkrypcjach
materiały na określony temat, a następnie dostać krótkie, średnie i długie
opracowanie z odnośnikami do filmów źródłowych.

## Zasady nadrzędne

- **Pierwsze wyszukiwanie jest deterministyczne — bez LLM.** Używaj regexu
  (`topic_search.py`, `grep` lub `rg`), nie modelu językowego.
- **Nie zmyślaj źródeł ani treści.** Każda teza w raportach musi mieć
  odzwierciedlenie w transkrypcji albo być wyraźnie oznaczona jako kontekst
  zewnętrzny.
- **Parafrazuj.** Nie kopiuj długich fragmentów transkrypcji; streszczaj.
  Transkrypcje są lokalne i mogą podlegać prawom autorskim.
- **Rozdzielaj rodzaje wiedzy:** bezpośrednie twierdzenia autorów filmów,
  opisy badań, doświadczenia/anegdoty i ogólny konsensus medyczny. Przy
  tematach zdrowotnych dodaj zastrzeżenie, że to nie jest porada medyczna.
- **Nie mieszaj kanałów bez oznaczenia.** W raportach podawaj kanał, datę
  i link do filmu.

## Krok 1 — ustal temat i wzorce

Ustal:

- `slug` tematu, np. `migrena`, `insulinoopornosc`, `witamina-d`;
- etykietę, np. `Migrena`;
- wzorzec podstawowy z rdzeniem polskich odmian, np. `migren` (łapie
  migrena, migreny, migrenie, migreną, migrenom, migrenowy itd.);
- opcjonalnie synonimy do drugiego przebiegu.

Nie używaj LLM do wyszukiwania. Wzorzec ma być jawny i powtarzalny.

## Krok 2 — pierwszy przebieg (tylko słowa kluczowe)

Z katalogu repo:

```bash
python3 .opencode/skills/transcript-topic-research/scripts/topic_search.py \
  --topic migrena \
  --label "Migrena" \
  --pattern 'migren' \
  --root transkrypcje \
  --out transkrypcje/_tematy/migrena.md \
  --json transkrypcje/_tematy/migrena.json
```

Skrypt:

- przeszukuje wszystkie `*.txt` poza `.staging`, `.archives` i `_tematy`;
- liczy trafienia i czyta nagłówki `Title:`, `URL:`, `Published:`;
- zapisuje indeks Markdown i opcjonalny JSON;
- nie korzysta z sieci ani z modelu.

Równoważny szybki podgląd:

```bash
rg -il 'migren' transkrypcje --glob '*.txt' --glob '!.staging/**' --glob '!.archives/**'
```

Zapisz wynik pierwszego przebiegu. To jest **indeks tematyczny** wymagany
przez użytkownika.

## Krok 3 — drugi przebieg (synonimy, opcjonalnie)

Jeśli pierwszy przebieg daje mało trafień albo temat bywa opisywany inaczej,
zrób osobny przebieg z jawnymi synonimami i zapisz go jako
`transkrypcje/_tematy/<slug>-synonimy.md`. Nie mieszaj go po cichu z pierwszym
indeksem — w raporcie napisz, jakie wzorce zastosowano.

Przykład dla migreny:

```bash
python3 .opencode/skills/transcript-topic-research/scripts/topic_search.py \
  --topic migrena-synonimy \
  --label "Migrena — synonimy" \
  --pattern 'ból głowy|bóle głowy|bólu głowy|bólom głowy|bólem głowy|hemikrani|aura migrenowa' \
  --out transkrypcje/_tematy/migrena-synonimy.md
```

## Krok 4 — przegląd i notatki

1. Otwórz indeks i sprawdź, czy trafienia nie są przypadkowe (np. wzmianka
   w opisie innego tematu).
2. Przeczytaj transkrypcje z trafieniami. Przy dużej liczbie zacznij od
   największej liczby trafień i od kanałów specjalistycznych.
3. Zapisz robocze notatki w `transkrypcje/_tematy/<slug>-notatki.md`
   (plik lokalny, ignorowany przez git):
   - twierdzenie;
   - kto i w jakim filmie to mówi;
   - czy to badanie, doświadczenie, opinia czy anegdota;
   - data i link.
4. Oddzielaj przyczyny, czynniki wyzwalające, profilaktykę, metody naturalne,
   leki i objawy alarmowe.

## Krok 5 — trzy raporty

Zapisz raporty w `docs/tematy/<slug>/`:

```text
docs/tematy/migrena/
├─ README.md
├─ 01-krotki.md
├─ 02-sredni.md
└─ 03-dlugi.md
```

Długość licz dla tempa ok. 200 słów/min:

| Plik | Czas czytania | Orientacyjna długość |
| --- | --- | --- |
| `01-krotki.md` | 1–3 min | 250–600 słów |
| `02-sredni.md` | 5–8 min | 1000–1600 słów |
| `03-dlugi.md` | 10–25 min | 2000–5000 słów |

Wymagania:

- **Krótki:** najważniejsze wnioski, 3–5 praktycznych punktów, 3–5 źródeł.
- **Średni:** sekcje tematyczne, mechanizmy, przyczyny, profilaktyka, metody
  naturalne, leki, zastrzeżenia; przypisy `[1]`, `[2]` i lista źródeł z
  linkami YouTube oraz nazwami plików.
- **Długi:** pełny przegląd, różnice między źródłami, jakość dowodów,
  praktyczne protokoły, przeciwwskazania, pytania do lekarza, obszerna
  bibliografia.
- **README:** jednozdaniowy opis, spis raportów, data, zakres kanałów i wzorce
  wyszukiwania.

Dla tematów medycznych stosuj szkielet: definicja → przyczyny i mechanizmy →
czynniki wyzwalające → profilaktyka → metody naturalne → leki → kiedy do
lekarza → jakość dowodów → bibliografia.

## Krok 6 — kontrola jakości

- Sprawdź liczbę słów w każdym raporcie.
- Sprawdź, czy każdy przypis prowadzi do istniejącego pliku i linku YouTube.
- Sprawdź, czy w raportach nie ma nieoznaczonych twierdzeń spoza transkrypcji.
- Sprawdź, czy indeks tematyczny obejmuje wszystkie pliki z trafieniami.
- Nie dodawaj transkrypcji ani ich fragmentów do gita; raporty w `docs/` są
  streszczeniem, nie kopią źródeł.

## Szablon przypisów

```markdown
[1] **Kanał**, „Tytuł filmu”, 2024-05-01.
    [YouTube](https://www.youtube.com/watch?v=ID) ·
    plik: `transkrypcje/Kanał/2024-05-01 - Tytuł.txt`
```

## Szybki start dla nowego tematu

```bash
python3 .opencode/skills/transcript-topic-research/scripts/topic_search.py \
  --topic <slug> --label "<Etykieta>" --pattern '<rdzeń>' \
  --out transkrypcje/_tematy/<slug>.md
```
