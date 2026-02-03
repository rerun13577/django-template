from django.db import models

class AquaticLife(models.Model):
    # 定義縣市選項
# 定義全台縣市選項
    CITY_CHOICES = [
        ('KLU', '基隆市'), ('TP', '臺北市'), ('NTP', '新北市'), ('TY', '桃園市'),
        ('HCU', '新竹市'), ('HCH', '新竹縣'), ('ILN', '宜蘭縣'), ('MLI', '苗栗縣'),
        ('TC', '臺中市'), ('CHH', '彰化縣'), ('NTO', '南投縣'), ('YLN', '雲林縣'),
        ('CYI', '嘉義市'), ('CYH', '嘉義縣'), ('TN', '臺南市'), ('KH', '高雄市'),
        ('PTH', '屏東縣'), ('HUA', '花蓮縣'), ('TTT', '臺東縣'), ('PEH', '澎湖縣'),
        ('KMN', '金門縣'), ('LJN', '連江縣'),
    ]

    # 定義生物分類
    CATEGORY_CHOICES = [
        ('SHRIMP', '米蝦/螯蝦'),
        ('FISH', '觀賞魚'),
        ('PLANT', '水生植物'),
        ('OTHER', '其他'),
    ]

    # 欄位設定
    name = models.CharField(max_length=100, verbose_name="品種名稱")
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default='SHRIMP', verbose_name="分類")
    city = models.CharField(max_length=5, choices=CITY_CHOICES, default='NTP', verbose_name="所在地點")
    price = models.IntegerField(default=0, verbose_name="價格")
    stock = models.IntegerField(default=0, verbose_name="庫存數量")
    description = models.TextField(blank=True, verbose_name="詳細描述")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="上架時間")
    image = models.ImageField(upload_to='aquatic_images/', null=True, blank=True)

    def __str__(self):
        return f"[{self.get_city_display()}] {self.name}"