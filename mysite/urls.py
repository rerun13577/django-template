from aquatic import views_old

# 以下是新的版本
from aquatic.views.product import (
    AddProductView,
    DashboardView,
    EditProductView,
    IndexView,
    ProductDetailView,
    ShopView,
    ToggleProductActiveView,
)
from aquatic.views.profile import (
    EditProfileView,
    ProfileView,
    ToggleFollowView,
    UpdateProfileView,
)
from aquatic.views.template import (
    NoticeAPIView,
    SpecAPIView,
)
from django.conf import settings
from django.contrib import admin
from django.urls import include, path  # 🚀 多引入 re_path
from django.views.generic import TemplateView

urlpatterns = [
    # 以下是重構好的檔案-------------------------------------------------------
    path("admin/", admin.site.urls),
    path("", IndexView.as_view(), name="index"),
    # 🔐 帳號系統 (保留 allauth)
    # loginview在裡面
    path("accounts/", include("allauth.urls")),
    path("shop/", ShopView.as_view(), name="shop"),
    path("manage/", DashboardView.as_view(), name="dashboard"),
    # 這個要放下面那位大哥上面，因為我的edit會被他當變數吃掉
    path(
        "product/<int:pk>/edit/",
        EditProductView.as_view(),
        name="edit-product",
    ),
    path(
        "product/<int:pk>/<str:action>/",
        ToggleProductActiveView.as_view(),
        name="toggle_product",
    ),
    path(
        "api/manage-template/",
        NoticeAPIView.as_view(),
        name="api-notice",
    ),
    # 上架小魚
    path("api/add-product/", AddProductView.as_view(), name="add-product"),
    path(
        "profile/<str:username>/toggle_follow/",
        ToggleFollowView.as_view(),
        name="toggle_follow",
    ),
    # ---------------------------------------------
    path("api/manage-spec/", SpecAPIView.as_view(), name="api-spec"),
    path(
        "product/<int:product_id>/",
        ProductDetailView.as_view(),
        name="product_detail",
    ),
    path("profile/<str:username>/", ProfileView.as_view(), name="user_profile"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path(
        "profile/<str:username>/edit-form/",
        EditProfileView.as_view(),
        name="edit_profile_form",
    ),
    path(
        "profile/<str:username>/update/",
        UpdateProfileView.as_view(),
        name="update_profile",
    ),
    # 以下是尚未重構的------------------------------------------------------------
    # 🏠 首頁與部落格
    path("blog/", views_old.BlogView.as_view(), name="blog"),
    path("blog/post/<int:pk>/", views_old.ArticleDetailView.as_view(), name="article"),
    # ✍️ 留言與發文
    path(
        "blog/api/create/", views_old.CreatePostView.as_view(), name="create_post_api"
    ),
    path(
        "post/<int:post_id>/comment/",
        views_old.AddCommentView.as_view(),
        name="add_comment",
    ),
    # ❤️ 按讚功能 (API)
    path(
        "blog/like/<int:post_id>/",
        views_old.ToggleLikeView.as_view(),
        name="toggle_like",
    ),
    path(
        "comment/like/<int:comment_id>/",
        views_old.ToggleCommentLikeView.as_view(),
        name="comment_like",
    ),
    # 🧪 實驗室
    path("lab/", TemplateView.as_view(template_name="index.html")),
    # 下面這些還沒重構完成--------------------------------------------------------------------------------
    # 🎯 2. 變數路徑放下面：如果不是 edit (例如 delist, delete)，才會掉下來給這個類別處理
    # path(
    #     "product/<int:pk>/edit/",
    #     views_old.edit_product_view,
    #     name="edit-product",
    # ),
    # path(
    #     "profile/<str:username>/edit-form/",
    #     views_old.EditProfileFormView.as_view(),
    #     name="edit_profile_form",
    # ),
    # path(
    #     "profile/<str:username>/update/",
    #     views_old.UpdateProfileView.as_view(),
    #     name="update_profile",
    # ),
    # path(
    #     "api/manage-template/<int:pk>/",
    #     views_old.ManageTemplateView.as_view(),
    #     name="manage-template-detail",
    # ),
    # path(
    #     "api/manage-spec/",
    #     views_old.ManageSpecAPIView.as_view(),
    #     name="api_manage_spec",
    # ),
    # path(
    #     "product/<int:product_id>/",
    #     views_old.ProductDetailView.as_view(),
    #     name="product_detail",
    # ),
    # path(
    #     "profile/<str:username>/", views_old.ProfileView.as_view(), name="user_profile"
    # ),
    # path("profile/", views_old.ProfileView.as_view(), name="profile"),
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
