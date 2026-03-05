// aquatic/static/js/like-btn.js

// 1. 處理「文章」按讚
document.querySelectorAll(".like-btn").forEach((button) => {
  button.addEventListener("click", async function (e) {
    e.preventDefault();
    const postId = this.dataset.postId;
    const actionNum = this.querySelector(".action-num");

    try {
      const response = await fetch(`/blog/like/${postId}/`, {
        method: "POST",
        headers: {
          "X-CSRFToken": getCookie("csrftoken"),
          "Content-Type": "application/json",
        },
      });

      // 🚀 關鍵：必須在這裡判斷 401 狀態碼
      if (response.status === 401) {
        const data = await response.json();
        window.location.href = data.login_url; // 跳轉到登入頁
        return;
      }

      if (response.ok) {
        const data = await response.json();
        this.classList.toggle("liked", data.is_liked);
        actionNum.innerText = data.new_count;
      }
    } catch (error) {
      console.error("請求出錯：", error);
    }
  });
});

// 2. 處理「留言」按讚
document.querySelectorAll(".comment-like-btn").forEach((button) => {
  button.addEventListener("click", async function (e) {
    e.preventDefault();
    const commentId = this.dataset.commentId;
    const actionNum = this.querySelector(".action-num");

    try {
      const response = await fetch(`/comment/like/${commentId}/`, {
        method: "POST",
        headers: {
          "X-CSRFToken": getCookie("csrftoken"),
          "Content-Type": "application/json",
        },
      });

      // 🚀 關鍵：留言這邊也要判斷 401
      if (response.status === 401) {
        const data = await response.json();
        window.location.href = data.login_url;
        return;
      }

      if (response.ok) {
        const data = await response.json();
        this.classList.toggle("liked", data.is_liked);
        actionNum.innerText = data.new_count;
      }
    } catch (error) {
      console.error("請求出錯：", error);
    }
  });
});

// 抓取 CSRF Token 的工具
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