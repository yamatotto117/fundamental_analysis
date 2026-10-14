import os
from datetime import datetime


def save_report(report: str, out_dir: str = "reports") -> str:
    """レポートをタイムスタンプ付きファイルに保存し、保存先パスを返す。"""
    os.makedirs(out_dir, exist_ok=True)
    filename = f"report_{datetime.now():%Y%m%d_%H%M%S}.txt"
    path = os.path.join(out_dir, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(report)
    return path
