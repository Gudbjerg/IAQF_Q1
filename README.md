# IAQF 2026 – Question 1: Cross-Currency Basis (BTC/USDT vs BTC/USD)

This repository contains code, data and analysis for Question 1 of the IAQF 2026 student competition. The goal is to measure and explain the **cross-currency basis** between BTC priced in USDT (Binance BTCUSDT) and BTC priced in USD (Coinbase BTCUSD).

## Project Structure

- `notebooks/Q1_cross_currency_basis.ipynb` – main analysis notebook.
- `src/download_coinbase_candles.py` – script to download historical BTC-USD candles from Coinbase.
- `data/raw/` – raw 1-minute candle data from Binance (BTCUSDT) and Coinbase (BTCUSD).
- `data/processed/` – cleaned and aligned datasets used by the notebook.
- `tests/` – basic data-integrity tests.
- `requirements.txt` – Python dependencies.

## Data and Sample

- **Assets:** BTCUSDT (Binance spot) and BTCUSD (Coinbase spot).
- **Frequency:** 1-minute OHLCV candles.
- **Period:** 2023-03-01 to 2023-03-21 (UTC).
- **Cleaning:**
  - Remove duplicate timestamps.
  - Drop rows with non-positive prices or negative volume.
  - Align both series on a common 1-minute UTC grid over their overlapping window.
  - Drop minutes where either leg has a missing close price when constructing the basis.

## Basis Definition

Let \(P^{USDT}_t\) be the BTCUSDT price (Binance) and \(P^{USD}_t\) the BTCUSD price (Coinbase). The **log cross-currency basis** is

$$
 b_t = \log P^{USDT}_t - \log P^{USD}_t.
$$

- \(b_t < 0\): BTCUSDT trades at a **discount** to BTCUSD.
- \(b_t > 0\): BTCUSDT trades at a **premium** to BTCUSD.

We primarily work with log prices to make relative differences symmetric and better behaved in regressions.

## Transaction Costs and No-Arb Band

To assess whether differences are economically meaningful, we model a simple transaction-cost "no-arb" band:

- Binance taker fee: 0.10% (\(0.001\)).
- Coinbase taker fee: 0.40% (\(0.004\)).

For small fees, \(\log(1+x) \approx x\), so the total round-trip log cost is approximated as

$$
 \tau \approx 0.001 + 0.004 = 0.005 \quad (0.5\%).
$$

We treat \(\pm \tau\) as a **no-arbitrage band**:

- If \(|b_t| \le \tau\), the deviation is too small to cover trading costs.
- If \(|b_t| > \tau\), the deviation is large enough to be potentially arbitrageable.

We also store direction-specific bands (currently numerically equal) so we can later allow for asymmetric or time-varying costs by leg.

## Core Empirical Findings

All numbers below are computed in `Q1_cross_currency_basis.ipynb`.

### 1. Level of the Cross-Currency Basis

Over the full sample (≈29,950 valid 1-minute observations):

- **Mean basis:** ≈ **−0.24%**.
- **Median basis:** ≈ **−0.23%**.
- **Standard deviation:** ≈ **0.29%**.
- Basis distribution is clearly **left-skewed**: BTCUSDT usually trades at a **discount** to BTCUSD.

Extremes relative to this distribution:

- About **6.2%** of minutes have \(|b_t - \bar b| > 2\sigma\).
- About **2.0%** of minutes have \(|b_t - \bar b| > 3\sigma\).

These large deviations are heavily concentrated around the March 10–13 stress episode.

### 2. After Transaction Costs (No-Arb Band)

Using \(\tau \approx 0.5\%\):

- **Share of minutes with \(|b_t| > \tau\):** ≈ **13.3%**.
- **Count of such minutes:** 3,986 out of 29,950.
- **Direction:**
  - Share with \(b_t > \tau\) (BTCUSDT rich vs BTCUSD): **0.0**.
  - Share with \(b_t < -\tau\) (BTCUSDT cheap vs BTCUSD): **13.3%**.

So, after a conservative cost band, economically large dislocations occur in about one out of eight minutes and are almost entirely **one-sided**: BTC priced in USDT is cheap relative to BTC priced in USD. These cost-band breaches cluster in and around the March 10–13 stress period.

### 3. Persistence of the Basis

We estimate an AR(1) model

$$
 b_t = \alpha + \phi b_{t-1} + \varepsilon_t.
$$

- **Overall AR(1) coefficient:** \(\phi \approx 0.9985\).
- **Implied half-life:** ≈ **7.5 hours** (≈448 minutes).
- Augmented Dickey–Fuller test: statistic ≈ −2.77, p-value ≈ 0.063 → the basis is very persistent but likely stationary over this window.

Splitting by regime using a stress dummy (March 10–13 = 1, otherwise 0):

- **Normal periods:** \(\phi_{\text{normal}} \approx 0.9972\), half-life ≈ **4.1 hours**.
- **Stress periods:** \(\phi_{\text{stress}} \approx 0.9980\), half-life ≈ **5.7 hours**.

Thus, basis shocks decay over **hours**, not minutes, and are somewhat **more persistent in stress**.

### 4. Distribution by Regime

Histograms of \(b_t\) show:

- **Normal days (stress = 0):**
  - Tight concentration around small negative values.
  - Deep discounts (≤ −0.5%) are rare.
- **Stress days (stress = 1):**
  - Distribution shifts strongly left.
  - Many observations between roughly −0.5% and −1.2%; near-zero deviations become rare.

This confirms that the cross-currency basis is **regime-dependent**, widening and becoming more negative during market stress.

### 5. Drivers of the Basis (Regression)

We run a linear regression of the form

$$
 b_t = \beta_0 + \beta_1 \text{stress}_t + \beta_2 \text{rv\_usd\_60,t}
       + \beta_3 \text{volume\_usd\_scaled,t} + \beta_4 b_{t-1} + \varepsilon_t,
$$

where:

- `stress`: dummy = 1 on 2023-03-10–13 (systemic stress), 0 otherwise.
- `rv_usd_60`: 60-minute rolling volatility of BTCUSD 1-minute log returns (realized volatility proxy).
- `volume_usd_scaled`: BTCUSD volume divided by its median (liquidity proxy).
- `basis_lag1`: lagged basis, capturing AR(1) persistence.

Key qualitative results:

- **Lagged basis** (\(\beta_4\)) ≈ 0.997 – confirms very strong short-run persistence.
- **Realized volatility** (\(\beta_2\)) is significantly **negative**:
  - Higher BTCUSD volatility is associated with a **more negative basis** (larger USDT discount).
- **Stress dummy** (\(\beta_1\)) is also **negative** conditional on volatility:
  - Even after controlling for volatility and persistence, stress periods tilt the basis further negative.
- **USD volume** (\(\beta_3\)) is small and **positive**:
  - Higher Coinbase volume is associated with a slightly **less negative** basis, suggesting that deeper USD liquidity helps limit dislocations.

## Economic Interpretation

The empirical results are consistent with the following story:

1. **Persistent USDT Discount:**
   - BTC priced in USDT trades at a small but persistent discount to BTC priced in USD (≈0.2–0.3% on average).
   - This likely reflects credit/peg and regulatory risk in USDT and off-shore venues relative to bank USD on regulated venues.

2. **Stress and Volatility Amplify the Discount:**
   - During the March 10–13 stress episode, the discount widens sharply (to ~1–1.5%) and remains below the transaction-cost band for long stretches.
   - Higher realized volatility and the stress dummy both point to wider, more negative basis during turbulent periods.

3. **Arbitrage is Constrained:**
   - AR(1) half-lives of several hours (especially in stress) suggest that dislocations are not arbitraged away instantly.
   - Directional results (almost all cost-band breaches are BTCUSDT cheap vs BTCUSD) indicate that arbitrage is one-sided and constrained by funding, capital, or regulatory frictions.

4. **Role of USD Liquidity:**
   - Higher BTCUSD volume on Coinbase is associated with somewhat smaller discounts, hinting that strong USD-side liquidity facilitates better price alignment across venues.

Overall, the analysis documents a **persistent, stress-sensitive cross-currency basis** between BTC/USDT and BTC/USD that is usually a USDT discount, occasionally large enough to overcome realistic transaction costs, and driven by volatility, stress, and liquidity conditions.

## Reproducing the Analysis

1. Create and activate a virtual environment in the project root:

```bash
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\\Scripts\\activate  # Windows
pip install -r requirements.txt
```

2. Ensure raw data CSVs are present under `data/raw/binance/BTCUSDT/` and `data/raw/coinbase/BTCUSD/`.

3. Open `notebooks/Q1_cross_currency_basis.ipynb` in VS Code or Jupyter and run all cells.

This will regenerate the cleaned data, basis series, cost-band metrics, persistence diagnostics, driver regressions, and plots described above.
