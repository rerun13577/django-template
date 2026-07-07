from django.contrib.auth import authenticate, login  # 補上 authenticate

# 🎯 終極防線：直接用 method_decorator 確保不管前端丟什麼 Method
from django.shortcuts import redirect, render
from django.views import View

# 🚀 既然 CORE_SPECS 已經不存在了，就不要 import 它
# 1. Model 從 models 資料夾抓

# 2. 工具從 utils 檔案抓 🚀


# 登入完重新導向回原本頁面
class LoginView(View):
    # 🚀 GET：當使用者「看到」登入頁面時執行
    def get(self, request):
        next_url = request.GET.get("next", "/")
        return render(request, "login.html", {"next": next_url})

    # 🚀 POST：當使用者「按下」登入按鈕送出表單時執行
    def post(self, request):
        next_url = request.POST.get("next", "/")
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # 登入成功，去他想去的地方
            return redirect(next_url)
        else:
            # 登入失敗，帶著錯誤訊息回原頁面
            return render(
                request,
                "login.html",
                {"next": next_url, "error_message": "帳號或密碼錯誤，請再試一次"},
            )
