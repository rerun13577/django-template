from django.shortcuts import render
from aquatic.models import AquaticLife # 引入你的模型
from .models import Post # 記得引入模型


# 下面是資料庫的環節環節

# --- 部落格邏輯 ---
def blog(request):
    # 抓取資料庫裡所有的文章
    all_posts = Post.objects.all().order_by('-created_at') # 建議加上排序，最新的在前
    
    # 這是正確的送貨員，包裹裡有裝 'posts'
    return render(request, 'blog.html', {'posts': all_posts})


def index(request):
    # 撈出資料庫裡所有的水生生物
    items = AquaticLife.objects.all()
    
    # 把這筆資料打包傳給網頁
    return render(request, 'index.html', {'items': items})


# 下面是html的環節

def home(request):
    # 👈 兇手就是這裡！
    # 這裡寫 'index.html'，首頁就是 index.html
    # 如果你改成 'dashboard.html'，首頁就會瞬間變成 dashboard.html
    return render(request, 'index.html')



def login_view(request): 
    # 只負責顯示不負責去後面抓資料
    return render(request, 'login.html')