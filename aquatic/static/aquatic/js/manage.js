// 1. 分頁切換邏輯
function switchTab(btn, tabId) {
  // 隱藏所有區塊
  document.querySelectorAll(".tab-section").forEach((section) => {
    section.style.display = "none";
  });
  // 顯示目標區塊
  const target = document.getElementById("tab-" + tabId);
  if (target) {
    target.style.display = "block";
  }

  // 切換按鈕樣式
  document.querySelectorAll(".tab-item").forEach((item) => {
    item.classList.remove("active");
  });
  btn.classList.add("active");
}

// 2. 獲取 CSRF Token 的輔助函式 (因為外部 JS 抓不到 Django 標籤)
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

// 3. HTMX 配置：自動蓋印章
document.addEventListener("DOMContentLoaded", () => {
  document.body.addEventListener("htmx:configRequest", (event) => {
    // 從 Cookie 抓取 csrftoken
    event.detail.headers["X-CSRFToken"] = getCookie("csrftoken");
  });
});
