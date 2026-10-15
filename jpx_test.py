from src.collector import load_cache
from src.checklist import check_risks

data = load_cache()
by_code = {d["code"]: d for d in data}

# 1. RAIZNEXT(6379) に配当警告が付くか
print("=== RAIZNEXT (6379) ===")
d = by_code.get("6379")
if d:
    r = check_risks(d)
    print(f"  price={d['price']} dividend_rate={d['dividend_rate']} dividend_yield={d['dividend_yield']}")
    print(f"  リスク{r['risk_level']}")
    for w in r["warnings"]:
        print(f"   ⚠ {w}")

# 2. 配当警告が付いた銘柄の総数と、高配当だが警告が付かなかった健全株の確認
print("\n=== 配当関連の警告が付いた銘柄数 ===")
flagged = []
for d in data:
    r = check_risks(d)
    if any("配当" in w for w in r["warnings"]):
        flagged.append((d, r))
print(f"  配当警告あり: {len(flagged)} / {len(data)} 社")

# 3. 不整合と高すぎを分けて集計
mismatch = [x for x in flagged if any("不整合" in w for w in x[1]["warnings"])]
toohigh = [x for x in flagged if any("高すぎ" in w for w in x[1]["warnings"])]
print(f"   うち 配当データ不整合: {len(mismatch)} 社")
print(f"   うち 配当利回り高すぎ: {len(toohigh)} 社")

# 4. 健全な高配当株（利回り4-6%）が誤爆していないかサンプル確認
print("\n=== 利回り4-6%の銘柄サンプル（誤爆チェック・先頭10社）===")
healthy = [d for d in data if d.get("dividend_yield") and 0.04 <= d["dividend_yield"] <= 0.06]
for d in healthy[:10]:
    r = check_risks(d)
    div_warn = [w for w in r["warnings"] if "配当" in w]
    mark = "⚠誤爆?" if div_warn else "OK"
    print(f"  {mark} {d['code']} {d['name'][:24]:　<24} 利回り{d['dividend_yield']:.1%} 配当額{d['dividend_rate']}")
