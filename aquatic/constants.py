# constants.py
# 這是你定義的「底層協議」，所有範本與商品都要遵守這些 Key
# constants.py
# 這 5 個是你說的「核心 5 欄位」，會直接對應到資料庫的直行 (Column)
# 🚀 核心數據定義：增加 type 屬性
# constants.py

# constants.py

CORE_SPECS_CONFIG = [
    {
        "label": "生物種類",
        "key": "category",
        "type": "select",
        "options": ["魚類", "蝦類", "水草類", "螺蚌類", "其他"],
    },
    {"label": "適宜溫度", "key": "temp", "type": "range"},
    {"label": "pH值", "key": "ph", "type": "range"},
    {"label": "體長(cm)", "key": "adult_length", "type": "single"},
    {"label": "建議大小(cm)", "key": "min_tank_size", "type": "single"},
]

# 重新挑選後的次要規格
# 移除了「活動水層」
# 保留「水流強度」（因為對蝦缸溶氧很重要）
# 增加「光照需求」（因為你有在做造景）
EXTRA_SPECS = ["GH硬度", "KH硬度", "性情", "食性", "比重", "水流強度", "光照需求"]

FISH_SPECS_LABELS = [item["label"] for item in CORE_SPECS_CONFIG] + EXTRA_SPECS
