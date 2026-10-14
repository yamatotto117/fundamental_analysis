from config import WATCH_LIST
from src.stock_price import fetch_stock_data
from src.screener import screen_stock
from src.checklist import check_risks

for code in WATCH_LIST:
    data = fetch_stock_data(code)
    s = screen_stock(data)
    r = check_risks(data)

    mark = "★候補" if s["is_candidate"] else " "
    print(f"{mark} {s['code']} {s['name']} ({s['passed']}/{s['total']})")

    for name, c in s["checks"].items():
        ok = "○" if c["pass"] else "×"
        print(f"      {ok} {name}: {c['value']}  [{c['desc']}]")
    print()

    if r["warnings"]:
        print("       ⚠ 危険信号:")
        for w in r["warnings"]:
            print(f"          - {w}")
    print()
