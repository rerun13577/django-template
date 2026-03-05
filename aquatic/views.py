from aquatic.models import AquaticLife # 引入你的模型
from .models import Post , Comment # 記得引入模型
from django.shortcuts import render, get_object_or_404 , redirect
from django.contrib.auth.decorators import login_required

import json # 🚀 處理前端傳來的 JSON 字串
from django.http import JsonResponse # 🚀 回傳成功或失敗的訊息給 JS
from django.core.files.storage import default_storage # 🚀 處理內文照片的儲存
from .models import Post, Comment, compress_image # 🚀 確保有引入你的壓縮工具


# aquatic/views.py
from django.db.models import Exists, OuterRef

# 下面是資料庫的環節環節

# # --- 部落格邏輯 ---
# def blog(request):
#     # 抓取資料庫裡所有的文章
#     all_posts = Post.objects.all().order_by('-created_at') # 建議加上排序，最新的在前
    
#     # 這是正確的送貨員，包裹裡有裝 'posts'
#     return render(request, 'blog.html', {'posts': all_posts})


# --- 部落格邏輯 ---
def blog(request):

    user = request.user# 🚀 1. 統一用一個變數就好，先抓基礎資料
    posts = Post.objects.select_related('author').order_by('-created_at')

    if user.is_authenticated:
        # 🚀 預先標記 is_liked 狀態
        posts = posts.annotate(
            is_liked=Exists(
                Post.objects.filter(id=OuterRef('pk'), likes=user)
            )
        )
    # 🚀 3. 確保包裹裡的名稱也是 posts
    return render(request, 'blog.html', {'posts': posts})


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



@login_required # 確保有登入才能點讚
def toggle_like(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    user = request.user
    
    if user in post.likes.all():
        post.likes.remove(user)
        is_liked = False
    else:
        post.likes.add(user)
        is_liked = True
    
    return JsonResponse({
        "is_liked": is_liked,
        "new_count": post.likes.count()
    })




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

# 發文邏輯-----------------------------------------------------------------------------------------------------
@login_required
def create_post_api(request):
    if request.method == "POST":
        # 1. 抓取標題與大圖
        title = request.POST.get("title")
        cover_image = request.FILES.get("cover_image")
        
        # 2. 抓取內容清單 (JSON 字串變回 Python 列表)
        raw_content = request.POST.get("content_json", "[]")
        content_list = json.loads(raw_content)

        # 3. 🚀 處理內文中的多張照片 (巡邏說明書，把暗號換成網址)
        for block in content_list:
            if block["type"] == "image_group":
                real_urls = []
                for secret_key in block["value"]:
                    file_obj = request.FILES.get(secret_key)
                    if file_obj:
                        # 呼叫你 models.py 寫好的壓縮功能
                        compressed_file = compress_image(file_obj)
                        # 儲存到 media/blog_photos/ 並拿網址
                        path = default_storage.save(f'blog_photos/{compressed_file.name}', compressed_file)
                        real_urls.append(default_storage.url(path))
                
                # 替換 JSON 裡的內容
                block["value"] = real_urls

        # 4. 正式存入資料庫
        new_post = Post.objects.create(
            title=title,
            image=cover_image,  # 這裡會觸發 Post.save() 裡的自動壓縮
            content=content_list,
            author=request.user
        )

        return JsonResponse({
            "status": "success", 
            "post_id": new_post.id,
            "url": f"/blog/post/{new_post.id}/" # 跳轉回文章頁
        })

    return JsonResponse({"status": "error", "message": "無效請求"}, status=400)