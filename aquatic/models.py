import sys
from PIL import Image
from io import BytesIO
from django.db import models
from django.core.files.uploadedfile import InMemoryUploadedFile

# --- 壓縮積木放在上面 ---
def compress_image(uploaded_image, threshold_kb=500):
    file_size = uploaded_image.size 
    
    # 小於門檻直接回傳
    if file_size <= threshold_kb * 1024:
        return uploaded_image

    img = Image.open(uploaded_image)
    if img.mode != 'RGB':
        img = img.convert('RGB')
        
    output = BytesIO()
    img.save(output, format='JPEG', quality=70) 
    output.seek(0)

    # 這裡用了 sys.getsizeof，現在 import 在最上面，它就亮了
    return InMemoryUploadedFile(
        output, 'ImageField', 
        f"{uploaded_image.name.split('.')[0]}.jpg", 
        'image/jpeg', output.getbuffer().nbytes, None
    )
# sys.getsizeof(output) 壓縮照片有錯在換回來
# --- 資料庫模型放在下面 ---
class AquaticLife(models.Model):
    CITY_CHOICES = [
        ('KLU', '基隆市'), ('TP', '臺北市'), ('NTP', '新北市'), ('TY', '桃園市'),
        ('HCU', '新竹市'), ('HCH', '新竹縣'), ('ILN', '宜蘭縣'), ('MLI', '苗栗縣'),
        ('TC', '臺中市'), ('CHH', '彰化縣'), ('NTO', '南投縣'), ('YLN', '雲林縣'),
        ('CYI', '嘉義市'), ('CYH', '嘉義縣'), ('TN', '臺南市'), ('KH', '高雄市'),
        ('PTH', '屏東縣'), ('HUA', '花蓮縣'), ('TTT', '臺東縣'), ('PEH', '澎湖縣'),
        ('KMN', '金門縣'), ('LJN', '連江縣'),
    ]

    CATEGORY_CHOICES = [
        ('SHRIMP', '米蝦/螯蝦'),
        ('FISH', '觀賞魚'),
        ('PLANT', '水生植物'),
        ('OTHER', '其他'),
    ]

    name = models.CharField(max_length=100, verbose_name="品種名稱")
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default='SHRIMP', verbose_name="分類")
    city = models.CharField(max_length=5, choices=CITY_CHOICES, default='NTP', verbose_name="所在地點")
    price = models.IntegerField(default=0, verbose_name="價格")
    stock = models.IntegerField(default=0, verbose_name="庫存數量")
    description = models.TextField(blank=True, verbose_name="詳細描述")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="上架時間")
    image = models.ImageField(upload_to='aquatic_images/', null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.image:
            # 確保這裡呼叫得到上面的函數
            self.image = compress_image(self.image, threshold_kb=500)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"[{self.get_city_display()}] {self.name}"