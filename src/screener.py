from config import SCREEN_CRITERIA


def screen_stock(data: dict, criteria: dict = SCREEN_CRITERIA) -> dict:
    """
    1銘柄のデータを条件に照らし、各項目の合否と総合判定を返す。
    データが None の項目は "不明" 扱いで合格にはしない。
    """
    checks = {}

    # per = data.get("per")
    # checks["PER"] = {
    #     "value": per,
    #     "pass": per is not None and per <= criteria["per_max"],
    #     "desc": f"PER <= {criteria['per_max']}",
    # }

    # pbr = data.get("pbr")
    # checks["PBR"] = {
    #     "value": pbr,
    #     "pass": pbr is not None and pbr <= criteria["pbr_max"],
    #     "desc": f"PBR <= {criteria['pbr_max']}",
    # }

    psr = data.get("psr")
    checks["PSR"] = {
        "value": psr,
        "pass": psr is not None and psr <= criteria["psr_max"],
        "desc": f"PSR <= {criteria['psr_max']}",
    }

    eq = data.get("equity_ratio")
    checks["自己資本比率"] = {
        "value": eq,
        "pass": eq is not None and eq >= criteria["equity_ratio_min"],
        "desc": f"自己資本比率 >= {criteria['equity_ratio_min']}",
    }

    # roe = data.get("roe")
    # checks["ROE"] = {
    #     "value": roe,
    #     "pass": roe is not None and roe >= criteria["roe_min"],
    #     "desc": f"ROE >= {criteria['roe_min']}",
    # }

    dy = data.get("dividend_yield")
    checks["配当利回り"] = {
        "value": dy,
        "pass": dy is not None and dy >= criteria["dividend_yield_min"],
        "desc": f"配当利回り >= {criteria['dividend_yield_min']}",
    }

    passed = sum(1 for c in checks.values() if c["pass"])
    total = len(checks)

    return {
        "code": data.get("code"),
        "name": data.get("name"),
        "checks": checks,
        "passed": passed,
        "total": total,
        "is_candidate": passed == total,  # 全条件クリアで買い候補
    }
