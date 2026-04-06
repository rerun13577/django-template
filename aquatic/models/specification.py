# aquatic/models.py
from django.contrib.auth.models import User
from django.db import models


class SpecTemplate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)  # 範本名稱
    # 這裡存老闆選了哪幾項標籤，以及他填的預設值
    # 格式：{"pH值": "6.5", "適宜溫度": "26"}
    data = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.name
