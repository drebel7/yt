# Mark Minervini — SEPA, Trend Template and VCP

**A methodology reconstruction for algorithmic trading**

**Source corpus:** `docs/trading/Minevrini/` — 10 articles (English, German, Polish) and the Mark Minervini chapter from Jack Schwager's *Stock Market Wizards*.  
**Prepared:** 2026-10-22  
**Purpose:** an implementation reference for screening, signal generation, position sizing, exit logic and backtesting.  
**Disclaimer:** educational material, not investment advice. All rules must be validated on point-in-time data before capital is deployed.

> **A note on spelling:** the repository directory is spelled `Minevrini`; the trader's name is spelled **Minervini**. This document uses the correct spelling in the text and keeps the directory name only in paths.

---

## 0. Scope, sources and confidence

### 0.1 What this document is

This document reconstructs Mark Minervini's trading method — **SEPA (Specific Entry Point Analysis)** — from the material in `docs/trading/Minevrini/`. It is written for a developer or quant who needs to turn the discretionary method into testable code. It therefore contains:

- the exact rules and numbers stated in the corpus;
- the conflicts between sources, resolved explicitly;
- computable definitions for vague chart concepts;
- pseudocode for screening, pattern detection, entry, sizing and exits;
- a catalogue of the setups Minervini uses, separating what is documented from what is inferred;
- every real trade example found in the corpus, with company, ticker and date.

### 0.2 Source corpus

| Source | Language | Type | Main contribution |
|---|---|---|---|
| `chartmill-sepa-explained.md` | EN | Methodology article | Five SEPA elements, Trend Template, fundamentals, catalyst, VCP entry, exits |
| `chartmill-trend-template.md` | EN | Methodology article | Eight Trend Template criteria, KD example |
| `financialtechwiz-vcp.md` | EN | Pattern article | VCP anatomy, four stages, entry, stop, 25%→12%→6% example |
| `financialtechwiz-minervini-strategy.md` | EN | Strategy article | SEPA, Stage Analysis, Trend Template, risk, XLE trade |
| `finermarketpoints-stock-screener.md` | EN | Screening guide | Screening funnel, fundamentals, TradingView implementation, market-health indicator |
| `finermarketpoints-sepa-methodology.md` | EN | Framework article | Stage Analysis, entry types, pivot types, position sizing, assessment, ASX notes |
| `finermarketpoints-vcp-criteria.md` | EN | Checklist | Seven-point VCP checklist, volume dry-up, pivot, Stage 2, RS, earnings, market |
| `finermarketpoints-sepa-vcp-guide.md` | EN | Strategy guide | Four-letter SEPA, track record, VCP, earnings, catalyst, workflow, sizing |
| `kagels-trading-mark-minervini.md` | DE | Strategy/book review | Five SEPA elements, Trend Template, VCP, risk, primary base, book review |
| `sos-minervini-zasady-tradingu.md` | PL | Profile/rules | Ten trading rules, base counting, price floor, no cheap stocks, psychology |
| `Market Wizards - Minevrini.md` | EN | Book chapter | Schwager interview: risk, 10% study, price-action sandwich, ~20 patterns, re-entry |

### 0.3 Confidence labels

Every important rule is tagged:

- **[A] explicit** — stated directly in at least one source, often as a rule or a number.
- **[B] inferred** — a repeatable pattern across sources or examples, but no single explicit definition.
- **[C] ambiguous / implementation choice** — sources conflict, omit the detail, or the rule is discretionary. These are parameters to test, not facts.

### 0.4 Important limitations

1. **The corpus is secondary literature, not Minervini's full books.** Only one primary-source interview (Schwager) is included. The books *Trade Like a Stock Market Wizard* and *Think & Trade Like a Champion* are referenced but not present in full.
2. **Minervini deliberately does not disclose all his patterns.** In the Schwager interview he says he uses about twenty named patterns and refuses to describe them. This document can only reconstruct the documented VCP family and the explicitly mentioned variants.
3. **The corpus contains only two fully identified real examples:** KD (Trend Template) and XLE (VCP). There is no complete trade log with entry, stop, size and exit for a portfolio of stocks. Do not calibrate a backtest on two examples.
4. **Numbers conflict across sources.** The most important conflicts are collected in §23.
5. **The method is predominantly long-only and bull-market-oriented.** Minervini goes to cash in corrections; there is no short-selling module in this corpus. A bear-market module must be built separately, if at all.

### 0.5 How the document is organised

| Part | Sections | Content |
|---|---|---|
| **I. Foundations** | 1–4 | Summary, track record, philosophy, SEPA framework |
| **II. Selection** | 5–8 | Stage Analysis, Trend Template, universe/screening, market regime |
| **III. Setups** | 9–17 | Setup catalogue, VCP, flat base, cup-with-handle, primary base, pullback, failed breakout, base-on-base, pivots/entries |
| **IV. Risk and exits** | 18–19 | Position sizing, portfolio caps, exit framework |
| **V. Implementation** | 20–21 | Algorithmic pipeline, pseudocode, MVP plan, setup comparison |
| **VI. Evidence and validation** | 22–27 | Examples, discrepancies, backtest risks, Qullamaggie comparison, checklist, source map |
| **Appendices** | A–B | Formulas, glossary |

---

## 1. Executive summary — ten points

1. **Only Stage 2.** Minervini buys stocks in a confirmed Stage 2 uptrend. Stage 1 (basing), Stage 3 (topping) and Stage 4 (declining) are not buy candidates. The Trend Template is the mechanical test for Stage 2.
2. **The Trend Template is a qualifier, not a trigger.** Passing all eight criteria means the stock deserves further work. The entry is a separate decision, taken at a specific pivot.
3. **Fundamentals provide the fuel.** Accelerating EPS and revenue, expanding margins, high ROE, positive surprises and revisions. Weak fundamentals can be overridden only by exceptional relative strength (top ~2% of the market).
4. **A catalyst explains why the move can continue.** New product, new management, regulatory change, new market, contract win, industry tailwind. If you cannot state the catalyst in one sentence, skip the trade.
5. **The core setup is the VCP.** Two to six progressively smaller pullbacks, declining volume, a tight final contraction, and a breakout above the pivot on expanding volume.
6. **The pivot is precise.** It is the high of the final contraction, not a vague "breakout zone". Entry is a buy-stop 1–2% above the pivot. Do not chase more than ~5% above it.
7. **The stop is pre-written.** Just below the final contraction low, and never wider than 7–8% from entry. If the structure requires a wider stop, the trade is skipped.
8. **Risk is fixed before entry.** Default 1.0–1.25% of equity per trade, hard cap 2%. Position size is the output of the risk budget, not conviction. Apply a 20–25% position cap as an implementation guard (the corpus gives the risk budget and the 4–8 position concentration, but not an explicit position cap).
9. **Exits are structural, not target-based.** Take a partial at roughly 1R, move to break-even, take another partial at 2–3R, trail the rest with the 10-, 21- or 50-day MA. Never let a winner become a loser.
10. **The market filter overrides the stock signal.** In a correction, even perfect VCPs fail. Go to cash, reduce exposure, or trade only exceptional setups at a fraction of normal risk.

---

## 2. Who Minervini is, and what the track record actually supports

Mark Minervini is a US growth-stock swing trader, author and two-time winner of the US Investing Championship. He is profiled in Jack Schwager's *Stock Market Wizards* (2001). He trades US-listed growth stocks, mostly long, with holding periods from several weeks to several months. He is not a day trader.

| Claim | Value in corpus | Status |
|---|---|---|
| 1997 US Investing Championship | 155% while ~50% invested (Kagels, SOS); 255% (Financial Tech Wiz) | Conflicting; 155% is the more common figure, 255% appears in one source |
| 2021 US Investing Championship | 334.8% in the $1M category | Audited and publicly reported per Kagels |
| Five-year average return | ~220% per year, 33,500% cumulative, one down quarter | Self-reported, not audited like the championship result |
| Typical holding period | Weeks to months | Consistent across sources |
| Style | Long-only growth momentum; cash in corrections | Consistent |
| Win rate | Around 50% in the Schwager interview | Not a fixed system parameter |

**Implementation consequence:** do not use the return figures to calibrate the algorithm. Use them only to understand the return profile: concentrated, long-only, bull-market-biased, with large winners and small controlled losses. The edge is in the asymmetry and the market filter, not in a high hit rate.

---

## 3. Philosophy and sources of edge

### 3.1 Buy strength, not cheapness

- Minervini does not buy low P/E stocks. A low P/E is not a buy reason; a high P/E is not a sell reason. Growth stocks often look expensive because the market discounts future earnings. In the Schwager interview he notes that the biggest winners typically traded at **above-average P/E ratios even before they became big winners**.
- He never buys stocks below **$12**; typically his stocks trade at **$20 or higher**. Low-priced stocks are usually low for a reason.
- He wants **market leaders in leading sectors**, not turnarounds or laggards hoping to catch up.
- A stock making new highs is bullish because it has eliminated the supply of trapped buyers waiting to break even. After a correction, the first leg to new highs often runs very fast.
- In the Schwager interview he describes the fundamental/technical weighting as roughly **fifty-fifty**. Price action is always the trigger, but he might consider a stock with apparently negative fundamentals if its relative price performance is in the **top 2%** of the market, because the price may be discounting a change not yet visible in the reported numbers.

### 3.2 Risk first

- "Containing your losses is 90 percent of the battle, regardless of the strategy." (Schwager)
- "Being wrong is acceptable, but staying wrong is totally unacceptable."
- The stop is a line in the sand, defined before entry. It is never widened. Losing positions are never averaged down.
- The goal is not to be right often; it is to make much more on winners than you lose on losers.
- Minervini's own analysis: capping losses at 10% would have increased his profits by ~70%. His current maximum is tighter, 7–8%.

### 3.3 Asymmetry and concentration

- Average win must be materially larger than average loss; the corpus repeatedly cites a minimum 2:1 reward-to-risk, ideally 3:1.
- Diversification is not protection; it dilutes. Minervini prefers **4–8 high-conviction positions**, not 20–30.
- Position size is determined by the distance to the stop, not by how strongly he believes in the story.

### 3.4 Preparation and re-entry

- Every trade needs a contingency plan: what if it gaps through the stop, what if it stops out and re-forms, what if it runs.
- Getting stopped out is not a reason to abandon a stock. If it sets up again, Minervini will re-enter — sometimes multiple times. A shakeout followed by a reclaim can be a higher-probability trade than the original entry.
- "I would rather get stopped out of a trade five times in a row, taking a small loss each time, than take one large loss."
- Minervini is explicitly against paper trading. Trade small real size — small enough that you can afford the loss, large enough that you feel it. Paper trading teaches the wrong emotional response and creates bad habits. For algorithm validation this means: backtest first, then forward-test with small real capital, not only a simulator.

### 3.5 The "price action sandwich"

Schwager's interview describes Minervini's selection as a sandwich:

1. **Long-term price action** — the Trend Template and Stage Analysis screen.
2. **Fundamental confirmation** — earnings, sales, margins, catalyst.
3. **Short-term price action** — the precise pivot and breakout trigger.

The long-term screen and the fundamentals can be overridden in rare cases, but the short-term price action is always the trigger. This is the conceptual basis for the algorithmic pipeline in §20.

### 3.6 Minervini's ten rules

The Polish profile (`sos-minervini-zasady-tradingu.md`) reproduces a list Minervini published on X. The rules are discretionary, but each has a direct algorithmic translation.

| # | Rule | Algorithmic translation |
|---|---|---|
| 1 | Always use a stop-loss | Every position has a non-null stop before entry |
| 2 | Define the stop-loss before entering | Sizing is computed from the stop, not after the fill |
| 3 | Never risk more than you can gain | Enforce a minimum 2:1 reward-to-risk estimate |
| 4 | Protect decent profits | Partial at +1R and/or +2–3R; move stop to BE |
| 5 | Never let a good profit turn into a loss | `stop = max(stop, entry)` after +1R |
| 6 | Never average down | No adds below the entry price; adds only on confirmation |
| 7 | Never be too bold when you are unlucky | Reduce risk after losses/drawdown; no size escalation |
| 8 | Size up when doing best, down when doing worst | Risk multiplier tied to equity curve and regime |
| 9 | See the worst-case scenario clearly | Model gap risk, slippage and max drawdown |
| 10 | Avoid frequent style changes | Freeze the rule set; change only after out-of-sample evidence |

Rules 1–6 are mechanical and should be enforced by the execution layer. Rules 7–10 are portfolio-governance rules; they belong in the risk overlay, not in the signal generator.

---

## 4. The SEPA framework

SEPA stands for **Specific Entry Point Analysis**. The corpus uses two related decompositions.

### 4.1 Five elements

| # | Element | Question it answers | Failure mode it removes |
|---|---|---|---|
| 1 | **Trend** | Is the stock in a confirmed Stage 2 uptrend? | Buying downtrends, bottoms and laggards |
| 2 | **Fundamentals** | Is the business growing and accelerating? | Technically perfect charts with no institutional fuel |
| 3 | **Catalyst** | Why is the growth happening, and why can it continue? | Temporary tailwinds, "story" stocks with no substance |
| 4 | **Entry** | Is there a specific, low-risk pivot? | Chasing, buying in the middle of a base, entering too early |
| 5 | **Exit** | Where is the stop, and where will profits be taken? | Holding losers, giving back winners, improvised exits |

The order is deliberate: trend filters out most of the market, fundamentals remove most of what remains, the catalyst forces a thesis, the entry gives a day and a price, and the exit defines the risk.

### 4.2 Four-letter variant

Some sources present SEPA as:

- **S** — Specific Entry Point
- **E** — Earnings
- **P** — Price Action
- **A** — Announcement / Catalyst

This is the same framework with the trend element folded into "Price Action". A third variant in the corpus expands SEPA as **Stage, Entry, Pivot, Add** (position sizing). For implementation, use the five-element version: it is more explicit about Stage Analysis and exits, and it makes the position-sizing step a first-class component rather than a hidden "Add".

### 4.3 No partial credit

A stock must satisfy all elements. A perfect VCP without earnings growth is rejected. Strong earnings without Stage 2 are rejected. A great chart with no catalyst is a watchlist candidate at best. The corpus repeats this across sources. The algorithm should therefore use **hard gates**, not a weighted sum that allows one missing element to be compensated by another. The score is only for ranking stocks that already passed the gates.

---

## 5. Stage Analysis

Minervini adapted Stage Analysis from Stan Weinstein. Every stock is in one of four stages.

| Stage | Name | Price structure | Moving averages | Volume | Action |
|---|---|---|---|---|---|
| **1** | Basing / accumulation | Sideways after a decline; no clear trend | 200-day flattens; price oscillates around it | Low, drying up | Watch, do not buy unless a clear Stage 2 transition occurs |
| **2** | Advancing / markup | Higher highs and higher lows | Price above rising 50/150/200; 50 > 150 > 200 | Expands on rallies, contracts on pullbacks | **The only stage to buy** |
| **3** | Topping / distribution | Sideways at highs; rallies fail; volatility rises | 200-day flattens; price whipsaws around MAs | Erratic, heavy on down days | Exit, do not initiate |
| **4** | Declining / markdown | Lower highs and lower lows | Price below falling 200; 50 < 150 < 200 | Heavy on declines | Avoid entirely; no bottom-fishing |

### 5.1 Computable stage classifier

A robust implementation needs hysteresis, because stage boundaries are not exact. The following is a starting point.

```text
def classify_stage(bars, i):
    c      = close[i]
    s50    = SMA(close, 50)[i]
    s150   = SMA(close, 150)[i]
    s200   = SMA(close, 200)[i]
    slope200_1m = s200 / SMA(close, 200)[i-22] - 1
    slope200_3m = s200 / SMA(close, 200)[i-66] - 1

    # Stage 4: clear decline
    if c < s200 and slope200_1m < 0 and s50 < s150 < s200:
        return 4

    # Stage 2: confirmed advance
    if (c > s50 > s150 > s200
        and slope200_1m > 0
        and slope200_3m > 0
        and higher_highs_and_lows(bars, i, 60)):
        return 2

    # Stage 3: after a Stage 2, 200-day flattens, price whipsaws
    if recent_stage_was(2) and abs(slope200_1m) < 0.01 and abs(c / s200 - 1) < 0.10:
        return 3

    # Stage 1: flat 200-day, low volatility, sideways
    if abs(slope200_1m) < 0.01 and abs(c / s200 - 1) < 0.10:
        return 1

    # Transitional / unknown: treat as non-tradeable
    return 0
```

Use a confirmation window (e.g., 5–10 sessions) before changing stage, and never let a single day flip a stock from Stage 2 to Stage 1. The Trend Template is a stricter, binary version of Stage 2; use it as the hard gate and the stage classifier for context and exits.

### 5.2 Why Stage 3 exits matter

Most of Minervini's sell discipline is about detecting the transition from Stage 2 to Stage 3 before the price breaks the stop. Signals include:

- the 200-day MA flattening;
- the stock failing to make new highs while the market does;
- wider and more erratic daily ranges;
- heavy volume on down days;
- relative strength deteriorating (e.g., RS falling from 90+ to 60–70);
- the stock dropping out of the Trend Template.

The algorithm should treat these as **exit warnings**, not just as reasons not to enter.

---

## 6. The Trend Template

### 6.1 Canonical eight criteria

The canonical version, as stated in *Trade Like a Stock Market Wizard* and reproduced by ChartMill, is:

| # | Criterion | Formula | Notes |
|---|---|---|---|
| 1 | Price above the 150-day and 200-day MA | `C > SMA150` and `C > SMA200` | Long-term uptrend |
| 2 | 150-day MA above 200-day MA | `SMA150 > SMA200` | Intermediate trend stronger than long-term |
| 3 | 200-day MA rising | `SMA200[t] > SMA200[t-22]` | At least one month; preferably 4–5 months |
| 4 | 50-day MA above 150-day and 200-day MA | `SMA50 > SMA150` and `SMA50 > SMA200` | Short-term strength |
| 5 | Price above 50-day MA | `C > SMA50` | Short-term uptrend intact |
| 6 | Price at least 30% above 52-week low | `C >= 1.30 * MIN(Low, 252)` | Preferably 100%+ above the low |
| 7 | Price within 25% of 52-week high | `C >= 0.75 * MAX(High, 252)` | Closer is better |
| 8 | Relative Strength rank ≥ 70 | `RS >= 70` | Preferably 80–90+ |

Many online versions omit criterion 6 (30% above the 52-week low) or split criterion 1 into two. The canonical list above is the one to implement. It produces **nine binary tests** if you split every sub-condition; treat them as eight criteria with sub-clauses.

### 6.2 Computable function

```text
def trend_template(ctx):
    i       = ctx.i
    c       = ctx.close
    s50     = SMA(ctx.close, 50)
    s150    = SMA(ctx.close, 150)
    s200    = SMA(ctx.close, 200)
    low52   = MIN(ctx.low, 252)
    high52  = MAX(ctx.high, 252)
    rs      = ctx.rs_rank          # percentile 1..99

    tests = {
        "price_above_50":    c > s50,
        "price_above_150":   c > s150,
        "price_above_200":   c > s200,
        "sma50_above_150":   s50 > s150,
        "sma150_above_200":  s150 > s200,
        "sma200_rising_1m":  s200 > SMA(ctx.close, 200)[i - 22],
        "sma200_rising_3m":  s200 > SMA(ctx.close, 200)[i - 66],   # quality, not hard gate
        "above_52w_low":     c >= 1.30 * low52,
        "near_52w_high":     c >= 0.75 * high52,
        "rs_above_70":       rs >= 70,
    }

    hard = all(tests[k] for k in [
        "price_above_50", "price_above_150", "price_above_200",
        "sma50_above_150", "sma150_above_200", "sma200_rising_1m",
        "above_52w_low", "near_52w_high", "rs_above_70",
    ])
    return hard, tests
```

### 6.3 Relative Strength is not RSI

- **RS rank** compares the stock's price performance with the rest of the universe, expressed as a percentile from 1 to 99. An RS of 90 means the stock outperformed 90% of stocks.
- **RSI** is an oscillator calculated from the stock's own up/down closes. It is not the same metric and must not be used as a substitute.
- IBD's exact RS formula is proprietary. A workable proxy:

```text
rs_raw = 0.40 * return_63d
       + 0.20 * return_126d
       + 0.20 * return_189d
       + 0.20 * return_252d

rs_rank = percentile_rank(rs_raw, universe_rs_raw)   # 1..99
```

Test alternatives: pure 12-month return percentile, and equal-weighted 3/6/12-month return. The exact formula matters less than using a consistent, point-in-time cross-sectional rank. If you use ChartMill, its **CRS** (ChartMill Relative Strength) is a functionally similar percentile; map Minervini's RS ≥ 70 to CRS ≥ 70.

### 6.4 Moving averages are simple, not exponential

The sources explicitly state that the Trend Template uses **simple moving averages**. Do not silently substitute EMAs. The only common EMA exception is the **10-month EMA** used as a market-regime filter (§8), which is a monthly construct.

### 6.5 The template is not a buy signal

The most repeated warning in the corpus: a stock can pass the Trend Template in the middle of an extended run, well past a reasonable entry. The template confirms the trend; the pivot confirms the entry. They are two different decisions, often taken on different days.

### 6.6 Worked example: KD

See §22.1. Kyndryl (KD) passed all eight criteria on the 27 December 2024 chart snapshot: price above all MAs, 50 > 150 > 200, 200 rising, price ~78–81% above the 52-week low, ~4.4% below the 52-week high, RS above 94.

---

## 7. Universe and screening funnel

### 7.1 Hard universe filters

| Filter | Value | Confidence | Comment |
|---|---|---|---|
| Listing | US-listed common stocks; liquid ETFs allowed | B | XLE example is an ETF; keep ETFs in a separate sleeve |
| Price | ≥ $12; preferably ≥ $20 | A | Minervini: "I never buy stocks under $12" |
| Average volume | ≥ 400,000 shares/day; preferably ≥ 1,000,000 | A | Institutional-quality liquidity |
| Dollar volume | ≥ $20M/day as an implementation guard | C | Not stated by Minervini; use to avoid illiquid names |
| Market cap | No hard rule; institutional quality implied | B | Avoid nano-caps and ultra-thin names |
| ADR / country | No explicit rule | C | ADRs are allowed if liquid; test separately |
| Short interest / float | No explicit long filter | C | Relevant for short module only |

The corpus also says Minervini runs a preliminary screen on roughly **10,000 companies** and narrows to about **800 charts** each night, then to **30–40 interesting charts**, and finally to a handful of candidates. That is a useful capacity model: the first screen should cut ~90–95%, the chart review another ~95%, and the entry list to 1–5 names per day.

### 7.2 Fundamental filters

| Metric | Minimum | Preferred | Confidence |
|---|---|---|---|
| Quarterly EPS growth (YoY) | ≥ 20–25% | ≥ 40–50% | A |
| Revenue growth (YoY) | ≥ 15% | ≥ 20–25% | A/B |
| EPS acceleration | Current quarter > previous quarter | 2–3 quarters of acceleration | A |
| Revenue acceleration | Current quarter > previous quarter | Consistent acceleration | B |
| Profit margins | Stable or expanding | Expanding gross/operating/net | A |
| ROE | ≥ 17% | > 17% and rising | A/B |
| Earnings surprises | Positive | Several consecutive beats | A |
| Estimate revisions | Upward | Upward across recent quarters | A |
| Institutional ownership | 20–80% | 30–70%, rising | B |
| Debt / equity | Low | < 30–40% | B |

The corpus uses slightly different thresholds (EPS 20% vs 25%, revenue 15% vs 20%). A practical starting point: **EPS ≥ 25%, revenue ≥ 15%, ROE ≥ 17%**, with acceleration and positive revisions as bonus points. Test the looser 20% threshold separately.

### 7.3 Composite fundamental scores

ChartMill's **HGM (High Growth Momentum)** rating is a 0–10 composite of EPS/sales growth, acceleration, surprise and revisions. The corpus suggests **HGM ≥ 6** as a working filter, with 6–8 being the sweet spot; HGM 10 is often a crowded, fully priced name. ChartMill's **Setup Quality** score (0–10) is a structural complement: 6–9 is the workable range, while 9–10 often means the breakout has already happened. If you do not have HGM, build an equivalent score:

```text
fund_score = 0
fund_score += 0.30 if eps_yoy >= 0.25
fund_score += 0.15 if eps_yoy >= 0.40
fund_score += 0.20 if rev_yoy >= 0.15
fund_score += 0.15 if eps_accelerating
fund_score += 0.10 if margins_expanding_or_stable
fund_score += 0.05 if roe >= 0.17
fund_score += 0.05 if positive_surprise_or_revision
# fund_score in [0, 1]
```

### 7.4 Catalyst checklist

A catalyst is the reason the growth is happening and can continue. The corpus lists:

- new product or product cycle;
- new management;
- new regulatory environment or approval;
- new addressable market;
- contract win;
- market-share gain;
- structural industry tailwind;
- policy change;
- earnings surprise or guidance raise.

**Operational rule:** before a name enters the watchlist, write the catalyst in one sentence. If you cannot, skip it. A chart-only thesis is not a SEPA thesis.

If you use ChartMill, the corpus suggests adding **Industry Strength ≥ 70** as a sector overlay to the Trend Template + HGM screen. It narrows the list and tends to leave the cleanest setups of the week.

For an algorithm, catalyst detection can be approximated with event flags:

```text
catalyst_score =
    0.4 * earnings_surprise_flag
  + 0.3 * guidance_raise_flag
  + 0.2 * material_news_flag
  + 0.1 * hot_sector_flag
```

But the final confirmation should be human-readable. Store the one-sentence thesis in the trade journal.

### 7.5 Screening funnel

| Stage | Rule | Expected count (US) |
|---|---|---|
| 0. Raw universe | All US-listed common stocks + liquid ETFs | ~10,000 |
| 1. Liquidity / price | Price ≥ $12, ADV ≥ 400k, dollar volume ≥ $20M | ~3,000–5,000 |
| 2. Trend Template | All eight criteria pass | 30–50 in a strong bull market; 10–20 neutral; 0–5 in a correction |
| 3. Fundamentals | EPS/revenue/ROE/margins/revisions | 5–20 |
| 4. Pattern | VCP or valid base, pivot defined | 1–5 actionable |
| 5. Entry | Breakout + volume + regime | 0–3 per day |

The number of stocks passing the Trend Template is itself a market-health indicator:

- **30+** — bullish, trade actively;
- **10–20** — neutral, trade selectively;
- **0–5** — bearish, preserve capital.

This is one of the most useful algorithmic breadth signals in the corpus.

### 7.6 Watchlist states

The corpus describes four practical watchlist buckets. They map directly to algorithm states.

| State | Definition | Monitoring |
|---|---|---|
| **Near breakout** | Final contraction, pivot defined, likely to trigger within 1–2 weeks | Daily; alert at pivot |
| **Formation watch** | Second contraction forming, no clear pivot yet | Weekly |
| **Early stage** | Recently cleared a first base, waiting for the first consolidation | Weekly |
| **Research queue** | Passed technical/fundamental filters but catalyst or data still missing | As needed |

Only the "near breakout" bucket should generate intraday alerts. The others are preparation, not signals.

### 7.7 Screening cadence

- **Daily after the close:** run the full screen, update the Trend Template and pattern status, set pivot alerts. Review the 5-year and 1-year chart for context, and the daily chart for the base.
- **Weekly:** review weekly charts, base count, fundamentals, catalysts, and sector leadership.
- **Intraday:** only monitor names already on the watchlist; do not scan for new ideas intraday. Use the intraday chart for execution, not for thesis generation.

The corpus warns that SEPA is entry-driven: a clean pivot can form, fire and disappear within one or two sessions. A weekly-only scan misses entries.

### 7.8 Adaptations for non-US markets

The corpus includes an ASX adaptation; the same principles apply to other thinner markets.

- **Liquidity:** use dollar volume rather than share count. A $400k daily turnover floor may be more appropriate than 400k shares for low-priced stocks.
- **Volatility:** mining/resources and small caps may need **10–12% stops** instead of 7–8%, with a proportionally smaller position to keep dollar risk constant.
- **Base duration:** VCPs in thinner markets can take **20–30 weeks** to form; do not reject a base only because it is longer than the US 4–12 week norm.
- **Breakout volume:** a 100–150% expansion may be normal in a thin stock, versus 300–400% in a liquid US tech name; calibrate the volume multiplier to the stock's own history, not to a US average.
- **Fundamentals:** reporting may be half-yearly, and institutional ownership data may be quarterly or incomplete. Use the best available point-in-time data and flag lower confidence.
- **Benchmark:** use the local index for RS and regime; do not compare an ASX stock with the S&P 500.

---

## 8. Market regime — the top-level filter

### 8.1 Evidence in the corpus

- Minervini: "When the market's in a correction, I go to cash. I don't fight it. I wait for the environment to improve."
- 90.77% of successful breakouts occur when major indices trade above their monthly 10-period EMA (cited in the Finer Market Points articles).
- Market conditions can change the probability of a winning trade by more than 50%.
- 90% of Minervini's major winning trades occurred in confirmed bull markets with indices in uptrends.
- The number of stocks passing the Trend Template is a breadth indicator (§7.5).

### 8.2 Regime inputs

Use a broad benchmark (SPY or QQQ for the US; the relevant local index for other markets). Inputs:

1. Benchmark close vs 200-day SMA.
2. Benchmark close vs 10-month EMA (≈ 210 trading days).
3. Breadth: percentage of the universe above its 200-day SMA.
4. Trend Template pass count.
5. Optional: distribution-day count (heavy-volume down days in the index); the corpus does not define it, so treat it as an implementation overlay.

### 8.3 Regime classifier

```text
def market_regime(ctx):
    bench = ctx.benchmark
    above200 = bench.close > SMA(bench.close, 200)
    above10m = bench.close > EMA(bench.close, 210)
    breadth = pct_universe_above_sma200(ctx)
    tt_count = count_trend_template(ctx)

    # A market below both long-term anchors is RED regardless of breadth.
    if not above200 and not above10m:
        return "RED"

    # GREEN requires both anchors plus at least one breadth confirmation.
    if above200 and above10m and (breadth >= 0.50 or tt_count >= 30):
        return "GREEN"

    # One anchor intact: YELLOW, trade selectively.
    if above200 or above10m:
        return "YELLOW"

    return "RED"
```

The exact exposure percentages and risk levels in the table below are implementation choices [C]. The corpus only states the direction: increase exposure in a confirmed uptrend, reduce it in a neutral market, and go to cash in a correction.

### 8.4 Exposure and risk by regime

| Regime | Conditions | Max gross exposure | Risk per trade | New entries | Position count |
|---|---|---|---|---|---|
| **GREEN** | Above 200-day and 10-month EMA, breadth ≥ 50% or TT count ≥ 30 | 80–100% | 1.0–1.25% (max 2%) | All A/A+ setups | 4–8 |
| **YELLOW** | One long-term anchor intact (above 200-day or above 10-month EMA), but not both with breadth confirmation | 30–60% | 0.5–0.75% | Only score ≥ 80, A+ setups | 3–4 |
| **RED** | Below both the 200-day and the 10-month EMA (breadth and TT count usually weak) | 0–20% | 0–0.25% | No new longs by default; exceptional A+ only at 0.25% | 0–2 |

The regime multiplier should be applied to the risk budget, not to the stop distance:

```text
risk_dollars = equity * base_risk_pct * regime_multiplier
# GREEN 1.0, YELLOW 0.5, RED 0.25 or 0
```

### 8.5 Regime is a gate, not a score

A perfect stock in a RED regime is not a buy. The corpus is explicit that even perfect setups fail in corrections. The algorithm should reject new entries when the regime is RED, except for a separately tested "exceptional strength" module with reduced size.

---

## 9. Setup catalogue

The corpus documents the VCP as the primary setup and mentions several related patterns. The table separates documented from inferred setups.

| # | Setup | Status | Context | Trigger | Stop | Horizon |
|---|---|---|---|---|---|---|
| 1 | **VCP breakout** | Documented, core [A] | Stage 2, 2–6 contractions, volume dry-up | Breakout above final contraction high on volume | Below final contraction low | Weeks–months |
| 2 | **Flat / tight base** | Documented as a VCP variant [B] | Stage 2, shallow 1–2 contraction base | Breakout above base high | Below base low | Weeks |
| 3 | **Cup-with-handle** | Mentioned as related [B] | Stage 2, rounded cup + handle (handle = final contraction) | Breakout above handle high | Below handle low | Weeks–months |
| 4 | **Primary base / IPO base** | Documented [B] | First major consolidation after IPO | Breakout above base high | Below base low | Months–years |
| 5 | **Pullback to 10/21/50 MA** | Documented as an entry technique [A/B] | Stage 2, first pullback after breakout or MA support | Reclaim of MA / prior day high | Below pullback low | Days–weeks |
| 6 | **Failed breakout / undercut-and-rally** | Inferred [B] | Stage 2, shakeout below pivot/base low, then reclaim | Reclaim of pivot on volume | Below undercut low | Days–weeks |
| 7 | **Base-on-base / late-stage base** | Inferred [C] | New base above prior base high; base count 2–3 | Breakout above new base high | Below new base low | Weeks–months |
| 8 | **Pivot variants** | Documented [A] | Clean, complex, round-number, MA pivot | Breakout above the relevant pivot | Below pivot structure | Same as parent setup |

**What is missing:** Minervini says he uses about twenty named patterns and declines to describe them (Schwager). Any implementation that claims to reproduce "all Minervini setups" is overstating the evidence. The VCP family above is what the corpus supports.

Patterns such as the **high tight flag**, **ascending base**, or **three-weeks-tight** belong to the broader O'Neil/Minervini vocabulary but are not described in this corpus. They are therefore not listed as Minervini-specific setups here. If you want to implement them, source them from primary material and test them as separate modules.

---

## 10. Setup 1 — VCP (Volatility Contraction Pattern)

### 10.1 Definition

A VCP is a base formed inside an existing Stage 2 uptrend in which:

1. the stock has already had a strong prior advance;
2. it pulls back, rallies, pulls back less, rallies, and repeats **two to six times**;
3. each contraction is smaller in percentage depth than the previous one;
4. volume dries up through the contractions;
5. the final contraction is tight and quiet;
6. the stock breaks above the **pivot** — the high of the final contraction — on expanding volume.

The pattern is a supply-demand story: each pullback flushes out weaker holders; when the last sellers are gone, a small amount of demand can move the price sharply. The corpus traces the idea to Wyckoff's accumulation logic and notes that the VCP shares DNA with a bull flag; Minervini isolated and named the multi-contraction version.

### 10.2 Anatomy

| Element | Definition | Typical values |
|---|---|---|
| Prior uptrend | Advance from the pre-base low to the base high | ≥ 30% (implementation choice), ideally 50–100%+ |
| Base duration | From the base high to the current bar | 3–18 weeks; ideal 4–12 weeks |
| Number of contractions | Completed pullbacks | 2–6; ideal 3–4 |
| First contraction depth | (H1 − L1) / H1 | 15–33%; can be up to ~35–40% |
| Contraction progression | Each depth vs the previous | 20–30% smaller per step; "about half" in one source |
| Final contraction depth | (H_last − L_last) / H_last | 3–8%; hard max ~10% |
| Base depth | (Base high − Base low) / Base high | 10–35%; hard max ~40% |
| Volume dry-up | Final 5-day volume / 50-day average | ≤ 0.6; ideally 0.4–0.5 |
| Breakout volume | Breakout day volume / 50-day average | 1.4–1.5×; stronger is better |
| Pivot | High of the final contraction | Price level, not a zone |
| Stop | Just below the final contraction low | 3–8% below entry; never > 8% |

The visual tell of genuine dry-up is **3–5 consecutive days of extraordinarily low volume with minimal price movement** in the final contraction. If volume is merely "below average" but still active, the supply has not been exhausted.

### 10.3 Contraction sequences in the corpus

The exact percentages are illustrative, not a formula:

- 25% → 12% → 6% (`financialtechwiz-vcp.md`, `financialtechwiz-minervini-strategy.md`)
- 18% → 12% → 6% (`finermarketpoints-sepa-vcp-guide.md`)
- 15% → 10% → 5% (`finermarketpoints-vcp-criteria.md`)
- 20–25–33% → 10–15% → 3–8% (Minervini quote in `finermarketpoints-sepa-methodology.md`)

The invariant is **monotonic contraction**, not the specific numbers.

### 10.4 Hard gates for a valid VCP

Use these as binary filters before scoring:

| Gate | Rule | Confidence |
|---|---|---|
| G1. Stage 2 | Trend Template passes; price above rising 50/150/200 | A |
| G2. Prior advance | Base high ≥ 1.30 × pre-base low (120-day window) | B |
| G3. Base duration | 15–90 trading days | B |
| G4. Contraction count | 2–6 completed contractions | A |
| G5. Monotonic contraction | `depth[i] < depth[i-1]` for every i; quality if ≤ 0.85× | A/B |
| G6. Final depth | Final contraction ≤ 10% (ideal ≤ 8%) | A/B |
| G7. Base depth | ≤ 40% (ideal ≤ 35%) | B |
| G8. Higher lows | At least 60% of lows are higher than the prior low (1% tolerance) | B |
| G9. Volume dry-up | Final 5-day volume / ADV50 ≤ 0.65; down-leg volume < up-leg volume | A/B |
| G10. Tightness | Last 10-day range / pivot ≤ 10%; ATR5/ATR20 ≤ 0.7 | B |
| G11. Pivot cleanliness | Base high / pivot − 1 ≤ 3% (no significant overhead resistance) | B |
| G12. Price position | 0.90 ≤ close / pivot ≤ 1.03 (not broken out, not too far below) | B |
| G13. RS | RS ≥ 70 (prefer ≥ 80–90) | A |
| G14. Fundamentals | Fundamental score ≥ threshold, OR RS ≥ 98 (top 2% override) | A/B |
| G15. Regime | Market regime ≠ RED | A |
| G16. Liquidity | Price/ADV/dollar-volume filters pass | A/B |
| G17. Earnings | Optional blackout window before earnings (0–5 days) | C |

The Finer Market Points version of the checklist collapses the same requirements into seven points:

| Seven-point checklist | Corresponding gate(s) |
|---|---|
| 1. Progressive contractions (decreasing volatility) | G4, G5, G6 |
| 2. Volume dry-up | G9 |
| 3. Clear pivot point | G11, G12 |
| 4. Stage 2 uptrend | G1 |
| 5. Relative Strength > 70 | G13 |
| 6. Accelerating earnings growth ≥ 20% | G14 |
| 7. Bullish market environment | G15 |

### 10.5 Pivot definition

The pivot is the **highest price of the final, tightest contraction** — the resistance level the stock must clear. It is not necessarily the highest price of the entire base, although in a clean VCP the two are close.

```text
pivot = max(high[last_contraction_start : last_contraction_end])
overhead = max(high[base_start : last_contraction_end]) / pivot - 1
```

If `overhead > 3%`, there is meaningful supply above the pivot; either lower the score or wait for a new, cleaner base. A "clean pivot" has one obvious high; a "complex pivot" has a resistance zone with several similar highs; a "round-number pivot" sits at $50/$100; a "moving-average pivot" uses the 20/50-day MA in a shallow pullback.

### 10.6 Entry

**Primary method — standard breakout:**

- Place a buy-stop **1–2% above the pivot** [A].
- Require breakout volume ≥ **1.4–1.5× ADV50** [A/B].
- Do not chase more than **5% above the pivot** [A/B]. Entries within 5% preserve the risk-reward; entries 10–15% above destroy it.
- If the stock gaps more than 5% above the pivot at the open, skip the trade and wait for a pullback or a new base.
- **Follow-through:** the days after the breakout should maintain elevated volume (roughly 30–40% above average) for 2–5 days. If volume collapses immediately, the breakout is suspect [A/B].

**Alternative methods:**

| Method | When | Entry | Stop | Size |
|---|---|---|---|---|
| **Anticipation** | Final contraction is extremely tight, volume dry, pivot obvious | Limit in the upper half of the final contraction, before the breakout | Below final contraction low | 0.5× normal |
| **Pullback** | Breakout already happened; first pullback to 10/20-day MA | Reclaim of MA or prior day high | Below pullback low | 0.5–1× normal |
| **Failed-breakout reclaim** | Shakeout below pivot/base low, then reclaim | Close above pivot on volume | Below undercut low | 0.5–1× normal |

Anticipation is explicitly riskier: you are buying before the market confirms demand. The corpus describes it as an advanced technique; the algorithm should default to standard breakout and treat anticipation as a separate, smaller-size module.

### 10.7 Stop

- Structural stop: **just below the final contraction low**, with a small buffer (0.5–1%).
- Hard maximum: **7–8% below entry**. If the structural stop is wider than 8%, **skip the trade**; do not widen the stop to accommodate the pattern.
- Minimum stop: ~3% or 0.5×ATR20, whichever is larger, to avoid noise stops. If the final contraction is only 1–2% deep, the structural stop may be too tight; use the minimum.
- Average loss target: **3–4%** across all losing trades. If the average loss is drifting above 5%, the entries are too extended or the stops are too wide.

```text
stop = min(final_low * 0.995, entry * 0.97)   # at least 3% below entry
if (entry - stop) / entry > 0.08:
    skip_trade()
```

### 10.8 Initial risk and reward

- `R = entry - stop`.
- Minimum reward-to-risk: **2:1**, ideally **3:1** [A].
- The corpus does not define a fixed target. For the R:R gate, use a conservative upside estimate: the base height projected from the pivot, the prior swing high, or 2–3×ATR20. If the realistic upside is less than 2R, skip the trade.
- Do not use a fixed profit target as the primary exit; use partials and a trailing stop.

### 10.9 Management

| Trigger | Action | Confidence |
|---|---|---|
| Entry | Stop below final contraction low; risk ≤ 1–2% of equity | A |
| +1R (or +8% in the source example) | Sell ~50%; move stop to break-even | A/B |
| +2R | Sell another 1/3 of the remainder; stop to +0.5R or trail | A/B |
| +3R | Sell another 1/3; trail the rest | B |
| Close below 10-day MA | Exit the remainder (fast growth names) | A/B |
| Close below 21-day MA | Exit (normal swing names) | B |
| Close below 50-day MA on volume | Exit (slower/large-cap names) | A |
| Trend Template fails | Exit or reduce sharply | A |
| RS deteriorates (e.g., 90 → 60) | Exit or reduce | A/B |
| Stage 3/4 transition | Exit | A |
| Extended / climax move (e.g., >30% above the 10-day MA) | Sell into strength | C (threshold is an implementation overlay; the corpus only says to trim into extended moves) |
| Market regime RED | Reduce exposure; exit weak positions | A |

**Two partial-profit patterns coexist in the corpus.** One is "up ~8%, with an 8% stop, sell half and move to break-even" (`finermarketpoints-sepa-methodology.md`). The other is "take a third to half off at 2–3× initial risk" (`chartmill-sepa-explained.md`). They are not the same rule and should not be stacked blindly, or the position may be sold down too fast. Recommended: choose one as the primary partial rule and test the other as an alternative. The default in this document uses +1R for the first partial and +2–3R for the second, which is a blend; treat it as an implementation choice [C] until tested.

### 10.10 Failure modes

- **Light-volume breakout:** the most common false signal. Volume below 1.4× ADV50 → skip (or wait for a second-day confirmation).
- **Loose, wide base:** deep contractions, overlapping candles, no clear pivot → not a VCP.
- **Late-stage base:** base 4 or 5 in a long advance → higher failure rate; reduce size or skip.
- **Extended entry:** buying 10–15% above the pivot → stop too wide, R:R broken.
- **Stage 3 disguised as Stage 2:** 200-day flattening, erratic volume, RS falling → skip.
- **No catalyst:** a technically perfect base with no fundamental reason to attract institutions.
- **Earnings binary event:** if the stock is in a binary event window and there is no profit cushion, reduce or skip. The corpus does not define a blackout, so this is a risk overlay.
- **False breakout / shakeout:** price breaks the pivot, reverses, then reclaims. The failed-breakout module can re-enter, but the initial stop must be honored.

### 10.11 VCP detection pseudocode

The following is a complete, implementable starting point. It uses confirmed swing pivots and never looks ahead.

```text
def detect_vcp(bars, i, p):
    # bars: adjusted daily OHLCV up to index i
    # p: parameter object

    # 1. Stage 2 / Trend Template gate
    if not trend_template(bars, i).hard:
        return None

    # 2. Confirmed swing pivots (3-bar fractal, confirmed with a 3-bar lag)
    pivots = confirmed_swings(bars[:i+1], left=3, right=3)
    highs = [x for x in pivots if x.type == "H"]
    lows  = [x for x in pivots if x.type == "L"]
    if len(highs) < 2 or len(lows) < 2:
        return None

    # 3. Base start: most recent confirmed swing high that has not been exceeded
    #    by more than 2% and is followed by at least two lower highs.
    base_start = None
    for h in reversed(highs):
        if h.index < i - p.min_base_days:
            window = bars[h.index:i+1]
            if max(x.high for x in window) <= h.price * 1.02:
                base_start = h
                break
    if base_start is None:
        return None
    if i - base_start.index > p.max_base_days:
        return None

    # 4. Build alternating contractions H -> L from base_start.
    #    Append each H->L leg, including the final leg whose next high
    #    has not formed yet. If no next high exists, the final leg ends
    #    at the current bar.
    contractions = []
    current_high = base_start
    for l in lows_after(lows, base_start.index):
        if l.index >= i:
            break
        next_high = first_high_after(highs, l.index)
        next_high_index = next_high.index if next_high and next_high.index < i else i
        depth = (current_high.price - l.price) / current_high.price
        contractions.append(Contraction(
            high=current_high, low=l,
            depth=depth,
            duration=l.index - current_high.index,
            down_volume=mean_volume(bars, current_high.index, l.index),
            up_volume=mean_volume(bars, l.index, next_high_index),
        ))
        if next_high is None or next_high.index >= i:
            break
        current_high = next_high

    # 5. The last contraction is the one whose low is the most recent
    #    and whose high is the pivot. Current price must still be below the pivot.
    if len(contractions) < 2 or len(contractions) > 6:
        return None
    last = contractions[-1]
    if bars[i].close > last.high.price * 1.03:
        return None
    if bars[i].close < last.high.price * 0.90:   # too far below the pivot
        return None
    if bars[i].close < last.low.price * 0.98:
        return None

    # 6. Hard gates
    depths = [c.depth for c in contractions]
    if any(depths[k] >= depths[k-1] for k in range(1, len(depths))):
        return None
    if last.depth > 0.10:
        return None
    if max(depths) > 0.40:
        return None
    base_high = max(c.high.price for c in contractions)
    base_low  = min(c.low.price for c in contractions)
    if (base_high - base_low) / base_high > 0.40:
        return None

    higher_lows = sum(
        1 for k in range(1, len(contractions))
        if contractions[k].low.price >= contractions[k-1].low.price * 0.99
    ) / (len(contractions) - 1)
    if higher_lows < 0.60:
        return None

    # Use the prior 50 sessions for the baseline, not the current breakout day.
    vol_ratio = mean_volume(bars, i-4, i) / mean_volume(bars, i-50, i-1)
    if vol_ratio > p.max_vol_dryup:             # e.g. 0.65
        return None
    if mean(c.down_volume for c in contractions) >= mean(c.up_volume for c in contractions):
        return None

    last_range = (max(x.high for x in bars[i-9:i+1]) -
                  min(x.low  for x in bars[i-9:i+1])) / last.high.price
    if last_range > p.max_last_range:            # e.g. 0.10
        return None
    if atr(bars, 5, i) / atr(bars, 20, i) > p.max_atr_ratio:  # e.g. 0.70
        return None

    pivot = last.high.price
    overhead = base_high / pivot - 1
    if overhead > p.max_overhead:                # e.g. 0.03
        return None

    # 7. Prior advance
    prior_low = min(x.low for x in bars[max(0, base_start.index-120):base_start.index+1])
    if pivot / prior_low - 1 < p.min_prior_advance:  # e.g. 0.30
        return None

    return VCP(
        base_start=base_start, contractions=contractions,
        pivot=pivot, final_low=last.low.price,
        vol_ratio=vol_ratio, last_range=last_range,
        overhead=overhead, higher_lows=higher_lows,
    )
```

**Practical notes:**

- The pivot sequence must alternate high–low–high–low. If two highs or two lows occur in a row, keep the extreme (highest high or lowest low) and drop the other; otherwise the contraction list is invalid.
- Apply a minimum swing threshold (e.g., 2–3% or 1.5×ATR20) when confirming pivots; otherwise minor noise creates spurious contractions. The threshold should be smaller for the final contraction than for the first.
- `confirmed_swings` must only use pivots whose right-hand confirmation bars are already in the past. A 3-bar fractal confirms a pivot three bars later; do not use the pivot before confirmation.
- Do not choose the base start that maximizes the score. Use the most recent valid swing high. Otherwise the detector has look-ahead bias.
- The final contraction may be still forming. If the current price is inside the final contraction and the pivot is known, the setup is "forming", not "triggered". The entry engine waits for the breakout.
- The detector should output both `FORMING` and `TRIGGERED` states, not only a binary yes/no.

### 10.12 VCP scoring

After the hard gates, rank candidates with a 0–100 score. Weights are a starting point, not a revealed truth.

```text
def vcp_score(v, ctx):
    # contraction quality: how much each contraction shrinks
    ratios = []
    for k in range(1, len(v.contractions)):
        prev = v.contractions[k-1].depth
        cur  = v.contractions[k].depth
        ratios.append(clip((prev - cur) / max(prev, 1e-6) / 0.30, 0, 1))
    c_score = mean(ratios) if ratios else 0

    # volume dry-up: 0.30 -> 1.0, 0.70 -> 0.0
    v_score = clip((0.70 - v.vol_ratio) / 0.40, 0, 1)

    # tightness: 4% -> 1.0, 12% -> 0.0
    t_score = clip((0.12 - v.last_range) / 0.08, 0, 1)

    # pivot cleanliness: no overhead -> 1.0
    p_score = 1 - clip(v.overhead / 0.03, 0, 1)

    # trend / RS
    r_score = clip((ctx.rs - 70) / 25, 0, 1)

    # fundamentals and catalyst
    f_score = ctx.fund_score          # 0..1
    cat_score = ctx.catalyst_score    # 0..1

    # base count: first/second base best
    b_score = 1.0 if ctx.base_count <= 2 else 0.5 if ctx.base_count == 3 else 0.0

    score = 100 * (
        0.25 * c_score +
        0.20 * v_score +
        0.15 * t_score +
        0.10 * p_score +
        0.10 * r_score +
        0.10 * f_score +
        0.05 * cat_score +
        0.05 * b_score
    )
    return score
```

Suggested thresholds: **≥ 80 = A+**, **70–79 = A**, **60–69 = B** (only in GREEN regime, reduced size), **< 60 = reject**. These cut-offs and the weights above are implementation choices [C]; calibrate them on a labeled sample, not on the two examples in §22.

### 10.13 VCP parameter table

| Parameter | Starting value | Range to test | Confidence |
|---|---|---|---|
| Min prior advance | 30% | 20–50% | B |
| Base duration | 15–90 days | 10–120 days | B |
| Ideal base duration | 20–60 days | — | B |
| Contractions | 2–6 | 2–6 | A |
| Ideal contractions | 3–4 | — | B |
| Contraction shrink ratio | Hard: `< previous`; quality: ≤ 0.85 per step | 0.70–0.90 | B |
| Final contraction depth | ≤ 10% | 6–12% | A/B |
| Ideal final depth | 3–8% | — | A/B |
| Base depth max | 40% | 30–50% | B |
| Volume dry-up ratio | ≤ 0.65 | 0.40–0.70 | A/B |
| Breakout volume | ≥ 1.4× ADV50 | 1.3–2.0× | A/B |
| Last 10-day range | ≤ 10% | 6–12% | B |
| ATR5/ATR20 | ≤ 0.70 | 0.50–0.80 | B |
| Pivot overhead | ≤ 3% | 2–5% | B |
| Entry buffer above pivot | 1–2% | 0–3% | A |
| Max chase above pivot | 5% | 3–7% | A/B |
| Max stop | 8% | 6–10% | A |
| Min stop | 3% | 2–4% | C |
| Risk per trade | 1.0–1.25% | 0.5–2.0% | A/B |
| Max position | 20% (25% A+) | 15–25% | C (implementation guard) |
| Partial 1 | 50% at +1R | 1.0–1.5R | A/B |
| Partial 2 | 1/3 at +2R | 2–3R | A/B |
| Trail | 10/21/50 MA | 10/20/50 | A/B |

### 10.14 VCP vs triangle vs bull flag

The corpus explicitly distinguishes the VCP from two patterns that share some of its geometry.

| Feature | VCP | Triangle | Bull flag |
|---|---|---|---|
| Prior move | Strong Stage 2 advance | Can occur in many contexts | Sharp move up |
| Structure | 2–6 progressively smaller pullbacks | One or more symmetric contractions; converging trendlines | One short pullback |
| Duration | Weeks to months | Variable | Days |
| Volume | Dries up through contractions; expands on breakout | Often dries up, but no progressive-contraction requirement | Dries up in the flag; expands on breakout |
| Entry | Breakout above final contraction high | Breakout of triangle boundary | Breakout above flag high |
| Stop | Final contraction low | Opposite side of triangle | Flag low |

A detector that only looks for "tight range + volume dry-up" will confuse a bull flag with a VCP. The distinguishing test is the **number of completed contractions and the monotonic decrease in depth**. If there is only one contraction, treat it as a flat base or a bull flag, not a VCP.

---

## 11. Setup 2 — Flat / tight base

### 11.1 Definition

A flat base is a shallow, sideways consolidation in a Stage 2 uptrend. It is essentially a VCP with only one or two contractions and a small depth. It appears in the corpus as part of the VCP family; Minervini's broader base library includes tight, flat structures.

**Confidence note:** the corpus documents the VCP family and tight bases, but does not give separate flat-base numbers. The duration, depth and contraction thresholds below are implementation choices [C], derived from the VCP rules. Test them as a separate module and do not assume they are Minervini's exact parameters.

### 11.2 Rules

| Element | Value |
|---|---|
| Context | Stage 2; price above rising 50/150/200 |
| Duration | 15–40 trading days |
| Depth | 3–12% |
| Contractions | 1–2 (if 2, the second should be smaller) |
| Volume | Dries up in the base; expands on breakout |
| Pivot | Base high |
| Entry | Breakout above pivot + 1–2% buffer, volume ≥ 1.4× ADV50 |
| Stop | Below base low; max 7–8% |
| Management | Same as VCP |

### 11.3 Detector differences

- Relax the `min_contractions` gate to 1.
- Require `base_depth ≤ 0.12` and `last_range ≤ 0.06`.
- Increase the weight on tightness and volume dry-up; decrease the weight on contraction count.
- Treat a flat base that is **below** the 50-day MA or has a falling 200-day MA as invalid.

### 11.4 Failure modes

- A flat base at the top of a parabolic move is often a distribution shelf, not accumulation.
- A flat base with rising volume on down days is supply, not dry-up.
- A flat base with a wide, loose range (e.g., 15–20%) is not tight enough.

---

## 12. Setup 3 — Cup-with-handle

### 12.1 Definition

A cup-with-handle is a rounded consolidation (the cup) followed by a short, shallow pullback (the handle) near the old high. In Minervini's framework, **the handle is essentially the final contraction**; the pattern is a VCP cousin.

**Confidence note:** the corpus only states the handle-is-final-contraction relationship. The numeric cup and handle thresholds below are standard chart-pattern conventions, not Minervini-specific rules; treat them as implementation choices [C] and test them separately.

### 12.2 Rules

| Element | Value |
|---|---|
| Context | Stage 2 uptrend |
| Cup depth | 15–35% (avoid > 50%) |
| Cup duration | 7–30 weeks |
| Cup shape | Rounded U, not a sharp V; volume dries up at the bottom |
| Handle duration | 3–15 trading days |
| Handle depth | 3–10% |
| Handle position | In the upper half of the cup; drifting down or sideways |
| Handle volume | Dry-up; no heavy distribution |
| Pivot | Handle high |
| Entry | Breakout above handle high + 1–2%, volume ≥ 1.4× ADV50 |
| Stop | Below handle low; max 7–8% |
| Management | Same as VCP |

### 12.3 Detector

Use the same swing/contraction engine, but add a cup-shape check:

```text
cup_depth = (cup_high - cup_low) / cup_high
cup_duration = weeks(cup_low -> handle_start)
handle_depth = (handle_high - handle_low) / handle_high
handle_duration = days(handle_start -> handle_end)
handle_position = (handle_low - cup_low) / (cup_high - cup_low)  # should be > 0.5
```

A valid cup has `cup_depth` between 0.15 and 0.35, `handle_depth` between 0.03 and 0.10, `handle_duration` between 3 and 15 days, and `handle_position > 0.5`. The handle high is the pivot; the handle low is the stop reference.

### 12.4 Failure modes

- V-shaped cup (too sharp, no rounding).
- Handle in the lower half of the cup.
- Handle too deep (> 12%) or too long (> 20 days).
- Handle with rising volume on down days.
- Cup depth > 50% (too much overhead supply).

---

## 13. Setup 4 — Primary base / IPO base

### 13.1 Definition

The **primary base** is the first major consolidation after a company's IPO. Kagels describes it as the first larger consolidation of a young company, often the starting point of a multi-year move. It is a special case because the stock has little or no long-term history, so the 200-day MA and the full Trend Template may not be available.

**Confidence note:** the concept is documented, but the numeric thresholds below (IPO age, base depth, duration) are implementation choices [C]. The corpus does not provide a primary-base checklist.

### 13.2 Rules

| Element | Value |
|---|---|
| Context | Recent IPO, typically < 24 months of trading history |
| Base duration | 3–12 weeks |
| Base depth | 10–30% |
| Volume | Dry-up in the base; expansion on breakout |
| Pivot | Base high / first rally high |
| Entry | Breakout above pivot + 1–2%, volume ≥ 1.4× ADV50 |
| Stop | Below base low; max 7–8% |
| Size | 0.5× normal (limited history, higher uncertainty) |
| Management | Same as VCP, but expect higher volatility |

### 13.3 Implementation caveat

The Trend Template cannot be fully computed without 200 days of history. Use a reduced template:

- price above the 50-day MA;
- 50-day MA rising;
- price within 25% of the post-IPO high;
- price at least 30% above the post-IPO low;
- RS ≥ 70 versus the universe.

Mark this as a separate module and do not mix its statistics with the standard VCP module. The corpus does not give exact IPO-age or depth thresholds; the values above are implementation choices [C].

---

## 14. Setup 5 — Pullback to the 10/21/50-day MA

### 14.1 Definition

In a Stage 2 uptrend, a stock pulls back to a key moving average (10-, 21- or 50-day), volume contracts, and the stock resumes higher. This is both a standalone entry and an add-on to an existing position.

### 14.2 Rules

| Element | Value |
|---|---|
| Context | Stage 2; Trend Template passes |
| Pullback depth | 3–15% from the recent high |
| Pullback duration | 3–10 trading days |
| MA support | 10-day (fast), 21-day (normal), 50-day (deep) |
| Volume | Declining into the pullback; expansion on the reclaim |
| Higher low | Pullback low above the prior swing low |
| Trigger | Close above the prior day's high, or reclaim of the MA |
| Stop | Below the pullback low; max 7–8% |
| Target | 2–3R; trail the rest |
| Size | 0.5–1× normal; add-on 0.25–0.5× |

### 14.3 Detector

```text
def pullback_setup(bars, i, ma_period):
    ma = SMA(bars.close, ma_period)
    recent_high = max(bars.high[i-20:i+1])
    pullback_low = min(bars.low[i-10:i+1])
    depth = (recent_high - pullback_low) / recent_high
    if not (0.03 <= depth <= 0.15):
        return None
    if pullback_low < ma[i] * 0.97:       # too deep below the MA
        return None
    if bars.close[i] <= bars.high[i-1]:   # no reclaim yet
        return None
    if volume[i] < 1.2 * ADV50[i]:
        return None
    return Setup(entry=bars.close[i], stop=pullback_low * 0.995)
```

### 14.4 Failure modes

- The pullback becomes a Stage 3 top (lower highs, heavy volume).
- The MA is broken decisively and not reclaimed within 1–3 days.
- The pullback is too deep (> 15–20%) or too long (> 15 days).
- The stock is extended above the 200-day MA and the pullback is the first crack in a parabolic move.

---

## 15. Setup 6 — Failed breakout / undercut-and-rally

### 15.1 Definition

A stock breaks out above a pivot, fails, and falls back below the pivot or the base low, shaking out weak holders. If it then reclaims the pivot within a few days on strong volume, the failed breakout can become a higher-probability entry than the original breakout. Schwager's interview states the principle: "A so-called failed signal can actually be the beginning of a more complex pattern that is far more reliable than the initial signal."

### 15.2 Rules

| Element | Value |
|---|---|
| Context | Stage 2 stock with a valid base/pivot |
| Shakeout | Price breaks below pivot or base low by 1–5% |
| Duration | Reclaim within 1–5 trading days |
| Volume on reclaim | ≥ 1.4× ADV50 |
| Trigger | Close above the pivot (or above the prior swing high) |
| Stop | Below the undercut low |
| Size | 0.5–1× normal |
| Confidence | B — the principle is documented, the exact rules are inferred |

### 15.3 Why it works

The failed breakout traps late buyers and stops out weak holders. When the stock reclaims the pivot, the supply from those participants is gone, and the next move can be violent. The risk is defined by the undercut low, which is usually close to the entry.

### 15.4 Failure modes

- The reclaim fails and the stock makes a lower high.
- The undercut is too deep (> 8–10%), implying real distribution.
- The reclaim happens on light volume.
- The market regime is RED; failed breakouts fail more often in weak markets.

---

## 16. Setup 7 — Base-on-base and late-stage bases

### 16.1 Base counting

Minervini counts bases in a Stage 2 advance. The first and second bases are the best buying opportunities; the fourth and fifth are late-stage and prone to deep corrections. In `sos-minervini-zasady-tradingu.md`, he says base counting is somewhat subjective.

Algorithmic proxy:

- Start counting when the stock first enters Stage 2 after a Stage 1/4 period.
- A **base** is a consolidation of at least 15 trading days with a depth of 3–20%, followed by a breakout.
- Increment `base_count` on each confirmed breakout.
- Penalize `base_count >= 3`; reject or reduce size for `base_count >= 4`.

### 16.2 Base-on-base

A base-on-base forms when a stock consolidates above the high of the previous base, then breaks out again. It is a sign of strength, but it is also a later-stage base. The corpus does not describe the exact rules; the following is an implementation choice [C]:

- prior base high is support;
- new base duration 3–10 weeks;
- new base depth 5–15%;
- new base low above the prior base high;
- pivot = new base high;
- size 0.5× if `base_count >= 3`.

### 16.3 Late-stage warning signs

- The stock has already had multiple bases and a large advance.
- The 200-day MA is flattening.
- RS is deteriorating.
- The base is wide and loose.
- The breakout fails on volume.
- The sector leadership is narrowing.

---

## 17. Pivot types and entry tactics

### 17.1 Pivot types

| Pivot type | Definition | Implementation | Quality |
|---|---|---|---|
| **Clean pivot** | One clear high in the final contraction | `pivot = max(highs)`; overhead ≤ 1–2% | Best |
| **Complex pivot** | Several similar highs form a resistance zone | `pivot_zone = [min(highs), max(highs)]`; require close above zone high | Good, needs volume |
| **Round-number pivot** | Pivot at $50/$100/$10 | Same as clean, but expect psychological resistance | Neutral |
| **MA pivot** | 20/50-day MA acts as the pivot in a shallow pullback | Entry on reclaim of MA + volume | Good for pullbacks |

For a complex pivot, do not enter on the first touch of the zone. Require a close above the entire zone and a volume expansion; otherwise the stock may reject the zone multiple times.

### 17.2 Entry methods compared

| Method | Timing | Risk | Reward | Skill required | Default |
|---|---|---|---|---|---|
| Standard breakout | After pivot + volume | Medium | Medium–high | Low–medium | Yes |
| Anticipation | Before breakout, in final contraction | High | High | High | No (0.5× size) |
| Pullback | After breakout, at 10/20 MA | Low–medium | Medium | Medium | Add-on |
| Failed-breakout reclaim | After shakeout, on reclaim | Medium | High | High | Optional |
| Add-on | After +1R or new base | Low (stop moved) | Medium | Medium | Yes, small |

### 17.3 Intraday execution

The corpus is not an intraday method, but execution can use intraday data. **This entire subsection is an implementation overlay [C], not a Minervini rule.**

- Place a buy-stop at `pivot * 1.01` to `1.02`.
- Require price above VWAP and volume pace ≥ 1.5× the 50-day average by 10:00–10:30.
- Cancel unfilled orders by the close; do not chase after 15:30.
- For daily backtests, use the next open after a confirmed close above the pivot, with slippage and a gap filter.

The corpus does not define a 5-minute opening-range rule for Minervini (that is Qullamaggie's territory). Do not import Qullamaggie's ORB rules into the Minervini module without separate testing.

---

## 18. Risk management and position sizing

### 18.1 Risk per trade

| Source | Risk per trade | Comment |
|---|---|---|
| `finermarketpoints-sepa-vcp-guide.md` | 1–2% of capital | Position size formula example uses 1% |
| `finermarketpoints-sepa-methodology.md` | 1–2% | "Maximum 1–2% risk per position" |
| `financialtechwiz-minervini-strategy.md` | 1.25–2.5% | With a 7% stop, 1.25% risk ≈ 18% position |
| `chartmill-sepa-explained.md` | Not stated; max stop 7–8%, average loss 3–4% | Risk is implicit |

**Recommended starting point:** **1.0–1.25% per trade**, hard cap **2.0%**. In a YELLOW regime, 0.5–0.75%; in RED, 0–0.25% or zero. The 2.5% upper bound in one source is inconsistent with a 20–25% position cap (our implementation guard) and the 7–8% stop; do not use it as a default.

### 18.2 Position size formula

```text
risk_dollars   = equity * risk_pct * regime_multiplier
risk_per_share = entry - stop
shares         = floor(risk_dollars / risk_per_share)
shares         = min(shares, floor(0.01 * ADV20))          # liquidity cap
shares         = min(shares, floor(max_position_pct * equity / entry))
position_value = shares * entry
```

Example from the corpus: $100,000 account, 1% risk ($1,000), entry $50, stop $46 (8% stop):

```text
shares = 1,000 / (50 - 46) = 250 shares
position value = 250 * 50 = $12,500 = 12.5% of equity
```

### 18.3 Position and portfolio caps

| Limit | Value | Confidence |
|---|---|---|
| Max position size | 20% of equity; 25% only for highly liquid A+ | C (implementation guard; not stated in the Minervini corpus) |
| Max risk per trade | 2% of equity | A |
| Max number of positions | 8; target 4–6 | A/B |
| Max sector exposure | 30–40% | C (risk overlay) |
| Max correlated positions | 2–3 in the same theme | C (risk overlay) |
| Total open risk (sum of initial R) | 4–6% GREEN; 2–3% YELLOW; 0–1% RED | C (risk overlay) |
| Max ADV participation | 1% of average daily volume | C (liquidity guard; imported from general execution practice) |
| Cash | Allowed; cash is a position | A |

The **total open risk** cap is often the binding constraint. Size positions so that the sum of initial R across all open positions does not exceed the regime limit, even if each individual position is within its own cap.

### 18.4 Progressive exposure and pyramiding

- Start with a **starter position** (e.g., 50% of target size). Add only after the trade confirms (e.g., +1R or a new base breakout).
- Do not add to a losing position. "Never average down" is one of Minervini's ten rules.
- When adding, move the stop on the entire position to at least break-even.
- Increase risk only when the portfolio is working; decrease risk after losses. This is rule 8 of the ten-rule list: size up when results are best, size down when they are worst.

### 18.5 Re-entry

- If stopped out, the stock can be re-entered if it forms a new valid setup.
- Re-entry must use the same risk budget; do not increase size to "get it back".
- Limit re-entries to 2–3 attempts per stock per base (implementation choice [C]); after that, wait for a genuinely new base.
- A shakeout/reclaim can justify re-entry at a higher price; the stop is the new undercut low.

### 18.6 Drawdown circuit breaker (risk overlay, not from the corpus)

| Portfolio drawdown | Action |
|---|---|
| < 5% | Normal risk |
| 5–10% | Cut risk per trade by 25%; review recent trades |
| 10–15% | Cut risk by 50%; only A+ setups |
| > 15% | Stop new entries; review the system, regime and execution |

This is a prudent implementation overlay. It is not stated by Minervini in the corpus, so test it separately and label it as an add-on.

---

## 19. Exit framework

### 19.1 The hierarchy of exits

1. **Hard stop** — the pre-defined structural stop, never wider than 7–8%.
2. **Partial profit** — sell into strength at ~1R and ~2–3R.
3. **Break-even stop** — after a meaningful profit, never let a winner become a loser.
4. **Trailing stop** — 10/21/50-day MA or a swing low.
5. **Thesis exit** — Trend Template failure, RS deterioration, Stage 3/4, catalyst invalidation.
6. **Regime exit** — market correction; reduce exposure even if individual stops are not hit.

### 19.2 Decision table

| Signal | Action | Confidence |
|---|---|---|
| Close below initial stop | Exit all | A |
| +1R (or ~+8%) | Sell ~50%; stop to break-even | A/B |
| +2R | Sell ~1/3 of remainder; stop to +0.5R | A/B |
| +3R | Sell ~1/3; trail the rest | B |
| Close below 10-day MA | Exit remainder (fast names) | A/B |
| Close below 21-day MA | Exit (normal names) | B |
| Close below 50-day MA on volume | Exit (slow/large names) | A |
| Trend Template fails | Exit or reduce | A |
| RS falls from 90+ to 60–70 | Reduce/exit | A/B |
| Stage 3/4 | Exit | A |
| Extended / climax move | Sell into strength | C (no fixed threshold in the corpus) |
| Market regime RED | Reduce exposure; exit weak positions | A |
| Earnings without cushion | Reduce or exit before the event | C (risk overlay) |
| No progress after 60–120 days | Optional time stop / capital reallocation | C (not from corpus) |

### 19.3 "Never let a winner become a loser"

This is one of the most important rules. Once a trade has moved meaningfully into profit, the stop moves to at least break-even. The corpus is explicit: the psychological cost of giving back a winner is what causes traders to abandon their system. Implement it mechanically:

```text
if mfe >= 1.0 * R:
    stop = max(stop, entry)
```

### 19.4 Selling into strength vs weakness

Minervini distinguishes two ways to liquidate:

- **Into strength:** sell partials as the stock extends, especially in a climax.
- **Into weakness:** exit the remainder when the structure breaks (stop, MA, Trend Template).

The algorithm should have a plan for both. Do not rely on a single trailing stop for the entire position; partials reduce the emotional and market risk of giving back gains.

### 19.5 The "50% rule"

ChartMill mentions a "50% rule" and "average cost basis discipline" in Minervini's exit framework, but the corpus does not define them precisely. Do not implement a 50% rule until you have the exact definition from *Think & Trade Like a Champion*. The partial-profit rules above are the documented substitute.

### 19.6 Psychology and process

The corpus is as much about behaviour as about patterns. The rules that matter for an algorithmic implementation are the ones that prevent the system from being overridden.

| Principle | Practical implementation |
|---|---|
| **Journal every trade** | Store entry, stop, size, R, partials, exit reason, MFE/MAE, setup score, regime, catalyst sentence |
| **Post-trade analysis** | Review stopped-out names: did they continue lower or rebound? Did winners keep running? |
| **Accept small losses** | A loss is a business cost, not a mistake; a widened stop is the mistake |
| **No averaging down** | The execution layer rejects any add below the entry price |
| **No revenge sizing** | Risk multiplier cannot increase after a loss; only after equity recovers |
| **No forcing trades** | If the watchlist is empty, hold cash; empty lists are signal, not failure |
| **No style drift** | Freeze the rule set for a full test period; change only after out-of-sample evidence |
| **No tips / no ego** | The market's verdict is the only opinion that counts; the system follows price, not narrative |
| **Patience** | Waiting for the pivot is part of the strategy; most of the time the correct action is no action |
| **Paper trading is not enough** | Forward-test with small real size; the emotional response is part of the system |

Minervini's own path supports this: he lost his first stake, was not consistently profitable for years, and only turned the corner after studying his own trades and capping losses. The algorithm should encode the **process**, not just the pattern.

---

## 20. Algorithmic model

### 20.1 Data requirements

| Data | Frequency | Use |
|---|---|---|
| OHLCV, split/dividend adjusted | Daily | Trend Template, VCP, signals |
| OHLCV | 1/5/30/60-min (optional) | Execution, intraday confirmation |
| Benchmark index | Daily | Market regime |
| Sector ETFs | Daily | Sector strength / rotation |
| Fundamentals | Quarterly, point-in-time | EPS, revenue, margins, ROE |
| Estimates / revisions | Quarterly/monthly | Surprise and revision score |
| Earnings dates | Point-in-time | Event filter |
| Institutional ownership | Quarterly | Fundamental score |
| Market cap / float / ADV | Daily | Liquidity and position sizing |
| Corporate actions / delistings | Event | Backtest integrity |
| News / catalyst flags | Event | Catalyst score (optional NLP) |

### 20.2 Pipeline

```text
1. universe = all US common stocks + liquid ETFs
   filter price >= 12
   filter ADV20 >= 400,000
   filter dollar_volume20 >= 20,000,000
   filter data_quality == OK

2. regime = market_regime(benchmark, breadth, tt_count)
   if regime == RED: no new longs (or 0.25% risk exceptional module)

3. for each symbol in universe:
       tt = trend_template(symbol)
       if not tt.hard: continue
       stage = classify_stage(symbol)
       if stage != 2: continue
       fund = fundamental_score(symbol)
       cat  = catalyst_score(symbol)
       base = detect_vcp(symbol) or detect_flat_base(symbol)
       if base is None: continue
       score = vcp_score(base, symbol, fund, cat)
       if score < threshold: continue
       watchlist.add(symbol, base.pivot, base.final_low, score)

4. for each symbol in watchlist:
       if breakout_triggered(symbol, base.pivot):
           size = position_size(symbol, entry, stop, regime)
           enter(symbol, size, stop)

5. manage_positions()
```

### 20.3 Trend Template function

See §6.2. The function should return both the binary result and the individual tests, so the journal can explain why a stock passed or failed.

### 20.4 Stage classifier

See §5.1. Use hysteresis and store the stage history. The Trend Template is the hard gate; the stage classifier is used for exits and for detecting Stage 3 deterioration.

### 20.5 Base / VCP detector

See §10.11. The detector should output:

```text
VCP(
  state: FORMING | TRIGGERED | INVALID,
  base_start,
  contractions[],
  pivot,
  final_low,
  score,
  gates: { ... },
  reasons: [ ... ]
)
```

Store the gates and reasons for every candidate. This is essential for debugging and for comparing the algorithm with manual chart review.

### 20.6 Scoring

See §10.12. The score is used only after the hard gates. Do not let a high score override a failed gate (e.g., a stock below its 200-day MA with a beautiful base).

### 20.7 Entry engine

```text
def on_bar(symbol, bar):
    if symbol.state != "ARMED":
        return
    pivot = symbol.pivot
    trigger = pivot * (1 + entry_buffer)       # 1–2%
    if bar.high < trigger:
        return
    if bar.open > pivot * (1 + max_chase):     # gap > 5%
        symbol.state = "SKIPPED"
        return
    if bar.volume < breakout_volume_mult * ADV50[bar.i - 1]:
        return
    entry = max(bar.open, trigger) + slippage
    stop = min(symbol.final_low * 0.995, entry * 0.97)   # at least 3% below entry
    if (entry - stop) / entry > max_stop_pct:
        symbol.state = "SKIPPED"
        return
    size = position_size(entry, stop, regime)
    if size == 0:
        return
    submit_buy(symbol, size, stop)
```

For a daily backtest, use the next open after a confirmed close above the pivot, and apply a gap filter. For an intraday backtest, use a buy-stop order and a volume-pace filter.

### 20.8 Position sizing

See §18.2. Apply the regime multiplier, the liquidity cap, the position cap, and the portfolio/sector caps. If the resulting size is below one share or below a minimum position value, skip.

### 20.9 Exit engine

```text
def manage(position, bar):
    R = position.entry - position.initial_stop

    # Gap-through or intraday stop; do not wait for the close.
    if bar.open <= position.stop:
        close(position, "STOP_GAP", price=bar.open)
        return
    if bar.low <= position.stop:
        close(position, "STOP", price=position.stop)
        return

    mfe = (bar.high - position.entry) / R

    # Execute partials at the trigger price, not at the bar close.
    if mfe >= 1.0 and not position.partial1:
        sell(position, 0.50, price=position.entry + 1.0 * R)
        position.stop = max(position.stop, position.entry)
        position.partial1 = True

    if mfe >= 2.0 and not position.partial2:
        sell(position, 0.33 * position.remaining, price=position.entry + 2.0 * R)
        position.stop = max(position.stop, position.entry + 0.5 * R)
        position.partial2 = True

    if mfe >= 3.0 and not position.partial3:
        sell(position, 0.33 * position.remaining, price=position.entry + 3.0 * R)
        position.partial3 = True

    if bar.close < trail_ma(position):
        close(position, "TRAIL_MA")
    elif trend_template_failed(position.symbol):
        close(position, "TT_FAIL")
    elif rs_rank(position.symbol) < 60:
        close(position, "RS_FAIL")
    elif stage(position.symbol) >= 3:
        close(position, "STAGE_3")
    elif regime == "RED" and position.unrealized_R < 1.0:
        close(position, "REGIME")
    elif bar.close > SMA10 * 1.30:          # implementation overlay
        sell(position, 0.33 * position.remaining, price=bar.close)
```

Choose `trail_ma` by volatility:

```text
if atr_pct(20) > 5%:   trail = SMA10
elif atr_pct(20) > 3%: trail = SMA21
else:                  trail = SMA50
```

The exact mapping is an implementation choice [C]. The corpus supports 10-, 21-, 50- and 200-day MAs as relevant levels; test each.

### 20.10 Portfolio construction

- Rank candidates by `score * regime_multiplier * catalyst_quality`.
- Fill the portfolio up to the regime's max exposure and max position count.
- Cap sector/theme exposure at 30–40%; cap correlated positions at 2–3.
- If a new candidate is only marginally better than an existing position, do not churn. Replace only when the existing position has broken its thesis and the new candidate is A+.
- Keep a cash buffer in YELLOW/RED regimes.
- Do not hold more than 8 positions; the target is 4–6.

### 20.11 Backtest protocol

| Issue | Requirement |
|---|---|
| Universe | Point-in-time, survivorship-bias-free; include delisted stocks |
| Fundamentals | Point-in-time, with report-date lag; no restated data |
| Earnings dates | Historical, confirmed where possible; flag estimates |
| Corporate actions | Split/dividend adjusted for signals; total-return for P&L |
| Pivot confirmation | No repainting; use confirmed swings only |
| Base start | Deterministic rule, not "best fit" |
| Entry | Daily close + next open, or intraday stop; model slippage |
| Slippage | 0.1–0.3% per side; higher for small caps and gaps |
| Liquidity | Max 1% ADV; reject fills above the cap |
| Regime | Separate results for GREEN/YELLOW/RED |
| Parameters | Walk-forward; no full-sample optimization |
| Statistics | ≥ 100 trades per setup; bootstrap confidence intervals |
| Benchmarks | S&P 500, QQQ, equal-weight momentum |
| Metrics | CAGR, max DD, win rate, avg win/loss, expectancy, R distribution, profit factor, exposure, turnover, MAE/MFE distribution |

### 20.12 Reference parameter set

| Parameter | Default | Range |
|---|---|---|
| Price floor | $12 | $10–20 |
| ADV floor | 400k shares | 200k–1M |
| Dollar volume floor | $20M | $10–50M |
| Trend Template | All 8 | — |
| RS hard gate | 70 | 60–80 |
| RS preferred | 80–90 | — |
| Base duration | 15–90 days | 10–120 |
| Contractions | 2–6 | 2–6 |
| Final contraction | ≤ 10% | 6–12% |
| Volume dry-up | ≤ 0.65 | 0.40–0.70 |
| Breakout volume | ≥ 1.4× | 1.3–2.0× |
| Entry buffer | 1% | 0–2% |
| Max chase | 5% | 3–7% |
| Max stop | 8% | 6–10% |
| Risk per trade | 1.0–1.25% | 0.5–2.0% |
| Max position | 20% | 15–25% |
| Max positions | 8 | 4–10 |
| Partial 1 | 50% at 1R | 1–1.5R |
| Partial 2 | 1/3 at 2R | 2–3R |
| Trail | 10/21/50 MA | 10/20/50 |
| Regime | SPY/QQQ 200d + 10m EMA + breadth | — |

Example configuration:

```yaml
strategy: minervini_sepa
universe:
  min_price: 12
  min_adv: 400000
  min_dollar_volume: 20000000
trend_template:
  sma_periods: [50, 150, 200]
  min_above_52w_low: 0.30
  max_below_52w_high: 0.25
  min_rs: 70
  require_sma200_rising_1m: true
vcp:
  min_base_days: 15
  max_base_days: 90
  min_contractions: 2
  max_contractions: 6
  max_final_depth: 0.10
  max_base_depth: 0.40
  max_vol_dryup: 0.65
  max_last_range: 0.10
  max_atr_ratio: 0.70
  max_overhead: 0.03
  min_prior_advance: 0.30
entry:
  buffer: 0.01
  max_chase: 0.05
  min_breakout_volume: 1.4
  max_stop: 0.08
  min_stop: 0.03
risk:
  risk_per_trade: 0.0125
  max_position: 0.20
  max_positions: 8
  max_sector: 0.35
  total_open_risk: 0.05
exits:
  partial_1_r: 1.0
  partial_1_size: 0.50
  partial_2_r: 2.0
  partial_2_size: 0.33
  trail_ma_fast: 10
  trail_ma_normal: 21
  trail_ma_slow: 50
regime:
  benchmark: SPY
  sma: 200
  ema_months: 10
  breadth_floor: 0.50
  tt_count_green: 30
```

The values are starting points for calibration, not universal constants. Walk-forward test each one.

### 20.13 Minimum viable implementation

Do not build the full system in one pass. A staged implementation isolates bugs and gives earlier evidence.

**v0 — core trend + breakout (1–2 weeks):**

- Trend Template (all eight criteria).
- 50-day high breakout on volume ≥ 1.4× ADV50.
- Stop below the 20-day low or 7%, whichever is tighter.
- Risk 1% per trade; max 5 positions.
- Trail with the 21-day MA.
- Purpose: validate the data pipeline, the Trend Template and the basic risk logic.

**v1 — VCP structure (2–4 weeks):**

- Add the contraction detector, volume dry-up, tightness and pivot scoring.
- Replace the 50-day high trigger with the VCP pivot trigger.
- Add the final-contraction stop and the max-8% rule.
- Add partials at +1R and +2R, break-even, and the 10/21/50 trail.
- Purpose: test whether the VCP structure adds value over a simple breakout.

**v2 — fundamentals and regime (2–4 weeks):**

- Add EPS/revenue/margins/ROE/revisions and the catalyst flag.
- Add the market regime classifier and the exposure/risk multipliers.
- Add sector and correlation caps.
- Purpose: test whether the SEPA confluence improves expectancy and drawdown.

**v3 — execution and breadth (ongoing):**

- Add intraday execution, slippage/gap models, and the failed-breakout module.
- Add the flat base, cup-with-handle, primary base and pullback modules.
- Add walk-forward optimization and capacity analysis.
- Purpose: production-grade system.

At every stage, keep a **baseline**: the S&P 500, QQQ, and a simple 50-day-high breakout with a 7% stop. If the full SEPA system cannot beat the baseline after costs, the extra complexity is not earning its keep.

### 20.14 Trade lifecycle state machine

| State | Entry condition | Next state |
|---|---|---|
| **WATCH** | Passes universe, Trend Template and fundamentals; no valid base yet | FORMING when a base is detected |
| **FORMING** | Base detected; contractions still developing or pivot not final | ARMED when the final contraction and pivot are confirmed |
| **ARMED** | Pivot defined; price within ~5% of pivot; alerts set | TRIGGERED on breakout + volume |
| **TRIGGERED** | Price > pivot + buffer; volume ≥ 1.4× ADV50; risk ≤ 8% | OPEN after fill |
| **OPEN** | Position filled; stop and initial R recorded | PARTIAL at +1R; CLOSED on stop/thesis |
| **PARTIAL** | One or more partials taken; stop at or above BE | TRAIL after final partial; CLOSED on trail/thesis |
| **TRAIL** | Remaining position trailed by MA or swing low | CLOSED on trail/thesis |
| **CLOSED** | Stop, trail, thesis or regime exit | WATCH/COOLDOWN; re-entry only on a new valid setup |
| **COOLDOWN** | Stopped out; same base may re-form | ARMED if a new pivot forms; otherwise WATCH |

The state machine prevents the two most common implementation errors: entering a stock that is still forming a base, and re-entering a stopped-out position without a new setup.

---

## 21. Setup comparison

| Setup | Context | Trigger | Stop | Management | Horizon | Confidence |
|---|---|---|---|---|---|---|
| **VCP** | Stage 2, 2–6 contractions, volume dry-up | Breakout above final contraction high + volume | Final contraction low; max 8% | Partial at 1R/2–3R, BE, trail 10/21/50 | Weeks–months | A |
| **Flat base** | Stage 2, shallow 1–2 contraction base | Breakout above base high + volume | Base low; max 8% | Same as VCP | Weeks | B |
| **Cup-with-handle** | Stage 2, rounded cup + handle | Breakout above handle high + volume | Handle low; max 8% | Same as VCP | Weeks–months | B |
| **Primary base** | Recent IPO, first consolidation | Breakout above base high + volume | Base low; max 8% | Same as VCP, 0.5× size | Months–years | B |
| **Pullback to MA** | Stage 2, pullback to 10/21/50 MA | Reclaim of MA / prior day high | Pullback low | Trail MA; partial at 2R | Days–weeks | A/B |
| **Failed breakout** | Stage 2, shakeout below pivot, reclaim | Close above pivot + volume | Undercut low | Same as VCP, 0.5–1× size | Days–weeks | B |
| **Base-on-base** | Stage 2, new base above prior base high | Breakout above new base high | New base low | Same as VCP, 0.5× size if late | Weeks–months | C |

---

## 22. Examples

The corpus contains only two fully identified real examples. Both are recorded below with the minimum fields: company, ticker, date and description. Schematic examples without a company/ticker are listed separately and explicitly marked as illustrations.

### 22.1 KD — Kyndryl Holdings (Trend Template pass)

| Field | Value |
|---|---|
| **Company** | Kyndryl Holdings, Inc. |
| **Ticker** | KD (NYSE) |
| **Date** | 2024-12-27 (daily chart snapshot in the source) |
| **Setup** | Trend Template pass; tight price range near the 52-week high |
| **Source** | `chartmill-trend-template.md`; image `images/chartmill-trend-template/02-kd-daily-chart.webp` |

**Data from the chart/article:**

- Close: **$34.83**
- 50-day MA: **$30.12**
- 150-day MA: **$26.53**
- 200-day MA: **$25.52**
- 52-week low: **$19.23**
- 52-week high: **$36.43**
- RS: **above 94**

**Trend Template check:** criterion 1 is split into two rows (price above 150-day and price above 200-day); the other criteria follow the canonical list.

| Criterion | Calculation | Pass? |
|---|---|---|
| Price > 50-day MA | 34.83 > 30.12 | Yes |
| Price > 150-day MA | 34.83 > 26.53 | Yes |
| Price > 200-day MA | 34.83 > 25.52 | Yes |
| 50 > 150 | 30.12 > 26.53 | Yes |
| 150 > 200 | 26.53 > 25.52 | Yes |
| 200-day rising | Source states it is trending upward; chart shows a rising 200-day MA | Yes |
| ≥ 30% above 52-week low | 34.83 / 19.23 − 1 = **81.1%** (the article says 78%; both pass) | Yes |
| Within 25% of 52-week high | 34.83 / 36.43 − 1 = **−4.4%** (the article says 4.5%) | Yes |
| RS ≥ 70 | 94 | Yes |

**Description:** KD is a textbook Trend Template qualifier. The stock is above all three key moving averages, the averages are correctly stacked, the 200-day is rising, price is far above the 52-week low and within ~4.4% of the 52-week high, and relative strength is in the 90s. The chart also shows a tight price range near the high and strong volume during the prior uptrend. This is a **qualifier, not a buy signal**: the source does not provide a VCP pivot, entry, stop or subsequent trade result. It is useful for calibrating the Trend Template, not for measuring the edge.

### 22.2 XLE — Energy Select Sector SPDR Fund (VCP breakout)

| Field | Value |
|---|---|
| **Company** | Energy Select Sector SPDR Fund (ETF) |
| **Ticker** | XLE |
| **Date** | 2022-01-03 (bought); tweeted 2022-01-04 |
| **Setup** | Weekly VCP breakout in a Stage 2 uptrend |
| **Source** | `financialtechwiz-minervini-strategy.md`; image `images/financialtechwiz-minervini-strategy/03-xle-chart-tradingview.png` |

**Description:** Minervini tweeted on 4 January 2022 that he had bought XLE the day before. The weekly chart shows a Stage 2 uptrend with higher lows, a tight consolidation, and a breakout from a textbook VCP. The chart marks the entry near **$58.45**. The Ichimoku cloud is green, confirming the uptrend. The fundamental/catalyst layer was macro: energy was the top-performing sector, oil was recovering sharply from the 2020 collapse, OPEC supply discipline was holding, and major oil companies were seeing accelerating earnings revisions.

According to the source, XLE rallied **over 70%** to its peak after the entry. The stop is not disclosed; the correct implementation is to apply the standard 7–8% maximum stop and the final-contraction low, then manage with partials and a trailing MA.

**Why it is useful:** it is the only real VCP example in the corpus, and it shows the full SEPA stack: Stage 2 trend, tight base, pivot breakout, sector catalyst, and a large winner. It is an ETF, not a stock, so keep it in a separate ETF sleeve when backtesting.

### 22.3 Schematic examples (no company/ticker/date)

These are pattern illustrations from the corpus. They are useful for calibrating the detector, but they are **not** real trades and must not be counted as evidence.

| Pattern illustration | Sequence | Source | Notes |
|---|---|---|---|
| VCP contractions | 25% → 12% → 6% | `financialtechwiz-vcp.md`, `financialtechwiz-minervini-strategy.md` | Textbook contraction sequence; 2–6 contractions |
| VCP contractions | 18% → 12% → 6% | `finermarketpoints-sepa-vcp-guide.md` | Three contractions |
| VCP contractions | 15% → 10% → 5% | `finermarketpoints-vcp-criteria.md` | Three contractions; each ~20–30% smaller |
| VCP contractions | 20–25–33% → 10–15% → 3–8% | `finermarketpoints-sepa-methodology.md` (Minervini quote) | First correction can be 20–33%; later ones roughly half |
| Hypothetical ASX stock | $2.00 → $1.70 (−15%), $2.10 → $1.95 (−7%), $2.15 → $2.08 (−3%) | `finermarketpoints-vcp-criteria.md` | Hypothetical illustration of progressive contraction |
| Primary base | First major consolidation after IPO | `kagels-trading-mark-minervini.md` | Schematic; no ticker or date |
| VCP schematic | Three shrinking pullbacks under a pivot, breakout on rising volume | `kagels-trading-mark-minervini.md` | Schematic; no ticker or date |

### 22.4 What the examples do not tell us

- There is **no complete Minervini stock trade** in the corpus with entry, stop, size and exit.
- KD has no entry trigger, stop or result.
- XLE has an entry date and a large result, but no disclosed stop, size or partial exits.
- The schematic percentages are illustrative, not a statistical sample.

**Consequence:** the algorithm must be validated on a broad, point-in-time universe. Do not tune parameters to make KD or XLE look good. Use them only as sanity checks: the Trend Template should pass KD on 2024-12-27, and the VCP detector should flag XLE's weekly base in late 2021 / early 2022.

### 22.5 Example record template

When adding new examples to this document, use the following fields. This is the minimum needed to make an example reproducible.

| Field | Example / placeholder |
|---|---|
| Company / instrument | Kyndryl Holdings, Inc. |
| Ticker / exchange | KD / NYSE |
| Date of occurrence | 2024-12-27 |
| Setup | Trend Template pass; VCP forming (from source) |
| Stage / regime | Stage 2 / not stated in source |
| Base start → pivot | `YYYY-MM-DD → $XX.XX` |
| Entry trigger | `breakout above pivot + 1%` |
| Entry price | `$XX.XX` |
| Initial stop | `$XX.XX` (final contraction low) |
| Risk per share / R | `$X.XX` |
| Position size / risk % | `X%` |
| Partial 1 / partial 2 | `+1R / +2R` |
| Exit / result | `+X.XR` |
| Source | ChartMill article + chart |

The company, ticker, date and setup fields are taken from the KD example; the trading fields are placeholders, **not** a historical KD trade. The corpus does not contain enough examples to fill this template for a real Minervini stock trade. Future research should add them from primary sources (Minervini's books, interviews, audited statements) rather than from secondary articles.

---

## 23. Discrepancies and decisions before backtesting

These are the conflicts that matter most. Each one needs an explicit choice and a sensitivity test.

| # | Issue | What the sources say | Decision for the first backtest |
|---|---|---|---|
| 1 | 1997 return | 155% (Kagels, SOS) vs 255% (Financial Tech Wiz) | Use 155% as the common figure; do not calibrate on returns |
| 2 | 2021 return | 334.8% (Kagels) vs 335% (SOS) | Use 334.8% |
| 3 | Five-year return | 220% average / 33,500% cumulative, self-reported | Treat as marketing context, not audited data |
| 4 | Max stop | 7–8% (most sources) vs 10% historical study (Schwager) | Hard max 8%; test 6/7/8/10% |
| 5 | Average loss | 3–4% target; "5–6% in a bad market" | Target 3–4%; investigate if > 5% |
| 6 | Risk per trade | 1–2% vs 1.25–2.5% | Default 1.0–1.25%; hard cap 2.0% |
| 7 | Position size | 12.5–18% of equity vs 4–8 positions | Cap 20% (25% A+) as an implementation guard; target 4–6 positions |
| 8 | RS threshold | ≥ 70 hard; 80/90 preferred | Hard 70; require 80+ in GREEN for full size |
| 9 | 52-week low | 30% above (canonical) vs omitted in some lists | Include 30% as hard gate; test 25% |
| 10 | Contractions | 2–6 vs 2–4 vs 3–4; "80% have ≥ 3" | Hard 2–6; prefer 3–4 |
| 11 | Contraction shrink | 20–30% smaller vs "about half" | Hard `< previous`; quality ratio ≤ 0.85; test 0.7–0.9 |
| 12 | Breakout volume | 40–50% above average vs "140–150% above average" | Interpret as 1.4–1.5× ADV50; test 1.3–2.0× |
| 13 | VCP duration | 4–12 weeks vs 3–15 weeks | 15–90 sessions; ideal 20–60 |
| 14 | EPS growth | ≥ 20% vs ≥ 25% | 25% default; test 20% |
| 15 | Revenue growth | ≥ 15% vs ≥ 20% | 15% default; test 20% |
| 16 | Institutional ownership | 20–80% vs 30–70% | 20–80% hard; 30–70% scoring bonus |
| 17 | 200-day slope | ≥ 1 month vs 4–5 months | 1 month hard; 3–5 months quality |
| 18 | Market regime | 200-day vs 10-month EMA vs breadth vs TT count | Rule-based: both anchors + breadth/TT confirmation; test each input |
| 19 | Earnings policy | No explicit blackout; prefers post-catalyst entries | Optional 0–5 day blackout; test 0/3/5 |
| 20 | Trail MA | 10/21/50/200 depending on source | Volatility-based 10/21/50; test each |
| 21 | "50% rule" | Mentioned but undefined | Do not implement until the definition is sourced |
| 22 | Base count | Explicitly "somewhat subjective" | Algorithmic proxy; manual audit |
| 23 | All ~20 patterns | Minervini refuses to disclose them | Implement only documented VCP family; do not claim completeness |

---

## 24. Backtest and implementation risks

### 24.1 Look-ahead bias

- **Pivot confirmation:** a swing high is only known after the right-hand bars. Use a confirmed-pivot function with a lag.
- **Base start:** choose the most recent valid swing high, not the one that produces the best score.
- **Fundamentals:** use report dates plus a lag; never use restated or future data.
- **Earnings dates:** use confirmed historical dates; flag estimates.
- **Universe:** use point-in-time membership; do not use today's index constituents.

### 24.2 Survivorship bias

The corpus is full of winners because it is a book/article corpus. A backtest must include stocks that failed, were acquired, or were delisted. Use a survivorship-bias-free database and include delisting returns.

### 24.3 Pattern-labeling bias

The VCP is a discretionary pattern. Algorithmic detection will not match a human expert exactly. Mitigate with:

- a written rule set (this document);
- a random sample of 100–200 charts labeled by hand;
- precision/recall reporting for the detector;
- a manual audit of all A+ signals in the first live year.

### 24.4 Liquidity and slippage

- Cap positions at 1% of ADV20 as a liquidity guard (implementation choice, not a Minervini rule).
- Model spread and slippage; small caps and gap openings are expensive.
- Do not assume fills at the pivot; use the next tick or a slippage model.
- Avoid names with wide spreads or thin books, even if they pass the price/volume filter.

### 24.5 Regime dependence

The method is long-only and bull-market-biased. Test separately:

- 1990s bull market;
- 2000–2002 bear market;
- 2003–2007 bull market;
- 2008 bear market;
- 2009–2020 bull market;
- 2022 bear market;
- 2023–2026 AI/tech cycle.

A strategy that only works in 2020–2021 is not a strategy; it is a regime bet.

### 24.6 Parameter sensitivity

The VCP has many parameters. Do not optimize all of them on the full sample. Use:

- walk-forward optimization with a purge/embargo between train and test;
- a small parameter grid;
- out-of-sample holdout;
- bootstrap confidence intervals;
- deflated Sharpe ratio for multiple testing.

### 24.7 Capacity

The strategy is concentrated and can hold illiquid small caps. Capacity is limited by the 1% ADV cap and the 20–25% position cap. Test with realistic account sizes ($100k, $1M, $10M) and report capacity-adjusted returns.

### 24.8 Execution risk

- Gap risk through stops: model gaps; a stop is not a guaranteed price.
- Earnings gaps: binary events can jump the stop.
- Halts and limit-up/limit-down: fills may be impossible.
- Borrow/short: not relevant for the long-only core; separate module if added.
- **Daily-bar ambiguity:** if a bar touches both the stop and a partial-profit level, daily data cannot tell which came first. Use intraday data, or adopt the conservative assumption that the stop is hit first. Never assume the favorable path.

### 24.9 Data quality

- Splits and dividends: use adjusted data for signals; total-return for P&L.
- ETFs vs stocks: separate sleeves; different volatility and fundamentals.
- ADRs: currency and jurisdiction risk; test separately.
- Delistings: include the terminal return.

---

## 25. Relationship to the Qullamaggie playbook

The repository also contains `docs/trading/Qullamaggie/Qullamaggie-strategia.md`. The two methods share the "buy strength" philosophy but differ in setup, horizon and execution. They should be separate modules with separate statistics.

| Dimension | Minervini | Qullamaggie |
|---|---|---|
| Primary setup | VCP / base breakout | Episodic Pivot (EP), breakout, ORB |
| Holding period | Weeks–months | Days–weeks (swing), minutes–hours (ORB) |
| Trend filter | 50/150/200 MA + Trend Template | 10/20/50 MA, QQQ 10/20 regime |
| Fundamentals | Required (EPS/revenue/margins), RS override possible | Fuel, but price/volume trump |
| Entry | Pivot + 1–2%, volume confirmation | 5-min opening range high, LOD stop |
| Stop | Final contraction low, max 7–8% | Low of day / ORL, often tighter |
| Exits | Partial at 1R/2–3R, trail 10/21/50 | Partial after 3–5 days, trail 10/20 MA |
| Market regime | 200-day + 10-month EMA + breadth + TT count | QQQ 10/20 + 100-day slope |
| Win rate | ~50% (Schwager) | ~20–35% |
| Data needs | Daily + quarterly fundamentals | Daily + 1/5/60-min intraday |

**Implementation advice:** do not merge the two signal sets into one score. Run them as separate strategies with separate risk budgets and compare their R distributions. A portfolio can allocate to both, but the correlation and regime exposure must be monitored.

---

## 26. Implementation checklist

### Data and infrastructure

- [ ] Point-in-time universe, including delisted stocks.
- [ ] Split/dividend-adjusted daily OHLCV.
- [ ] Quarterly fundamentals with report-date lag.
- [ ] Earnings dates and estimate revisions.
- [ ] Sector ETFs and benchmark index.
- [ ] Optional intraday 1/5/30/60-min data.
- [ ] Corporate actions and delisting returns.
- [ ] Slippage and commission model.

### Screening

- [ ] Price ≥ $12, ADV ≥ 400k, dollar volume ≥ $20M.
- [ ] Trend Template with all eight criteria.
- [ ] Stage classifier with hysteresis.
- [ ] Fundamental score (EPS, revenue, margins, ROE, revisions).
- [ ] Catalyst flag / one-sentence thesis.
- [ ] RS percentile rank (not RSI).
- [ ] Market regime score (200-day, 10-month EMA, breadth, TT count).

### Pattern detection

- [ ] Confirmed swing pivots, no repainting.
- [ ] Base start deterministic.
- [ ] 2–6 contractions, monotonic.
- [ ] Final contraction ≤ 10%.
- [ ] Volume dry-up ≤ 0.65.
- [ ] Tightness: 10-day range ≤ 10%, ATR5/ATR20 ≤ 0.7.
- [ ] Pivot overhead ≤ 3%.
- [ ] Base count and late-stage penalty.
- [ ] VCP score and gate log.

### Entry and sizing

- [ ] Buy-stop 1–2% above pivot.
- [ ] Breakout volume ≥ 1.4× ADV50.
- [ ] Max chase 5%.
- [ ] Structural stop below final low; max 8%.
- [ ] Risk 1.0–1.25% default; cap 2%.
- [ ] Position cap 20% (25% A+).
- [ ] Max 8 positions; sector/correlation caps.
- [ ] Regime multiplier.
- [ ] Re-entry rules.

### Exits

- [ ] Hard stop.
- [ ] Partial at +1R; break-even.
- [ ] Partial at +2R; trail.
- [ ] Trail 10/21/50 MA by volatility.
- [ ] Trend Template failure exit.
- [ ] RS deterioration exit.
- [ ] Stage 3/4 exit.
- [ ] Regime RED reduction.
- [ ] Extended/climax trim (threshold is an implementation overlay).
- [ ] No widening, no averaging down.

### Validation

- [ ] Walk-forward, not full-sample optimization.
- [ ] Separate results by regime, sector, market cap, base count.
- [ ] ≥ 100 trades per setup.
- [ ] Bootstrap confidence intervals.
- [ ] Manual audit of 100–200 charts.
- [ ] Capacity test at $100k/$1M/$10M.
- [ ] Compare with S&P 500, QQQ and a simple momentum baseline.
- [ ] Paper-trade or small live test before full size.

---

## 27. Source map

| Source | Key sections used |
|---|---|
| `chartmill-sepa-explained.md` | Five SEPA elements; Trend Template; HGM; Setup Quality; exit rules; catalyst; common mistakes |
| `chartmill-trend-template.md` | Eight criteria; KD example; sector and volume tips |
| `financialtechwiz-vcp.md` | VCP definition; four stages; 25/12/6; entry/stop; VCP vs flag |
| `financialtechwiz-minervini-strategy.md` | SEPA; Stage Analysis; Trend Template; VCP; risk; XLE trade |
| `finermarketpoints-stock-screener.md` | Screening funnel; fundamentals; TradingView; market-health indicator; common mistakes |
| `finermarketpoints-sepa-methodology.md` | Stage Analysis; entry/pivot types; position sizing; assessment; ASX notes |
| `finermarketpoints-vcp-criteria.md` | Seven-point VCP checklist; volume dry-up; pivot; Stage 2; RS; earnings; market |
| `finermarketpoints-sepa-vcp-guide.md` | Four-letter SEPA; track record; VCP; earnings; catalyst; workflow; sizing |
| `kagels-trading-mark-minervini.md` | Five elements; Trend Template; VCP; risk; primary base; book review |
| `sos-minervini-zasady-tradingu.md` | Ten rules; base counting; price floor; no cheap stocks; psychology |
| `Market Wizards - Minevrini.md` | Risk; 10% study; price-action sandwich; ~20 patterns; re-entry; discipline |

### 27.1 Primary sources to acquire next

The corpus is secondary literature. To close the remaining gaps, obtain:

1. **Mark Minervini, *Trade Like a Stock Market Wizard*** — the canonical Trend Template, SEPA and VCP definitions.
2. **Mark Minervini, *Think & Trade Like a Champion*** — the exit framework, the "50% rule", average cost basis discipline, and the full trade-management rules.
3. **Mark Minervini, *Momentum Masters*** — roundtable discussion of setups and execution.
4. **Jack Schwager, *Stock Market Wizards*** — the full Minervini chapter (the excerpt is already in the corpus).
5. **IBD / MarketSmith RS data** or a licensed RS rating — to replace the proxy in §6.3.
6. **A point-in-time fundamentals and earnings-date database** — to avoid look-ahead bias.
7. **Minervini's own interviews and Master Trader Program material** — for the ~20 named patterns he does not disclose publicly.

Until these are available, treat the present document as a **testable reconstruction**, not a complete reproduction of Minervini's private system.

---

## Appendix A — Formula reference

### A.1 Moving averages

```text
SMA(n)[t] = mean(close[t-n+1 : t+1])
EMA(n)[t] = alpha * close[t] + (1 - alpha) * EMA(n)[t-1], alpha = 2/(n+1)
```

### A.2 52-week range

```text
low52  = min(low[t-251 : t+1])
high52 = max(high[t-251 : t+1])
```

### A.3 ATR

```text
TR[t] = max(high[t] - low[t],
            abs(high[t] - close[t-1]),
            abs(low[t]  - close[t-1]))
ATR(n)[t] = mean(TR[t-n+1 : t+1])
```

### A.4 Contraction depth

```text
depth[i] = (high[i] - low[i]) / high[i]
```

### A.5 Volume dry-up

```text
vol_dryup = mean(volume[t-4 : t+1]) / mean(volume[t-50 : t])   # prior 50 sessions
```

### A.6 Tightness

```text
last_range = (max(high[t-9 : t+1]) - min(low[t-9 : t+1])) / pivot
atr_ratio  = ATR(5) / ATR(20)
```

### A.7 Position size

```text
shares = floor(equity * risk_pct * regime_multiplier / (entry - stop))
shares = min(shares, floor(0.01 * ADV20))
shares = min(shares, floor(max_position_pct * equity / entry))
```

### A.8 Expectancy

```text
expectancy_R = win_rate * avg_win_R - (1 - win_rate) * avg_loss_R
```

### A.9 Helper functions used in the pseudocode

| Function | Meaning |
|---|---|
| `clip(x, lo, hi)` | `min(max(x, lo), hi)` |
| `percentile_rank(x, universe)` | Percentile of `x` within `universe`, scaled 1–99 |
| `confirmed_swings(bars, left, right)` | Fractal pivots confirmed only after `right` bars |
| `mean_volume(bars, start, end)` | Mean volume over the inclusive bar range |
| `first_high_after(highs, index)` | First confirmed swing high after a given bar index |
| `lows_after(lows, index)` | Confirmed swing lows after a given bar index |
| `higher_highs_and_lows(bars, i, lookback)` | Boolean test for a sequence of higher highs and higher lows |
| `recent_stage_was(stage)` | Stateful check of the stage history |
| `ADV50[i]` | Mean volume over the 50 sessions ending at `i-1` (prior sessions) |

---

## Appendix B — Glossary

| Term | Meaning |
|---|---|
| **SEPA** | Specific Entry Point Analysis — Minervini's complete framework |
| **VCP** | Volatility Contraction Pattern — progressively smaller pullbacks before a breakout |
| **Trend Template** | Eight technical criteria that define a Stage 2 uptrend |
| **Stage 2** | The advancing/markup phase; the only stage Minervini buys |
| **Pivot** | The high of the final contraction; the breakout level |
| **Contraction** | A pullback from a local high to a local low within a base |
| **Base** | A consolidation in a Stage 2 uptrend |
| **Volume dry-up** | Declining volume through the contractions, indicating supply exhaustion |
| **RS rank** | Relative strength percentile versus the universe; not RSI |
| **CRS** | ChartMill Relative Strength — a proprietary percentile analogous to RS |
| **HGM** | High Growth Momentum — ChartMill's 0–10 fundamental composite |
| **Setup Quality** | ChartMill's 0–10 structural score |
| **R** | Initial risk per share = entry − stop |
| **MFE** | Maximum favorable excursion — the best unrealized profit of a trade |
| **BE** | Break-even stop |
| **ADV** | Average daily volume |
| **Primary base** | First major consolidation after an IPO |

---

*Document generated from the `docs/trading/Minevrini/` corpus on 2026-10-22. All rules must be verified on point-in-time market data. The corpus is secondary literature and contains conflicting numbers; see §23. This document is not investment advice.*
