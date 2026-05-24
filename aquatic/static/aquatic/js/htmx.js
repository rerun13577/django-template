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
  const responseText = e.detail.xhr.responseText;

  // 🛡️ 鋼鐵防線：因果過濾！如果後端噴回來的是整張 HTML 網頁 (例如 404、500 報錯頁)
  // 絕對不能丟進 Toast，否則會把前端排版直接物理撐爆
  if (responseText && (responseText.trim().startsWith("<!DOCTYPE") || responseText.includes("<html"))) {
    console.error(`[HTMX 系統重磅報錯] 狀態碼: ${e.detail.xhr.status}。後端直接吐回了整張 HTML 網頁，拒絕寫入 Toast！`);
    window.showCustomToast("系統電路跳電，請工程師檢查控制台！");
    return; // 物理斷路，拒絕向下執行
  }

  try {
    // 嘗試解析是不是 JSON 格式
    const res = JSON.parse(responseText);
    errorMsg = res.message || errorMsg;

    if (res.login_url) {
      setTimeout(() => {
        window.location.href = res.login_url;
      }, 1500);
    }
  } catch (err) {
    // 如果後端直接丟回一般純文字提示
    errorMsg = responseText || errorMsg;
  }

  // 正常的錯誤文字，安全送進紅框 Toast
  window.showCustomToast(errorMsg);
});
