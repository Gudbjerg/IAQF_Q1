"""Download Coinbase BTC-USD 1m candles for March 1-21, 2023.

This script calls the public Coinbase Exchange REST API `/products/{product_id}/candles`
endpoint in safe-sized time chunks so as not to exceed the 300-candle limit per
request (for 1-minute granularity).

Output:
    data/raw/coinbase/BTCUSD/BTCUSD-1m-2023-03-01_2023-03-21.csv

Run from the project root, e.g.:
    python -m src.download_coinbase_candles
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable, List

import requests

BASE_URL = "https://api.exchange.coinbase.com"
PRODUCT_ID = "BTC-USD"
GRANULARITY = 60  # 1 minute
MAX_CANDLES_PER_REQUEST = 300


@dataclass
class Candle:
    time: int  # Unix timestamp (seconds since epoch, UTC)
    low: float
    high: float
    open: float
    close: float
    volume: float


def fetch_candles_once(
    product_id: str,
    start: datetime,
    end: datetime,
    granularity: int = GRANULARITY,
) -> List[Candle]:
    """Fetch a single batch of candles between start and end.

    Coinbase returns up to 300 candles for the given granularity.
    """

    params = {
        "start": start.isoformat().replace("+00:00", "Z"),
        "end": end.isoformat().replace("+00:00", "Z"),
        "granularity": granularity,
    }

    headers = {
        "User-Agent": "IAQF-Q1-candles-script",
        "Accept": "application/json",
    }

    resp = requests.get(
        f"{BASE_URL}/products/{product_id}/candles",
        params=params,
        headers=headers,
        timeout=15,
    )
    resp.raise_for_status()

    data = resp.json()

    candles: List[Candle] = []
    for row in data:
        # Coinbase schema: [time, low, high, open, close, volume]
        t, low, high, open_, close, volume = row
        candles.append(
            Candle(
                time=int(t),
                low=float(low),
                high=float(high),
                open=float(open_),
                close=float(close),
                volume=float(volume),
            )
        )

    return candles


def chunked_time_ranges(
    start: datetime,
    end: datetime,
    granularity_seconds: int,
    max_candles: int,
) -> Iterable[tuple[datetime, datetime]]:
    """Yield [start, end] ranges that respect the max_candles limit.

    For granularity=60 and max_candles=300 this creates ~5h chunks.
    """

    step = timedelta(seconds=granularity_seconds * max_candles)
    current = start
    while current < end:
        next_end = min(current + step, end)
        yield current, next_end
        current = next_end


def write_candles_to_csv(candles: List[Candle], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    # Sort and de-duplicate by time
    candles_sorted = sorted(
        {c.time: c for c in candles}.values(), key=lambda c: c.time)

    with path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["time", "low", "high", "open", "close", "volume"])
        for c in candles_sorted:
            writer.writerow([c.time, c.low, c.high, c.open, c.close, c.volume])


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    output_path = project_root / "data" / "raw" / "coinbase" / \
        "BTCUSD" / "BTCUSD-1m-2023-03-01_2023-03-21.csv"

    start = datetime(2023, 3, 1, 0, 0, 0, tzinfo=timezone.utc)
    end = datetime(2023, 3, 21, 23, 59, 0, tzinfo=timezone.utc)

    all_candles: List[Candle] = []

    for i, (chunk_start, chunk_end) in enumerate(
        chunked_time_ranges(start, end, GRANULARITY, MAX_CANDLES_PER_REQUEST), start=1
    ):
        print(
            f"Fetching chunk {i}: {chunk_start.isoformat()} -> {chunk_end.isoformat()}")
        batch = fetch_candles_once(
            PRODUCT_ID, chunk_start, chunk_end, GRANULARITY)
        print(f"  Retrieved {len(batch)} candles")
        all_candles.extend(batch)

    print(f"Total candles fetched: {len(all_candles)}")
    write_candles_to_csv(all_candles, output_path)
    print(f"Saved CSV to {output_path}")


if __name__ == "__main__":
    main()
