/**
 * ⚡ 獨立水族藝廊調包大腦
 * 因：點擊下方小圖槽 (.detail-thumb-slot)
 * 果：調包大圖 src 訊號，並利用 class 轉移高亮權限
 */
function executeGallerySwitch(slotElement) {
  const clickedImg = slotElement.querySelector("img");
  const viewportImg = document.getElementById("fisshGalleryViewport");
  const placeholderBox = document.getElementById("galleryPlaceholder");

  // 安全檢查：防線確認
  if (clickedImg && viewportImg) {
    // 1. 物理調包大圖的 src 網址
    viewportImg.src = clickedImg.src;

    // 2. 確保大圖顯示，佔位符功成身退
    viewportImg.style.display = "block";
    if (placeholderBox) {
      placeholderBox.style.display = "none";
    }

    // 3. 物理清除所有小圖槽的激活高亮 (由 CSS 接手控制外觀)
    document.querySelectorAll(".detail-thumb-slot").forEach((slot) => {
      slot.classList.remove("active-focus");
    });

    // 4. 幫當前點擊的槽位加上高亮 Class
    slotElement.classList.add("active-focus");
  }
}
