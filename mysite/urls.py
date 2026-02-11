"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView
from aquatic import views # 確保有這行
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'), # 改成這樣，它才會去執行你撈資料庫的邏輯
    path('blog/', views.blog, name='blog'),
    path('login/', views.login_view, name='login'),
    

    # 這是你的安全實驗室：
    # 只要在瀏覽器打 127.0.0.1:8000/lab 就能看到新模板
    path('lab/', TemplateView.as_view(template_name='index.html')),

    

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


