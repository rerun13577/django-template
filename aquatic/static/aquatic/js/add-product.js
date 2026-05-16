function handleBatchConfirm() {
  const countInput = document.getElementById("batchCountInput");
  const count = parseInt(countInput.value);
  if (isNaN(count) || count <= 0) return;

  // 1. 執行生成格子 (維持你原本的)
  generateBatchSlots(count);

  // 2. 抓取批量表單與按鈕
  const batchForm = document.getElementById("batchUploadForm");
  const actionArea = document.getElementById("actionArea");

  // 🚀 因：格子已在表單內生成完畢。果：直接把整個批量表單跟上架按鈕秀出來。
  if (batchForm) batchForm.style.display = "block";
  if (actionArea) actionArea.style.display = "block";

  // 3. 隱藏輸入格數的 Banner
  const setupSection = document.getElementById("setupSection");
  if (setupSection) setupSection.style.display = "none";
}

// 把html這個變數裡面的東西都送進一個叫 batchSlotsContainer 的元素裡面
function generateBatchSlots(count) {
  const container = document.getElementById("batchSlotsContainer");
  const finalCount = Math.min(Math.max(count, 1), 20);

  let html = "";
  for (let i = 1; i <= finalCount; i++) {
    html += `
        <div class="slot-item">
            <div class="split-tool">
                <div class="split-left">
                    <div class="slot-header">第 ${i} 隻生物</div>
                </div>
                <div class="split-right">
                    <button type="button"
                            class="remove-slot-btn"
                            onclick="this.closest('.slot-item').remove(); updateSlotNumbers();"
                            title="移除此格">
                        ${ICON_X} </button>
                </div>
            </div>

            <div class="slot-field">
                <label class="custom-upload-box">
                    <input type="file"
                           name="fish_image[]"
                           accept="image/*"
                           onchange="handlePreview(this)"
                           style="display: none"
                           data-label="生物照片"
                           required>
                    <div class="upload-placeholder">
                        ${ICON_UPLOAD}
                    </div>
                    <img class="preview-img" src="" style="display: none;">
                </label>
            </div>

            <div class="slot-field">
                          <input type="text"
                           name="fish_name[]"
                           placeholder="品種名稱 (如：極火蝦)"
                           data-label="品種名稱"
                           required>
            </div>

            <div class="slot-field field-with-btn">
                <input type="number"
                       name="fish_price[]"
                       placeholder="單價"
                       data-label="單價"
                       required>
                <button type="button"
                        class="apply-all-btn"
                        onclick="syncAll('fish_price[]', this)"
                        title="將此價格套用到所有格子">套用</button>
            </div>

            <div class="slot-field field-with-btn">
                <select name="fish_spec[]"
                        data-label="規格範本"
                        required>
                    ${GLOBAL_SPEC_OPTIONS}
                </select>
                <button type="button"
                        class="apply-all-btn"
                        onclick="syncAll('fish_spec[]', this)"
                        title="將此規格套用到所有格子">套用</button>
            </div>

            <div class="slot-field field-with-btn">
                <select name="fish_notice[]"
                        data-label="提醒範本"
                        required>
                    ${GLOBAL_NOTICE_OPTIONS}
                </select>
                <button type="button"
                        class="apply-all-btn"
                        onclick="syncAll('fish_notice[]', this)"
                        title="將此提醒套用到所有格子">套用</button>
            </div>
        </div>
        `;
  }
  container.innerHTML = html;
}

function handlePreview(input) {
  const box = input.closest(".custom-upload-box");
  const previewImg = box.querySelector(".preview-img");
  const placeholder = box.querySelector(".upload-placeholder");

  if (input.files && input.files[0]) {
    // 因：讀取到檔案。果：建立臨時網址。
    const reader = new FileReader();
    reader.onload = function (e) {
      previewImg.src = e.target.result;
      previewImg.style.display = "block"; // 顯示圖片
      placeholder.style.display = "none"; // 隱藏文字
    };
    reader.readAsDataURL(input.files[0]);
  }
}

function syncAll(fieldName, btnElement) {
  const parent = btnElement.parentElement;
  const sourceField = parent.querySelector(`[name="${fieldName}"]`);
  const valueToCopy = sourceField.value;

  const allFields = document.querySelectorAll(`[name="${fieldName}"]`);

  if (valueToCopy === "" && !confirm("當前數值為空，確定要清空所有格子的設定嗎？")) {
    return;
  }

  allFields.forEach((field) => {
    field.value = valueToCopy;
  });

  // --- 視覺回饋開始 ---

  // 🚀 因：需要恢復原狀。果：先存下原本的 HTML 內容（可能是文字或之前的圖示）。
  const originalContent = btnElement.innerHTML;

  // 🚀 因：要顯示圖示。果：使用 innerHTML 插入 SVG 代碼。
  btnElement.innerHTML = ICON_CHECK;

  // 🚀 因：套用全域變數。果：顏色變更為你的成功綠。
  btnElement.style.color = "var(--success)";

  setTimeout(() => {
    // 1秒後還原
    btnElement.innerHTML = originalContent;
    btnElement.style.color = "";
  }, 1000);
}
function updateSlotNumbers() {
  // 1. 找出所有真正的生物卡片 (排除加號卡片)
  const items = document.querySelectorAll(".slot-item:not(.add-slot-card)");

  // 2. 更新標題編號
  items.forEach((item, index) => {
    const header = item.querySelector(".slot-header");
    if (header) {
      header.innerText = `第 ${index + 1} 隻生物`;
    }
  });

  // 🚀 3. 因果邏輯判斷：根據數量顯示或隱藏加號
  const addBtn = document.getElementById("addSlotBtn");
  if (items.length < 20) {
    // 因：格數小於 20。果：顯示加號讓老闆繼續加。
    addBtn.style.display = "flex";
  } else {
    // 因：格數已滿 20。果：強制隱藏加號。
    addBtn.style.display = "none";
  }
}

// 🚀 封裝：產生單個卡片的 HTML (因：避免重複代碼。果：維護方便。)
function getSingleSlotHTML(index) {
  return `
    <div class="slot-item">
        <div class="split-tool">
            <div class="split-left"><div class="slot-header">第 ${index} 隻生物</div></div>
            <div class="split-right">
                <button type="button" class="remove-slot-btn" onclick="this.closest('.slot-item').remove(); updateSlotNumbers();">${ICON_X}</button>
            </div>
        </div>
        <div class="slot-field">
            <label class="custom-upload-box">
                <input type="file" name="fish_image[]" accept="image/*" onchange="handlePreview(this)" style="display: none" data-label="生物照片" required>
                <div class="upload-placeholder">${ICON_UPLOAD}</div>
                <img class="preview-img" src="" style="display: none;">
            </label>
        </div>
        <div class="slot-field">
            <input type="text" name="fish_name[]" placeholder="品種名稱" data-label="品種名稱" required>
        </div>
        <div class="slot-field field-with-btn">
            <input type="number" name="fish_price[]" placeholder="單價" data-label="單價" required>
            <button type="button" class="apply-all-btn" onclick="syncAll('fish_price[]', this)">套用</button>
        </div>
        <div class="slot-field field-with-btn">
            <select name="fish_spec[]" data-label="規格範本" required>${GLOBAL_SPEC_OPTIONS}</select>
            <button type="button" class="apply-all-btn" onclick="syncAll('fish_spec[]', this)">套用</button>
        </div>
        <div class="slot-field field-with-btn">
            <select name="fish_notice[]" data-label="提醒範本" required>${GLOBAL_NOTICE_OPTIONS}</select>
            <button type="button" class="apply-all-btn" onclick="syncAll('fish_notice[]', this)">套用</button>
        </div>
    </div>`;
}

function addSingleSlot() {
  const container = document.getElementById("batchSlotsContainer");
  const addBtn = document.getElementById("addSlotBtn");

  // 1. 取得目前生物格的數量
  const currentItems = container.querySelectorAll(".slot-item:not(.add-slot-card)");
  const currentCount = currentItems.length;

  // 🚀 因：限制數量。果：超過 20 則不執行。
  if (currentCount >= 20) {
    alert("批次上架上限為 20 個喔！");
    return;
  }

  // 2. 插入新格子
  const newSlotHTML = getSingleSlotHTML(currentCount + 1);
  addBtn.insertAdjacentHTML("beforebegin", newSlotHTML);

  // 3. 再次檢查，如果剛好滿 20 個，就把加號按鈕藏起來
  if (currentCount + 1 >= 20) {
    addBtn.style.display = "none";
  }

  updateSlotNumbers();
}

// 修正：也要在初始化 generateBatchSlots 時檢查
function generateBatchSlots(count) {
  const container = document.getElementById("batchSlotsContainer");
  // 強制限制初始數量不超過 20
  const finalCount = Math.min(count, 20);

  let html = "";
  for (let i = 1; i <= finalCount; i++) {
    html += getSingleSlotHTML(i);
  }

  // 如果初始就滿 20 個，就不顯示加號
  const showAddBtn = finalCount < 20 ? "flex" : "none";

  html += `
        <div id="addSlotBtn" class="slot-item add-slot-card" onclick="addSingleSlot()" style="display: ${showAddBtn}">
            <div class="plus-icon">${ICON_PLUS}</div>
            <span>點擊新增生物格</span>
        </div>
    `;
  container.innerHTML = html;
}

// 🚀 處理單獨上架的「引用開關」
// 🚀 1. 搬移與狀態切換函數
// manage.js 裡面的 toggleTemplate 函數

function toggleTemplate(btn, state, fieldName) {
  const parent = btn.closest(".template-group");
  const selectField = parent.querySelector("select");
  const manualArea = parent.querySelector(".accordion-body");
  const wrapper = btn.closest(".mini-toggle-wrapper");
  const activeBg = wrapper.querySelector(".mini-tab-active");

  if (!activeBg || !selectField) return;

  activeBg.style.left = `${btn.offsetLeft}px`;
  activeBg.style.width = `${btn.clientWidth}px`;
  activeBg.style.height = `${btn.clientHeight}px`;

  wrapper.querySelectorAll(".mini-tab").forEach((t) => t.classList.remove("active"));
  btn.classList.add("active");

  if (state === "off") {
    // 【手動輸入模式】
    selectField.style.display = "none";
    selectField.required = false;

    if (manualArea) {
      manualArea.style.display = "block";
      // 🚀 注意：你 HTML 寫的是 e-spec-input-field，這裡要對齊
      manualArea.querySelectorAll(".e-spec-input-field, textarea").forEach((input) => {
        if (input.placeholder !== "選填") {
          input.required = true;
        }
      });
    }
  } else {
    // 【引用範本模式】
    selectField.style.display = "block";
    selectField.required = true;

    if (manualArea) {
      manualArea.style.display = "none";

      // 🚀 核心修正點：加入 textarea，把隱藏區的所有必填通通拔掉！
      manualArea.querySelectorAll("input, select, textarea").forEach((el) => {
        el.required = false;
      });
    }
  }
}

// 🚀 2. 初始化與視窗縮放處理 這是處理他要不要自定義
const initAllMiniToggles = () => {
  document.querySelectorAll(".mini-tab.active").forEach((tab) => {
    // 取得當前狀態 (是 'on' 還是 'off')
    // 這裡建議在 HTML 加上 onclick 的時候傳參數，或者從文字判斷
    const isOff = tab.innerText.includes("關閉");
    toggleTemplate(tab, isOff ? "off" : "on");
  });
};

// 網頁載入時執行
window.addEventListener("load", initAllMiniToggles);

// 🚀 補上這個：防止視窗縮放時，因為絕對定位導致藥丸跟丟按鈕
window.addEventListener("resize", initAllMiniToggles);

// 🚀 讓 HTMX 每次發請求都自動帶上 CSRF Token
document.body.addEventListener("htmx:configRequest", (event) => {
  event.detail.headers["X-CSRFToken"] = "{{ csrf_token }}";
});
