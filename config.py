# 分析対象の銘柄コード（証券コード4桁）。好きに足し引きしてOK
WATCH_LIST = [
    "7203",  # トヨタ
    "6758",  # ソニー
    "9984",  # ソフトバンクG
    "8306",  # 三菱UFJ
    "6861",  # キーエンス
]

# スクリーニング閾値（A: 良い銘柄を拾う条件）
SCREEN_CRITERIA = {
    "per_max": 15.0,
    "pbr_max": 1.5,
    "psr_max": 1.0,  # PSR 1.0以下で割安
    "roe_min": 0.10,
    "dividend_yield_min": 0.05,
    "equity_ratio_min": 0.50,  # 自己資本比率 50%以上（小数0.50）
}

# 危険信号の閾値（B: チェックリストで警告を出す条件）
RISK_CRITERIA = {
    "debt_to_equity_max": 200.0,  # 負債比率がこれ超で警告（%表記）
    "current_ratio_min": 1.0,  # 流動比率がこれ未満で警告
    "roe_min": 0.0,  # ROEがマイナスで警告
    "revenue_growth_min": 0.0,  # 減収で警告
    "earnings_growth_min": 0.0,  # 減益で警告
    "dividend_yield_high": 0.08,  # 配当利回りがこれ超は高すぎ→要確認（分割/記念配当/減配リスク）
    "dividend_mismatch_ratio": 1.5,  # 配当額からの逆算利回りと利回りがこの倍率以上ズレたら不整合疑い
}

# 1銘柄あたりの投資予算上限（円）。
# 日本株は100株単位なので「株価 × 100」がこれ以下の銘柄だけを候補とする。
# 自分の予算に合わせて自由に変更する。
BUDGET_PER_STOCK = 200000  # 例: 30万円
