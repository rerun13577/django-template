// aquatic/static/js/like-btn.js

const likeButtons = document.querySelectorAll(".like-btn");

likeButtons.forEach((button) => {
  button.addEventListener("click", async function (e) {
    // 1. 阻止預設行為（防止如果是 <a> 標籤會跳轉）
    e.preventDefault();

    // 2. 抓取這篇文章的 ID (要在 HTML 補上 data-post-id)
    const postId = this.dataset.postId;
    const actionNum = this.querySelector(".action-num");

    try {
      // 3. 🚀 發送簡訊給 Django
      const response = await fetch(`/blog/like/${postId}/`, {
        method: "POST",
        headers: {
          "X-CSRFToken": getCookie("csrftoken"), // 這是 Django 必備的防偽貼紙
          "Content-Type": "application/json",
        },
      });

      if (response.ok) {
        const data = await response.json();

        // 4. 根據 Django 回傳的結果，決定要不要貼上「紅愛心」貼紙
        if (data.is_liked) {
          this.classList.add("liked");
        } else {
          this.classList.remove("liked");
        }

        // 5. 更新旁邊的數字
        actionNum.innerText = data.new_count;
      }
    } catch (error) {
      console.error("按讚失敗，是不是沒登入？", error);
    }
  });
});

// 🚀 這段是幫你抓 Django CSRF 貼紙的小工具（直接貼上即可）
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}