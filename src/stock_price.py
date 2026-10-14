import yfinance as yf


def fetch_stock_data(code: str) -> dict:
    """
    日本株の証券コード（例: "7203"）を受け取り、指標を dict で返す。
    取得に失敗した銘柄は None を返す（呼び出し側でスキップする想定）。
    """
    try:
        ticker = yf.Ticker(f"{code}.T")
        info = ticker.info
    except Exception as e:
        print(f"  [取得失敗] {code}: {e}")
        return None

    # info が空、または価格が取れない銘柄は無効扱い
    if not info or info.get("currentPrice") is None:
        return None

    def pick(key):
        return info.get(key)

    # 配当利回りだけ yfinance は % 表記で返すので /100 して小数に統一する
    div = pick("dividendYield")
    dividend_yield = div / 100 if div is not None else None

    # 自己資本比率を貸借対照表から計算（純資産 ÷ 総資産）
    equity_ratio = None
    try:
        bs = ticker.balance_sheet

        # 行名はyfinanceの表記ゆれがあるので候補から探す
        def bs_value(candidates):
            for name in candidates:
                if name in bs.index:
                    val = bs.loc[name].iloc[0]
                    if val is not None:
                        return float(val)
            return None

        total_assets = bs_value(["Total Assets"])
        total_equity = bs_value(
            [
                "Stockholders Equity",
                "Total Equity Gross Minority Interest",
                "Common Stock Equity",
            ]
        )
        if total_assets and total_equity and total_assets != 0:
            equity_ratio = total_equity / total_assets
    except Exception:
        equity_ratio = None

    return {
        "code": code,
        "name": pick("longName") or pick("shortName"),
        "sector": pick("sector"),
        "price": pick("currentPrice"),
        "week52_high": pick("fiftyTwoWeekHigh"),
        "week52_low": pick("fiftyTwoWeekLow"),
        "market_cap": pick("marketCap"),
        "per": pick("trailingPE"),
        "pbr": pick("priceToBook"),
        "psr": pick("priceToSalesTrailing12Months"),  # 株価売上高倍率
        "roe": pick("returnOnEquity"),  # 小数（0.124 = 12.4%）
        "roa": pick("returnOnAssets"),  # 小数
        "dividend_yield": dividend_yield,  # 小数に統一（0.035 = 3.5%）
        "dividend_rate": pick("dividendRate"),  # 1株あたり年間配当額（円）
        "debt_to_equity": pick("debtToEquity"),  # %表記（114.9 = 114.9%）
        "current_ratio": pick("currentRatio"),
        "operating_cashflow": pick("operatingCashflow"),
        "revenue_growth": pick("revenueGrowth"),  # 小数
        "earnings_growth": pick("earningsGrowth"),  # 小数
        "profit_margins": pick("profitMargins"),  # 小数
        "equity_ratio": equity_ratio,  # 自己資本比率（小数, 0.5 = 50%）B/Sから計算
    }


def min_lot_cost(data: dict, lot_size: int = 100) -> float | None:
    """1単元（通常100株）を買うのに必要な金額。株価が無ければ None。"""
    price = data.get("price")
    if price is None:
        return None
    return price * lot_size


def within_budget(data: dict, budget: float, lot_size: int = 100) -> bool:
    """1単元の必要額が予算以内なら True。株価不明の銘柄は False（買えないので除外）。"""
    cost = min_lot_cost(data, lot_size)
    if cost is None:
        return False
    return cost <= budget


def annual_dividend_per_lot(data: dict, lot_size: int = 100) -> float | None:
    """1単元（通常100株）あたりの年間配当額（円）。無配・不明は None。"""
    rate = data.get("dividend_rate")
    if rate is None:
        return None
    return rate * lot_size


def week52_position(
    data: dict,
) -> float | None:
    """
    現在値が52週レンジ（高値〜安値）のどこにいるかを 0〜100(%) で返す。
    0% = 52週安値, 100% = 52週高値。計算不能なら None。
    """
    price = data.get("price")
    high = data.get("week52_high")
    low = data.get("week52_low")
    if price is None or high is None or low is None:
        return None
    if high == low:
        return None
    pos = (price - low) / (high - low) * 100
    # 分割・急変で範囲外になることがあるので 0〜100 に収める
    return max(0.0, min(100.0, pos))
