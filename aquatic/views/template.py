from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from aquatic.models import ShopNotice

from .utility import FisshAPIBase


class NoticeAPIView(FisshAPIBase):
    """
    常用備註管理 API。

    功能：
    - GET：取得單筆備註的編輯表單
    - POST：新增、修改或刪除備註
    """

    def get(self, request, pk=None, *args, **kwargs):
        if not pk:
            return HttpResponse("找不到指定備註", status=400)

        notice = get_object_or_404(
            ShopNotice,
            id=pk,
            user=request.user,
        )

        return render(
            request,
            "partials/notice_edit_form.html",
            {
                "n": notice,
            },
        )

    def post(self, request, *args, **kwargs):
        notice_id = request.POST.get("id")
        action = request.POST.get("action")

        # 刪除備註
        if action == "delete":
            notice = get_object_or_404(
                ShopNotice,
                id=notice_id,
                user=request.user,
            )

            notice.delete()

            return self.render_notice_list(request)

        # 新增或修改備註
        title = request.POST.get("title", "").strip()
        content = request.POST.get("content", "").strip()

        if not title:
            return HttpResponse("備註標題不可為空", status=400)

        if not content:
            return HttpResponse("備註內容不可為空", status=400)

        if notice_id:
            notice = get_object_or_404(
                ShopNotice,
                id=notice_id,
                user=request.user,
            )

            notice.title = title
            notice.content = content
            notice.save(
                update_fields=[
                    "title",
                    "content",
                ]
            )
        else:
            ShopNotice.objects.create(
                user=request.user,
                title=title,
                content=content,
            )

        return self.render_notice_list(request)

    def render_notice_list(self, request):
        notices = ShopNotice.objects.filter(
            user=request.user,
        ).order_by("-created_at")

        return render(
            request,
            "component/notice_list_items.html",
            {
                "notices": notices,
            },
        )
