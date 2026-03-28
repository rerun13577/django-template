import json  # 🚀 處理前端傳來的 JSON 字串
from uuid import uuid4

from django.contrib.auth import authenticate, login  # 補上 authenticate
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage  # 🚀 處理內文照片的儲存
from django.db.models import Exists, OuterRef, Prefetch
from django.http import JsonResponse  # 🚀 回傳成功或失敗的訊息給 JS
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.timezone import now  # 🚀 這是用來抓現在時間的機器

# 1. Model 從 models 資料夾抓
from .models import (  # 記得引入模型
    AquaticLife,
    Comment,
    Post,
)

# 2. 工具從 utils 檔案抓 🚀
from .utils import compress_image

# url就是跟前端的連結
# 當你要直接轉換一個網址直接{裡面引用url裡面的name}
# url， views.index 代表他要連結的 view裡面的哪個函數 你就可以用那個函數直接去引用後台的資料


# objects (管理員)：這是 Django 自動幫每個模型裝上去的「機器人」。它的工作只有一個：跟資料庫溝通。
# 以後可以叫他抓出特定物種

# request： 這是在函式一開始就傳進來的。
# 它記錄了是誰、從哪裡、用什麼方式（GET 或 POST）連進你的網站。render 必須帶著它，才能把結果回傳給正確的人。

# "index.html"：「請把資料套進這份 HTML 模板裡」。
# Django 會去你的資料夾找到這份檔案，把它當成一個「空的框架」。

# {"items": items}：這是最重要的「包裹」
# 左邊的 "items" (引號裡面的)：這是 「標籤名稱」。你在 HTML 裡面寫 {% for item in items %} 時，指的就是這個標籤。
# 右邊的 items (變數名稱)：這是你在 views.py 上一行從資料庫撈出來的 「真實資料」。

# 如果你在 views.py 這樣寫：
# return render(request, "index.html", {"shrimp_list": items})
# 那你在 index.html 裡面就不能寫 {% for item in items %} 了，你必須改成：
# {% for item in shrimp_list %} 因為 HTML 只認識你給它的那個 「標籤名稱」

# 如果括號裡沒包 request，第一行 user = request.user 就會直接報錯，因為程式找不到 request 這個變數。
# 獨立性：每一次點擊（Request）都是一個獨立的事件。函式裡面的變數在執行完後就會被釋放掉。 不可以寫在外面
# 正確性：當「王小明」連進來，blog(request) 裡面的 request.user 就是王小明；
# 當「陳大華」連進來，產生的又是另一個獨立的 request.user。


def index(request):
    # 撈出資料庫裡所有的水生生物
    items = AquaticLife.objects.all()

    # request有關係這個使用者的各種資訊 傳過來的個人資訊也要傳回去 訂單詳細貼紙
    # 指定這些東西要塞去哪裡 要送去哪裡
    # 回傳水生生物 訂單內容
    return render(request, "index.html", {"items": items})


# 那個 - 號：代表 由新到舊（遞減）。
# 如果沒加 -，你的首頁會永遠顯示你兩年前寫的第一篇文章，使用者會以為你網站倒閉了。

# 作者 (Maker)：就在 select_related("author") 裡面。
# 這句已經把作者的所有資訊（名字、頭像）通通打包進 posts 變數了。
# 點讚數：因為你在 models.py 裡有寫 like_count = models.IntegerField(default=0)
# ，所以每一篇 post 物件生出來時，身上就自帶了這個數字。

# 如果你希望 FisshShop 的首頁顯示的是 「最熱門的文章」，而不是最新的，你確實可以改掉它：
# # 讓點讚數最多的排在最前面
# posts = Post.objects.select_related("author").order_by("-like_count")


#     return render(request, "blog.html", {"posts": posts})
def blog(request):
    user = request.user

    # 解決N+1的問題
    # select_related("author")：這是一個 SQL JOIN。
    # 它在抓文章時，順便把作者的名字、頭像通通「焊」在一起帶過來。
    # 我要先進auther 再去社交帳號 因為他有可能是用他自己的帳號密碼登入
    # 如果直接跳社交帳號就是預設立場我的客人只會用第三方軟件登入
    # 使用者（User）可能有「多個」社群帳號
    posts = (
        Post.objects.select_related("author")
        .prefetch_related("author__socialaccount_set")
        .order_by("-created_at")
    )

    if user.is_authenticated:
        # 🚀 預先標記 is_liked 狀態
        # annotate 的意思是 「動態增加欄位」 如果有按讚就是附加在post一起傳給前面

        # is_liked 這是你自訂的暫存器名稱
        # Exists 判斷是否存在
        # OuterRef("pk") 就是js 的this
        posts = posts.annotate(
            is_liked=Exists(Post.objects.filter(id=OuterRef("pk"), likes=user))
        )

    return render(request, "blog.html", {"posts": posts})


# 下面是html的環節


def home(request):
    # 👈 兇手就是這裡！
    # 這裡寫 'index.html'，首頁就是 index.html
    # 如果你改成 'dashboard.html'，首頁就會瞬間變成 dashboard.html
    return render(request, "index.html")


def login_view(request):
    # 拿到網址裡的 next 參數，如果沒有就預設去首頁
    next_url = request.GET.get("next", "/")

    if request.method == "POST":
        # 1. 抓取表單填寫的內容
        username = request.POST.get("username")
        password = request.POST.get("password")

        # 2. 🚀 核心：驗證身分 (這行會定義 user，消除紅線)
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # 3. 驗證成功，正式登入
            login(request, user)

            # 4. 跳轉邏輯：優先去 next 頁面，沒有才去 next_url
            redirect_to = request.POST.get("next", next_url)
            return redirect(redirect_to)
        else:
            # 5. 驗證失敗：帶一個錯誤訊息回前端
            return render(
                request,
                "login.html",
                {"next": next_url, "error_message": "帳號或密碼錯誤，請再試一次"},
            )

    # GET 請求：單純顯示登入頁面
    return render(request, "login.html", {"next": next_url})


def article_view(request, pk):
    user = request.user

    # 1. 🚀 建立一個專門給「回覆」用的查詢集，也要標記 is_liked
    reply_queryset = Comment.objects.select_related("author")
    if user.is_authenticated:
        reply_queryset = reply_queryset.annotate(
            is_liked=Exists(Comment.objects.filter(id=OuterRef("pk"), likes=user))
        )

    # 2. 🚀 修改留言的查詢集，讓 prefetch_related 使用上面那個帶有標記的 reply_queryset
    comment_queryset = Comment.objects.select_related("author").prefetch_related(
        Prefetch("replies", queryset=reply_queryset.order_by("created_at"))  # 標記回覆
    )

    if user.is_authenticated:
        # 標記第一層留言
        comment_queryset = comment_queryset.annotate(
            is_liked=Exists(Comment.objects.filter(id=OuterRef("pk"), likes=user))
        )

    # 3. 抓取文章
    post_queryset = Post.objects.select_related("author").prefetch_related(
        Prefetch("comments", queryset=comment_queryset.filter(parent=None))
    )

    if user.is_authenticated:
        post_queryset = post_queryset.annotate(
            is_liked=Exists(Post.objects.filter(id=OuterRef("pk"), likes=user))
        )

    post = get_object_or_404(post_queryset, pk=pk)
    return render(request, "article.html", {"post": post})


# requset 傳入前端的要求到函數裡面處理
def toggle_like(request, post_id):
    if not request.user.is_authenticated:
        return JsonResponse(
            {
                "status": "unauthorized",  # 改成這樣
                "login_url": f"/accounts/login/?next={request.path}",
            },
            status=401,
        )

    post = get_object_or_404(Post, id=post_id)
    user = request.user

    if post.likes.filter(id=user.id).exists():
        post.likes.remove(user)
        is_liked = False
    else:
        post.likes.add(user)
        is_liked = True

    # 🚀 關鍵修正：同步更新資料庫裡的 like_count 欄位
    # 我們用 update 繞過你 models.py 裡那個會報錯的 save() 檢查
    current_count = post.likes.count()
    Post.objects.filter(id=post_id).update(like_count=current_count)

    # 🚀 確保回傳的 key (new_count) 跟你的 JS 抓的名字是一樣的
    return JsonResponse({"is_liked": is_liked, "new_count": current_count})


def toggle_comment_like(request, comment_id):

    # 🚀 留言這邊也要手動判斷，不能只靠 @login_required
    if not request.user.is_authenticated:
        return JsonResponse(
            {
                "status": "unauthorized",  # 改成這樣
                "login_url": f"/accounts/login/?next={request.path}",
            },
            status=401,
        )

    comment = get_object_or_404(Comment, id=comment_id)
    user = request.user

    # .filter(id=user.id) 只會找特定的人
    # .exists() 只會回傳 True/False，不會搬運整串名單
    if comment.likes.filter(id=user.id).exists():
        comment.likes.remove(user)
        is_liked = False
    else:
        comment.likes.add(user)
        is_liked = True

    return JsonResponse({"is_liked": is_liked, "new_count": comment.likes.count()})


# if not request.user.is_authenticated: 裡面回傳的東西是給前端的js下面的程式就不會繼續執行
# comment.likes.remove(user) 資料庫刪除用戶 或者增加用戶
# 意思就是comment 裡面的 likes 然後 移除這個用戶0
# .filter(id=user.id) 只會找特定的人
# .exists() 只會回傳 True/False，不會搬運整串名單 剛好可以進if 判斷


@login_required  # 確保有登入才能留言
def add_comment(request, post_id):
    if request.method == "POST":
        post = get_object_or_404(Post, id=post_id)
        content = request.POST.get("content")  # 抓取 HTML 裡 textarea 的內容

        if content:
            # 建立留言物件但先不存檔
            comment = Comment(post=post, author=request.user, content=content)

            # 如果是回覆某則留言，抓取 parent_id
            parent_id = request.POST.get("parent_id")
            if parent_id:
                comment.parent = Comment.objects.get(id=parent_id)

            comment.save()  # 正式存入資料庫

    return redirect("article", pk=post_id)


# 發文邏輯-----------------------------------------------------------------------------------------------------
@login_required
def create_post_api(request):
    if request.method == "POST":
        title = request.POST.get("title")
        cover_image = request.FILES.get("cover_image")
        raw_content = request.POST.get("content_json", "[]")
        content_list = json.loads(raw_content)

        # 🚀 1. 產生這篇文章唯一的「門牌號碼」
        date_str = now().strftime("%Y/%m/%d")
        article_token = uuid4().hex[:8]

        # 2. 處理內文中的多張照片 (這部分不變)
        for block in content_list:
            if block["type"] == "image_group":
                real_urls = []
                for secret_key in block["value"]:
                    file_obj = request.FILES.get(secret_key)
                    if file_obj:
                        compressed_file = compress_image(file_obj)

                        # 🚀 3. 內文路徑對齊 (使用剛剛產生的 article_token)
                        content_file_path = f"blog/{date_str}/{article_token}/content/{uuid4().hex[:8]}.webp"

                        path = default_storage.save(content_file_path, compressed_file)
                        real_urls.append(default_storage.url(path))

                block["value"] = real_urls

        # 🚀 4. 正式存入資料庫 (關鍵修改處！)
        new_post = Post.objects.create(
            title=title,
            folder_uuid=article_token,  # 🔥 補上這行！讓 Model 知道門牌號碼
            image=cover_image,  # 此時 Model 會抓到 folder_uuid 並算對路徑
            content=content_list,
            author=request.user,
        )

        return JsonResponse(
            {
                "status": "success",
                "url": f"/blog/post/{new_post.id}/",
            }
        )

    return JsonResponse({"status": "error", "message": "無效請求"}, status=400)
