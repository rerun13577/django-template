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
    # 只負責顯示不負責去後面抓資料
    return render(request, 'login.html')



# 2. 這是新的詳情頁函式
def article_view(request, pk):
    # 去 Post 資料庫裡，找一個 ID (pk) 符合的文章
    # 如果找不到（比如網址亂打），它會自動跳出 404 頁面
    post = get_object_or_404(Post, pk=pk)
    
    # 把這篇抓到的文章交給 post_detail.html 這個網頁檔案
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
            
    return redirect('article_detail', pk=post_id) # 留言完跳回文章頁