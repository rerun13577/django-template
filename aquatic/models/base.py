from uuid import uuid4  # 🚀 現在它會亮了，因為下面有用它

from django.db import models


class BaseModel(models.Model):
    # 每個物件專屬的 8 位數資料夾 ID
    folder_uuid = models.CharField(max_length=8, editable=False, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")

    class Meta:
        abstract = True  # 告訴 Django 這只是骨架

    # 🚀 這裡就是「亮燈」的關鍵！
    def save(self, *args, **kwargs):
        if not self.folder_uuid:
            # 如果還沒有 UUID，就現場生一個 8 位數的
            self.folder_uuid = uuid4().hex[:8]
        super().save(*args, **kwargs)
