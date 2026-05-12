// 🚀 全域監聽 invalid 事件
document.addEventListener(
  "invalid",
  (function () {
    return function (e) {
      // 阻止瀏覽器彈出那個醜氣泡
      e.preventDefault();

      // 這裡觸發你自定義的提醒 (例如 SweetAlert2 或自建 Toast)
      showCustomToast(`${e.target.placeholder || e.target.name} 不可留空喔！`);
    };
  })(),
  true,
);

function showCustomToast(message) {
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
}
