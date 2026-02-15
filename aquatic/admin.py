from django.contrib import admin
from .models import AquaticLife # 引入你剛剛寫的模型
from .models import Post # 引入你剛寫好的模型

 # 在後台登記它
admin.site.register(Post)

# 把你的水生生物模型註冊進管理後台
admin.site.register(AquaticLife)