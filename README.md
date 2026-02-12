# IAQF 2026 – Question 1: Cross-Currency Basis (BTC/USDT vs BTC/USD)

This repository contains code, data and analysis for Question 1 of the IAQF 2026 student competition. The goal is to measure and explain the **cross-currency basis** between BTC priced in USDT (Binance BTCUSDT) and BTC priced in USD (Coinbase BTCUSD) over March 2023, with particular focus on the March 10–13 banking/stablecoin stress episode.

All empirical results are generated in the notebook `notebooks/Q1_cross_currency_basis.ipynb`.

---

## 1. Question and Setup

In words, we ask: **How do BTC/USDT and BTC/USD prices differ over time, is there a persistent cross-currency basis once realistic transaction costs are included, and what drives that basis?** We study BTCUSDT on Binance and BTCUSD on Coinbase at 1‑minute frequency from **2023‑03‑01 to 2023‑03‑21 (UTC)**, a period that includes a major banking and stablecoin stress around **March 10–13**.

---

## 2. Data, Cleaning, and Alignment

- **Assets:** BTCUSDT (Binance spot) and BTCUSD (Coinbase spot).
- **Frequency:** 1‑minute OHLCV candles.
- **Period:** 2023‑03‑01–2023‑03‑21 (UTC).
- **Cleaning and alignment:**
  - Parse timestamps to UTC and keep core OHLCV columns.
  - Remove duplicate timestamps.
  - Drop rows with non‑positive prices or negative volume.
  - Align both legs on a common 1‑minute UTC grid over their overlapping window.
  - Drop minutes where either close price is missing when forming the basis.

Key outputs:

- Overlapping window: full sample in the stated period.
- Number of valid basis minutes: **≈ 29 950**.
- Coinbase BTCUSD has **≈ 290** genuine "no trade" 1‑minute gaps that we treat as missing, not errors.

Economically, Binance BTCUSDT trades almost every minute (deep off‑shore USDT venue), while Coinbase BTCUSD has occasional gaps (shallower on‑shore USD venue).

Figure 1 plots the mid prices of BTCUSDT and BTCUSD over the sample, while Figure 2 reports the corresponding trading volumes on Binance and Coinbase, illustrating both the tight co‑movement in prices and the asymmetry in liquidity across venues.

---

## 3. Basis Definition and Transaction Costs

Let \(P^{USDT}_t\) be the BTCUSDT price (Binance) and \(P^{USD}_t\) the BTCUSD price (Coinbase). The log cross‑currency basis is

$$
b_t = \log P^{USDT}_t - \log P^{USD}_t.
$$

- \(b_t < 0\): BTCUSDT is cheaper than BTCUSD (USDT **discount**).
- \(b_t > 0\): BTCUSDT is richer than BTCUSD (USDT **premium**).

We work with log prices so that small relative differences behave like percentage gaps: for small changes, \(b_t \approx (P^{USDT}_t - P^{USD}_t)/P^{USD}_t\).

### Transaction-cost band (no‑arb region)

We proxy spot taker fees as:

- Binance: 0.10% \((0.001)\).
- Coinbase: 0.40% \((0.004)\).

For small \(x\), \(\log(1+x) \approx x\), so the total round‑trip log cost is approximated by

$$
  au \approx 0.001 + 0.004 = 0.005 \quad (\text{about } 0.5\%).
$$

We treat \(\pm \tau\) as a **no‑arbitrage band**:

- If \(|b_t| \le \tau\), the deviation is not large enough to cover trading costs.
- If \(|b_t| > \tau\), the deviation is potentially exploitable after costs.

We also store direction‑specific bands (currently equal numerically) so that asymmetric or time‑varying cost assumptions can be imposed later.

---

## 4. Level of Premium/Discount

Over the full sample of ≈29 950 minutes, the basic moments of the basis are:

| Statistic                | Value (approx.) |
|--------------------------|-----------------|
| Mean basis               | −0.24%          |
| Median basis             | −0.23%          |
| Standard deviation       | 0.29%           |
| Share with \(|z_t|>2\)   | 6.2%            |
| Share with \(|z_t|>3\)   | 2.0%            |

where \(z_t = (b_t - \bar b)/\sigma_b\) is the z‑score.

- BTCUSDT and BTCUSD prices track each other extremely closely at 1‑minute frequency, but **BTCUSDT trades at a systematic discount**: mean and median around **−0.24% to −0.23%**.
- The discount is **regime‑dependent**:
  - In calm days (March 1–9), the basis fluctuates narrowly around a small negative level.
  - During the March 10–13 stress window, the basis falls sharply (down to roughly **−1.5%**) and then settles into a more negative post‑stress plateau.
- About **6.2%** of minutes are more than **2σ** away from the mean and **2.0%** more than **3σ**, with these extremes heavily concentrated in the stress period.

The notebook provides time‑series charts of BTCUSDT/BTCUSD mid prices and of the basis with horizontal lines at 0 and ±\(\tau\), as well as histograms for the full sample and for normal vs stress regimes.
In particular, Figure 3 shows the basis time series together with the 0.5% transaction‑cost band, and Figure 4 displays the distribution of the basis overall and split into normal vs stress periods.

---

## 5. After Transaction Costs: No‑Arb Band

Using the symmetric fee band \(\tau \approx 0.5\%\):

| Metric                                      | Value (approx.) |
|---------------------------------------------|------------------|
| Total basis minutes                         | 29 950           |
| Minutes with \(|b_t| > \tau\)               | 3 986            |
| Share with \(|b_t| > \tau\)                 | 13.3%            |
| Share with \(b_t > \tau\) (USDT rich)       | 0.0%             |
| Share with \(b_t < -\tau\) (USDT cheap)     | 13.3%            |

- About **13.3%** of minutes have \(|b_t|\) larger than our 0.5% fee band.
- **All** such minutes are negative basis: BTCUSDT is cheap vs BTCUSD; there are effectively **no minutes** where BTCUSDT is rich enough after costs to justify the opposite trade.
- These cost‑adjusted dislocations cluster in and around the March 10–13 stress period; in calmer days, deviations rarely clear the fee band.

Thus, once trading costs are included, large, economically meaningful gaps appear reasonably often, but almost exclusively on the **USDT‑discount** side.

---

## 6. Persistence of the Cross-Currency Basis

We estimate an AR(1) model

$$
b_t = \alpha + \phi b_{t-1} + \varepsilon_t
$$

on the 1‑minute basis series and compute half‑lives

$$
  ext{half-life} = \frac{\ln 0.5}{\ln |\phi|}.
$$

| Regime   | \(\phi\) (approx.) | Half‑life (minutes) | Half‑life (hours) |
|----------|----------------------|----------------------|-------------------|
| Overall  | 0.9985               | ≈ 448                | ≈ 7.5             |
| Normal   | 0.9972               | ≈ 248                | ≈ 4.1             |
| Stress   | 0.9980               | ≈ 341                | ≈ 5.7             |

An Augmented Dickey–Fuller test yields a statistic of about −2.77 with p‑value ≈ 0.063: the basis is very persistent but likely stationary over this window.

Interpretation:

- Once a basis shock appears—especially in stress—it decays only gradually over **several hours**, not within a few minutes.
- Dislocations that are large enough to beat costs are therefore **persistent in time**, not fleeting microstructure noise.

---

## 7. What Drives the Basis? (Stress, Volatility, Volume)

We construct the following drivers from the BTCUSD leg and the stress window definition:

- `stress`: dummy = 1 during **2023‑03‑10–13**, 0 otherwise.
- `rv_usd_60`: 60‑minute rolling standard deviation of BTCUSD 1‑minute log returns (realized volatility proxy).
- `volume_usd_scaled`: BTCUSD volume divided by its median (liquidity proxy).
- `basis_lag1`: previous‑minute basis, included to capture persistence.

The main regression is

$$
	ext{basis}_t = \beta_0 + \beta_1\,\text{stress}_t + \beta_2\,\text{rv\_usd\_60,t}
                  + \beta_3\,\text{volume\_usd\_scaled,t} + \beta_4\,\text{basis}_{t-1} + \varepsilon_t.
$$

Qualitative results (from the OLS output):

- **Lagged basis** (\(\beta_4 \approx 0.997\)) dominates short‑run dynamics, confirming the strong AR(1) persistence.
- **Realized volatility** (\(\beta_2 < 0\)) is significantly negative: when BTCUSD volatility is high, the BTCUSDT–BTCUSD basis becomes **more negative** (USDT‑leg cheapens).
- **Stress dummy** (\(\beta_1 < 0\)) is also negative conditional on volatility: even after controlling for volatility and persistence, the stress window tilts the basis further negative.
- **USD volume** (\(\beta_3 > 0\)) is small and positive: greater USD‑venue liquidity is associated with a slightly **less negative** basis.

Interpretation: volatility and systemic stress widen the USDT discount, while deeper USD liquidity on Coinbase modestly mitigates it.

---

## 8. Economic Interpretation: Why a USDT Discount?

Putting the distributions, cost‑band exceedances, persistence, and regressions together yields a coherent narrative:

- **USDT carries credit/peg and regulatory risk** relative to bank USD. Investors demand a discount to hold BTC in USDT terms, especially in stress.
- **Off‑shore vs on‑shore segmentation:** Binance (USDT, off‑shore) is deep but less regulated; Coinbase (USD, on‑shore) is shallower but carries regulatory and banking protections. Capital, KYC, and regulatory frictions slow down arbitrage flows between these venues.
- **Stress dynamics:** During the March 10–13 banking/stablecoin turmoil, demand for "real USD" BTC rises and off‑shore venues see forced selling and funding pressures, deepening the USDT discount and generating the pronounced negative tail.
- **Constrained arbitrage:** High AR(1) coefficients and long half‑lives show that even large, cost‑adjusted dislocations do not disappear instantly, consistent with capital, balance‑sheet, and risk‑limit constraints on arbitrageurs.

---

## 9. Conclusions (Directly Answering Q1)

Relative to the competition question, the evidence shows that:

1. **Price relationship over time:** BTCUSDT and BTCUSD track each other very closely at 1‑minute frequency, but BTCUSDT trades at a **systematic discount** of roughly **0.2–0.3%** on average. The discount widens sharply (down to ~1–1.5%) during the March 10–13 stress event and remains more negative afterwards.
2. **After transaction costs:** With a conservative **0.5%** round‑trip fee band, about **13.3%** of minutes (3 986 out of 29 950) have \(|b_t|\) above costs. These cost‑adjusted dislocations are almost entirely **one‑sided**: BTCUSDT is cheap vs BTCUSD; BTCUSDT is never meaningfully rich after costs.
3. **Persistence:** AR(1) estimates imply very high persistence (overall \(\phi \approx 0.9985\)) with half‑lives of **4–6 hours** across regimes and about **7.5 hours** overall. The ADF test suggests the basis is extremely persistent but likely stationary. Economically, once a premium/discount opens—especially in stress—it decays only over hours, not minutes.
4. **Drivers:** A regression with an AR(1) term shows that higher 60‑minute BTCUSD volatility and being in the stress window are associated with a **more negative basis**, while higher BTCUSD volume is modestly associated with a **less negative basis**. This supports a story where credit, funding, and regulatory frictions between USD and USDT markets, amplified by stress and volatility, create a persistent USDT discount that arbitrage cannot instantly close.

---

## Figures

- **Figure 1** – BTCUSDT vs BTCUSD mid prices (1‑minute). See [figures/fig_mid_prices.png](figures/fig_mid_prices.png). Prices on Binance (USDT) and Coinbase (USD) move almost indistinguishably, confirming that we are observing the same underlying asset.
- **Figure 2** – Trading volume by venue (1‑minute). See [figures/fig_volumes.png](figures/fig_volumes.png). Binance volumes are much higher and spikier than Coinbase volumes, consistent with Binance being the deeper off‑shore USDT venue.
- **Figure 3** – BTCUSDT–BTCUSD log basis with 0.5% cost band. See [figures/fig_basis_with_band.png](figures/fig_basis_with_band.png). The basis oscillates around a modest negative level in calm periods, plunges well below the cost band during the March 10–13 stress episode, and settles into a more negative post‑stress regime.
- **Figure 4** – Basis histograms: full sample, normal vs stress. See [figures/fig_basis_histograms.png](figures/fig_basis_histograms.png). The overall distribution is left‑skewed, with a pronounced negative tail that becomes much thicker in the stress subsample, documenting the widening and asymmetry of the USDT discount.

---

## Project Structure and How to Reproduce

- `notebooks/Q1_cross_currency_basis.ipynb` – main analysis notebook (all tables and plots referenced above are produced here).
- `src/download_coinbase_candles.py` – script to download historical BTC‑USD candles from Coinbase.
- `data/raw/` – raw 1‑minute candle data from Binance (BTCUSDT) and Coinbase (BTCUSD).
- `data/processed/` – cleaned and aligned datasets used by the notebook.
- `tests/` – basic data‑integrity tests.
- `requirements.txt` – Python dependencies.

### Reproducing the analysis

1. Create and activate a virtual environment in the project root:

```bash
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\\Scripts\\activate  # Windows
pip install -r requirements.txt
```

2. Ensure raw data CSVs are present under `data/raw/binance/BTCUSDT/` and `data/raw/coinbase/BTCUSD/` (or re‑run `src/download_coinbase_candles.py` for Coinbase).

3. Open `notebooks/Q1_cross_currency_basis.ipynb` in VS Code or Jupyter and run all cells.

This will regenerate the cleaned data, basis series, cost‑band metrics, persistence diagnostics, regression tables and the plots referred to in this README.
