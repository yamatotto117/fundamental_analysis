import os
import csv
from datetime import datetime


def save_report(report: str, out_dir: str = "reports") -> str:
    """レポート（テキスト）をタイムスタンプ付きファイルに保存し、保存先パスを返す。"""
    os.makedirs(out_dir, exist_ok=True)
    filename = f"report_{datetime.now():%Y%m%d_%H%M%S}.txt"
    path = os.path.join(out_dir, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(report)
    return path


# CSVの列定義（表示名, 値を取り出す関数）。1銘柄=1行でExcel等でソート/フィルタしやすくする。
CSV_COLUMNS = [
    ("コード", lambda row: row["d"].get("code")),
    ("銘柄名", lambda row: row["d"].get("name")),
    ("業種", lambda row: row["d"].get("sector")),
    ("候補", lambda row: "★" if row["s"]["is_candidate"] else ""),
    ("通過数", lambda row: row["s"]["passed"]),
    ("リスク", lambda row: row["r"]["risk_level"]),
    ("警告数", lambda row: len(row["r"]["warnings"])),
    ("株価", lambda row: row["d"].get("price")),
    ("1単元額", lambda row: row.get("lot_cost")),
    ("年間配当", lambda row: row.get("lot_dividend")),
    ("PER", lambda row: row["d"].get("per")),
    ("PBR", lambda row: row["d"].get("pbr")),
    ("PSR", lambda row: row["d"].get("psr")),
    ("ROE", lambda row: row["d"].get("roe")),
    ("配当利回り", lambda row: row["d"].get("dividend_yield")),
    ("自己資本比率", lambda row: row["d"].get("equity_ratio")),
    ("52週位置", lambda row: row.get("week52_pos")),
    ("警告", lambda row: " / ".join(row["r"]["warnings"])),
]


def save_report_csv(results: list[dict], out_dir: str = "reports") -> str:
    """
    分析結果を1銘柄=1行のCSVで保存する。
    Excel/スプレッドシートで開けば列ヘッダからソート・フィルタできる。
    results の各要素は {"d","s","r","lot_cost","lot_dividend","week52_pos"} を持つ想定。
    """
    os.makedirs(out_dir, exist_ok=True)
    filename = f"report_{datetime.now():%Y%m%d_%H%M%S}.csv"
    path = os.path.join(out_dir, filename)

    headers = [name for name, _ in CSV_COLUMNS]
    # Excelで文字化けしないよう utf-8-sig（BOM付き）で書く
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for row in results:
            writer.writerow([getter(row) for _, getter in CSV_COLUMNS])

    return path
