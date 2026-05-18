from aquatic import views
from django.conf import settings
from django.contrib import admin
from django.urls import include, path  # 🚀 多引入 re_path
from django.views.generic import TemplateView

urlpatterns = [
    path("admin/", admin.site.urls),
    # 🏠 首頁與部落格
    path("", views.IndexView.as_view(), name="index"),
    path("blog/", views.BlogView.as_view(), name="blog"),
    path("blog/post/<int:pk>/", views.ArticleDetailView.as_view(), name="article"),
    # ✍️ 留言與發文
    path("blog/api/create/", views.CreatePostView.as_view(), name="create_post_api"),
    path(
        "post/<int:post_id>/comment/",
        views.AddCommentView.as_view(),
        name="add_comment",
    ),
    # ❤️ 按讚功能 (API)
    path(
        "blog/like/<int:post_id>/", views.ToggleLikeView.as_view(), name="toggle_like"
    ),
    path(
        "comment/like/<int:comment_id>/",
        views.ToggleCommentLikeView.as_view(),
        name="comment_like",
    ),
    # 🔐 帳號系統 (保留 allauth)
    path("accounts/", include("allauth.urls")),
    # 🧪 實驗室
    path("lab/", TemplateView.as_view(template_name="index.html")),
    # 格人頁面系統
    # 🚀 方案：兩條路徑都找同一個 View，邏輯交給 View 裡面的 if not username 處理
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("profile/<str:username>/", views.ProfileView.as_view(), name="user_profile"),
    # 🚀 下面這個「api/template/save/」維持不動
    # urls.py
    # 🚀 只需要這一個入口，以後 JS 全部打這條路徑
    # 🚀 這裡要改成你現在 View 真正的名字
    # 唯一的頁面入口
    path("manage/", views.ManageDashboardView.as_view(), name="manage_dashboard"),
    # 兩個寫入用的 API 接口
    path(
        "api/manage-template/",
        views.ManageTemplateView.as_view(),
        name="manage-template",  # 🚀 把 api_ 拿掉，對齊你的 HTML
    ),
    # 🚀 為了讓 HTMX 能拿「編輯表單」，你還需要補這條帶 ID 的路徑
    path(
        "api/manage-template/<int:pk>/",
        views.ManageTemplateView.as_view(),
        name="manage-template-detail",
    ),
    path("api/manage-spec/", views.ManageSpecAPIView.as_view(), name="api_manage_spec"),
    # 🚀 這一行就是你在 Template 裡 {% url 'manage-template' %} 找的東西
    path("api/add-product/", views.AddProductBatchView.as_view(), name="add-product"),
    # 🚀 修正這行：前面補上 views. 讓它對齊整體的引入規格
    path("shop/", views.ShopListView.as_view(), name="shop_list"),
    path(
        "product/<int:pk>/<str:action>/",
        views.ProductToggleActiveView.as_view(),
        name="toggle_product",
    ),
]

# 🚀 只有在 DEBUG 模式下才啟用 Toolbar
if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns

# Django 的路由系統（URLconf）底層其實只認識「函式」。當你把 View 寫成「類別」時，它是一個物件，不是函式。
# path(
#     "comment/like/<int:comment_id>/", views.toggle_comment_like, name="comment_like"
# ),
# 這不是網頁 url是一個後端處理的接口 只要有人
# comment/like/<int:comment_id> 這段可以讓你按讚只有這個會做動 不會其他的讚一起亮
# 後端會抓下來comment_id 然後去他的資料庫加一
# url 一個view對應到一個前端的頁面 這個view裡面會有一個函式叫做as_view() 這個函式會把類別轉換成函式
