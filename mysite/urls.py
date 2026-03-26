from aquatic import views
from django.conf import settings
from django.contrib import admin
from django.urls import include, path  # 🚀 多引入 re_path
from django.views.generic import TemplateView

# name='...'：這是你的「任意門」 你只要引用name的變數就可以叫東西出來
# 你會這樣寫：{% url 'article' pk=post.id %}。
# 好處：Django 會根據 name='article' 自動幫你算出正確的網址。
# 就算你明天把 blog/post/ 改成 shrimp/content/(就是path的第一格)
# 只要 name 沒改，你的 HTML 完全不用動！

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.index, name="index"),
    path("blog/", views.blog, name="blog"),
    path("blog/api/create/", views.create_post_api, name="create_post_api"),
    # 網址是 Address，而真正的資料是在 Data Bus 上跑，因為照片那些不可能透過網址傳送
    path("blog/post/<int:pk>/", views.article_view, name="article"),
    path("post/<int:post_id>/comment/", views.add_comment, name="add_comment"),
    path("accounts/", include("allauth.urls")),
    path("lab/", TemplateView.as_view(template_name="index.html")),
    path("blog/like/<int:post_id>/", views.toggle_like, name="toggle_like"),
    path(
        "comment/like/<int:comment_id>/", views.toggle_comment_like, name="comment_like"
    ),
]

# 🚀 只有在 DEBUG 模式下才啟用 Toolbar
if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns


# path(
#     "comment/like/<int:comment_id>/", views.toggle_comment_like, name="comment_like"
# ),
# 這不是網頁 url是一個後端處理的接口 只要有人
# comment/like/<int:comment_id> 這段可以讓你按讚只有這個會做動 不會其他的讚一起亮
# 後端會抓下來comment_id 然後去他的資料庫加一
