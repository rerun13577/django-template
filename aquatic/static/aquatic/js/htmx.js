// ────────────────────────────────────────────────────────
// 1. 全域自定義 Toast 提示框函數 (掛載到 window 確保全域可用)
// ────────────────────────────────────────────────────────
window.showCustomToast = function (message) {
  // 先移除舊的 (避免重複彈出)
  const oldToast = document.querySelector(".custom-toast");
  if (oldToast) oldToast.remove();

  const toast = document.createElement("div");
  toast.className = "custom-toast";
  toast.innerText = message;
  document.body.appendChild(toast);

  // 3秒後自動消失
  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transition = "0.5s";
    setTimeout(() => toast.remove(), 500);
  }, 3000);
};

// ────────────────────────────────────────────────────────
// 2. 🚀 前端防線：全域監聽 HTML5 原生表單驗證失敗事件
// ────────────────────────────────────────────────────────
document.addEventListener(
  "invalid",
  (function () {
    return function (e) {
      // 阻止瀏覽器彈出那個醜氣泡
      e.preventDefault();

      // 優先抓自定義的 data-label，抓不到才退回抓 placeholder 或 name
      const displayName = e.target.dataset.label || e.target.placeholder || e.target.name;

      // 觸發自定義的提醒
      window.showCustomToast(`${displayName} 不可留空喔！`);
    };
  })(),
  true,
);

// ────────────────────────────────────────────────────────
// 3. 🚀 後端防線：全域監聽 HTMX 傳回的錯誤狀態碼 (400, 401, 500 等)
// ────────────────────────────────────────────────────────
document.addEventListener("htmx:responseError", function (e) {
  let errorMsg = "伺服器發生未知錯誤喔！";

  try {
    // 因：嘗試解析後端回傳的是不是 JSON 格式 (例如 401 未登入保險箱)
    const res = JSON.parse(e.detail.xhr.responseText);
    errorMsg = res.message || errorMsg;

    // 果：如果是未登入造成的錯誤，自動導向登入頁
    if (res.login_url) {
      setTimeout(() => {
        window.location.href = res.login_url;
      }, 1500);
    }
  } catch (err) {
    // 因：如果後端直接丟回純文字 (例如我們剛剛在 View 寫的 status=400 錯誤提示)
    errorMsg = e.detail.xhr.responseText || errorMsg;
  }

  // 🔥 果：不管後端發生什麼慘事，通通送進你漂亮的紅框 Toast！
  window.showCustomToast(errorMsg);
});
