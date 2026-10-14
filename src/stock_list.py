import pandas as pd

JPX_URL = "https://www.jpx.co.jp/markets/statistics-equities/misc/tvdivq0000001vg2-att/data_j.xlsx"

# 母集団に含める市場・商品区分。まずはプライムのみ。
# 3市場に広げたいときは下2行のコメントを外す。
TARGET_MARKETS = [
    "プライム（内国株式）",
    "スタンダード（内国株式）",
    "グロース（内国株式）",
]


def load_stock_list(local_path: str = "data_j.xlsx") -> pd.DataFrame:
    """
    JPXの銘柄一覧（ローカル保存済みのxlsx）を読み込み、
    対象市場の普通株だけに絞った DataFrame を返す。
    列: コード / 銘柄名 / 市場・商品区分 / 33業種区分
    """

    df = pd.read_excel(local_path)
    df = df[df["市場・商品区分"].isin(TARGET_MARKETS)].copy()

    # コードを4桁文字列に統一（yfinanceは "7203.T" 形式を使うため）
    df["コード"] = df["コード"].astype(str).str.zfill(4)
    return df[["コード", "銘柄名", "市場・商品区分", "33業種区分"]].reset_index(drop=True)


def get_target_codes(local_path: str = "data_j.xlsx") -> list[str]:
    """対象銘柄の証券コード（4桁文字列）のリストを返す。"""
    df = load_stock_list(local_path)
    return df["コード"].tolist()
