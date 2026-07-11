// 1. 通用「空狀態」產生器 (當沒圖時，畫出上傳提示虛線框)
function renderEmptyState(container) {
  container.innerHTML = `
        <div class="profile-placeholder">
            <div class="upload-icon-wrapper">
                <svg
                xmlns="http://www.w3.org/2000/svg"
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
                class="lucide lucide-upload-icon lucide-upload"
                >
                <path d="M12 3v12" />
                <path d="m17 8-5-5-5 5" />
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                </svg>
                <span class="upload-text">點擊重新上傳</span>
            </div>
        </div>
    `;
}

// 2. 通用預覽生成器 (當有圖時，建構圖片與叉叉按鈕)
function buildPreviewContent(previewContainer, imageUrl) {
  previewContainer.innerHTML = "";

  const imgWrapper = document.createElement("div");
  imgWrapper.classList.add("image-preview-wrapper");

  const img = document.createElement("img");
  img.src = imageUrl;
  img.classList.add("image-preview");

  const removeBtn = document.createElement("button");
  removeBtn.type = "button";
  removeBtn.classList.add("remove-image-btn");
  removeBtn.innerHTML = "&times;";

  imgWrapper.appendChild(img);
  imgWrapper.appendChild(removeBtn);
  previewContainer.appendChild(imgWrapper);
}

// 3. 全域點擊監聽器：專職處理「所有叉叉按鈕」的刪除行為
document.addEventListener("click", (e) => {
  const removeBtn = e.target.closest(".remove-image-btn");
  if (!removeBtn) return;

  // 🎯 核心防線：同時阻斷預設行為與事件冒泡，防止 label 再次觸發 input file 開窗
  e.preventDefault();
  e.stopPropagation();

  const container = removeBtn.closest(".image-preview-container");
  if (!container) return;

  const fieldGroup = container.closest(".input-field-group");
  const input = fieldGroup.querySelector(".profile-image-input");

  // 因果：執行清空，外觀轉為虛線框，實體 input 歸零
  renderEmptyState(container);
  if (input) input.value = "";
});

// 4. 全域變更監聽器：專職處理「所有照片上傳」的即時預覽行為
document.addEventListener("change", (e) => {
  const input = e.target.closest(".profile-image-input");
  if (!input) return;

  const file = e.target.files[0];
  const previewSelector = input.dataset.preview;
  const previewContainer = document.querySelector(previewSelector);

  if (!previewContainer) return;

  if (file) {
    const reader = new FileReader();
    reader.onload = (readerEvent) => {
      // 因果：讀取完成，強制覆蓋舊畫面，生成帶有叉叉的新圖片
      buildPreviewContent(previewContainer, readerEvent.target.result);
    };
    reader.readAsDataURL(file);
  }
});
