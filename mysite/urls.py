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
    # 個人頁面系統
    path("profile/", views.ProfileView.as_view(), name="profile"),
    # 唯一的頁面入口
    path("manage/", views.ManageDashboardView.as_view(), name="manage_dashboard"),
    # 兩個寫入用的 API 接口
    path(
        "api/manage-template/",
        views.ManageTemplateView.as_view(),
        name="manage-template",
    ),
    path(
        "api/manage-template/<int:pk>/",
        views.ManageTemplateView.as_view(),
        name="manage-template-detail",
    ),
    path("api/manage-spec/", views.ManageSpecAPIView.as_view(), name="api_manage_spec"),
    path("api/add-product/", views.AddProductBatchView.as_view(), name="add-product"),
    path("shop/", views.ShopListView.as_view(), name="shop_list"),
    path(
        "product/<int:pk>/edit/",
        views.edit_product_view,
        name="edit-product",
    ),
    # 🎯 2. 變數路徑放下面：如果不是 edit (例如 delist, delete)，才會掉下來給這個類別處理
    path(
        "product/<int:pk>/<str:action>/",
        views.ProductToggleActiveView.as_view(),
        name="toggle_product",
    ),
    path(
        "product/<int:product_id>/",
        views.ProductDetailView.as_view(),
        name="product_detail",
    ),
    path(
        "profile/<str:username>/edit-form/",
        views.EditProfileFormView.as_view(),
        name="edit_profile_form",
    ),
    path(
        "profile/<str:username>/update/",
        views.UpdateProfileView.as_view(),
        name="update_profile",
    ),
    path("profile/<str:username>/", views.ProfileView.as_view(), name="user_profile"),
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
