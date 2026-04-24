# aquatic/models.py
from django.contrib.auth.models import User
from django.db import models


class SpecTemplate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, verbose_name="規格範本名稱")

    # 這裡存的是 20 個格子的原始數據
    # 格式範例：{"pH值_min": 6.5, "pH值_max": 7.5, "性情": "溫和"...}
    data = models.JSONField(default=dict, blank=True, verbose_name="範本數據")

    def __str__(self):
        return self.name
