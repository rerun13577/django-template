from django.shortcuts import redirect, render
from aquatic.models import AquaticLife # 引入你的模型
from .models import Post , Comment # 記得引入模型
from django.shortcuts import render, get_object_or_404 , redirect
from django.contrib.auth.decorators import login_required


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
    # 拿到網址裡的 next 參數，如果沒有就預設去首頁 (LOGIN_REDIRECT_URL)
    next_url = request.GET.get('next', '/') 

    if request.method == 'POST':
        # ... 執行你的登入驗證程式碼 ...
        # if user_is_valid:
            login(request, user)
            
            # 關鍵：登入成功後，檢查 POST 資料裡有沒有帶 next
            # 因為 HTML Form 送出後，next 會變成 POST 資料的一部分
            redirect_to = request.POST.get('next', next_url)
            return redirect(redirect_to)
    
    return render(request, 'login.html', {'next': next_url})



def article_view(request, pk):
    # 優化版：一次把文章、留言、回覆、留言者頭像通通抓好
    # 這樣你在 HTML 跑迴圈時，才不會因為留言太多而卡住
    post = Post.objects.prefetch_related(
        'comments__replies',     # 預抓回覆
        'comments__author'      # 預抓留言者資料
    ).get(pk=pk)
    
    # 這裡你可以順便計算總留言數（包含回覆）傳給前端
    return render(request, 'article.html', {'post': post})



@login_required # 確保有登入才能留言
def add_comment(request, post_id):
    if request.method == "POST":
        post = get_object_or_404(Post, id=post_id)
        content = request.POST.get('content') # 抓取 HTML 裡 textarea 的內容
        
        if content:
            # 建立留言物件但先不存檔
            comment = Comment(
                post=post,
                author=request.user,
                content=content
            )
            
            # 如果是回覆某則留言，抓取 parent_id
            parent_id = request.POST.get('parent_id')
            if parent_id:
                comment.parent = Comment.objects.get(id=parent_id)
                
            comment.save() # 正式存入資料庫
            
    return redirect('article', pk=post_id)