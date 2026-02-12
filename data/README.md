# Data Layout for Q1

- Raw Binance BTC/USDT candles (1m, 2023-03-01 to 2023-03-21):
  - Existing: `BTCUSDT_rawDATA/` (Binance standard kline CSVs).
  - Optional copy: `data/raw/binance/BTCUSDT/`.

- Raw BTC/USD candles (1m, 2023-03-01 to 2023-03-21):
  - Expected: `data/raw/coinbase/BTCUSD/` (or another USD spot venue).

- Processed / cleaned data used in analysis:
  - `data/processed/` (e.g. merged, cleaned basis-ready datasets).

This layout is for Question 1 (cross-currency basis BTC/USDT vs BTC/USD).