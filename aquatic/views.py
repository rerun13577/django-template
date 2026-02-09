from django.shortcuts import render
from aquatic.models import AquaticLife # 引入你的模型

def index(request):
    # 撈出資料庫裡所有的水生生物
    items = AquaticLife.objects.all()
    
    # 把這筆資料打包傳給網頁
    return render(request, 'index.html', {'items': items})


def home(request):
    # 👈 兇手就是這裡！
    # 這裡寫 'index.html'，首頁就是 index.html
    # 如果你改成 'dashboard.html'，首頁就會瞬間變成 dashboard.html
    return render(request, 'index.html')
