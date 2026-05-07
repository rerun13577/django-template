// manage.js

function toggleBatchMode() {
  const layout = document.getElementById("manageLayout");
  const btnText = document.getElementById("btnText");
  const container = document.getElementById("batchSlotsContainer");

  const isActive = layout.classList.toggle("is-batch-mode");

  if (isActive) {
    // 因：開啟模式。果：按鈕文字改變，並預設生成 5 個格子讓畫面不空洞。
    if (btnText) btnText.innerText = "關閉批量模式";
    generateBatchSlots();
  } else {
    // 因：關閉模式。果：清空內容以節省效能，並還原文字。
    if (btnText) btnText.innerText = "批量新增";
    container.innerHTML = "";
  }
}

function generateBatchSlots() {
  const countInput = document.getElementById("batchCount");
  // 如果畫面上還沒畫出 input，就預設生成 5 個
  const count = countInput ? countInput.value : 5;
  const container = document.getElementById("batchSlotsContainer");

  const finalCount = Math.min(Math.max(count, 1), 20);

  let html = "";
  for (let i = 1; i <= finalCount; i++) {
    html += `
            <div class="slot-item">
                <div class="slot-header">小魚 ${i}</div>
                <div class="slot-body">
                    <input type="text" name="fish_name[]" class="batch-input" placeholder="小魚名稱">
                    <input type="number" name="fish_price[]" class="batch-input" placeholder="價格">
                </div>
            </div>
        `;
  }

  container.innerHTML = html;
}

function generateBatchSlots() {
  const count = document.getElementById("batchCount").value;
  const container = document.getElementById("batchSlotsContainer");
  const finalCount = Math.min(Math.max(count, 1), 20);

  let html = "";
  for (let i = 1; i <= finalCount; i++) {
    html += `
            <div class="slot-item">
                <label class="slot-upload-box">
                    <input type="file" name="fish_image[]" accept="image/*" hidden onchange="previewSlotImage(this)">
                    <div class="upload-placeholder">
                        <span style="font-size: 24px;">+</span>
                    </div>
                    <img src="" class="preview-img" style="display:none; width:100%; height:100%; object-fit:cover; position:absolute;">
                </label>
                <input type="text" name="fish_name[]" class="slot-name-input" placeholder="小魚名稱 ${i}">
            </div>
        `;
  }
  container.innerHTML = html;
}

// 處理照片預覽
function previewSlotImage(input) {
  const box = input.closest(".slot-upload-box");
  const preview = box.querySelector(".preview-img");
  const placeholder = box.querySelector(".upload-placeholder");

  if (input.files && input.files[0]) {
    const reader = new FileReader();
    reader.onload = function (e) {
      preview.src = e.target.result;
      preview.style.display = "block";
      placeholder.style.display = "none";
    };
    reader.readAsDataURL(input.files[0]);
  }
}
