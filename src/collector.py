import os
import csv
import time

from src.stock_list import get_target_codes
from src.stock_price import fetch_stock_data

# 保存先。1行=1銘柄のデータ。
CACHE_PATH = "data/stock_cache.csv"

# dict のキー順（CSVの列順）。fetch_stock_data の返り値に合わせる。
FIELDS = [
    "code",
    "name",
    "sector",
    "price",
    "week52_high",
    "week52_low",
    "market_cap",
    "per",
    "pbr",
    "psr",
    "roe",
    "roa",
    "dividend_yield",
    "dividend_rate",
    "debt_to_equity",
    "current_ratio",
    "operating_cashflow",
    "revenue_growth",
    "earnings_growth",
    "profit_margins",
    "equity_ratio",
]


def _load_done_codes() -> set[str]:
    """すでに取得済みの銘柄コードを返す（再開用）。"""
    if not os.path.exists(CACHE_PATH):
        return set()
    done = set()
    with open(CACHE_PATH, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None or "code" not in reader.fieldnames:
            return set()
        for row in reader:
            if row.get("code"):
                done.add(row["code"])
        return done


def collect(limit: int | None = None, sleep_sec: float = 1.0) -> None:
    """
    対象銘柄を取得して CACHE_PATH に追記保存する。
    すでに取得済みの銘柄はスキップするので、再実行で続きから進む。
    limit を指定すると、その件数だけ処理（テスト用）。
    """
    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)

    codes = get_target_codes()
    done = _load_done_codes()
    print("DEBUG done件数:", len(done), "先頭5件:", list(done)[:5])
    todo = [c for c in codes if c not in done]
    if limit is not None:
        todo = todo[:limit]

    print(f"全{len(codes)}/社 / 取得済み{len(done)}社 / 今回対象{len(todo)}社")

    # ファイルが無ければヘッダを書く
    new_file = not os.path.exists(CACHE_PATH)
    with open(CACHE_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if new_file:
            writer.writeheader()

        for i, code in enumerate(todo, 1):
            data = fetch_stock_data(code)
            if data is None:
                print(f"{i:>4}/{len(todo)} {code} -> スキップ")
            else:
                writer.writerow(data)
                f.flush()
                print(f"{i:>4}/{len(todo)} {code} {data['name']}")
            time.sleep(sleep_sec)
    print("完了")


def load_cache() -> list[dict]:
    """キャッシュ済みの全銘柄データを dict のリストで返す。"""
    if not os.path.exists(CACHE_PATH):
        return []
    rows = []
    with open(CACHE_PATH, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            # CSVは全部文字列なので、数値列を float に変換（空は None）
            for key in FIELDS:
                if key in ("code", "name", "sector"):
                    continue
                val = row.get(key, "")
                row[key] = float(val) if val not in ("", None) else None
            rows.append(row)
    return rows
