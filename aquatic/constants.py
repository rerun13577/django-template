# constants.py
# 這是你定義的「底層協議」，所有範本與商品都要遵守這些 Key
# constants.py
# 這 5 個是你說的「核心 5 欄位」，會直接對應到資料庫的直行 (Column)
CORE_SPECS = ["pH值", "成魚體長", "適宜溫度", "難易度", "建議缸徑"]

# 剩下的這些我們會打包進 JSON 存儲
EXTRA_SPECS = ["GH硬度", "KH硬度", "性情", "活動水層", "食性", "比重", "水流強度"]

# 合起來給前端長格子
FISH_SPECS_LABELS = CORE_SPECS + EXTRA_SPECS
