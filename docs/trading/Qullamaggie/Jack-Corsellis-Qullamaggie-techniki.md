# Jack Corsellis o strategii Qullamaggie

## Opracowanie technik pod implementację systemu tradingowego

**Wersja:** 1.0 · **Data:** 2026-10-19  
**Źródła:** 31 transkrypcji filmów z kanału [Jack Corsellis](https://www.youtube.com/@JackCorsellis) (2022-11-21 → 2026-10-06), wymienionych w sekcji 12.  
**Zakres:** techniki Qullamaggie w interpretacji i wykonaniu Jacka Corsellisa: screening, setupy, **metody wejścia**, stop loss, zarządzanie pozycją i wyjścia. Dokument jest podstawą do implementacji algorytmu, nie poradą inwestycyjną.

**Oznaczenia:**

- **S1–S31** — identyfikatory źródeł; pełne URL-e w sekcji 12 oraz w tabelach przykładów.
- **b.d.** — brak danych w transkrypcji.
- **†** — liczba, ticker lub data niepewne z powodu automatycznego rozpoznawania mowy (ASR).
- **Q** — Kristjan Kullamägi (Qullamaggie); **Jack** — Jack Corsellis, autor filmów.

> **Ważne:** transkrypcje są automatyczne. ASR regularnie zniekształca tickery („Cypher” = CIFR, „Tempest AI” = TEM, „call week” = CRWV, „Sandis” = SNDK), gubi kropki dziesiętne („24751” = 247.51) i miesza nazwy spółek. Wszystkie liczby należy traktować jako materiał do weryfikacji na danych rynkowych, nie jako gotowe prawdy. Tam, gdzie to możliwe, liczby zostały przeliczone i oznaczone.

**Spis treści:** 0. Streszczenie · 1. Zakres i źródła · 2. Model strategii · 3. Screening · 4. Continuation breakout · 5. High Tight Flag · 6. Episodic Pivot · 7. ORB — mechanika wejścia · 8. Ryzyko i zarządzanie · 9. Przykłady · 10. Model implementacyjny · 11. Sprzeczności i luki · 12. Źródła · 13. Zastrzeżenie.

---

## 0. Streszczenie dla implementatora

1. **To nie jest system „kup dobry wykres”.** To system handlu **leading momentum stocks**: akcja po dużym impulsie, w silnym trendzie, z kontrakcją zmienności, którą kupuje się w momencie rozpoczęcia kolejnego „stopnia” wzrostowego. Qullamaggie nazywa to „stairs”: impuls → konsolidacja → impuls (S4).
2. **Dwa zasadnicze setupy long:** **continuation breakout** (flaga, VCP, cup & handle, Darvas box, HTF) oraz **Episodic Pivot** (gap na wynikach/newsie). **ORB nie jest setupem** — jest metodą wejścia w setup zidentyfikowany na daily (S10).
3. **Domyślne wejście 2025–2026:** **5-min ORB** — high pierwszej świecy 9:30–9:35 ET, zakup w pierwszych sekundach po 9:35. 1-min tylko dla wyjątkowo silnych gapów; 15/30-min do wolniejszych akcji i swingów (S22, S29, S31).
4. **Stop:** **low of day − 0,01 USD** (Q/ORB), alternatywnie **low trigger bara** (flagi/HTF, adaptacja Jacka). Stop ma być **1/4–1/2 ADR20**, maksymalnie ~2/3; twardy soft-cap **5%** (S4, S9, S19).
5. **Pozycja:** ryzyko **0,25–0,75% konta** na trade (Q: 0,3–0,5%), maks. **25% konta** w jednej akcji (S4, S9).
6. **Free roll:** sprzedaj **1/2 przy 1R** albo **1/3 przy 2R** (opcjonalnie 1/4 przy 3R), następnie trailing **10 EMA / 21 EMA** (swing) lub **5-min 6 EMA** (day trade) (S9, S10, S22).
7. **Jakość:** 12-punktowa checklista; minimum **9/12**, cel **10/12+**. Punktuje trend, RS, pierwszą świecę, grupę, extension od 10 EMA, opór, historię ORB i news (S25, S28).
8. **Kontekst jest częścią systemu:** market regime (QQQ/SPY), **group/theme confirmation** (ETF + 2–5 spółek), intraday RS vs index. „Lone strength = no trade” (S14, S22, S27).
9. **Edge jest asymetryczny, nie wysoko skuteczny:** win rate Q ~20–25% (S4); liczą się małe straty i kilka 10–50R. System nie może optymalizować samego win rate.
10. **Największe ryzyko implementacyjne:** brak jednego sztywnego zestawu parametrów, dyskrecja w „tightness”, „overhead resistance” i „group”, oraz sprzeczne wersje między latami. Sekcja 11 zbiera te rozbieżności.

---

## 1. Zakres, źródła i metoda

### 1.1. Co jest przedmiotem opracowania

Dokument opisuje **sposób, w jaki Jack Corsellis stosuje i tłumaczy strategię Qullamaggie** na podstawie własnych transakcji, backtestów i skanów. Nie jest to dosłowny zapis reguł Qullamaggie: Jack wielokrotnie mówi, że bierze „części” strategii i adaptuje je do własnego stylu, zwłaszcza do day tradingu i ORB (S9, S10, S25).

Rozróżnienie na potrzeby implementacji:

| Warstwa | Qullamaggie (kanon) | Jack (wykonanie) |
|---|---|---|
| Setupy | continuation breakout, episodic pivot, parabolic short | continuation breakout, HTF, EP; short pominięty |
| Wejście | ORB 1/5/60 min lub buy stop przez pivot | ORB 1/5/15/30 min; buy stop limit 0,5–1% nad trigger barem |
| Stop | low of day, ≤ ATR/ADR | low of day **lub** low trigger bara / 5-min 6 EMA |
| Zarządzanie | 1/3–1/2 po 3–5 dniach, BE, trailing 10/20 MA | free roll 1R/2R tego samego dnia, trailing 5-min 6 EMA / 10–21 EMA |
| Filozofia | małe straty, duże zyski, cierpliwość | to samo + 12-point checklist i group/theme confirmation |

### 1.2. Źródła i ich charakter

31 filmów można podzielić na:

- **przeglądy strategii Q** (S4, S5, S6, S9) — definicje setupów, statystyki, przykłady historyczne;
- **tutoriale ORB** (S8, S10, S13, S16–S24, S28–S31) — mechanika wejścia, zarządzanie, case studies;
- **HTF i skany** (S1–S3, S15, S26) — definicja flagi, parametry, screening;
- **EP** (S5, S11) — gap-up, jakość pierwszej świecy, zarządzanie;
- **5-star / high ADR** (S6, S7) — jakość setupu i zmienność;
- **narzędzia** (S26, S29, S30) — TradingView indicator, screener, alerty, workflow.

### 1.3. Ograniczenia materiału

- **Brak jednolitej specyfikacji.** Jack mówi wprost: „thinking trader setup”, „no one size fits all”; parametry zależą od charakteru akcji i rynku (S16, S22).
- **Zmiana preferencji w czasie.** W 2024 uważał 30-min ORB za najlepszy; w 2025–2026 używa głównie 5-min (S10 vs S19–S31).
- **Brak twardych progów** dla: gap %, ceny akcji, risk per trade w ORB, minimalnego RVOL, definicji „tight”.
- **Sprzeczne liczby** dla tego samego trade’a (np. TSLA 2024: 247.50 vs 247.55; PRTS: stop 8.47 vs 8.57) — patrz sekcja 11.
- **Wiele przykładów nie ma daty sesji.** W tabeli przykładów oznaczono to jako „film RRRR-MM-DD; data sesji b.d.”.

### 1.4. Słownik pojęć

| Pojęcie | Znaczenie |
|---|---|
| **ORB** | Opening Range Breakout — wejście przez high pierwszej świecy sesji na wybranym TF |
| **ORH** | Opening Range High — high pierwszej świecy |
| **LOD / HOD** | Low / High of Day — dzienne ekstremum sesji regularnej |
| **PDH / PDL** | Prior Day High / Low |
| **PMH** | Premarket High |
| **ADR20%** | 20-day Average Daily Range percentage, bez gapów |
| **R** | Initial risk per share = entry − stop |
| **RVOL** | Relative volume vs 30-bar average |
| **RS** | Relative strength vs index / grupa |
| **TML** | True Market Leader (O’Neil/CANSLIM) |
| **EP** | Episodic Pivot — gap na earnings/newsie |
| **HTF** | High Tight Flag |
| **VCP** | Volatility Contraction Pattern |
| **Trigger bar** | Wąska, niskowolumenowa świeca na MA, której high jest pivotem |
| **Free roll** | Sprzedaż części pozycji przy 1R/2R tak, by reszta była risk-free |

---

## 2. Model strategii

### 2.1. Cztery etapy każdego trade’a

Jack powtarza w niemal każdym filmie sekwencję **identify → control → mitigate → optimize** (S9, S11, S18):

1. **Identify** — znajdź leading stock i setup na daily; oceń trend, RS, grupę, bazę, ADR, catalyst.
2. **Control** — zaplanuj entry i stop tak, aby ryzyko było małe względem ADR i potencjału; dobierz rozmiar.
3. **Mitigate** — free roll: zdejmij część przy 1R/2R, przenieś stop do BE, pozostaw „risk-free runner”.
4. **Optimize** — trailing 10/21 EMA, 5-min 6 EMA, „lower the day”, wyjście na change of character.

### 2.2. Trzy koszyki akcji

Jack klasyfikuje każdą akcję do jednego lub kilku koszyków (S8, S9, S22):

1. **TML — True Market Leader** (O’Neil/CANSLIM): duże earnings, sales, rosnące szacunki, nowy produkt/technologia, institutional sponsorship, blisko 52-week/ATH, często młode IPO.
2. **Momentum leader:** wysokie **20-day ADR%** (5%+, idealnie 8–10%+), duża płynność, historia gwałtownych trendów, czasem high short interest.
3. **Group/theme leader:** lider grupy z świeżym katalizatorem (crypto, semis, AI infrastructure, clean energy, quantum, space, miners).

**Reguła decyzyjna:** akcja musi być w co najmniej jednym koszyku, a najlepiej w dwóch–trzech. „Tier 3” = brak wyraźnej przewagi → odpuść (S9).

### 2.3. Market regime

- **Idealny long:** NASDAQ Composite / QQQ w uptrendzie; 10 EMA powyżej 20 EMA, 20 EMA powyżej 50 SMA, wszystkie rosną (S4).
- **Zły regime:** 10/20 EMA opadają, 10 jest pod 20, index robi lower highs/lower lows → high failure rate; wtedy cash, małe rozmiary lub day trading (S4, S25).
- **Choppy market:** Jack przechodzi na szybsze realizowanie zysków i day-trading; „there's times to sit and be a real swing position trader and there's times to be much more of a day trader” (S25).
- **Intraday:** jeśli QQQ/SPY robi LOD, a akcja nie potrafi zrobić HOD, nie kupuj „against the algo tide”; jeśli akcja robi HOD, gdy index robi LOD — to najsilniejszy sygnał RS (S16, S22).

### 2.4. Charakter edge

- Qullamaggie: **win rate ~20–25%**, najlepsze lata <35%; 80% zysku z ~20% trade’ów (S4, S9).
- Badanie Jacka 500 breakoutów: średni initial stop **4,95%**; średni wzrost do pierwszego close poniżej 10 EMA **28,82%**, poniżej 21 EMA **42%**; R/R **5,71** i **7,82** (S4).
- Badanie 60 „perfect” 5-star breakoutów 1976–2022: średni stop **~3,5%**; średni zysk do close <10 EMA **98%**, <21 EMA **148%**, <50 SMA **194%**; średnio **26/45/72 dni** (S6).
- Wniosek: **nie optymalizuj win rate**. Optymalizuj expectancy i rozkład R; system musi przetrwać serię 10–20 strat z rzędu.

### 2.5. Czego w materiale nie ma

- **VWAP** nie występuje ani razu w 14 analizowanych filmach ORB; nie dodawaj go jako warunku „bo Jack tak mówi” (S8–S24).
- Brak twardego **progu gap %** dla ORB (jest tylko „materialny catalyst”).
- Brak **progu ceny akcji** dla ORB.
- Brak **risk per trade jako % konta** w filmach ORB; jest „size down” przy szerokim stopie i „hit it hard” przy wąskim (S22).
- Brak **win rate / profit factor** dla samego ORB.

---

## 3. Uniwersum i screening

### 3.1. „5 kryteriów” — wersja 2026

Najprostszy, powtarzany w 2026 skan (S29, S30, S31):

1. `Close > 21-day EMA`
2. `Close > 50-day SMA`
3. `Close > 200-day SMA`
4. `50-day average dollar volume > 250 mln USD`
5. `20-day ADR% > 2%`

Wyniki zależą od dnia i bazy: Jack pokazuje **6,5–6,7 tys. → 142 / 99 / 134** po ADR >2%, oraz **44 / 56 / 59** po ADR >4% (S29–S31). Dla porównania filtr `ADDV > 100 mln` dawał **3379** wyników, dlatego 250 mln to „crème de la crème” (S29).

**Wersja 2024** (S9): `>21 EMA`, `>50 SMA`, `>200 SMA`, `ADDV > 100 mln`, `ADR > 2,25%` → **99** spółek z ~5–5,5 tys.

### 3.2. ADR% — najważniejszy filtr zmienności

Definicja (S22, S28):

```
ADR20% = średnia z 20 sesji: (High_t - Low_t) / Close_{t-1} * 100
```

**Bez gapów** — liczy się zakres intraday, nie gap (S28, S31).

Progi z materiału:

| Kontekst | Próg | Źródło |
|---|---|---|
| Minimum „wolniej niż index” | 1,5–2× ADR indeksu; QQQ/SPY ~1% → **~2–3%** | S6, S7 |
| „Real juicy” | **3–4% minimum**, idealnie **5–6–8–10%+** | S4, S7 |
| Momentum leader | **>5%**, idealnie **8–10%+** | S22 |
| Screen 2025 (HTF) | **>6%** | S15 |
| Screen 2026 (ORB) | **>2%** (lub >4% dla węższej listy) | S29–S31 |

**Ważne:** wysoki ADR to „fuel tank”. Jeśli akcja ma ADR 8%, a stop 2%, to 1R wymaga ruchu 2% — czyli 1/4 przeciętnego dziennego zakresu. To zwiększa szansę na free roll (S28).

### 3.3. Płynność, cena, spread

- **Momentum leader:** wysoki dollar volume; COIN >1 mld USD/dzień = market orders akceptowalne (S8).
- **W filmach ORB:** 30-day average volume **250–500 tys. akcji**, average dollar volume **10/25/50 mln USD** — jako przykłady, nie jedna reguła (S22).
- **Małe biotech/microcap:** spread potrafi kosztować 3% w jedną stronę (6% round trip); Jack odrzuca wiele spółek jeszcze przed analizą wykresu (S5).
- **Cena:** brak twardego progu w ORB. W skanie 5-star startuje od **$1**, ale sam sugeruje podniesienie do **$10** i dodanie dollar volume, żeby odciąć penny stocks (S6).

### 3.4. Skan „5-star” (2023)

Filtry (S6):

- USA, ~5 000 spółek;
- `Close > $1`;
- `Close > 200 SMA`;
- `50-day average volume > 100 000`;
- `3-month gain > 50%`;
- `Close > 50 SMA`;
- wynik: **~64 spółki**;
- sortowanie/filtrowanie: **3-month RS ranking = 99**, alternatywnie „najbliżej 52-week high”, plus YoY sales growth;
- ręczny przegląd chartów (1–2 na rząd).

### 3.5. Skan HTF

| Wersja | Filtry | Wynik |
|---|---|---|
| 2022-12-30 (S2) | US ~5 200; 50d volume >200k; 3-month gain >75% **lub** 1-month >75%; price >200 SMA | ~80 |
| 2025-06-07 (S15) | price >50 SMA; price >200 SMA; 20-day ADR >6%; 50-day dollar volume >50 mln USD; sort po ADR | zależny od dnia |

### 3.6. Group/theme confirmation

To nie jest opcjonalny filtr „ładnie wygląda”. Jack traktuje go jako główny czynnik poprawy win rate (S27):

- wybierz **ETF sektora/tematu** + **2–5 spółek siostrzanych**;
- wszystkie powinny być zielone na ORB / mieć podobny first bar;
- wybierz **najsilniejszą** spółkę w grupie, nie „lone ranger”;
- jeśli ETF/2–3 siostry są słabe → **no trade**.

Przykłady map (S22, S24, S27):

| Spółka | Grupa / ETF | Siostry |
|---|---|---|
| BABA | Chiny / FXI | PDD, BIDU, BILI, JD |
| GOLD / KGC | miners / GDX | NEM, GFI, AU, KGC |
| OKLO / SMR | clean energy | NNE, SMR, OKLO |
| IONQ | quantum | QUBT, RGTI, QBTS |
| COIN | crypto | RIOT, MARA, IREN |
| XOM | oil & gas / XLE | CVX, XLE |
| AMD | semis | ASML, SMCI, MU, WDC, STX |
| CIFR | crypto miners/data centers | RIOT, MARA, HUT, IREN, APLD, WULF |

### 3.7. Tabela skanów

| Narzędzie / film | Filtry | Setup | Wynik |
|---|---|---|---|
| Stock Screen Hero 2022 (S2) | >200k vol; 3M/1M gain >75%; >200 SMA | HTF | ~80 |
| Stock Screen Hero 2023 (S6) | >$1; >200 DMA; >100k vol; 3M gain >50%; >50 DMA; RS 99 | 5-star | ~64 |
| Stock Screen Hero 2023 (S7) | high 20-day ADR; strong RS; 21 SMA | High ADR | b.d. |
| Stock Screen Hero 2025 (S15) | >50/200 SMA; ADR >6%; ADDV >$50M | HTF | b.d. |
| MarketSurge/TradingView 2024 (S9) | >21 EMA; >50/200 SMA; ADDV >$100M; ADR >2,25% | ORB/breakout | 99 |
| TradingView 2026 (S29–S31) | >21 EMA; >50/200 SMA; ADDV >$250M; ADR >2% | ORB | 99–142 (ADR >2%), 44–59 (ADR >4%) |

---

## 4. Setup 1: Continuation breakout / flaga

### 4.1. Definicja

Akcja po **dużym impulsie** („flag pole”) buduje **kontrakcję** (flagę, pennant, VCP, cup & handle, Darvas box, wedge), a następnie wybija się górą. Kupujemy **początek kolejnego stopnia**, nie dołek (S4, S5, S6).

### 4.2. Warunki ilościowe

| Element | Reguła | Źródło |
|---|---|---|
| Wcześniejszy impuls | **+30% do +100%+** w ostatnich 1–3 miesiącach | S4, S5 |
| Długość bazy | **2 tygodnie – 2 miesiące** (czasem 8–10 tygodni) | S4, S5 |
| Struktura | **higher lows**, narrowing range, volatility contraction | S4, S5 |
| MA | cena powyżej rosnących **10 EMA i/lub 21 EMA**, często 50 SMA | S4, S5 |
| Volume | wysycha w bazie; breakout na wyższym wolumenie | S4, S5 |
| RS | mocna linia RS, 52-week highs, odporność w dni spadkowe | S4, S6 |
| ADR | minimum ~3%, idealnie 5–10%+ | S4, S7 |
| Płynność | >100–200k akcji, brak szerokich spreadów | S2, S6 |

**Uwaga:** tightness i głębokość korekty są oceniane wizualnie; Jack nie podaje jednego procentowego progu dla zwykłej flagi (S6). Dla HTF podaje twarde 20–25% lub <2× ADR (S15).

### 4.3. Trigger bar

To najważniejszy element wykonawczy (S1, S3, S5):

- **wąski range** i **wąski real body**;
- najlepiej **inside day**, ale nie musi;
- położony **na 10 EMA** (najczęściej) lub **21 EMA**; przy długiej bazie na 50 SMA;
- **wolumen poniżej 30-day average** (im niżej, tym lepiej);
- high trigger bara = pivot; low = miejsce na stop;
- trigger bar w środku bazy, który jest „wedging up” i oddalony od 10 EMA, **nie jest** trigger barem.

### 4.4. Wejście

**Wariant A — buy stop limit (preferowany przez Jacka do flag):**

- buy stop = high trigger bara (lub high ostatnich 1–2 świec, jeśli daje lepszy stop);
- limit = **0,5–1% powyżej pivotu** (S5: „between 0.5% and 1%”; S6: „invariably within 0.5%”);
- stop = **low trigger bara − 0,01 USD**, jeśli możliwe także pod 10 EMA i pod okrągłym poziomem;
- średni stop: **1,5–4%** na zwykłych flagach, **3–7%** na HTF (S1, S5);
- order planowany dzień wcześniej; limit chroni przed slippage, ale może nie zfillować runaway (S8).

**Wariant B — ORB:**

- entry przez high pierwszej świecy 1/5/15/30 min;
- stop = LOD − 0,01 USD;
- wybierany, gdy buy stop limit daje stop > ADR lub gdy akcja jest zbyt szybka (S15, S20).

**Wariant C — pullback?**

Jack zasadniczo **nie kupuje pullbacku do MA** w sensie swingowym; czeka na breakout trigger bara lub ORB. Wyjątkiem jest jego własny **IML (intraday mean reversion long)** przy 10 EMA oraz opcjonalne doładowanie przy higher low w pyramidingu (S5, S22). Nie mylić z kupowaniem spadającej akcji.

### 4.5. Stop i zarządzanie

- Stop: trigger low − 0,01 USD (Jack) lub LOD (Q/ORB).
- Risk: **1/2–2/3 ADR**, single digits, „preferably sub 5%” (S6).
- Free roll: **1/3 przy 2R** (najczęstszy), opcjonalnie 1/2 przy 1R lub 1/4 przy 3R.
- Po free rollu: **1/3 close <10 EMA**, **1/3 close <21 EMA**, opcjonalnie część na 50 SMA.
- Przy parabolic move: **„lower the day”** — stop na low kolejnych dni.
- Wyjście natychmiastowe na **bearish synchronicity / change of character**: szeroka świeca, open near high, close near low, volume >30-day average.
- „Better to sell 10% too late than 100% too early” (S5).

### 4.6. Przykłady flag

- **PRTS 2020** — HTF; entry 8,92, stop 8,47 (5,5%); free roll 1/3 przy 9,93; pierwsza sprzedaż ~+30%, reszta ~+55% (S1).
- **AMD (film 2023)** — trigger 39,61, stop 39,03 (1,49%); +19% do close <21 EMA (S6).
- **PRTS (film 2023)** — trigger 8,84, stop 8,57 (3,05–3,16%); lower-the-bar ~+57% (S5, S6).
- **QCOM (film 2023)** — trigger 50,11, stop 47,98 (4,27%); +39% do 10 EMA (S5).
- **NVAX (film 2023)** — trigger 12,58, stop 12,14 (3,5%); free roll 1/2 przy 13,02 (S6).
- **BTC (film 2023)** — entry 47, stop 46 (1,93%); +73% do close <10/20 MA; „lower the day” ~+249% (S5).

> Daty sesji dla tych przykładów nie są podane; znany jest rok lub data publikacji filmu. Pełna tabela w sekcji 9.

### 4.7. Cechy do implementacji

- detekcja bazy: `prior_run >= 30%` w 20–65 sesji; `base_len` 10–40 sesji; `higher_lows >= 2`; `range_contraction` (średni range ostatnich 5 sesji / pierwszych 5 < 0,7); `volume_dryup` (średni wolumen bazy / wolumen impulsu < 0,7);
- detekcja trigger bara: `range <= 0,6 * ATR20`, `body <= 0,5 * range`, `close > 10 EMA`, `abs(close-EMA10)/EMA10 < 0,02`, `volume < 0,8 * avg30`;
- pivot = high trigger bara; entry = pivot + tick; stop = low trigger bara − 0,01; risk ratio = risk% / ADR20.

---

## 5. Setup 2: High Tight Flag (HTF)

### 5.1. Definicja

Najostrzejsza wersja continuation breakout (S1, S15):

- **flag pole:** wzrost **≥100% w mniej niż 8 tygodni**;
- **korekta:** peak-to-trough **≤20–25%**; w 2025 dodatkowo **<2× ADR20**;
- **czas bazy:** zwykle **2,5–8 tygodni**; 10–12 tygodni rzadko, wtedy można użyć 50 SMA;
- **higher lows** i **lower highs** — zakres zwęża się;
- wolumen w bazie **wysycha**;
- cena powyżej wszystkich kluczowych MA w trakcie flag pola; w bazie respectuje 10 EMA, potem 21 EMA;
- **52-week highs w bazie** i na RS line = ekstremalna siła;
- RS line stroma, ~45°.

Cytat (S1): „a stock that has made a move of 100 or greater in a period of less than eight weeks and then the peak to trough decline of that high tight flag base is not greater than 20 25”.

### 5.2. Sześć typów świec w bazie

Jack wymienia (S1):

1. **trigger bar** — najważniejsza, na końcu bazy;
2. **multiple tight range bars** — absorpcja supply / brak supply;
3. **shakeout demand tails** — wytrząsanie słabych rąk pod MA;
4. **gap-down reversal bars** — gap down, powrót, silny close;
5. **bullish synchronicity bars** — szeroki range, open low, close high, high volume;
6. **bullish ease of movement bars** — lekki ruch w górę, często na 52-week high.

### 5.3. Wejście i stop

- Preferowany **buy stop limit** przez high trigger bara; limit **0,5–1%** powyżej.
- Stop pod low trigger bara, pod 10/21 EMA, pod okrągłym poziomem.
- Średni stop **3–7%**, „never double digits, preferably sub 5%” (S1).
- Przy ADR 11% stop z trigger bara wyszedłby ~11% — wtedy Jack przechodzi na **5-min ORB** lub IML przy 10 EMA, ze stopem LOD (S15).
- ORB wymaga: MACD positive, intraday RS akcji i grupy, bullish 5-min candle z wolumenem, blisko 10 EMA (S15).

### 5.4. Zarządzanie

- Free roll **1/3 przy 2R** (standard).
- Po free rollu: 1/3 close <10 EMA, 1/3 close <21 EMA, opcjonalnie 50 SMA.
- Przy ekstremalnym ruchu **lower the day**.
- Wyjście na change of character.
- Sizing: w przykładzie HTF Jack bierze ~15% konta na nową pozycję, z czego ~5% zdejmuje szybko, ~10% zostawia na trend (S5).

### 5.5. SMR — 2025-06-06 (pełny przykład)

(S15)

- flag pole: **+127% w <8 tygodni**;
- pullback: **19,5%**; ADR **11,07%**; 19,5% < 2×11,07% = 22,14% → warunek spełniony;
- entry: **31,70** na 5-min ORB (ze slippage);
- stop: **30,73** = LOD − 0,01;
- risk: **3,06%**; risk/ADR ≈ **0,28** („nearly a quarter”);
- brak podanego wyniku; Jack targetuje potencjał +100%.

### 5.6. PRTS 2020 — klasyk

(S1)

- flag pole: **+821%**;
- pullback: **26%** (nieco powyżej sztywnego progu 20–25%; autor stosuje „common sense”);
- entry: **8,92**; stop: **8,47** (5,5%);
- free roll: 1/3 przy **9,93** (+11%) lub dynamicznie przy 9,67 (+8%);
- wyjścia: 1/3 ~+30% (close <10 EMA), reszta ~+55% (close <21/50);
- przy wejściu niżej i trzymaniu 21 EMA autor mówi nawet o **~650%** (ASR/niepewne).

### 5.7. Implementacja HTF

```
pole_return = (peak / trough - 1) * 100
pole_days = sessions(trough -> peak)
if pole_return < 100 or pole_days > 40: reject
pullback = (peak - trough_after_peak) / peak * 100
if pullback > 25 or pullback > 2 * adr20: reject
base_days = sessions(peak -> breakout)  # 10-40
higher_lows = count(pivot_lows increasing) >= 2
lower_highs = count(pivot_highs decreasing) >= 1
volume_dryup = avg_vol(base) / avg_vol(pole) < 0.7
ma_ok = close > ema10 and close > ema21 and close > sma50
trigger = last tight bar on ema10/21 with volume < avg30
entry = high(trigger) + tick (or 5m ORB high)
stop = min(low(trigger), lod) - 0.01
```

---

## 6. Setup 3: Episodic Pivot (EP)

### 6.1. Definicja

EP to **gwałtowna zmiana wyceny na nowej informacji** (S4, S5):

- reakcja na **earnings** (beat + raise guidance, backlog, nowy kontrakt);
- **FDA approval / phase 3 data**;
- **government contract**;
- **partnership / collaboration**;
- **sympathy play** (NVIDIA → semis);
- **hot theme** (AI, vaccines, EV, crypto);
- czasem bez widocznego newsa — „stock could be gapping up because it's in a hot theme”.

### 6.2. Warunki ilościowe i jakościowe

| Element | Reguła | Źródło |
|---|---|---|
| Gap | **>10%** (najlepiej znacznie więcej) | S4 |
| Volume | huge relative volume; często **average daily volume w pierwszych 15–30 min** | S4 |
| Baza | multi-month base przed gapem (CELH 4 mies., IOT 4 mies., SMCI ~2 mies., ENPH 4 mies.) | S5 |
| Poziom | gap **ponad high bazy**, often 52-week high; ponad overhead resistance | S4, S5 |
| MA | powyżej wszystkich kluczowych MA; ideał: rosnące 10/21/50/100/200 | S4, S5 |
| Trend | **nie** w długoterminowym downtrendcie; **nie** gap w declining 50/200 SMA | S4, S5 |
| Fundamenty | triple-digit EPS/sales growth, ROE, institutional sponsorship, duży beat | S5 |
| Płynność | unikać microcapów 7–90 mln USD, spreadów 3%+, first-minute dollar volume <50k | S5 |
| Win rate | „high-risk strategy, expected win rate under 50%”; większość „cowboy EP” nie działa | S5 |

### 6.3. Wejście

- **ORB 1-min lub 5-min:** entry przez high pierwszej świecy; stop LOD − 0,01.
- 1-min: ciaśniejszy stop, więcej whipsaw; 5-min: kompromis.
- 15/30/60-min: gdy pierwsze minuty nie dają dobrego R/R; często stop > ADR → odrzuć.
- **Pora:** identyfikuj przed open; entry w pierwszych minutach sesji; TSLA 2024 o **9:35:17**.
- **Jakość pierwszej świecy:** open near low, close near high, wide range, high relative volume; unikaj doji/supply shoot.
- **Slippage:** zakładaj 0,2–0,5%; na microcapach więcej.

### 6.4. Zarządzanie

- Free roll: **1/2 przy 1R** (TSLA 2024), **1/3 przy 2R** (wariant 2023), **1/4 przy 3R**.
- Po free rollu: trailing **10 EMA / 21 EMA** albo **lower the day**.
- Dla TSLA 2024 Jack mówi, że 10/21/50 nie działały dobrze; najlepsze było „low the day” (S11).
- Duże, płynne EP (CELH, IOT, SMCI, ENPH) można trzymać na intermediate trend; microcappy szybko zdejmować.
- Failure exit: powrót pod LOD/trigger; jeśli po stopie resetuje się nowy ORB, można próbować ponownie.

### 6.5. TSLA — 2024-10-24 (pełny przykład)

(S11, S13)

- premarket: **+14%** po earnings;
- 5-min: pierwsza świeca open ~244, trade down, reversal, close w **upper 90–95% range**, huge relative volume;
- entry: **247,50** (IBKR 9:35:17; na chartcie 247,51);
- stop: **242,64** = LOD − 0,01; risk **1,97%**; **$4,87/share**;
- ADR: **3,45%**; 1,97% ≈ **2/3 ADR**;
- free roll: sprzedaż **połowy** przy **252,38** o 11:18:50 = **+1R**;
- reszta: plan „low the day, low the day, low the day”;
- kontekst: TSLA above all key daily MAs, duża baza boczna, ale jeszcze nie przebiła base highs.

W filmie S13 ten sam trade ma entry **247,55** i risk **1,98%** — różnica 5 centów, prawdopodobnie inny fill/zaokrąglenie.

### 6.6. Inne przykłady EP

**Pozytywne / klasyczne:**

- **CELH** (film 2023; data sesji b.d.): 4-mies. baza; gap 108 → 118; 1-min ORB 122,12, stop 118,25, risk 3,17 (~2,6%); 5-min 123,36, stop 118,25, risk 4,14 ≈ ADR; EPS surprise 106%, sales 259 mln (S5).
- **IOT** (film 2023; data sesji b.d.): 4-mies. baza, base high 22,59; gap ~19 → 23; 1-min 23,10, stop 22,19, risk 3,94; 5-min 23,14, stop 22,19, risk ~4,11 (S5).
- **ENPH** (film 2023; data sesji b.d.): 4-mies. baza, pivot 220,99; gap 217 → 235/236; 5-min 239,40, stop 228,99, risk 4,35 > ADR → ostrzeżenie (S5).
- **SMCI** (film 2023; data sesji b.d.): 2-mies. baza, base high 119,24; gap 106 → 116; 1-min stop 114,31, risk 3,31; 5-min 118,76, stop 114,31, risk 3,75; później **>+100%** od EP (S5).
- **SHOP (2023-05):** EP; 1-min 55,94/53,88 (3,68%), 5-min 56,00/53,88 (3,79%), 60-min 59,31/53,88 (9,16% ≈ 2× ADR) → tylko 1/5-min (S4).
- **UBER (2023-05):** EP, ale słabszy (downtrend, base highs); 1-min 35,10/34,23 (2,46%), 5-min 35,24/34,23 (2,86%), 60-min 2,86% (S4).

**Negatywne / edukacyjne:**

- **BMR:** 1-min stop ~12%, 5-min 22% → stopped out; morał: nie brać setupu z 22% stopem (S5).
- **AI (C3.ai):** 1-min ORB 37,75, stopped −3,45; drugi ORB też stopped; 5-min 37,75/36,17, −4,22; ADR 13% (S5).
- **TRVN:** downtrend, fail na 200 SMA, cap 11 mln; 1-min risk 9,5%, 5-min 16,5% → „probably not” (S5).
- **MBOT:** downtrend, pump-and-dump; reset ORB 1,98/1,60, risk 19,5% → odpuść (S5).
- **NNOX:** FDA clearance; pierwszy ORB stop −5%, reset 9,79/8,55, risk 12–13%, ADR 10,72% (S5).
- **IMGN:** gap 6 → 10,50; 5-min 11/10,30, risk 6,5%, ADR 5,59%; fast sell-off, nearly stopped, recovered (S5).

### 6.7. Implementacja EP

```
gap_pct = (open - prev_close) / prev_close * 100
if gap_pct < 10: reject
volume_ratio = volume_first_15m / avg_daily_volume
if volume_ratio < 0.5: reject
base = detect_base(prior 20-120 sessions)
if not gap_above(base.high, prior_day.high, premarket.high): reject
if close < sma50 or close < sma200: reject
if sma200_slope < 0 and gap_into_sma200: reject
catalyst = classify(earnings, fda, contract, sympathy, theme)
quality_score = fundamentals + base_quality + ma_alignment + overhead_clearance
entry = high(first_5m_bar) + tick
stop = lod - 0.01
```

---

## 7. ORB — mechanika wejścia

### 7.1. Rola ORB

ORB to **order entry method**, nie setup. Najpierw na daily musi istnieć setup (flaga, HTF, VCP, trigger bar, EP, gap-up), potem ORB służy do wejścia (S10).

### 7.2. Warianty czasowe

| Wariant | Opening range (ET) | Trigger | Charakter | Kiedy |
|---|---|---|---|---|
| **1-min** | 9:30–9:31 | high pierwszej 1-min świecy | najszybszy, najwięcej false breakouts, najciaśniejszy stop | bardzo silne gap-upy (COIN, AMD, UBER) |
| **5-min** | 9:30–9:35 | high pierwszej 5-min świecy | **domyślny 2025–2026**; balans trend/stop | większość trade’ów |
| **15-min** | 9:30–9:45 | high pierwszej 15-min świecy | mniej false breakouts, szerszy stop | swing, wolniejsze akcje (DXYZ, SMCI, HOOD 2024) |
| **30-min** | 9:30–10:00 | high pierwszej 30-min świecy | najmniej false breakouts, najszerszy stop | swing, 2024 „best” wg Jacka (LYFT, KGC, AEM, SLV, AMD) |
| **60-min** | 9:30–10:00* | high pierwszej świecy | rzadko; często stop > ADR | teoretyczny |

\* W S4 Jack zauważa, że pierwsza świeca „60-min” na jego wykresie jest w praktyce 30-minutowa (9:30–10:00), bo sesja ma 6,5 h i świece są alignowane do pełnej godziny. W implementacji należy jawnie zdefiniować alignację barów, a nie polegać na etykiecie „60-min”.

**Zmiana poglądów:** 2024-07-20 Jack mówi, że 30-min jest najlepszy, 15-min „slightly behind”, 5-min daje więcej false breakouts (S10). Od 2025 używa głównie 5-min, bo pozwala złapać cały intraday trend przy wąskim stopie (S19–S31). **Default implementacyjny: 5-min; 15/30-min jako fallback i do swingów.**

### 7.3. Timeline sesji

- **9:30–9:35** — pierwsza 5-min świeca = **signal bar**;
- **9:35** — entry, gdy cena przebija high signal bara; wchodzi się **kilka sekund** po zamknięciu pierwszej świecy, nie czeka na close drugiej;
- przykłady: TSLA 2025-09-24 entry **9:35:06 ET**; RIOT **9:35:11 ET** (S22);
- 15-min ORB — entry od 9:45; 30-min — od 10:00; 1-min — od 9:31;
- day trade exit: **15:55 ET** (S21, S22).

### 7.4. Jakość pierwszej świecy

„Bullish synchronicity” = pozytywny price action + high relative volume (S8, S17):

1. **wide range** na tle poprzednich świec;
2. **open near low / close near high**;
3. **szerokie real body**, mały upper wick (brak supply shoot);
4. **high relative volume** vs 30-bar average;
5. gap up i open na low = immediate demand.

Hierarchia (S17, S21):

| Grade | Wygląd | Interpretacja |
|---|---|---|
| **A++** | open = LOD, close = HOD, no/small upper wick, wide body, high RVOL | instantaneous demand |
| **A** | open near low, close near high, small upper wick | bardzo silny demand |
| **B** | shakeout demand tail (lower wick), potem strong close | demand wygrał, ale była chwilowa podaż |
| **C** | doji, small body, open w środku range | brak przewagi; false breakout |
| **D** | supply shoot, weak close, gap-and-fade | podaż dominuje; **nie brać** |

**Ważne:** nie trzeba „mega volume”. W S21 Jack mówi, że nie ma obsesji na punkcie wolumenu na ORB; zbyt duży volume może rozszerzyć świecę tak, że stop/ADR się rozjeżdża.

### 7.5. Trigger i typ zlecenia

- **Trigger:** buy stop **powyżej high pierwszej świecy**; entry bar to następna świeca.
- **Buy stop + stop loss** — preferowane, gdy jesteś przy ekranie; stop od razu w systemie.
- **Buy stop limit** — chroni przed slippage, ale może nie zfillować runaway:
  - COIN 2024: buy stop limit nie fill; ORB by fill (S8);
  - AMD 2024: buy stop 176,84, limit 177,72; nie fill, bo gap poszedł bez pullbacku (S8).
- **Market order** — tylko dla very liquid large caps; dla małych spółek spread/slippage zabija (S8).
- **Slippage:** oczekiwany, ~0,5%; w backteście zakładaj fill powyżej triggera 0,2–0,5% i stop poniżej LOD 0,1–0,3% (S16, S22).
- **Nie czekaj na close entry bara.** Entry jest w momencie przebicia high; jeśli natychmiast wraca pod high signal bara, traktuj jako failed breakout.

### 7.6. Zwykły ORB vs gap-up ORB

**Zwykły (pivot) ORB:**

1. daily setup: flaga, cup & handle, Darvas box, VCP, trigger bar, shakeout tail;
2. cena musi najpierw wybić pivot (prior day high, high trigger bara, high shakeout tail);
3. entry przez high pierwszej świecy;
4. stop LOD − 0,01.

**Gap-up ORB:**

1. gap z powodu earnings, news (S&P inclusion, buyback, FDA phase 3, kontrakt) lub group/sympathy;
2. gap często „czyści” pivot (prior day high, base high, premarket high);
3. entry przez high pierwszej świecy;
4. wymagane: above all key daily MAs, najlepiej gap z bazy w 52-week/ATH, limited overhead;
5. ORB pozwala wejść w akcję, która przy klasycznym breakoutcie byłaby już za extended.

**Gap-up ORB nie oznacza „kup każdy gap”:** liczy się materialność katalizatora i **reakcja rynku**, nie tylko komunikat firmy (S13).

### 7.7. 12-point checklist

(S25, S28)

1. Stock above all key daily MAs (10/21/50/65/200).
2. Relative strength on the daily chart vs index.
3. Stronger technical position vs prior session high/low vs index (esp. prior session open).
4. Intraday relative strength at the ORB signal vs index.
5. Opening candle opens very near low and closes very near high.
6. Group/theme intraday RS at the ORB signal vs index.
7. Stock stronger than others in its group/theme on the ORB.
8. At entry, stock **<1× 20-day ADR% from 10 EMA**.
9. Prior character of successful ORBs.
10. No significant logical resistance within **1R**.
11. Intraday RS vs index on breakout through high of ORB signal (entry candle).
12. Fresh news reacted to positively.

**Scoring:** 9/12 = **B** (minimum), 10/12 = **A**, 11–12/12 = **A+ / star**. Score wpływa na sizing (S25).

**Wyjątek:** XOM 2026-07-13 dostał 10/12 mimo ceny poniżej 50/65 MA, bo reclaim 10/21, theme RS, prior ORB character i news były wystarczające (S26). Checklista dopuszcza counter-trend ORB w liderze grupy, jeśli reszta się zgadza.

### 7.8. Relative strength i group

- Dla tech: **QQQ**; dla non-tech: **SPY**.
- Porównuj pierwszą 5-min świecę: stock open near low/close near high, a index supply shoot/weak close → stock stronger.
- W trakcie trade: stock robi **new HOD**, gdy index robi **new LOD** = najsilniejszy sygnał (S16, S20).
- Stock trzyma się 5-min 6 EMA, gdy index jest poniżej 5-min 21 EMA = intraday RS.
- **Nie kupuj laggarda:** jeśli index robi new highs, a stock dopiero „teraz ja” — to nie leading stock.
- **Lone strength = no trade.** BABA: „if FXI first 3 candlesticks looked like this, I would not have taken the position” (S14).

### 7.9. Przykład porównania 1/5/60-min — SHOP, SMCI, UBER (2023-05)

(S4)

| Ticker | 1-min entry/stop | Risk | 5-min entry/stop | Risk | 60-min entry/stop | Risk | ADR |
|---|---|---|---|---:|---|---:|---|---:|
| SHOP | 55,94 / 53,88 | 3,68% | 56,00 / 53,88 | 3,79% | 59,31 / 53,88 | 9,16% | 4,29% |
| SMCI | 118,22 / 114,32 | 3,30% | 118,76 / 114,32 | 3,74% | 128,90 / 114,32 | 11,31% | 5,77% |
| UBER | 35,10 / 34,23 | 2,46% | 35,24 / 34,23 | 2,86% | 35,24 / 34,23 | 2,86% | 3,60% |

**Wniosek:** 60-min daje stop 2–3× ADR i jest odrzucany; 1-min daje najciaśniejszy stop, ale wymaga natychmiastowej reakcji; 5-min jest kompromisem. To jest empiryczne uzasadnienie defaultu 5-min.

### 7.10. Pseudokod ORB

```python
# 9:35 ET
signal = bar("09:30", "09:35")
trigger = signal.high + tick
stop = session_low - 0.01
risk_pct = (trigger - stop) / trigger * 100
risk_ratio = risk_pct / adr20

if not signal.close_location >= 0.7: skip
if signal.upper_wick / signal.range > 0.3: skip
if signal.rvol < 1.2: downgrade
if risk_pct > 5: skip
if risk_ratio > 0.67: skip  # chyba że catalyst A+ i size down
if not above_all_daily_mas: skip
if not intraday_rs(stock, qqq, signal): skip
if not group_confirmed(theme, signal): skip
if overhead_within_1R(trigger): skip
if extension_from_ema10(trigger) > 1.0: skip

place buy_stop(trigger, stop=stop)
```

### 7.11. Wybór metody wejścia — tabela decyzyjna

| Sytuacja | Preferowane wejście | Alternatywa | Uwagi |
|---|---|---|---|
| EP / gap-up na earnings lub newsie | **5-min ORB** przez high pierwszej świecy | 1-min ORB, jeśli pierwsza świeca jest bardzo silna i stop <1/3 ADR | 15/30-min tylko gdy 5-min stop jest za szeroki; wtedy często odpuść |
| Flaga / VCP / cup & handle | **buy stop limit 0,5–1% nad high trigger bara** | 5-min ORB, jeśli akcja jest zbyt szybka | buy stop limit może nie zfillować runaway |
| HTF przy ADR >10% | **5-min ORB** | IML przy 10 EMA | stop z trigger bara byłby ~1× ADR → za szeroko |
| ORB w leading stock bez gapu | **5-min ORB** | 15/30-min dla wolniejszych akcji | wymagany prior pivot / above key MAs |
| Wejście missed / stop na 1-min | **reset na 15/30-min** | odpuść | nie ścigaj po extension; UBER 2024 |
| Bardzo płynna mega-cap | market order + stop | buy stop | slippage mniejszy, ale nadal modeluj |
| Mała spółka / szeroki spread | **buy stop limit** | odpuść | spread >2–3% = przewaga kosztowa |

**Zasada nadrzędna:** entry ma być tak dobrane, aby **risk/ADR ≤ 0,5** (twardy limit 0,67), a stop nie był szerszy niż 5%. Jeśli żadna metoda nie spełnia tego warunku, setup jest odrzucany — nie „dopasowuje się” stopu do pozycji.

---

## 8. Ryzyko, pozycja i zarządzanie

### 8.1. Stop loss

| Sytuacja | Stop | Źródło |
|---|---|---|
| ORB / EP | **LOD − 0,01 USD** | S8–S31 |
| Flaga / HTF przez buy stop limit | **low trigger bara − 0,01**, pod 10/21 EMA, pod round number | S1, S5 |
| Day trade 2026 | LOD **lub** pod **5-min 6 EMA** (often half opening bar range) | S27, S28 |
| LOD na round number | 2–3 centy poniżej | S22 |
| Tuż pod LOD key MA | stop pod MA | S22 |

**Stop nie może być szerszy niż ADR/ATR.** Idealnie **1/4–1/2 ADR**; akceptowalne do **2/3**; >1× ADR = „out of whack” (S4, S19, S22).

### 8.2. Risk/ADR — rzeczywiste wartości

| Trade | Risk% | ADR% | Risk/ADR | Źródło |
|---|---:|---:|---:|---|
| AMD 1-min (2024) | 0,56 | 4,06 | 0,14 | S8 |
| COIN 1-min (2024) | 1,93 | 7,09 | 0,27 | S8 |
| SMCI 15-min (2024) | 3,18 | 10,69 | 0,30 | S8 |
| DXYZ 15-min (2024) | 4,15 | 17,87 | 0,23 | S12 |
| LYFT 30-min (2024) | 2,89 | 6,75 | 0,43 | S8 |
| NVDA 5-min (2024) | 2,43 | 3,54 | 0,69 | S8 |
| UBER 1-min (2024) | 2,00 | 3,00 | 0,67 | S8 |
| PLTR earnings 5-min (2024) | 3,10 | 5,40 | 0,57 | S13 |
| APP 5-min (2024) | 5,42 | 7,63 | 0,71 | S13 |
| SMMT 5-min (2024) | 8,65 | 6,31 | 1,37 | S13 |
| CRWV 5-min (2025) | 2,55 | 14,20 | 0,18 | S16 |
| HOOD 5-min (2025) | 1,13 | 4,83 | 0,23 | S18 |
| TSLA 5-min (2025) | 1,55 | 3,47 | 0,45 | S19 |
| TEM 5-min (2025) | 2,76 | 7,95 | 0,35 | S20 |
| INTC 5-min (2025) | 1,30 | 4,30 | 0,30 | S23 |

**Obserwacja:** większość dobrych trade’ów ma ratio **0,14–0,45**, czyli ciaśniej niż werbalna reguła „half to 2/3”. W implementacji traktuj **0,5 jako soft ceiling**, a nie cel (S22).

### 8.3. Position sizing

- Qullamaggie: **0,3–0,5%** konta na trade (rzadko >0,5%); małe konto **1–2%** (S4).
- Jack: **0,25–0,75%**, średnio **~0,5%** (S9).
- Max **25% konta** w jednej akcji (S4, S9).
- Nowa pozycja w przykładzie HTF: **~15% konta**, po free rollu ~5% zdjęte, ~10% na trend (S5).
- Przy bardzo ciasnym stopie (AMD 0,56%, HOOD 1,13%) można „hit it hard”; przy szerokim (SMMT 8,65%, APP 5,42%) **size down** (S22).

```python
risk_dollars = equity * account_risk_pct / 100
shares = floor(risk_dollars / (entry - stop))
shares = min(shares, floor(equity * max_position_pct / 100 / entry))
shares = min(shares, floor(max_adv_pct / 100 * adv20 / entry))
```

### 8.4. Free roll — matematyka

`R = entry - stop` (risk per share). Sprzedaż ułamka `f` przy `m×R` daje risk-free, gdy:

```
f * m = 1 - f  =>  f = 1 / (m + 1)
```

| Poziom | Frakcja | Przykład |
|---|---|---|
| 1R | **1/2** | TSLA 2024 (S11), COIN 2024 (S9): half @ 1R |
| 2R | **1/3** | AMD / PRTS: 1/3 @ 2R |
| 3R | **1/4** | opcjonalnie |

Po free rollu stop → breakeven. „Being risk-free creates a carefree state of mind” (S9).

### 8.5. Trailing

**Intraday (day trade):**

1. **5-min 6 EMA** — preferowany; exit po **back-to-back closes** poniżej + undercut low of bar lub MACD bearish (S22, S28).
2. **5-min 21 EMA** — alternatywny; RKLB/DELL trzymały go całą sesję (S24).
3. **5-min 60 MA** — wolniejszy; „encapsulates the entirety of the move”.
4. **Lower the bar** — przy parabolic move / >2× ADR: stop pod low każdej kolejnej 5-min świecy.
5. **LOD** — dla day trade, zwłaszcza PLTR.
6. **MACD** — potwierdzenie, nie samodzielny sygnał.

**Swing (daily):**

- **pierwszy close poniżej 10 EMA** — podstawowy exit;
- **21 EMA** — gdy akcja jest short-term extended;
- **50 SMA** — rzadko, mała część „for the 50”;
- **low of day** — „low the day, low the day” dla szybkich akcji (TSLA, PLTR);
- podział: 1/3 na 10 EMA, 1/3 na 21 EMA, 1/3 na 50 SMA (S5).

### 8.6. Wyjścia

- Free roll 1/2 @1R lub 1/3 @2R.
- 1/3 close <10 EMA; 1/3 close <21 EMA; opcjonalnie 50 SMA.
- **Change of character / bearish synchronicity** — natychmiast: szeroka świeca, open high, close low, volume >30-day average (S9).
- **Lower the day** przy ekstremalnym ruchu.
- Day trade: **15:55 ET**.
- Event risk: nie trzymaj longa przez weekend/earnings, jeśli nie masz cushion (S16).
- „Better to sell 10% too late than 100% too early” (S5).

### 8.7. Day trade vs swing — drzewo decyzyjne

**Zostaw swing, jeśli:**

- akcja closed strong, above all daily MAs;
- intraday RS utrzymane do close;
- group/theme strong;
- market supportive, nie extended;
- masz profit cushion i free-rolled part.

**Zamknij day trade, jeśli:**

- supply shoot / lower highs;
- 5-min 6 EMA traci z back-to-back closes;
- index robi LOD, a stock nie może;
- akcja zrobiła 1–2× ADR i „fuel” się kończy;
- event risk / hostile market.

**Nie mieszaj:** ORB nie mówi „trzymaj 3 dni”. O horyzoncie decyduje feedback z rynku i regime (S22, S25).

---

## 9. Przykłady

### 9.1. Przykłady z jawną datą sesji

> Data = data sesji podana przez autora. „b.d.” = brak danych. Ceny bez kropki dziesiętnej w transkrypcie zostały zinterpretowane (np. „24750” = 247,50); liczby niepewne oznaczono †.

| Data sesji | Ticker | Setup / wariant | Wejście | Stop / risk | Wynik / zarządzanie | Źródło |
|---|---|---|---|---|---|---|
| 2024-10-24 | **TSLA** | EP / earnings gap + 5-min ORB | **247,50** (9:35:17) | **242,64** (LOD−0,01); **1,97%**; ADR 3,45% | half **252,38** (11:18:50) = 1R; reszta „lower the day” | [S11](https://www.youtube.com/watch?v=YyNOhw2OLuI), [S13](https://www.youtube.com/watch?v=7GcJR1RiwYA) |
| 2024-12-04 | **DXYZ** | flag/trigger bar + 15-min ORB | **~44,1†** | **~42,3†** (LOD−0,01); **4,15%**; ADR 17,87% | **+50% w ~3 sesje** (>10R); ~$40 → $60–70 | [S12](https://www.youtube.com/watch?v=37Kj_zlKHtA) |
| 2025-06-06 | **SMR** | HTF + 5-min ORB | **31,70** | **30,73**; **3,06%**; ADR 11,07% | b.d.; risk/ADR ~0,28 | [S15](https://www.youtube.com/watch?v=DzeXCwziHls) |
| 2025-06-13 | **CRWV** | 5-min ORB, leading stock | **146,22** | **142,49**; **2,55%**; ADR 14,2% | max **+8,42%** (LOD→HOD); exit na supply shoot / 5-min 21 EMA | [S16](https://www.youtube.com/watch?v=4rlgyUB7jZs) |
| 2025-07-25 | **HOOD** | 5-min ORB, leading stock | **102,19** | LOD; **1,13%**; ADR 4,83% | max **+5,28%** (LOD→HOD); exit near HOD | [S18](https://www.youtube.com/watch?v=LknH6QfRoXM) |
| 2025-08-06 | **TSLA** | 5-min ORB, tight daily base | **311,75** | **306,92**; **1,55%**; ADR 3,47% | b.d.; intraday RS vs QQQ | [S19](https://www.youtube.com/watch?v=GnpEucZpz8Y) |
| 2025-09-11 | **TEM** (Tempus AI) | 5-min ORB | **81,65** | **79,40**; **2,76%**; ADR 7,95% | max **+14,5%** (LOD→HOD, ~2× ADR) | [S20](https://www.youtube.com/watch?v=gIs99JG_Izo) |
| 2025-09-19 | **PLTR** | 5-min ORB | b.d. | LOD; **1,3%**; ADR 4,28% | b.d. | [S21](https://www.youtube.com/watch?v=1f0lrPz4I4Q) |
| 2025-09-19 | **QUBT** | 5-min ORB, quantum | b.d. | LOD | max **+28%** (LOD→HOD, ~4× ADR); risk/ADR b.d. | [S21](https://www.youtube.com/watch?v=1f0lrPz4I4Q) |
| 2025-09-19 | **OKLO** | 5-min ORB, clean energy | b.d. | LOD | max **+18%** (LOD→HOD, ~2,2× ADR); NNE jako sibling | [S21](https://www.youtube.com/watch?v=1f0lrPz4I4Q) |
| 2025-09-19 | **GOLD** | 5-min ORB, miners | b.d. | LOD | max **+8%** (LOD→HOD, ~4× ADR); open at low | [S21](https://www.youtube.com/watch?v=1f0lrPz4I4Q) |
| 2025-09-24 | **TSLA** | 5-min ORB | **9:35:06 ET** | LOD | b.d. | [S22](https://www.youtube.com/watch?v=goxPDqDlh9s) |
| 2025-09-24 | **RIOT** | 5-min ORB, crypto | **9:35:11 ET** | LOD; ADR 6,89% | max **+13%** (LOD→HOD, ~2× ADR) | [S22](https://www.youtube.com/watch?v=goxPDqDlh9s) |
| 2025-09-25 | **PLTR** | 5-min / quasi-ORB | **9:49 ET** | LOD | b.d. | [S22](https://www.youtube.com/watch?v=goxPDqDlh9s) |
| 2025-09-25 | **ONDS** | 5-min / quasi-ORB | **9:47 ET** | LOD | b.d. | [S22](https://www.youtube.com/watch?v=goxPDqDlh9s) |
| 2025-09-25 | **CRWV** | 5-min ORB | b.d. | LOD | b.d. | [S22](https://www.youtube.com/watch?v=goxPDqDlh9s) |
| 2025-11-28 | **INTC** | 5-min ORB | b.d. | LOD; **1,3%**; ADR 4,3% | **+~7%** by close; held swing | [S23](https://www.youtube.com/watch?v=WmrCrQbIqHw) |
| 2026-05-08 | **RKLB** | 5-min ORB, earnings gap z Darvas box | **89,75** | LOD | **+17%** from ORB by close | [S24](https://www.youtube.com/watch?v=-uJ9QMZ5ZcQ) |
| 2026-05-08 | **DELL** | 5-min ORB, leading stock | **238,64** | LOD | **+8–9%** from ORB by close | [S24](https://www.youtube.com/watch?v=-uJ9QMZ5ZcQ) |
| 2026-06-22 | **AMD** | 5-min ORB + semis group | b.d. | LOD | b.d.; group confirmation | [S27](https://www.youtube.com/watch?v=zZls8f2At9k) |
| 2026-06-22 | **CIFR** | 5-min ORB + crypto/data-center group | b.d. | LOD | b.d.; group confirmation | [S27](https://www.youtube.com/watch?v=zZls8f2At9k) |
| 2026-07-06 | **CRDO** | 5-min ORB | b.d. | LOD; ADR 11,35% | exit ~**13%** (>1× ADR); score **10/12** | [S25](https://www.youtube.com/watch?v=tPgKH0P11Dg) |
| 2026-07-13 | **XOM** | 5-min ORB, oil & gas theme | b.d. | LOD | score **10/12 = A**; b.d. | [S26](https://www.youtube.com/watch?v=oEycNytDvf4) |
| 2026-07-24 | **AAPL** | 5-min ORB, day trade | b.d. | LOD / 5-min 6 EMA; ADR 2,67% | exit **~333,50**; move **4%** (~1,5× ADR); score 10/12 | [S28](https://www.youtube.com/watch?v=PsRpkYWjEJ0) |
| 2026-09-03 | **CRCL** | 5-min ORB | b.d. | LOD | b.d. | [S29](https://www.youtube.com/watch?v=_19ZQz7e6XE) |
| 2026-09-03 | **PLTR** | 5-min ORB | b.d. | LOD | b.d. | [S29](https://www.youtube.com/watch?v=_19ZQz7e6XE) |
| 2026-09-03 | **SPCX** | 5-min ORB | b.d. | LOD | b.d. | [S29](https://www.youtube.com/watch?v=_19ZQz7e6XE) |
| 2026-09-04 | **SNDK** | 5-min ORB + trigger bar | b.d. | LOD | b.d. | [S29](https://www.youtube.com/watch?v=_19ZQz7e6XE) |
| 2026-09-04 | **SKHY** | 5-min ORB + shakeout tail | b.d. | LOD | b.d. | [S29](https://www.youtube.com/watch?v=_19ZQz7e6XE) |
| 2026-09-04 | **MU** | 5-min ORB | b.d. | LOD | b.d. | [S29](https://www.youtube.com/watch?v=_19ZQz7e6XE) |
| 2026-09-16 | **SPCX** | 5-min ORB | b.d. | LOD | b.d. | [S30](https://www.youtube.com/watch?v=BLuTBAX6uOQ) |
| 2026-09-17 | **SMCI** | 5-min ORB | b.d. | LOD | b.d. | [S30](https://www.youtube.com/watch?v=BLuTBAX6uOQ) |
| 2026-09-18 | **MSTR** | 5-min ORB, reclaim 200 SMA | b.d. | LOD | b.d. | [S30](https://www.youtube.com/watch?v=BLuTBAX6uOQ) |
| 2026-09-18 | **CRCL** | 5-min ORB, reclaim 21 EMA | b.d. | LOD | b.d. | [S30](https://www.youtube.com/watch?v=BLuTBAX6uOQ) |
| 2026-09-18 | **SNDK** | 5-min ORB | b.d. | LOD | b.d. | [S30](https://www.youtube.com/watch?v=BLuTBAX6uOQ) |
| 2026-10-02 | **SPCX** | 2-min ORB | b.d. | LOD | b.d. | [S31](https://www.youtube.com/watch?v=IrpZVGY7sVk) |
| 2026-10-05 | **SPCX** | 5-min ORB | b.d. | LOD | b.d. | [S31](https://www.youtube.com/watch?v=IrpZVGY7sVk) |

**Uwagi do tabeli:**

- **SPCX** to ticker z tytułu filmu; w audio Jack mówi „SpaceX”. Traktować jako oznaczenie z materiału, nie potwierdzony publiczny ticker (S29–S31).
- **SKHY** prawdopodobnie SK Hynix ADR; ticker może być inny (S29).
- **CRWV** w S22 jest zapisane przez ASR jako „call week”; to CoreWeave.
- **HOOD** stop w transkrypcie brzmi „104”, ale przy entry 102,19 i risk 1,13% wychodzi ~101,03; w tabeli podano LOD i risk%, nie błędną cenę (S18).
- **DXYZ**: transkrypt gubi kropkę dziesiętną. Risk **$1,83/share = 4,15%** i cena ~**$44** (nie $4); entry/stop w tabeli wyliczono z tych danych i oznaczono † (S12).
- **AAPL** data: film mówi „24th of July”, później „23rd of June” — przyjęto 2026-07-24 (S28).
- **RKLB/DELL** data „last Friday” względem publikacji 2026-05-11 = 2026-05-08 (S24).

### 9.2. Przykłady bez pełnej daty sesji

| Data / źródło | Ticker | Setup | Wejście / stop | Risk | Wynik / uwagi | Źródło |
|---|---|---|---|---|---|---|
| 2020 (S1) | **PRTS** | HTF | 8,92 / 8,47 | 5,5% | 1/3 @ 9,93; ~+30% i ~+55%; do ~650% przy 21 EMA† | [S1](https://www.youtube.com/watch?v=ZLNl5D9YjIQ) |
| 2023-05 (S4) | **SHOP** | EP, 1/5/60-min ORB | 55,94 / 53,88 (1m); 56,00 / 53,88 (5m) | 3,68% / 3,79% | 60-min risk 9,16% → odrzucony; ADR 4,29% | [S4](https://www.youtube.com/watch?v=we5LLjFlHCc) |
| 2023-05 (S4) | **SMCI** | EP, 1/5/60-min ORB | 118,22 / 114,32 (1m); 118,76 / 114,32 (5m) | 3,30% / 3,74% | 60-min risk 11,31% → odrzucony; ADR 5,77% | [S4](https://www.youtube.com/watch?v=we5LLjFlHCc) |
| 2023-05 (S4) | **UBER** | EP, 1/5/60-min ORB | 35,10 / 34,23 (1m); 35,24 / 34,23 (5m) | 2,46% / 2,86% | 60-min 2,86%; ADR 3,6%; słabszy setup | [S4](https://www.youtube.com/watch?v=we5LLjFlHCc) |
| film 2023 (S5) | **CELH** | EP | 122,12 / 118,25 (1m); 123,36 / 118,25 (5m) | 3,17% / 4,14% | klasyczny CANSLIM; EPS surprise 106%; data sesji b.d. | [S5](https://www.youtube.com/watch?v=KOoHYrIY4Kk) |
| film 2023 (S5) | **IOT** | EP | 23,10 / 22,19 (1m); 23,14 / 22,19 (5m) | 3,94% / 4,11% | 4-mies. baza; base high 22,59; data sesji b.d. | [S5](https://www.youtube.com/watch?v=KOoHYrIY4Kk) |
| film 2023 (S5) | **ENPH** | EP | 239,40 / 228,99 (5m) | 4,35% | risk > ADR → ostrzeżenie; data sesji b.d. | [S5](https://www.youtube.com/watch?v=KOoHYrIY4Kk) |
| film 2023 (S5) | **SMCI** | EP | 118,76 / 114,31 (5m) | 3,75% | >+100% od EP; data sesji b.d. | [S5](https://www.youtube.com/watch?v=KOoHYrIY4Kk) |
| film 2024-03-22 (S9) | **COIN** | cup & handle + 5-min ORB | 174,38 / 168,40 | 3,43% | half 180,36 (1R) ~35 min; reszta trail | [S9](https://www.youtube.com/watch?v=9_4HLIKLJyY) |
| film 2024-03-22 (S9) | **AMD** | tight continuation base + 1-min ORB | 180,80 / 179,78 | 0,56% | 1/3 182,84 (2R); supply shoot 120M/$25B | [S9](https://www.youtube.com/watch?v=9_4HLIKLJyY) |
| film 2024-03-22 (S9) | **PLTR** | earnings gap + 5-min ORB | b.d. / LOD | 3,61% | free roll half 21,24 / third 21,98 | [S9](https://www.youtube.com/watch?v=9_4HLIKLJyY) |
| film 2024-03-07 (S8) | **COIN** | cup & handle + 1-min ORB | 171,71 / 168,40 | 1,93% | half @175,02 ~7–8 min → risk-free | [S8](https://www.youtube.com/watch?v=dMITd7mKppU) |
| film 2024-03-07 (S8) | **AMD** | tight base + 1-min ORB | 180,80 / 179,78 | 0,56% | free roll 3–4 min; buy stop limit missed | [S8](https://www.youtube.com/watch?v=dMITd7mKppU) |
| film 2024-03-07 (S8) | **UBER** | buyback gap + 1-min ORB | 75,94 / 74,42 | 2,0% | stopped −2% ~2 min; later 15-min re-entry | [S8](https://www.youtube.com/watch?v=dMITd7mKppU) |
| film 2024-03-07 (S8) | **LYFT** | earnings gap + 30-min ORB | 16,18 / 15,71 | 2,89% | 1R 16,65 not reached; next-day gap | [S8](https://www.youtube.com/watch?v=dMITd7mKppU) |
| film 2024-03-07 (S8) | **NVDA** | earnings gap into ATH + 5-min ORB | ~761 / ~742,2 | ~2,43% | 1R 779,22; free roll ~30 min | [S8](https://www.youtube.com/watch?v=dMITd7mKppU) |
| film 2024-03-07 (S8) | **PLTR** | earnings gap + 5-min ORB | 25,98 / 25,16 | 3,16% | first bar bearish; later reset | [S8](https://www.youtube.com/watch?v=dMITd7mKppU) |
| film 2024-03-07 (S8) | **AVAV** | earnings gap + 5-min ORB | 154,96 / 150,11 | 3,13% | targets 159,81 / 164,66 | [S8](https://www.youtube.com/watch?v=dMITd7mKppU) |
| film 2024-12-26 (S13) | **PLTR** | earnings gap + 5-min ORB | 48,35 / 46,85 | 3,10% | 15-min 5,28%; 30-min 6,09% | [S13](https://www.youtube.com/watch?v=7GcJR1RiwYA) |
| film 2024-12-26 (S13) | **PLTR** | S&P inclusion + 5-min ORB | 33,51 / 32,46 | ~3,13% | 15-min 4,22%; 30-min supply shoot → skip | [S13](https://www.youtube.com/watch?v=7GcJR1RiwYA) |
| film 2024-12-26 (S13) | **APP** | earnings gap + 5-min ORB | 241,16 / 228,09 | 5,42% | 30-min 9,39% → skip | [S13](https://www.youtube.com/watch?v=7GcJR1RiwYA) |
| film 2024-12-26 (S13) | **SMMT** | FDA phase 3 + 5-min ORB | 17,45 / 15,94 | 8,65% | wyjątek; 15/30-min >10% → skip | [S13](https://www.youtube.com/watch?v=7GcJR1RiwYA) |
| 2025 (S14) | **BABA** | flag + 5-min ORB | 143,27 / 139,97 | b.d. | group: FXI/PDD/BIDU/BILI/JD | [S14](https://www.youtube.com/watch?v=Qy2xvA57RX8) |

### 9.3. Przykłady historyczne High ADR (rok podany)

(wybór z [S7](https://www.youtube.com/watch?v=R0sgcovAw80))

| Rok | Ticker | ADR% | Index ADR% | Wynik |
|---|---|---:|---:|---|
| 1986 | **HOV** | 4,80 | 1,31 (Dow) | +62% w 13 sesji |
| 1998 | **EBAY** | 9,25 | 1,80 (S&P) | +175% vs S&P +9% |
| 1999 | **QCOM** | 6,16 | 1,25 (SPY) | +199% do close <21 EMA |
| 2009 | **CELH** | 7,00 | 1,79 (SPY) | +27% w 15 barach† |
| 2018 | **AMD** | 4,77 | 0,68 (S&P) | flag, 52-week highs w bazie |
| 2021 | **GME** | 9,48 | ~1,00 (S&P) | +1600% (short squeeze) |
| 2021 | **LEDS** | 31,00 | b.d. | +281% w 9 sesji |
| b.d. | **CODX** | 22,90 | b.d. | +500% w 4 sesje† |
| 2023 | **NVDA** | 2,84 | 1,19 (NDX) | +56% do close <21 EMA vs NDX +15% |
| 2023 | **ARM** | 7,42 | 0,93 (SPY) | +76% vs SPY +32% (w momencie filmu) |

**Wniosek:** high ADR nie jest gwarancją, ale jest „dźwignią” względem indeksu. Im wyższe ADR, tym większy potencjał i tym ciaśniejszy stop względem ADR można zaakceptować (S7).

---

## 10. Model implementacyjny

### 10.1. Architektura danych

Minimalny zestaw:

| Dane | Rozdzielczość | Zastosowanie |
|---|---|---|
| Daily OHLCV | 1 dzień | trend, MA, ADR, baza, RS, 52w high |
| Intraday OHLCV | 1 min (agregacja 2/5/15/30 min) | ORB, first bar, trailing |
| Premarket | 1 min lub snapshot | gap, PMH, catalyst |
| Earnings calendar | data + surprise | EP, event risk |
| News/catalyst | timestamp + typ | EP, 12-point checklist |
| Sector/theme mapping | ETF + siblings | group confirmation |
| Index data | QQQ/SPY/NASDAQ | RS, market regime |
| Corporate actions | split/dividend | ciągłość cen |

**Strefa czasowa:** wszystkie sesje w **America/New_York**, z obsługą DST. Opening range liczyć od 9:30 ET, nie od czasu lokalnego.

### 10.2. Formuły cech

```python
adr20 = mean((high[i] - low[i]) / close[i-1] for i in last_20) * 100
gap_pct = (open_t - close_{t-1}) / close_{t-1} * 100
rvol_bar = volume_bar / median(volume_same_bar, last_30)
close_location = (close - low) / (high - low)
upper_wick = (high - max(open, close)) / (high - low)
body_ratio = abs(close - open) / (high - low)
prior_run = (high_20 / low_60 - 1) * 100
base_depth = (base_high - base_low) / base_high * 100
range_contraction = mean(range_last_5) / mean(range_first_5)
volume_dryup = mean(volume_base) / mean(volume_pole)
extension_adr = ((entry - ema10) / ema10 * 100) / adr20
risk_ratio = ((entry - stop) / entry * 100) / adr20
overhead_1r = nearest_swing_high(entry) - entry < (entry - stop)
```

### 10.3. Detektory setupów

**Continuation breakout / flaga:**

```python
if prior_run < 30: reject
if not (10 <= base_len <= 40): reject
if higher_lows < 2: reject
if range_contraction > 0.8: reject
if volume_dryup > 0.8: reject
if not (close > ema10 and close > ema21 and close > sma50): reject
if not rs_line_rising: reject
if adr20 < 3: reject
trigger = last_tight_bar_on_ma()
```

**HTF:**

```python
if pole_return < 100 or pole_days > 40: reject
if pullback > min(25, 2 * adr20): reject
if not (10 <= base_len <= 40): reject
if not higher_lows_and_lower_highs: reject
if volume_dryup > 0.7: reject
if not (close > ema10 and close > ema21 and close > sma50): reject
if 52w_high_in_base or 52w_high_on_breakout: bonus
```

**EP:**

```python
if gap_pct < 10: reject
if volume_first_15m / avg_daily_volume < 0.5: reject
if not gap_above(base_high, prior_day_high, premarket_high): reject
if close < sma50 or close < sma200: reject
if sma200_slope < 0: reject
if spread_pct > 2: reject
if market_cap < 100_000_000: reject
if first_bar_quality < B: reject
```

**ORB:**

```python
signal = first_bar(timeframe)
if close_location < 0.7: reject
if upper_wick / range > 0.3: reject
if rvol < 1.2: downgrade
if risk_pct > 5: reject
if risk_ratio > 0.67: reject
if not above_all_daily_mas: reject
if extension_adr > 1.0: reject
if overhead_1r: reject
if not intraday_rs: reject
if not group_confirmed: reject
score = checklist_12()
if score < 9: reject
```

### 10.4. Scoring

**12-point checklist** — implementuj jako 12 binarnych funkcji; każda zwraca 0/1. Suma:

- 9 = B (minimum, mały size);
- 10 = A (normalny size);
- 11–12 = A+ (można zwiększyć size, jeśli risk/ADR < 0,3).

**5-star / high ADR** — nie ma formalnej definicji; w implementacji zastąp ją scoringiem:

- prior run 30–100%+ (0–2 pkt);
- base length i tightness (0–2);
- MA alignment (0–1);
- RS / 52w high (0–2);
- ADR (0–1);
- volume dry-up (0–1);
- catalyst/fundamenty (0–1).

### 10.5. Symulacja egzekucji

- **Buy stop:** jeśli `high_t >= trigger`, fill = `max(trigger, open_t) + slippage`; jeśli gap przez trigger, fill = open + slippage.
- **Buy stop limit:** fill tylko jeśli `low_t <= limit` po triggerze; inaczej anuluj (jak COIN/AMD 2024).
- **Stop loss:** jeśli `low_t <= stop`, fill = `min(stop, open_t) - slippage_stop`; po gap down fill = open - slippage.
- **Partial:** fill po osiągnięciu poziomu R; uwzględnij, że w szybkim ruchu cena może przeskoczyć poziom.
- **Trailing:** licz na close barów, nie na intrabar high/low, jeśli reguła mówi „close below MA”.
- **Slippage:** 0,2–0,5% dla entry; 0,1–0,3% dla stopu; większy dla małych spółek.
- **Koszty:** prowizja + spread; `spread_model = max(0,02%, 0,05 * ADR%)` — kalibrować na danych.

### 10.6. State machine

```
PENDING
  -> SIGNAL_VALID (score >= 9, risk checks)
  -> ORDER_PLACED (buy stop / buy stop limit)
  -> FILLED
  -> INITIAL_RISK (stop = LOD/trigger low)
  -> FREE_ROLLED (partial at 1R/2R, stop -> BE)
  -> TRAILING (5m EMA6 / 10 EMA / 21 EMA / lower day)
  -> CLOSED (stop, target, EOD, change of character)
```

Zdarzenia: `bar_close`, `stop_hit`, `target_hit`, `eod`, `regime_change`, `data_end`.

### 10.7. Parametry do kalibracji

| Parametr | Wartość startowa | Źródło | Pewność |
|---|---|---|---|
| `adr_lookback` | 20 | S22, S28 | wysoka |
| `adr_min_orb` | 2% (screen), 5% (momentum) | S29, S22 | średnia |
| `adr_min_flag` | 3% | S6, S7 | średnia |
| `addv_min` | 100 mln (2024), 250 mln (2026) | S9, S29 | średnia |
| `prior_run_min` | 30% | S4, S5 | wysoka |
| `base_len` | 10–40 sesji | S4, S5 | średnia |
| `htf_pole_min` | 100% w ≤40 sesji | S1, S15 | wysoka |
| `htf_pullback_max` | min(25%, 2×ADR) | S1, S15 | wysoka |
| `ep_gap_min` | 10% | S4 | wysoka |
| `risk_pct_max` | 5% | S8, S22 | średnia |
| `risk_ratio_max` | 0,67 (soft), 0,5 (ideal) | S8, S22 | średnia |
| `entry_slippage` | 0,2–0,5% | S16, S22 | średnia |
| `stop_buffer` | 0,01 USD | wszystkie | wysoka |
| `free_roll_1` | half @1R | S9, S11 | wysoka |
| `free_roll_2` | third @2R | S5, S8 | wysoka |
| `trail_intraday` | 5m EMA6, 2 closes | S22, S28 | średnia |
| `trail_swing` | 10 EMA close | S4, S5 | wysoka |
| `day_exit` | 15:55 ET | S21, S22 | wysoka |
| `checklist_min` | 9/12 | S25, S28 | wysoka |
| `max_position` | 25% equity | S4, S9 | wysoka |
| `account_risk` | 0,25–0,75% | S4, S9 | średnia |

### 10.8. Protokół backtestu

1. **Uniwersum point-in-time:** US common stocks + ADR, cena >$10 (lub >$1 dla wersji 5-star), wyklucz OTC/penny, uwzględnij delistingi.
2. **Dane:** daily + 1-min intraday; earnings dates point-in-time; news timestamp; sector/theme mapping.
3. **Setup labels:** niezależnie testuj flagę, HTF, EP i ORB; nie łącz ich w jeden sygnał.
4. **Fills:** modeluj buy stop/limit, slippage, stop gap-through, partiale.
5. **Metryki:** win rate, avg R, expectancy, profit factor, max DD, exposure, liczba trade’ów, rozkład R, wyniki per regime i per setup.
6. **Walk-forward:** parametry kalibruj na 2–3 latach, testuj na kolejnym roku; nie optymalizuj 12 punktów checklisty na całym okresie.
7. **Sensitivity:** sprawdź, czy wyniki nie zależą od jednego parametru (np. ADR 2% vs 2,25% vs 3%).
8. **Benchmark:** porównaj z buy-and-hold QQQ/SPY oraz z prostym ORB bez filtrów.
9. **Paper trading:** minimum 3–6 miesięcy przed realnym kapitałem.

### 10.9. Checklista wdrożeniowa

- [ ] Dane intraday z poprawną strefą ET i DST.
- [ ] ADR20 liczony bez gapów.
- [ ] Screening 5 kryteriów + ADR.
- [ ] Detektory flagi/HTF/EP z testami jednostkowymi na znanych przykładach.
- [ ] ORB signal bar i entry bar rozdzielone.
- [ ] Model buy stop/limit i slippage.
- [ ] Risk/ADR i position sizing.
- [ ] Free roll i trailing state machine.
- [ ] 12-point checklist z logowaniem każdego punktu.
- [ ] Group/theme mapping i RS vs index.
- [ ] Backtest per setup, per regime.
- [ ] Kill switch przy drawdownie.

### 10.10. Minimalny MVP — kolejność wdrożenia

**Faza 1 — ORB na flagach/EP (najprostsza):**

- daily screen: 5 kryteriów + ADR ≥3%;
- 5-min ORB, first-bar quality, stop LOD, risk ≤5% i risk/ADR ≤0,67;
- position sizing 0,5% konta, max 25%;
- free roll 1/2 @1R, trailing 5-min 6 EMA / 10 EMA;
- backtest tylko long, US, cena >$10, płynność >$50M ADDV.

**Faza 2 — jakość i kontekst:**

- 12-point checklist i scoring;
- group/theme mapping + intraday RS vs QQQ/SPY;
- extension <1× ADR od 10 EMA;
- overhead resistance <1R.

**Faza 3 — setupy swingowe:**

- detektor flagi/VCP;
- detektor HTF;
- detektor EP z earnings/news;
- osobne zarządzanie dla swing vs day.

**Faza 4 — adaptacja:**

- market regime (QQQ 10/20/50);
- day vs swing decision;
- „lower the day” i change-of-character exits;
- walk-forward i paper trading.

---

## 11. Sprzeczności, luki i ryzyka interpretacji

| Obszar | Rozbieżność | Rekomendacja implementacyjna |
|---|---|---|
| Główne MA | 10 SMA vs 10 EMA; 20 SMA vs 21 EMA; 50/65/200 | Użyj 10 EMA, 21 EMA, 50 SMA, 65 EMA, 200 SMA; testuj warianty |
| ORB TF | 2024: 30-min najlepszy; 2025–26: 5-min default | 5-min default; 15/30-min fallback i swing |
| Stop | LOD vs trigger low vs 5-min 6 EMA | LOD dla ORB/EP; trigger low dla flag; 5-min 6 EMA dla day trade |
| Risk/ADR | 1/2–2/3 (2024) vs 1/4–1/2 (2025–26) | Soft ceiling 0,5; twardy 0,67 |
| Free roll | 1/2 @1R vs 1/3 @2R vs 1/4 @3R | Menu; default 1/2 @1R dla ORB, 1/3 @2R dla flag |
| Partial timing | po 3–5 dniach (Q) vs tego samego dnia (Jack) | Zależy od setupu; ORB intraday, flag swing |
| ADR minimum | 3% vs 5% vs 6% vs 2% | 2% screen, 5% momentum, 6% HTF (konfigurowalne) |
| ADDV | 100 mln vs 250 mln | 100 mln dla szerokiego, 250 mln dla wąskiego |
| 5-star | subiektywna; 6/7-star retoryka | Zastąp scoringiem 12 punktów |
| Checklist threshold | S25: minimum 9/12; S26: „at least 10/12” | Ustaw 9 jako hard minimum, 10 jako preferencję i próg podwyższonego size |
| „Above all MAs” | XOM 2026 był poniżej 50/65, dostał 10/12 | Dopuść wyjątek, ale oznacz flagą `counter_trend=True` |
| Gap % | brak progu w ORB; EP >10% | EP 10%; ORB bez progu, ale catalyst + gap above PDH/base high |
| VWAP | nie występuje | Nie dodawaj jako warunku z tego materiału |
| Risk per trade | brak w ORB; 0,25–0,75% w innych | Ustaw 0,25–0,75%, kalibruj |
| Daty i ceny | ASR zniekształca; ten sam trade ma różne liczby | Weryfikuj na danych; loguj wersję źródła |

**Największe ryzyko:** dokument opisuje **dyskrecjonalny system**. Próba zakodowania go jako sztywnego zestawu reguł bez kalibracji może wygenerować wiele fałszywych sygnałów. Najlepsze rezultaty da połączenie:

1. twardych filtrów (MA, ADR, płynność, gap, risk),
2. scoringu (12 punktów),
3. kontekstu (group/theme, RS, regime),
4. adaptacyjnego zarządzania (free roll, trailing, day vs swing).

---

## 12. Źródła

Wszystkie transkrypcje znajdują się w `transkrypcje/Jack Corsellis/`. Linki prowadzą do filmów; data w nawiasie to data publikacji.

| ID | Data | Tytuł | URL |
|---|---|---|---|
| S1 | 2022-11-21 | High Tight Flag Tutorial | https://www.youtube.com/watch?v=ZLNl5D9YjIQ |
| S2 | 2022-12-30 | How to Scan for High Tight Flag Setups in Minutes | https://www.youtube.com/watch?v=f5gZa2aj9IA |
| S3 | 2023-03-30 | Can You Learn the High Tight Flag Pattern in 5 Minutes? | https://www.youtube.com/watch?v=WMyKXoP-ue4 |
| S4 | 2023-05-12 | QULLAMAGGIE Stock Trading Strategy EXPLAINED | https://www.youtube.com/watch?v=we5LLjFlHCc |
| S5 | 2023-06-17 | QULLAMAGGIE Breakout Setups: Flags & Episodic Pivots | https://www.youtube.com/watch?v=KOoHYrIY4Kk |
| S6 | 2023-09-29 | How to Trade & Scan for QULLAMAGGIE 5 Star Breakout Setups | https://www.youtube.com/watch?v=ZFmP6Deefy0 |
| S7 | 2023-12-15 | How to QUICKLY Scan & Trade QULLAMAGGIE PERFECT High ADR% Setups | https://www.youtube.com/watch?v=R0sgcovAw80 |
| S8 | 2024-03-07 | How to Trade Opening Range Breakouts (COIN AMD SMCI...) | https://www.youtube.com/watch?v=dMITd7mKppU |
| S9 | 2024-03-22 | QULLAMAGGIE Stock Breakout Trading Strategy Explained | https://www.youtube.com/watch?v=9_4HLIKLJyY |
| S10 | 2024-07-20 | Can the OPENING RANGE BREAKOUT Help Improve Your Trading? | https://www.youtube.com/watch?v=5teW50jtdMs |
| S11 | 2024-10-25 | Learn to Trade Qullamaggie Episodic Pivots (EPs) | https://www.youtube.com/watch?v=YyNOhw2OLuI |
| S12 | 2024-12-11 | My Member NAILS a MEGA SWING TRADE in DXYZ | https://www.youtube.com/watch?v=37Kj_zlKHtA |
| S13 | 2024-12-26 | Learn My SPECIFIC TRADING STRATEGY for Gap Up ORB | https://www.youtube.com/watch?v=7GcJR1RiwYA |
| S14 | 2025-03-18 | Learn How to Swing & Day Trade the ORB Setup | https://www.youtube.com/watch?v=Qy2xvA57RX8 |
| S15 | 2025-06-07 | HIGH TIGHT FLAG Chart Pattern Tutorial | https://www.youtube.com/watch?v=DzeXCwziHls |
| S16 | 2025-06-16 | Pro Traders LOVE Trading ORB Setups in LEADING Stocks | https://www.youtube.com/watch?v=4rlgyUB7jZs |
| S17 | 2025-06-27 | Learn the TRADING SETUP used by ELITE TRADERS (5-min ORB) | https://www.youtube.com/watch?v=KUrljNxrx7Q |
| S18 | 2025-07-30 | Learn the Trading Setup LOVED by SWING & DAY TRADERS | https://www.youtube.com/watch?v=LknH6QfRoXM |
| S19 | 2025-08-11 | WOW, HUGE TRADE IN TSLA: Learn ORB | https://www.youtube.com/watch?v=GnpEucZpz8Y |
| S20 | 2025-09-17 | ORB Trading Strategy: How to Catch Explosive Breakouts | https://www.youtube.com/watch?v=gIs99JG_Izo |
| S21 | 2025-09-20 | The BEST BREAKOUT Method: How to Trade ORB | https://www.youtube.com/watch?v=1f0lrPz4I4Q |
| S22 | 2025-09-26 | Easiest Trading Setups: ORB & INMERELO | https://www.youtube.com/watch?v=goxPDqDlh9s |
| S23 | 2025-12-03 | HOW TO BUY OPENING RANGE BREAKOUTS | https://www.youtube.com/watch?v=WmrCrQbIqHw |
| S24 | 2026-05-11 | Why Pro Traders LOVE the 5 Minute ORB Strategy | https://www.youtube.com/watch?v=-uJ9QMZ5ZcQ |
| S25 | 2026-07-07 | I Simplified Qullamaggie's Breakout Entry Strategy into 12 Rules | https://www.youtube.com/watch?v=tPgKH0P11Dg |
| S26 | 2026-07-14 | FREE Qullamaggie Inspired Breakout Indicator | https://www.youtube.com/watch?v=oEycNytDvf4 |
| S27 | 2026-07-24 | The 1 Change for How I Improve Win Rate | https://www.youtube.com/watch?v=zZls8f2At9k |
| S28 | 2026-08-04 | How I use Qullamaggie's Breakout Strategy for Day Trading | https://www.youtube.com/watch?v=PsRpkYWjEJ0 |
| S29 | 2026-09-07 | How to Trade Qullamaggie's Breakout Strategy: Indicator, Screener, Alerts | https://www.youtube.com/watch?v=_19ZQz7e6XE |
| S30 | 2026-09-21 | How to Trade Qullamaggie's Breakout Strategy in 30 Minutes a Day | https://www.youtube.com/watch?v=BLuTBAX6uOQ |
| S31 | 2026-10-06 | Learn to Trade Qullamaggie Breakout Strategy in 11 Minutes (SPCX) | https://www.youtube.com/watch?v=IrpZVGY7sVk |

---

## 13. Zastrzeżenie

Dokument ma charakter edukacyjny i implementacyjny. Nie jest rekomendacją inwestycyjną. Przedstawione reguły pochodzą z publicznych filmów i automatycznych transkrypcji, mogą zawierać błędy ASR i nie zostały zweryfikowane na danych rynkowych. Przed użyciem kapitału:

1. zbacktestuj system na danych point-in-time,
2. uwzględnij koszty, slippage i podatki,
3. przetestuj na paper tradingu,
4. ustal twarde limity drawdownu i ryzyka.

Strategia Qullamaggie ma niski win rate i może długo pozostawać w obsunięciu; bez dyscypliny w zarządzaniu pozycją sama selekcja setupów nie wystarcza.
