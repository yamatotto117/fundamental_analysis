from config import RISK_CRITERIA


def check_risks(data: dict, criteria: dict = RISK_CRITERIA) -> dict:
    """
    1銘柄のデータから危険信号を洗い出す。
    該当する警告のリストを返す。警告が無ければ空リスト。
    """
    warnings = []

    roe = data.get("roe")
    if roe is not None and roe < criteria["roe_min"]:
        warnings.append(f"ROEがマイナス（{roe:.1%}）: 赤字体質の疑い")

    dte = data.get("debt_to_equity")
    if dte is not None and dte > criteria["debt_to_equity_max"]:
        warnings.append(f"負債比率が高い（{dte:.0f}%）: 財務レバレッジ過大")

    cr = data.get("current_ratio")
    if cr is not None and cr < criteria["current_ratio_min"]:
        warnings.append(f"流動比率が低い（{cr:.2f}）: 短期の支払い能力に不安")

    rg = data.get("revenue_growth")
    if rg is not None and rg < criteria["revenue_growth_min"]:
        warnings.append(f"減収（売上成長率 {rg:.1%}）: 事業縮小の兆候")

    eg = data.get("earnings_growth")
    if eg is not None and eg < criteria["earnings_growth_min"]:
        warnings.append(f"減益（利益成長率 {eg:.1%}）: 収益悪化の兆候")

    ocf = data.get("operating_cashflow")
    if ocf is not None and ocf < 0:
        warnings.append(f"営業CFがマイナス（{ocf:,.0f}）: 本業で現金を稼げていない")

    # データ血相そのものも「判断材料不足」として知らせる
    missing = [k for k in ["roe", "per", "pbr", "debt_to_equity"] if data.get(k) is None]
    if missing:
        warnings.append(f"データ欠損あり（{', '.join(missing)}) : 要手動確認")

    return {
        "code": data.get("code"),
        "name": data.get("name"),
        "warnings": warnings,
        "risk_level": _risk_level(len(warnings)),
    }


def _risk_level(n: int) -> str:
    if n == 0:
        return "低"
    if n <= 2:
        return "中"
    return "高"
