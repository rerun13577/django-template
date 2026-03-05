from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from aquatic import views 
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'), 
    path('blog/', views.blog, name='blog'),
    path('login/', views.login_view, name='login'),
    
    # --- 文章相關 ---
    # 🚀 補上這行：這是處理「發表文章」封包的收貨處
    path('blog/api/create/', views.create_post_api, name='create_post_api'),
    
    # 瀏覽文章：<int:pk> 是文章 ID
    path('blog/post/<int:pk>/', views.article_view, name='article'),

    # --- 留言與其他 ---
    path('post/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('accounts/', include('allauth.urls')),
    
    # 安全實驗室
    path('lab/', TemplateView.as_view(template_name='index.html')),

    # 🚀 補上這行！JS 傳來的「讚」要送到這裡處理
    path('blog/like/<int:post_id>/', views.toggle_like, name='toggle_like'),

    # 🚀 補上這行：處理「留言」按讚
    path('comment/like/<int:comment_id>/', views.toggle_comment_like, name='comment_like'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)