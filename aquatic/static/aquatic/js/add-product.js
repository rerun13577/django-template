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
                    
                    <button class="delete-prod-pic-btn"
                            type="button"
                            onclick="removePhoto(this)"
                            style="display: none">
                        ${ICON_X}
                    </button>
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

// 🚀 1. 唯一的衣服模板工廠：只要這裡有叉叉，全世界都有叉叉
function getSingleSlotHTML(i) {
  return `
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
                    ${ICON_X}
                </button>
            </div>
        </div>

        <div class="slot-field1 photo-upload-container">
            
            <div class="main-cover-box single-photo-ratio" data-active-slot="1" onclick="triggerActiveInput(event)">
                <div class="custom-upload-box" style="position: relative; width: 100%; height: 100%;">
                    
                    <div class="upload-placeholder viewport-placeholder">
                        ${ICON_UPLOAD}
                        <span style="font-size: 0.85rem; color: var(--text-muted); margin-top: 0.5rem; display: block;">點擊選取或多選 4 張照片</span>
                    </div>
                    
                    <img class="preview-img viewport-img" src="" style="display: none;">
                    
                    <button class="b-delete-prod-pic-btn"
                            type="button"
                            onclick="removeActivePhoto(event)"
                            style="display: none">
                        ${ICON_X}
                    </button>
                </div>
            </div>

            <div class="photo-train-slots">
                <div class="sub-photo-slot active-focus" data-slot-index="1" onclick="handleSlotClick(this, '1', event)">
                    <div class="custom-upload-box sub-photo-ratio" style="position: relative;">
                        <input type="file" name="fish_image_${i}[]" accept="image/*" onchange="handleGalleryUpload(this, '1')" style="display: none;" multiple required>
                        <div class="upload-placeholder">+</div>
                        <img class="preview-img slot-thumb" src="" style="display: none;">
                    </div>
                </div>
                <div class="sub-photo-slot" data-slot-index="2" onclick="handleSlotClick(this, '2', event)">
                    <div class="custom-upload-box sub-photo-ratio" style="position: relative;">
                        <input type="file" name="fish_image_${i}[]" accept="image/*" onchange="handleGalleryUpload(this, '2')" style="display: none;" multiple>
                        <div class="upload-placeholder">+</div>
                        <img class="preview-img slot-thumb" src="" style="display: none;">
                    </div>
                </div>
                <div class="sub-photo-slot" data-slot-index="3" onclick="handleSlotClick(this, '3', event)">
                    <div class="custom-upload-box sub-photo-ratio" style="position: relative;">
                        <input type="file" name="fish_image_${i}[]" accept="image/*" onchange="handleGalleryUpload(this, '3')" style="display: none;" multiple>
                        <div class="upload-placeholder">+</div>
                        <img class="preview-img slot-thumb" src="" style="display: none;">
                    </div>
                </div>
                <div class="sub-photo-slot" data-slot-index="4" onclick="handleSlotClick(this, '4', event)">
                    <div class="custom-upload-box sub-photo-ratio" style="position: relative;">
                        <input type="file" name="fish_image_${i}[]" accept="image/*" onchange="handleGalleryUpload(this, '4')" style="display: none;" multiple>
                        <div class="upload-placeholder">+</div>
                        <img class="preview-img slot-thumb" src="" style="display: none;">
                    </div>
                </div>
            </div>
        </div>

        <div class="slot-field">
            <input type="text" name="fish_name[]" placeholder="品種名稱 (如：極火蝦)" required>
        </div>
        <div class="slot-field field-with-btn">
            <input type="number" name="fish_price[]" placeholder="單價" required>
            <button type="button" class="apply-all-btn" onclick="syncAll('fish_price[]', this)">套用</button>
        </div>
        <div class="slot-field field-with-btn">
            <select name="fish_spec[]" required>${GLOBAL_SPEC_OPTIONS}</select>
            <button type="button" class="apply-all-btn" onclick="syncAll('fish_spec[]', this)">套用</button>
        </div>
        <div class="slot-field field-with-btn">
            <select name="fish_notice[]" required>${GLOBAL_NOTICE_OPTIONS}</select>
            <button type="button" class="apply-all-btn" onclick="syncAll('fish_notice[]', this)">套用</button>
        </div>
    </div>
  `;
}

// 🚀 2. 指揮官 A：輸入數量一次生成大批卡片（你現在要修正的功能）
function generateBatchSlots(count) {
  const container = document.getElementById("batchSlotsContainer");
  const finalCount = Math.min(count, 20); // 限制最多 20 個

  let html = "";
  for (let i = 1; i <= finalCount; i++) {
    html += getSingleSlotHTML(i); // 拿回有叉叉的衣服
  }

  // 補上最後的 ＋ 號字卡
  const showAddBtn = finalCount < 20 ? "flex" : "none";
  html += `
        <div id="addSlotBtn" class="slot-item add-slot-card" onclick="addSingleSlot()" style="display: ${showAddBtn}">
            <div class="plus-icon">${ICON_PLUS}</div>
            <span>點擊新增生物格</span>
        </div>
    `;
  container.innerHTML = html;
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

// 🚀 預覽照片邏輯
// 🚀 預覽照片邏輯
function handlePreview(input) {
  const box = input.closest(".custom-upload-box");
  const placeholder = box.querySelector(".upload-placeholder");
  const previewImg = box.querySelector(".preview-img");

  /* ────────────────────────────────────────────────────────
     🚀 核心因果修正：利用 CSS 逗號選取器（代表「或」）
     不論是單獨卡的 class 還是批量卡的 b- class，誰在場就抓誰！
     ──────────────────────────────────────────────────────── */
  const deleteBtn = box.querySelector(".delete-prod-pic-btn, .b-delete-prod-pic-btn");

  if (input.files && input.files[0]) {
    const reader = new FileReader();

    reader.onload = function (e) {
      previewImg.src = e.target.result;
      previewImg.style.display = "block";
      placeholder.style.display = "none";
      if (deleteBtn) deleteBtn.style.display = "flex"; // 抓到誰，誰就亮出來
    };

    reader.readAsDataURL(input.files[0]);
  }
}

// 🚀 刪除照片邏輯（維持原樣，物理無敵）
function removePhoto(button) {
  // 阻止 label 被點擊再次觸發上傳視窗
  if (window.event) window.event.preventDefault();

  const box = button.closest(".custom-upload-box");
  const input = box.querySelector('input[type="file"]');
  const placeholder = box.querySelector(".upload-placeholder");
  const previewImg = box.querySelector(".preview-img");

  // 清空記憶體與預覽
  input.value = "";
  previewImg.src = "";
  previewImg.style.display = "none";
  placeholder.style.display = "flex";

  // 🚀 因果：因為變數 button 就是點擊的那個節點本人，
  // 瀏覽器直接對它執行隱藏，所以不管它是 delete 還是 b-delete 都絕對有效。
  button.style.display = "none";
}

// 下面是照片列的上傳與展示邏輯，這部分比較複雜，請務必細讀註解理解因果關係。

// 🚀 1. 點擊小格子智慧分流
function handleSlotClick(slotElement, slotIndex, event) {
  const container = slotElement.closest(".photo-upload-container");
  switchActiveSlot(container, slotIndex);

  const img = slotElement.querySelector(".slot-thumb");
  const input = slotElement.querySelector('input[type="file"]');

  if (!img.src || img.style.display === "none") {
    if (input) input.click();
  }
}

// 🚀 2. 獨立切換該卡片內的觀景窗展示
function switchActiveSlot(container, slotIndex) {
  const viewport = container.querySelector(".main-cover-box");
  viewport.setAttribute("data-active-slot", slotIndex);

  container.querySelectorAll(".sub-photo-slot").forEach((el) => el.classList.remove("active-focus"));
  const currentSlot = container.querySelector(`.sub-photo-slot[data-slot-index="${slotIndex}"]`);
  if (currentSlot) currentSlot.classList.add("active-focus");

  const slotImg = currentSlot.querySelector(".slot-thumb");
  const viewportImg = container.querySelector(".viewport-img");
  const viewportPlaceholder = container.querySelector(".viewport-placeholder");

  /* ────────────────────────────────────────────────────────
     🚀 核心相容修正：改用逗號，不管是 .delete- 還是 .b-delete- 通通抓得到！
     ──────────────────────────────────────────────────────── */
  const viewportDeleteBtn = container.querySelector(".delete-prod-pic-btn, .b-delete-prod-pic-btn");

  if (slotImg && slotImg.src && slotImg.style.display !== "none") {
    viewportImg.src = slotImg.src;
    viewportImg.style.display = "block";
    viewportPlaceholder.style.display = "none";
    if (viewportDeleteBtn) viewportDeleteBtn.style.display = "flex";
  } else {
    viewportImg.src = "";
    viewportImg.style.display = "none";
    viewportPlaceholder.style.display = "flex";
    if (viewportDeleteBtn) viewportDeleteBtn.style.display = "none";
  }
}

// 🚀 3. 多選與單選上傳分流演算法
function handleGalleryUpload(input, slotIndex) {
  if (!input.files || input.files.length === 0) return;

  const container = input.closest(".photo-upload-container");
  const startIndex = parseInt(slotIndex);
  const files = input.files;

  // 情況 A：單選
  if (files.length === 1) {
    const slotBox = input.closest(".custom-upload-box");
    const slotPlaceholder = slotBox.querySelector(".upload-placeholder");
    const slotImg = slotBox.querySelector(".preview-img");

    const reader = new FileReader();
    reader.onload = function (e) {
      slotImg.src = e.target.result;
      slotImg.style.display = "block";
      slotPlaceholder.style.display = "none";
      switchActiveSlot(container, slotIndex);
    };
    reader.readAsDataURL(files[0]);
    return;
  }

  // 情況 B：多選連續轟炸
  for (let i = 0; i < files.length; i++) {
    const currentTargetIndex = startIndex + i;
    if (currentTargetIndex > 4) break;

    const file = files[i];
    const targetSlot = container.querySelector(`.sub-photo-slot[data-slot-index="${currentTargetIndex}"]`);
    if (!targetSlot) continue;

    const targetInput = targetSlot.querySelector('input[type="file"]');
    const slotPlaceholder = targetSlot.querySelector(".upload-placeholder");
    const slotImg = targetSlot.querySelector(".preview-img");

    if (i > 0) {
      const dt = new DataTransfer();
      dt.items.add(file);
      targetInput.files = dt.files;
    }

    const reader = new FileReader();
    (function (img, placeholder) {
      reader.onload = function (e) {
        img.src = e.target.result;
        img.style.display = "block";
        placeholder.style.display = "none";
      };
    })(slotImg, slotPlaceholder);

    reader.readAsDataURL(file);
  }

  setTimeout(() => {
    switchActiveSlot(container, startIndex.toString());
  }, 100);
}

// 🚀 4. 點擊大框框重選照片
function triggerActiveInput(e) {
  if (e.target.closest(".b-delete-prod-pic-btn")) return;

  const viewport = e.currentTarget;
  const container = viewport.closest(".photo-upload-container");
  const activeIndex = viewport.getAttribute("data-active-slot");
  const activeInput = container.querySelector(`.sub-photo-slot[data-slot-index="${activeIndex}"] input[type="file"]`);

  if (activeInput) activeInput.click();
}

// 🚀 5. 大框框的大叉叉：連帶擊殺下方本體
function removeActivePhoto(e) {
  e.stopPropagation();

  const btn = e.currentTarget;
  const container = btn.closest(".photo-upload-container");
  const viewport = container.querySelector(".main-cover-box");
  const activeIndex = viewport.getAttribute("data-active-slot");

  const targetSlot = container.querySelector(`.sub-photo-slot[data-slot-index="${activeIndex}"]`);
  if (!targetSlot) return;

  const input = targetSlot.querySelector('input[type="file"]');
  const slotPlaceholder = targetSlot.querySelector(".upload-placeholder");
  const slotImg = targetSlot.querySelector(".preview-img");

  input.value = "";
  slotImg.src = "";
  slotImg.style.display = "none";
  slotPlaceholder.style.display = "flex";

  container.querySelector(".viewport-img").src = "";
  container.querySelector(".viewport-img").style.display = "none";
  container.querySelector(".viewport-placeholder").style.display = "flex";
  btn.style.display = "none";
}

// 編輯小魚

document.addEventListener("DOMContentLoaded", () => {
  // 🚀 核心因果修正：改用全域事件代理，直接監聽整個 document
  document.addEventListener("click", (e) => {
    // 🎯 1. 偵測點擊目標：不論新卡片還是舊卡片，只要點擊的對象（或其祖先）包含三個點 class
    const btn = e.target.closest(".fissh-card-menu-dots");

    if (btn) {
      // 因：使用者點擊了三個點。
      // 果：物理攔截！秒斷所有向上冒泡的電流，絕對不讓外層 <a> 標籤觸發 href="/" 的跳轉！
      e.preventDefault();
      e.stopPropagation();

      const pane = btn.nextElementSibling;
      const isOpen = pane.classList.contains("fissh-show");

      // 物理防護：先把畫面上所有可能開著的選單全數收起，避免重疊
      document.querySelectorAll(".fissh-card-menu-pane").forEach((p) => p.classList.remove("fissh-show"));

      if (!isOpen) {
        pane.classList.add("fissh-show"); // 面板就地顯形
      }
      return; // 阻斷後續邏輯，直接退場
    }

    // 🎯 2. 全局雷達防線：如果點擊的地方跟整個選單結構無關，代表使用者想關閉選單
    if (!e.target.closest(".fissh-card-menu-wrap")) {
      document.querySelectorAll(".fissh-card-menu-pane").forEach((pane) => {
        pane.classList.remove("fissh-show");
      });
    }
  });
});

// 3. 獨立功能觸發器：點擊選單選項時執行
function runFisshCardAction(event, action, itemId) {
  event.preventDefault();
  event.stopPropagation(); // 物理斷電：阻止外層 a 標籤跳轉

  const pane = event.currentTarget.closest(".fissh-card-menu-pane");
  if (pane) pane.classList.remove("fissh-show");

  // 🎯 精準定位當前點擊的這張商品卡片本體
  const card = document.getElementById(`product-card-${itemId}`);
  const csrftoken = document.cookie
    .split("; ")
    .find((row) => row.startsWith("csrftoken="))
    ?.split("=")[1];

  if (action === "edit") {
    console.log(`[ACTION] 編輯商品 ID: ${itemId}`);
  } else if (action === "delist") {
    // 因：準備向後端發送下架 POST。果：立刻幫卡片上一道鎖，變暗且防連點
    if (card) card.classList.add("fissh-loading");

    fetch(`/product/${itemId}/delist/`, {
      method: "POST",
      headers: { "X-CSRFToken": csrftoken },
    })
      .then((res) => {
        if (res.ok) {
          // 🎯 物理移動至下架區
          const inactiveGrid = document.getElementById("inactive-grid");
          if (card && inactiveGrid) {
            const emptyHint = inactiveGrid.querySelector(".empty-hint");
            if (emptyHint) emptyHint.remove();

            inactiveGrid.appendChild(card); // 卡片自動滾至下方

            // 動態重寫按鈕線路：改為上架屬性
            const delistBtn = card.querySelector('[onclick*="delist"]');
            if (delistBtn) {
              delistBtn.textContent = "上架商品";
              delistBtn.setAttribute("onclick", `runFisshCardAction(event, 'relist', '${itemId}')`);
            }
          }
        }
      })
      .finally(() => {
        // 果：不論後端成功或失敗，通訊結束物理開鎖，還原字體與亮度
        if (card) card.classList.remove("fissh-loading");
      });
  } else if (action === "relist") {
    // 因：準備向後端發送重新上架 POST。果：卡片立刻變暗、死鎖
    if (card) card.classList.add("fissh-loading");

    fetch(`/product/${itemId}/relist/`, {
      method: "POST",
      headers: { "X-CSRFToken": csrftoken },
    })
      .then((res) => {
        if (res.ok) {
          // 🎯 物理移動至上架區
          const activeGrid = document.getElementById("active-grid");
          if (card && activeGrid) {
            const emptyHint = activeGrid.querySelector(".empty-hint");
            if (emptyHint) emptyHint.remove();

            activeGrid.appendChild(card); // 卡片自動回彈至上方

            // 動態重寫按鈕線路：改回下架屬性
            const relistBtn = card.querySelector('[onclick*="relist"]');
            if (relistBtn) {
              relistBtn.textContent = "下架商品";
              relistBtn.setAttribute("onclick", `runFisshCardAction(event, 'delist', '${itemId}')`);
            }
          }
        }
      })
      .finally(() => {
        // 果：通訊完畢，解鎖卡片
        if (card) card.classList.remove("fissh-loading");
      });
  } else if (action === "delete") {
    console.log(`[ACTION] 觸發物理刪除，ID: ${itemId}`);

    // 🛡️ 防呆防線：萬一指頭殘點錯，直接在網頁層發射中斷訊號
    if (!confirm("幹，確定要刪除這商品嗎？刪掉就死透了、資料庫救不回來喔！")) {
      return; // 使用者按取消：電流直接掐斷，什麼都不發生
    }

    // 因：確定要刪，立刻上鎖變暗，防止使用者在傳輸的 0.2 秒內瘋狂連點
    if (card) card.classList.add("fissh-loading");

    // 發射非同步電訊號
    fetch(`/product/${itemId}/delete/`, {
      method: "POST",
      headers: { "X-CSRFToken": csrftoken },
    })
      .then((res) => {
        if (res.ok) {
          // 果：資料庫那邊已經燒毀。前端直接下達 remove() 指令
          if (card) {
            // 網頁節點（DOM）當場斷根，不留任何渣滓與排版空隙
            card.remove();
            alert("商品已徹底刪除！");
          }
        } else {
          alert("刪除失敗，後端電路可能有鬼。");
        }
      })
      .catch((err) => {
        console.error(err);
      })
      .finally(() => {
        // 安全退場：萬一沒刪成功，至少把卡片解鎖
        if (card) card.classList.remove("fissh-loading");
      });
  }
}
