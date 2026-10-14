from datetime import datetime

from config import BUDGET_PER_STOCK
from src.collector import load_cache
from src.screener import screen_stock
from src.checklist import check_risks
from src.stock_price import within_budget, min_lot_cost, annual_dividend_per_lot, week52_position
from src.notifier import save_report

TOP_N = 50  # レポートに載せる上位件数


def analyze_all(budget: float = BUDGET_PER_STOCK) -> list[dict]:
    """
    キャッシュ済み全銘柄を分析する。
    予算内（1単元が budget 以下）の銘柄だけを対象にし、
    スクリーニング通過数→1単元額の安い順で並べて返す。
    """
    data = load_cache()
    data = [d for d in data if within_budget(d, budget)]

    results = []
    for d in data:
        results.append(
            {
                "d": d,
                "s": screen_stock(d),
                "r": check_risks(d),
                "lot_cost": min_lot_cost(d),
                "lot_dividend": annual_dividend_per_lot(d),
            }
        )

    # リスクレベルを数値化（低→0, 中→1, 高→2）。小さいほど安全。
    risk_order = {"低": 0, "中": 1, "高": 2}

    def sort_key(x):
        passed = x["s"]["passed"]  # 多いほど良い
        risk = risk_order.get(x["r"]["risk_level"], 3)  # 小さいほど良い
        cost = x["lot_cost"] or float("inf")  # 小さいほど良い
        # passedは降順にしたいのでマイナス、riskとcostは昇順
        return (-passed, risk, cost)

    results.sort(key=sort_key)
    return results


def _fmt(d: dict) -> str:
    per = f"{d['per']:.1f}" if d.get("per") else "―"
    pbr = f"{d['pbr']:.2f}" if d.get("pbr") else "―"
    psr = f"{d['psr']:.2f}" if d.get("psr") else "―"
    roe = f"{d['roe']:.1%}" if d.get("roe") else "―"
    dy = f"{d['dividend_yield']:.1%}" if d.get("dividend_yield") else "―"
    eq = f"{d['equity_ratio']:.0%}" if d.get("equity_ratio") is not None else "―"
    return f"PER={per} PBR={pbr} PSR={psr} ROE={roe} 配当={dy} 自己資本{eq}"


def format_report(results: list[dict], budget: float = BUDGET_PER_STOCK) -> str:
    lines = []
    lines.append(f"=== ファンダメンタルズ分析レポート {datetime.now():%Y-%m-%d %H:%M} ===")

    candidates = [x for x in results if x["s"]["is_candidate"]]
    lines.append(f"予算 {budget:,.0f}円以内 / 対象 {len(results)}社 / 全条件クリア候補 {len(candidates)}社")
    lines.append("")

    lines.append(f"■ 上位{TOP_N}社（スクリーニング通過数→1単元の安い順）")
    for x in results[:TOP_N]:
        d, s, r = x["d"], x["s"], x["r"]
        mark = "★" if s["is_candidate"] else " "
        lot = f"{x['lot_cost']:,.0f}円" if x["lot_cost"] else "―"
        div = f"{x['lot_dividend']:,.0f}円/年" if x["lot_dividend"] else "無配"
        pos = week52_position(d)
        if pos is None:
            pos_s = "52週位置 -"
        else:
            zone = "高値圏⚠" if pos >= 80 else ("安値圏" if pos <= 20 else "中位")
            pos_s = f"52週位置 {pos:.0f}% ({zone})"
        lines.append(f"{mark} {d['code']} {d['name'][:28]}  " f"[{s['passed']}/{s['total']}] {_fmt(d)}")
        lines.append(f"      1単元 {lot} / 年間配当 {div} / {pos_s} / リスク{r['risk_level']}")
        for w in r["warnings"]:
            lines.append(f"      ⚠ {w}")

    return "\n".join(lines)


if __name__ == "__main__":
    results = analyze_all()
    report = format_report(results)
    print(report)

    path = save_report(report)
    print(f"\nレポートを保存しました: {path}")
