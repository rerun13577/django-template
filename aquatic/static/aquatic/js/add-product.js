// 控制流水線 輸入數字 產生卡片和確認按鈕 隱藏數入的格子
// function handleBatchConfirm() {
//   // 輸入格子的數字必須大於0
//   const countInput = document.getElementById("batchCountInput");
//   const count = parseInt(countInput.value);
//   if (isNaN(count) || count <= 0) return;

//   // 1. 執行生成格子 (維持你原本的)
//   generateBatchSlots(count);

//   // 2. 抓取批量表單與按鈕
//   const batchForm = document.getElementById("batchUploadForm");
//   const actionArea = document.getElementById("actionArea");

//   // 🚀 因：格子已在表單內生成完畢。果：直接把整個批量表單跟上架按鈕秀出來。
//   if (batchForm) batchForm.style.display = "block";
//   if (actionArea) actionArea.style.display = "block";

//   // 3. 隱藏輸入格數的 Banner
//   const setupSection = document.getElementById("setupSection");
//   if (setupSection) setupSection.style.display = "none";
// }

//照片的即時預覽，把加號隱藏 show 照片
// function handlePreview(input) {
//   const box = input.closest(".custom-upload-box");
//   const previewImg = box.querySelector(".preview-img");
//   const placeholder = box.querySelector(".upload-placeholder");

//   if (input.files && input.files[0]) {
//     // 因：讀取到檔案。果：建立臨時網址。
//     const reader = new FileReader();
//     reader.onload = function (e) {
//       previewImg.src = e.target.result;
//       previewImg.style.display = "block"; // 顯示圖片
//       placeholder.style.display = "none"; // 隱藏文字
//     };
//     reader.readAsDataURL(input.files[0]);
//   }
// }

//處理套用資訊 包含價格 提醒 規格邏輯

// function syncAll(fieldName, btnElement) {
//   const parent = btnElement.parentElement;
//   const sourceField = parent.querySelector(`[name="${fieldName}"]`);
//   const valueToCopy = sourceField.value;

//   const allFields = document.querySelectorAll(`[name="${fieldName}"]`);

//   if (valueToCopy === "" && !confirm("當前數值為空，確定要清空所有格子的設定嗎？")) {
//     return;
//   }

//   allFields.forEach((field) => {
//     field.value = valueToCopy;
//   });

//   // --- 視覺回饋開始 ---

//   // 🚀 因：需要恢復原狀。果：先存下原本的 HTML 內容（可能是文字或之前的圖示）。
//   const originalContent = btnElement.innerHTML;

//   // 🚀 因：要顯示圖示。果：使用 innerHTML 插入 SVG 代碼。
//   btnElement.innerHTML = ICON_CHECK;

//   // 🚀 因：套用全域變數。果：顏色變更為你的成功綠。
//   btnElement.style.color = "var(--success)";

//   setTimeout(() => {
//     // 1秒後還原
//     btnElement.innerHTML = originalContent;
//     btnElement.style.color = "";
//   }, 1000);
// }

//如果刪除卡片他可以更新的數值(模組)
// function updateSlotNumbers() {
//   // 1. 找出所有真正的生物卡片 (排除加號卡片)
//   const items = document.querySelectorAll(".slot-item:not(.add-slot-card)");

//   // 2. 更新標題編號
//   items.forEach((item, index) => {
//     const header = item.querySelector(".slot-header");
//     if (header) {
//       header.innerText = `第 ${index + 1} 隻生物`;
//     }
//   });

//   // 🚀 3. 因果邏輯判斷：根據數量顯示或隱藏加號
//   const addBtn = document.getElementById("addSlotBtn");
//   if (items.length < 20) {
//     // 因：格數小於 20。果：顯示加號讓老闆繼續加。
//     addBtn.style.display = "flex";
//   } else {
//     // 因：格數已滿 20。果：強制隱藏加號。
//     addBtn.style.display = "none";
//   }
// }

// 唯一的卡片模板
// function getSingleSlotHTML(i) {
//   return `
//     <div class="slot-item">
//         <div class="split-tool">
//             <div class="split-left">
//                 <div class="slot-header">第 ${i} 隻生物</div>
//             </div>
//             <div class="split-right">
//                 <button type="button"
//                         class="remove-slot-btn"
//                         onclick="this.closest('.slot-item').remove(); updateSlotNumbers();"
//                         title="移除此格">
//                     ${ICON_X}
//                 </button>
//             </div>
//         </div>

//         <div class="slot-field1 photo-upload-container">
            
//             <div class="main-cover-box single-photo-ratio" data-active-slot="1" onclick="triggerActiveInput(event)">
//                 <div class="custom-upload-box" style="position: relative; width: 100%; height: 100%;">
                    
//                     <div class="upload-placeholder viewport-placeholder">
//                         ${ICON_UPLOAD}
//                         <span style="font-size: 0.85rem; color: var(--text-muted); margin-top: 0.5rem; display: block;">點擊選取或多選 4 張照片</span>
//                     </div>
                    
//                     <img class="preview-img viewport-img" src="" style="display: none;">
                    
//                     <button class="b-delete-prod-pic-btn"
//                             type="button"
//                             onclick="removeActivePhoto(event)"
//                             style="display: none">
//                         ${ICON_X}
//                     </button>
//                 </div>
//             </div>

//             <div class="photo-train-slots">
//                 <div class="sub-photo-slot active-focus" data-slot-index="1" onclick="handleSlotClick(this, '1', event)">
//                     <div class="custom-upload-box sub-photo-ratio" style="position: relative;">
//                         <input type="file" name="fish_image_${i}[]" accept="image/*" onchange="handleGalleryUpload(this, '1')" style="display: none;" multiple required>
//                         <div class="upload-placeholder">+</div>
//                         <img class="preview-img slot-thumb" src="" style="display: none;">
//                     </div>
//                 </div>
//                 <div class="sub-photo-slot" data-slot-index="2" onclick="handleSlotClick(this, '2', event)">
//                     <div class="custom-upload-box sub-photo-ratio" style="position: relative;">
//                         <input type="file" name="fish_image_${i}[]" accept="image/*" onchange="handleGalleryUpload(this, '2')" style="display: none;" multiple>
//                         <div class="upload-placeholder">+</div>
//                         <img class="preview-img slot-thumb" src="" style="display: none;">
//                     </div>
//                 </div>
//                 <div class="sub-photo-slot" data-slot-index="3" onclick="handleSlotClick(this, '3', event)">
//                     <div class="custom-upload-box sub-photo-ratio" style="position: relative;">
//                         <input type="file" name="fish_image_${i}[]" accept="image/*" onchange="handleGalleryUpload(this, '3')" style="display: none;" multiple>
//                         <div class="upload-placeholder">+</div>
//                         <img class="preview-img slot-thumb" src="" style="display: none;">
//                     </div>
//                 </div>
//                 <div class="sub-photo-slot" data-slot-index="4" onclick="handleSlotClick(this, '4', event)">
//                     <div class="custom-upload-box sub-photo-ratio" style="position: relative;">
//                         <input type="file" name="fish_image_${i}[]" accept="image/*" onchange="handleGalleryUpload(this, '4')" style="display: none;" multiple>
//                         <div class="upload-placeholder">+</div>
//                         <img class="preview-img slot-thumb" src="" style="display: none;">
//                     </div>
//                 </div>
//             </div>
//         </div>

//         <div class="slot-field">
//             <input type="text" name="fish_name[]" placeholder="品種名稱 (如：極火蝦)" required>
//         </div>
//         <div class="slot-field field-with-btn">
//             <input type="number" name="fish_price[]" placeholder="單價" required>
//             <button type="button" class="apply-all-btn" onclick="syncAll('fish_price[]', this)">套用</button>
//         </div>
//         <div class="slot-field field-with-btn">
//             <select name="fish_spec[]" required>${GLOBAL_SPEC_OPTIONS}</select>
//             <button type="button" class="apply-all-btn" onclick="syncAll('fish_spec[]', this)">套用</button>
//         </div>
//         <div class="slot-field field-with-btn">
//             <select name="fish_notice[]" required>${GLOBAL_NOTICE_OPTIONS}</select>
//             <button type="button" class="apply-all-btn" onclick="syncAll('fish_notice[]', this)">套用</button>
//         </div>
//     </div>
//   `;
// }

// 輸入數量一次生成大批卡片
// function generateBatchSlots(count) {
//   const container = document.getElementById("batchSlotsContainer");
//   const finalCount = Math.min(count, 20); // 限制最多 20 個

//   let html = "";
//   for (let i = 1; i <= finalCount; i++) {
//     html += getSingleSlotHTML(i); // 拿回有叉叉的衣服
//   }

//   // 補上最後的 ＋ 號字卡
//   const showAddBtn = finalCount < 20 ? "flex" : "none";
//   html += `
//         <div id="addSlotBtn" class="slot-item add-slot-card" onclick="addSingleSlot()" style="display: ${showAddBtn}">
//             <div class="plus-icon">${ICON_PLUS}</div>
//             <span>點擊新增生物格</span>
//         </div>
//     `;
//   container.innerHTML = html;
// }

//把新的卡片插入再加號前面
// function addSingleSlot() {
//   const container = document.getElementById("batchSlotsContainer");
//   const addBtn = document.getElementById("addSlotBtn");

//   // 1. 取得目前生物格的數量
//   const currentItems = container.querySelectorAll(".slot-item:not(.add-slot-card)");
//   const currentCount = currentItems.length;

//   // 🚀 因：限制數量。果：超過 20 則不執行。
//   if (currentCount >= 20) {
//     alert("批次上架上限為 20 個喔！");
//     return;
//   }

//   // 2. 插入新格子
//   const newSlotHTML = getSingleSlotHTML(currentCount + 1);
//   addBtn.insertAdjacentHTML("beforebegin", newSlotHTML);

//   // 3. 再次檢查，如果剛好滿 20 個，就把加號按鈕藏起來
//   if (currentCount + 1 >= 20) {
//     addBtn.style.display = "none";
//   }

//   updateSlotNumbers();
// }

//非上傳處的部分的部分

// 🚀 處理單獨上架的「引用開關」
// 🚀 1. 搬移與狀態切換函數
// manage.js 裡面的 toggleTemplate 函數

// 客戶是要引用範本或者自定義(只有單獨上傳會用到)
// function toggleTemplate(btn, state, fieldName) {
//   const parent = btn.closest(".template-group");
//   const selectField = parent.querySelector("select");
//   const manualArea = parent.querySelector(".accordion-body");
//   const wrapper = btn.closest(".mini-toggle-wrapper");
//   const activeBg = wrapper.querySelector(".mini-tab-active");

//   console.log("偵測點 - 父層結構:", parent);
//   console.log("偵測點 - 找到的區塊:", manualArea);
//   if (manualArea) {
//     console.log("偵測點 - 區塊內內容:", manualArea.innerHTML.substring(0, 50));
//   }

//   if (!activeBg || !selectField) return;

//   activeBg.style.left = `${btn.offsetLeft}px`;
//   activeBg.style.width = `${btn.clientWidth}px`;
//   activeBg.style.height = `${btn.clientHeight}px`;

//   wrapper.querySelectorAll(".mini-tab").forEach((t) => t.classList.remove("active"));
//   btn.classList.add("active");

//   if (state === "off") {
//     // 【手動輸入模式】
//     selectField.style.display = "none";
//     selectField.required = false;

//     // 🚀 核心修正 1：物理清空下拉選單的值，徹底斬斷後端的範本優先級
//     selectField.value = "";

//     if (manualArea) {
//       manualArea.style.display = "block";
//       // 🚀 注意：你 HTML 寫的是 e-spec-input-field，這裡要對齊
//       manualArea.querySelectorAll(".e-spec-input-field, textarea").forEach((input) => {
//         if (input.placeholder !== "選填") {
//           input.required = true;
//         }
//       });
//     }
//   } else {
//     // 【引用範本模式】
//     selectField.style.display = "block";
//     selectField.required = true;

//     if (manualArea) {
//       manualArea.style.display = "none";

//       // 🚀 核心修正 2：拔掉必填的同時，順手物理清空隱藏區的殘留字串
//       manualArea.querySelectorAll("input, select, textarea").forEach((el) => {
//         el.required = false;
//         el.value = ""; // 物理蒸發自定義內容
//       });
//     }
//   }
// }

// 網頁剛進入的初始畫狀態
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
  const csrftoken = document.cookie
    .split("; ")
    .find((row) => row.startsWith("csrftoken="))
    ?.split("=")[1];

  if (csrftoken) {
    event.detail.headers["X-CSRFToken"] = csrftoken;
  }
});

// 🚀 預覽照片邏輯
// function handlePreview(input) {
//   const box = input.closest(".custom-upload-box");
//   const placeholder = box.querySelector(".upload-placeholder");
//   const previewImg = box.querySelector(".preview-img");

//   /* ────────────────────────────────────────────────────────
//      🚀 核心因果修正：利用 CSS 逗號選取器（代表「或」）
//      不論是單獨卡的 class 還是批量卡的 b- class，誰在場就抓誰！
//      ──────────────────────────────────────────────────────── */
//   const deleteBtn = box.querySelector(".delete-prod-pic-btn, .b-delete-prod-pic-btn");

//   if (input.files && input.files[0]) {
//     const reader = new FileReader();

//     reader.onload = function (e) {
//       previewImg.src = e.target.result;
//       previewImg.style.display = "block";
//       placeholder.style.display = "none";
//       if (deleteBtn) deleteBtn.style.display = "flex"; // 抓到誰，誰就亮出來
//     };

//     reader.readAsDataURL(input.files[0]);
//   }
// }

// 🚀 刪除照片邏輯（維持原樣，物理無敵）
// function removePhoto(button) {
//   // 阻止 label 被點擊再次觸發上傳視窗
//   if (window.event) window.event.preventDefault();

//   const box = button.closest(".custom-upload-box");
//   const input = box.querySelector('input[type="file"]');
//   const placeholder = box.querySelector(".upload-placeholder");
//   const previewImg = box.querySelector(".preview-img");

//   // 清空記憶體與預覽
//   input.value = "";
//   previewImg.src = "";
//   previewImg.style.display = "none";
//   placeholder.style.display = "flex";

//   // 🚀 因果：因為變數 button 就是點擊的那個節點本人，
//   // 瀏覽器直接對它執行隱藏，所以不管它是 delete 還是 b-delete 都絕對有效。
//   button.style.display = "none";
// }

// 📁 document (整張網頁)
//   ├── 📦 卡片：第 1 隻生物
//   │     ├── 🔲 小格子 A (slotElement) ── 找這裡面的 input
//   │     └── 🔲 小格子 B
//   └── 📦 卡片：第 2 隻生物
//         ├── 🔲 小格子 C
//         └── 🔲 小格子 D
// !img.src 如果IMG 裡面沒有SCR連結

// 下面是照片列的上傳與展示邏輯，這部分比較複雜，請務必細讀註解理解因果關係。

// 🚀 1. 點擊小格子智慧分流
// function handleSlotClick(slotElement, slotIndex, event) {
//   const container = slotElement.closest(".photo-upload-container");
//   switchActiveSlot(container, slotIndex);

//   const img = slotElement.querySelector(".slot-thumb");
//   const input = slotElement.querySelector('input[type="file"]');

//   if (!img.src || img.style.display === "none") {
//     if (input) input.click();
//   }
// }

//  獨立切換該卡片內的觀景窗展示
// function switchActiveSlot(container, slotIndex) {
//   const viewport = container.querySelector(".main-cover-box");
//   // .main-cover-box會被蓋上戳記 data-active-solt之類的
//   viewport.setAttribute("data-active-slot", slotIndex);

//   // 先把現在所有小格子上面的active 效果拔掉，然後在看要亮哪一個
//   container.querySelectorAll(".sub-photo-slot").forEach((el) => el.classList.remove("active-focus"));
//   const currentSlot = container.querySelector(`.sub-photo-slot[data-slot-index="${slotIndex}"]`);
//   if (currentSlot) currentSlot.classList.add("active-focus");

//   const slotImg = currentSlot.querySelector(".slot-thumb");
//   const viewportImg = container.querySelector(".viewport-img");
//   const viewportPlaceholder = container.querySelector(".viewport-placeholder");
//   // 她一次試著抓兩個人 如果第一個人有被抓到就結束 不會再去抓第二個人
//   const viewportDeleteBtn = container.querySelector(".delete-prod-pic-btn, .b-delete-prod-pic-btn");

//   if (slotImg && slotImg.src && slotImg.style.display !== "none") {
//     // 把數照片路徑相同這樣他們就會顯示一樣的照片的放大版
//     viewportImg.src = slotImg.src;
//     viewportImg.style.display = "block";
//     // 上面有定義下面的佔位符是要啥
//     viewportPlaceholder.style.display = "none";
//     // 如何有找到viewportDeleteBtn 那這個if就會被執行
//     if (viewportDeleteBtn) viewportDeleteBtn.style.display = "flex";
//   } else {
//     // 如果大照片是空的那我就顯示加號
//     viewportImg.src = "";
//     viewportImg.style.display = "none";
//     viewportPlaceholder.style.display = "flex";
//     if (viewportDeleteBtn) viewportDeleteBtn.style.display = "none";
//   }
// }

// 🚀 3. 多選與單選上傳分流演算法
// function handleGalleryUpload(input, slotIndex) {
//   // 如果你沒有上傳檔案就滾開
//   if (!input.files || input.files.length === 0) return;

//   // container這個會等於離輸入最近的photo-upload-container
//   const container = input.closest(".photo-upload-container");
//   // 紀錄boss現在點的是第幾格
//   const startIndex = parseInt(slotIndex);
//   // files這個變數等於老闆所有的照片
//   const files = input.files;

//   // 情況 A：單選
//   if (files.length === 1) {
//     const slotBox = input.closest(".custom-upload-box");
//     const slotPlaceholder = slotBox.querySelector(".upload-placeholder");
//     const slotImg = slotBox.querySelector(".preview-img");

//     // 新增用於照片的解碼的機器，一個只能對一個用
//     // 所以下面多次解碼照片有再創一個機器
//     const reader = new FileReader();
//     reader.onload = function (e) {
//       // 拿到事件中 scr的成品
//       // event她只會是跟這個函數有關係的事件
//       slotImg.src = e.target.result;
//       slotImg.style.display = "block";
//       slotPlaceholder.style.display = "none";
//       // 讓中央的的框框可以亮起來的函數
//       switchActiveSlot(container, slotIndex);
//     };
//     // 這機器會把照片吞進去 然後解碼成scr然後吐出來 我透過event把結果拿回來
//     reader.readAsDataURL(files[0]);
//     return;
//   }

//   // 情況 B：多選連續轟炸
//   // 當第0個資料進來她就會先跑原本的資料因為startIndex + 0
//   for (let i = 0; i < files.length; i++) {
//     const currentTargetIndex = startIndex + i;
//     if (currentTargetIndex > 4) break;

//     const file = files[i];
//     // currentTargetIndex 是變數然後他就會帶入他自己的數字進去
//     const targetSlot = container.querySelector(`.sub-photo-slot[data-slot-index="${currentTargetIndex}"]`);
//     // 如果大於5會找不到所以跳過 雙重保護
//     if (!targetSlot) continue;

//     // 前面已經定義了targetslot要是當前數字的格子
//     // 所以input一定會對，這也代表了我後面照片塞入的格子一定會對
//     const targetInput = targetSlot.querySelector('input[type="file"]');
//     const slotPlaceholder = targetSlot.querySelector(".upload-placeholder");
//     const slotImg = targetSlot.querySelector(".preview-img");

//     if (i > 0) {
//       // 如果塞入超過一張照片 一般來說一張只能有一格
//       // 但是這個如果他塞多張你就不用點那個多次 一次選多個檔案
//       // 拿出一塊全新的記憶體
//       const dt = new DataTransfer();
//       // 把你現在拿到的照片放進記憶體裡面
//       // file = files[i]; 一次只有一張照片所以一定會拿對照片
//       dt.items.add(file);
//       targetInput.files = dt.files;
//     }

//     const reader = new FileReader();
//     (function (img, placeholder) {
//       // 右邊函數會無腦塞給左邊然後左邊會有自己慢慢執行
//       reader.onload = function (e) {
//         img.src = e.target.result;
//         img.style.display = "block";
//         placeholder.style.display = "none";
//       };
//     })(slotImg, slotPlaceholder);
//     // slotImg 在這個函數裡面叫img slotPlaceholder 在這個函數裡面叫placeholder
//     // 所以傳入參數是在後面 因為函數裡面目前解碼的照片會跟外面的不一樣 所以要做隔離
//     // 所以非同步就是我一直在說的切換開關只要切下去就永遠有效
//     // 同步就是會回彈的按鈕 我只有當下會執行 後續就會自動取消

//     //解碼放下面因為跑太快了
//     reader.readAsDataURL(file);
//   }

//   setTimeout(() => {
//     switchActiveSlot(container, startIndex.toString());
//   }, 100);
// }
// 凡是牽涉到 onload、事件監聽（addEventListener）
// 或是事件代理（document.addEventListener）的邏輯，通通都是「切換開關模式」只要你打開定義了就永遠有效
// 不會隨著時間消失
// 「右邊一直塞給左邊，左邊自己留住」 $\rightarrow$ 叫 閉包（Closure）

// 🚀 4. 點擊大框框重選照片
function triggerActiveInput(e) {
  // 如果點到叉叉按鈕，直接攔截，不觸發選檔案
  if (e.target.closest(".delete-prod-pic-btn")) return;

  const viewport = e.currentTarget;
  const activeInput = viewport.querySelector("#fish-video-input");

  if (activeInput) activeInput.click();
}

// 🚀 5. 大框框的大叉叉：連帶擊殺下方本體
function removeActivePhoto(e) {
  e.stopPropagation(); // 阻止事件冒泡，避免刪除時又觸發選取檔案

  const btn = e.currentTarget;
  const container = btn.closest(".photo-upload-container");

  // 清空實體 input 檔案
  const input = container.querySelector("#fish-video-input");
  if (input) input.value = "";

  const bigVideo = container.querySelector(".viewport-video");
  const bigPlaceholder = container.querySelector(".viewport-placeholder");

  if (bigVideo) {
    bigVideo.pause();
    bigVideo.removeAttribute("src");
    bigVideo.load();
    bigVideo.style.display = "none";
  }

  // 還原外觀：顯示佔位符，隱藏叉叉
  if (bigPlaceholder) bigPlaceholder.style.display = "flex";
  btn.style.display = "none";
}

// 編輯小魚

// 非同步函數，click的全域永久開關
// 外面特別包一層是因為我等html骨架全部都載入完成才可以執行永久的監聽
// 傳統寫法
// document.addEventListener("click", function (e) {
// 程式碼
// });
// 現在
// document.addEventListener("click", (e) => {
//   // 程式碼
// });

document.addEventListener("DOMContentLoaded", () => {
  // 🚀 核心因果修正：改用全域事件代理，直接監聽整個 document
  document.addEventListener("click", (e) => {
    // 🎯 1. 偵測點擊目標：不論新卡片還是舊卡片，只要點擊的對象（或其祖先）包含三個點 class
    const btn = e.target.closest(".fissh-card-menu-dots");
    // 如果btn有被找到，就執行
    if (btn) {
      // 因：使用者點擊了三個點。
      // 果：物理攔截！秒斷所有向上冒泡的電流，絕對不讓外層 <a> 標籤觸發 href="/" 的跳轉！
      e.preventDefault();
      e.stopPropagation();

      const pane = btn.nextElementSibling;
      const isOpen = pane.classList.contains("fissh-show");

      // 我先搜尋全域的fissh-card-menu-pane 然後他css裡面的fissh-show移除這樣代表他就不可以顯示了
      // 我先關掉別的再開我現在有的
      // 那個p是什麼都無所謂 我設定我找到的元素叫做p
      document.querySelectorAll(".fissh-card-menu-pane").forEach((p) => p.classList.remove("fissh-show"));

      // 選單要顯示
      if (!isOpen) {
        pane.classList.add("fissh-show"); // 面板就地顯形
      }
      return; // 阻斷後續邏輯，直接退場
    }

    // 🎯 2. 全局雷達防線：如果點擊的地方跟整個選單結構無關，代表使用者想關閉選單
    // e.target就等於是用戶點擊的那個html實體 然後往上爬找不到html的外殼就執行
    if (!e.target.closest(".fissh-card-menu-wrap")) {
      document.querySelectorAll(".fissh-card-menu-pane").forEach((pane) => {
        pane.classList.remove("fissh-show");
      });
    }
  });
});
// .closest() 的物理規則永遠只有一條：
// 「從起跑點開始，往天花板（往上）爬，沿路檢查有沒有符合的標籤，包含起跑點自己。」
// 3. 獨立功能觸發器：點擊選單選項時執行
function runFisshCardAction(event, action, itemId) {
  // 因為我標籤是a所以要做這個動作
  // 我如果沒有寫後面的非同步動作還是會導致網頁重新更新
  // 因為a原生的關係
  event.preventDefault();
  event.stopPropagation(); // 物理斷電：阻止外層 a 標籤跳轉

  // 其實target也會通 currenttarget是表示你裝函數的地方
  // target表示你點的地方
  const pane = event.currentTarget.closest(".fissh-card-menu-pane");
  //如果有找到就執行
  // 如果有點到我先把表單關起來等一下要顯示其他東西
  if (pane) pane.classList.remove("fissh-show");

  // 🎯 精準定位當前點擊的這張商品卡片本體
  // 因為我同一個網頁會有很多卡片所以我必須用唯一的id去搜尋
  const card = document.getElementById(`product-card-${itemId}`);
  const csrftoken = document.cookie
    .split("; ")
    .find((row) => row.startsWith("csrftoken="))
    ?.split("=")[1];
  //  一開始會像
  // "sessionid=xyz987; theme=dark; csrftoken=abc123def456"
  // 只要看到 "; "切割刀切割
  // ["sessionid=xyz987", "theme=dark", "csrftoken=abc123def456"]
  // 我把所有元素取名叫row 然後我尋找有沒有東西開頭叫做csrftoken=
  // 因為如果第一次來我網頁他會沒有csrf ?的意思是說如果沒有就不要執行了
  // csrftoken=abc123def456 這時我在對等號切一刀 ["csrftoken", "abc123def456"]
  // 因為array裡面的第二個其實就是第1個因為從0開始 然後他[1]
  // 最後存進csrftoken這個變數裡面 鏈式語法

  if (action === "edit") {
    console.log(`[ACTION] 乾淨原生異步流：開始引導編輯 ID: ${itemId}`);

    // 加上變暗的css
    if (card) card.classList.add("fissh-loading");

    // 🎯 核心修正：改用原生 fetch。100% 隔絕 HTMX 與 <a> 標籤的漏電衝突！
    // 這是非同步 AJAX 技術的核心
    // 這個itemid是我早早就從前端傳進來的變數，然後現在就去後端找這個生物
    // 因為我是(get)取得用品 不是刪除或者修改 所以我不需要帶著我的scrf
    // 這個路徑我早早就在url和view已經接好了你只需要寫對就好了
    fetch(`/product/${itemId}/edit/`, {
      method: "GET", // 純淨無瑕的 GET 請求
    })
      // 你送出要求 然後他會給回應res(response)
      .then((res) => {
        console.log(`[後端響應] 狀態碼: ${res.status}`);
        // res只要落在200 到 299之間它就會是true
        // 我抽出裡面html部分然後傳送給後面的東西
        // res.ok是回應包裹的專屬屬性.ok檢查有沒有成功.status看編號.test()看包裹文字
        if (res.ok) {
          // 這個return 他會跳出的就只有這個then，剩下的還會執行
          // 然後這個就是下一個的htmlData
          return res.text();
        }
        // 如果壞掉就會直接跳進去最後面的err
        // 這個throw她跳過的不只是這個if剩下的所有then都會跳過
        // 這個NEW就是創建一個這個ERROR的CLASS
        // 那至個Error就是這個CLASS的名子然後擴號就是傳入的東西
        // 然後NEW就為了要產生一個新的實例
        throw new Error(`後端砸出錯誤碼: ${res.status}`);
      })
      // 下面的then輸入會是上一個丟進來的也就是
      // res.text()的東西在下個then會被叫做htmldata
      .then((htmlData) => {
        // 先找到那個空白頁面
        const modalContainer = document.getElementById("edit-modal-container");
        if (modalContainer) {
          // 他會把前面DIV裡面的東西全部模除然後寫新的上去
          modalContainer.innerHTML = htmlData;
          console.log("[電路全開] 表單灌入完畢，原地喚醒彈窗。");

          // 如果HTMX不是為定義的話！
          // 他會先檢查你有沒有引入HTMX函式庫 然後在執行 如果沒有引入就跳過
          // 如果沒有引入硬要用網站會崩潰
          if (typeof htmx !== "undefined") {
            // 讓HTMX重新檢查一次，目的是要把最新送進來的表單HTML裡面的HTMX接上功能
            htmx.process(modalContainer);
          }

          // 觸發你的開窗 JS
          // 保險機制如果沒有就不要做而已
          // 幹這函數我沒有定義有可能會有問題
          // typeof openEditModal 他會去找OpenEditModal的性質
          // 如果是函數他就會是函數 三個等號為嚴格比較 數值要一樣 性質也要一樣
          // 兩個等號可能會是數值一樣 但性質不一樣
          if (typeof openEditModal === "function") {
            openEditModal();
          }
        }
      })
      // 那個err只是傳入的變數你要取可以
      // catch就是為了抓住錯誤訊息而生的
      // console.error跟一般的console log他們只是顯示形式上的不一樣 顏色格式之類的
      .catch((err) => {
        // 他是傳統的組合 如果要在跟變數交錯你要使用%{}去接住變數
        console.error("[斷路點報錯] 編輯加載慘遭中斷:", err);
        alert("無法讀取商品資料，請檢查後端線路。");
      })
      .finally(() => {
        // 這步驟到後面其實只是卡片關掉 然後生成表單 最後在還原卡片
        // (就算你的表單開起來了卡片也要還原到可以點擊)
        if (card) card.classList.remove("fissh-loading");
      });
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
          // 我先找到下架區
          const inactiveGrid = document.getElementById("inactive-grid");
          // 如果下架區跟卡片我都有找到才執行
          if (card && inactiveGrid) {
            // 我先空生物提醒
            const emptyHint = inactiveGrid.querySelector(".empty-hint");
            // 如果有找到代表他現在是顯示的 然後因為我下架了 所以下面就會有東西
            // 所以空生物提醒就要刪除
            if (emptyHint) emptyHint.remove();

            // APPENDCHILD是在說把CARD移動 然後移動到inactiveGrid裡面
            inactiveGrid.appendChild(card); // 卡片自動滾至下方

            // 動態重寫按鈕線路：改為上架屬性
            // [onclick*="..."]：這是 CSS 的「屬性選擇器」。
            // onclick：代表我要找標籤身上有 onclick 這個屬性的。
            // *="delist" 代表包含delist
            const delistBtn = card.querySelector('[onclick*="delist"]');
            if (delistBtn) {
              // 把<div><div>裡面的文字改變 當然其他標籤也可以
              delistBtn.textContent = "上架商品";

              // 他可以修改HTML的屬性，因為我們如果是非同步我需要到下架區的時候
              // 她下架按鈕馬上變成上架的按鈕我這裡就是她屬性修改然後丟回去給HTML
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
    // 卡片立刻變暗、死鎖
    if (card) card.classList.add("fissh-loading");

    fetch(`/product/${itemId}/relist/`, {
      method: "POST",
      headers: { "X-CSRFToken": csrftoken },
    })
      .then((res) => {
        if (res.ok) {
          // 先尋找上架區
          const activeGrid = document.getElementById("active-grid");
          // 如果卡片跟上架區都有找到
          if (card && activeGrid) {
            // 因為我現在要上架上架如果有空提醒就取消因為我等等要上架了不會為空
            const emptyHint = activeGrid.querySelector(".empty-hint");
            if (emptyHint) emptyHint.remove();
            // 我把卡片移動到到上方
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
        // 這裡都一樣 要讓卡片回亮
        if (card) card.classList.remove("fissh-loading");
      });
  } else if (action === "delete") {
    console.log(`[ACTION] 觸發物理刪除，ID: ${itemId}`);

    // confirm是網頁上預設的提醒如果點擊comfire他會回傳false 但因為你前面有加一個bar 所以他會變回true
    if (!confirm("確定要刪除這商品嗎？此操作無法復原！")) {
      return; // 使用者按取消：電流直接掐斷，什麼都不發生
    }

    // 因：確定要刪，立刻上鎖變暗，防止使用者在傳輸的 0.2 秒內瘋狂連點
    if (card) card.classList.add("fissh-loading");

    // 發射非同步電訊號 這個格式是一定的
    fetch(`/product/${itemId}/delete/`, {
      method: "POST",
      headers: { "X-CSRFToken": csrftoken },
    })
      // 我後端是用action去分類
      // 這裡不用res.text()因為沒有html 你他媽的都刪掉了
      .then((res) => {
        if (res.ok) {
          // 果：資料庫那邊已經燒毀。前端直接下達 remove() 指令
          if (card) {
            // 網頁節點（DOM）當場斷根，不留任何渣滓與排版空隙
            card.remove();
            alert("商品已徹底刪除！");
          }
        } else {
          alert("刪除失敗，請再嘗試一次");
        }
      })
      // 就算前面沒有傳瀏覽器錯誤的時候他也會自己塞
      // 這個的真實性有待考察，因為我把生物刪除再沒有python manage.py runserver的時候他沒有錯誤
      .catch((err) => {
        console.error(err);
      })
      .finally(() => {
        // 安全退場：萬一沒刪成功，至少把卡片解鎖
        if (card) card.classList.remove("fissh-loading");
      });
  }
}
// 後端會寫if的迴圈去看你現在是post還是get殺小的然後去執行她需要做的事情
// POST（新增 / 送交
// GET（讀取 / 查詢
// PUT（全覆蓋修改） 新的全部覆蓋
// PATCH（局部修改） 舊的幫我表留 新的幫我修改
// DELETE（物理抹殺）

// 閉包就是會把函數留下執行完留下的數值留在函數內部，下次執行會繼續累加之類的

// 前端壓縮
// 🚀 1. 核心壓縮引擎：利用 Canvas 將 File 物件在記憶體內轉成輕量 WebP
// 🚀 1. 核心壓縮引擎：利用 Canvas 在記憶體內轉 WebP，因為我水管不夠大 所以我需要還是要先縮小再塞進去
// 可以調整品質
// function compressImageOnFrontend(file, maxWidth = 1200, quality = 0.75) {
//   return new Promise((resolve) => {
//     const reader = new FileReader();
//     reader.readAsDataURL(file);
//     reader.onload = (event) => {
//       const img = new Image();
//       img.src = event.target.result;
//       img.onload = () => {
//         const canvas = document.createElement("canvas");
//         let width = img.width;
//         let height = img.height;

//         // 等比例縮放計算
//         if (width > maxWidth) {
//           height = Math.round(height * (maxWidth / width));
//           width = maxWidth;
//         }

//         canvas.width = width;
//         canvas.height = height;
//         const ctx = canvas.getContext("2d");
//         ctx.drawImage(img, 0, 0, width, height);

//         // 導出 WebP 格式
//         canvas.toBlob(
//           (blob) => {
//             const newFilename = file.name.substring(0, file.name.lastIndexOf(".")) + ".webp";
//             const compressedFile = new File([blob], newFilename, { type: "image/webp" });
//             resolve(compressedFile);
//           },
//           "image/webp",
//           quality,
//         );
//       };
//     };
//   });
// }
// 要了解下面首先你要先知道
// 假如你的JOHN裡面只有定義名子跟歲數 再JAVASCRIPT裡面的物件是動態的 但是JAVA C++不是
// 就算CLASS裡面沒有定義，但你仍然可以賦予未定義的類別一個數值
// const john = new Person('John', 30);
// john.girlfriends = 5; // 幹，合法！John 瞬間有了 5 個女朋友。
// john.isRich = true;   // 又合法！
// 🚀 2. 全局監聽雷達：就地攔截、計算數據、回貼覆蓋
// 如果你使用ASYNC 你在裡面才可以用AWAIT 這是背景壓縮
// 使用者用滑鼠點擊、選取才會觸發 change 本質上是狀態改變
// document.addEventListener("change", async (e) => {
//   // 因為我這個監聽器是建立在全域函數 所以我需要match
//   // 之前query是主動尋找，e.target是被動比對
//   // input[type="file"] 我要尋找input標籤 且 他的type要是file 嚴格比對
//   // onclick*="delist" 這個比較簡單只她要有包含就可以了 然後必須有onclick
//   // ^=  開頭比對 [href^="https"]
//   // $=  結尾比 [src$=".png"]
//   if (e.target.matches('input[type="file"]')) {
//     // 等號右邊是瀏覽器原生的
//     let files = e.target.files;

//     // 如果沒有檔案就執行
//     // 如果本來的input有照片然後他誤點 他知道他誤觸 所以他按下了取消
//     // 但這時候的input還是會清除格子，所以我需要去找舊的壓縮檔回來再次塞回他的input格子裡面
//     // E可以讓我知道現在是誰再發生事情，所以我才可以把監聽器掛在全域
//     if (!files.length) {
//       // 這個在第一次的時候不會被執行，因為動態CLASS尚未被定義
//       // 下面有定義
//       if (e.target._fissh_file_cache) {
//         console.log(`%c[Fissh 記憶防線] 偵測到取消！自動還原快取照片。`, "color: #ff3b30; font-weight: bold;");
//         // DataTransfer() 因為前面有NEW所以他是一個CLASS 然後他是一個剪貼簿用來暫存東西的
//         const backupDataTransfer = new DataTransfer();
//         e.target._fissh_file_cache.forEach((file) => backupDataTransfer.items.add(file));
//         e.target.dataset.isCompressed = "true";
//         e.target.files = backupDataTransfer.files;
//         return;
//       }
//       return;
//     }

//     // 這時侯裡面的還是沒定義所以跳過
//     if (e.target.dataset.isCompressed === "true") {
//       // 要還原狀態，因為下一次修改照片還是要壓縮
//       e.target.dataset.isCompressed = "false";
//       return;
//     }

//     console.log(`%c[Fissh 壓縮雷達] 偵測到新照片，開始就地攔截壓縮...`, "color: #00caef; font-weight: bold;");
//     // 一個剪貼簿
//     const dataTransfer = new DataTransfer();
//     // 先定義一個矩陣然後後面丟東西進去
//     const cacheArray = [];

//     // 循環壓鎖 然後塞續我的剪貼簿裡面
//     for (let i = 0; i < files.length; i++) {
//       const file = files[i];

//       // ADD 跟 PUSH其實差不多 但因為要ARRAY所以用PUSH 然後cacheArray只能用ADD
//       if (file.type.startsWith("image/")) {
//         // await會等後面的東西弄完再給值，不然壓縮太慢網頁會自動跳過
//         // 再加上async可以多思緒 他可以同步處理現場跟後端的東西
//         const compressed = await compressImageOnFrontend(file);
//         dataTransfer.items.add(compressed);
//         cacheArray.push(compressed);
//       } else {
//         dataTransfer.items.add(file);
//         cacheArray.push(file);
//       }
//     }

//     // 💾 寫入快取
//     e.target._fissh_file_cache = cacheArray;
//     e.target.dataset.isCompressed = "true";
//     // 因為e.target.files它只接受 FileList 所以我datatransfer要加file
//     e.target.files = dataTransfer.files;

//     // 手動創造一個change事件 因為我剛剛用js修改檔案 但瀏覽器不知道檔案已經變了
//     // 如果瀏覽器不知道 那預覽的照片就不會改變
//     // bubbles: true這個狀態改變的尋號會向上傳遞 會讓所有的什麼照片預覽阿沙小阿都更新
//     e.target.dispatchEvent(new Event("change", { bubbles: true }));
//   }
// });

// 上傳小魚的網址
// document.addEventListener("DOMContentLoaded", () => {
//   // 先找到批量上傳的表單
//   const batchForm = document.getElementById("batchUploadForm");

//   if (batchForm) {
//     batchForm.addEventListener("submit", async (e) => {
//       // 取消a的自動跳轉
//       e.preventDefault();
//       e.stopPropagation();

//       // 找一下名子這裡有疑慮因為後面都是兩個一起找
//       const allNameInputs = batchForm.querySelectorAll('input[name="fish_name[]"] , input[name="fish_name"]');
//       const filledIndices = [];
//       // 陣列.forEach((當前物件, 當前索引值, 整個陣列) => { ... })，你如果沒有寫就是不在乎
//       // 我需要前後順序是因為我要資料對齊
//       allNameInputs.forEach((input, index) => {
//         // 輸入框要有東西 然後東西不能是空格 trim()是切出字串開頭跟結尾的空格
//         if (input.value && input.value.trim() !== "") {
//           // 因為他是矩陣的關係所以要用push
//           filledIndices.push(index);
//         }
//       });
//       // 因為我的htmx攔截了所以辦法顯示下面的東西
//       // 看一下我總共一次上傳多少的物件
//       const totalFilled = filledIndices.length;
//       if (totalFilled === 0) {
//         alert("請至少填寫一隻小魚的名字！");
//         return;
//       }
//       // 先定義我要多少為一組
//       const CHUNK_SIZE = 4;
//       // 餅乾重複了
//       const csrftoken = document.cookie
//         .split("; ")
//         .find((row) => row.startsWith("csrftoken="))
//         ?.split("=")[1];

//       // 我修尋button元素然後裡面要有type="submit"的標籤
//       const submitBtn = batchForm.querySelector('button[type="submit"]');

//       // 🔒 進入傳輸狀態：按鈕當場死鎖，防止使用者暴怒連點
//       if (submitBtn) {
//         submitBtn.disabled = true;
//         submitBtn.style.opacity = "0.6";
//         // 這是讓他不能點的關鍵
//         submitBtn.style.cursor = "not-allowed";
//       }

//       // 2. 開始切片發送
//       for (let i = 0; i < totalFilled; i += CHUNK_SIZE) {
//         // 🎯 核心進度回饋：因：進入當前組別發送。果：把進度直接洗在按鈕文字上，讓使用者安心
//         if (submitBtn) {
//           // 這個是在兩個數值中取小的給currentEnd
//           const currentEnd = Math.min(i + CHUNK_SIZE, totalFilled);
//           // 再submit裡面塞入文字 例如我第一輪他會顯示1 到
//           // currentend 因為我後面的那個總數跟區塊會取最小值所以3隻的時候也會顯示3隻
//           submitBtn.innerHTML = `正在上傳第 ${i + 1} ~ ${currentEnd} 隻小魚 (總共 ${totalFilled} 隻)，請勿關閉網頁...`;
//         }
//         // 會需要兩個臨時的剪貼簿是因為一台是小臺車(最多4個)
//         // 一台是大台的(最多20個)
//         const chunkFormData = new FormData();
//         const globalKeys = [
//           "global_spec",
//           "global_notice",
//           "content",
//           "生物種類",
//           "pH值_min",
//           "pH值_max",
//           "適宜溫度_min",
//           "適宜溫度_max",
//           "體長(cm)",
//           "建議水量(L)",
//           "GH硬度",
//           "KH硬度",
//           "性情",
//           "食性",
//           "比重",
//           "水流強度",
//           "光照需求",
//         ];

//         // 你如果需要同時傳送照片跟文字你不能用json，妳要用formdata打包資料
//         // 因為是class所以叫一台新的貨車過來
//         // 他會提取每個的name當作key 然後value當作value
//         // 如果一個name有多個value那這個value就會變成矩陣
//         const mainFormData = new FormData(batchForm);
//         // 對每一筆資料做過濾
//         globalKeys.forEach((key) => {
//           // 檢查這個 key 是否真的存在於 mainFormData 中
//           if (mainFormData.has(key)) {
//             chunkFormData.append(key, mainFormData.get(key));
//           } else {
//             // 如果標籤根本不存在，就把這個消失的 key 印出來
//             console.warn(`[偵錯警報] 在表單中找不到名為 "${key}" 的標籤，請檢查 HTML！`);
//           }
//         });
//         // FormData.append("key", "value") 整理資料
//         // document.appendChild(element) 搬運html
//         // 如果有空個小魚他就會切掉
//         // 你寫下原本大資料裡面的東西然後裝入小資料庫
//         const chunkIndices = filledIndices.slice(i, i + CHUNK_SIZE);
//         // 網頁上的絕對座標(可能不是1234 可能是5678)跟相對座標(1234)
//         chunkIndices.forEach((globalIndex, localIndex) => {
//           // 這就是矩陣輸入取變數位子出來而已我抽出value
//           const nameVal = allNameInputs[globalIndex].value;
//           // 最後面是鏈式語法 如果沒有找到globalIndex就跳出，
//           // 然後後面的話數值跟沒填選一個數入，例如如果是空白鍵他就會數入0
//           const priceVal = batchForm.querySelectorAll('[name^="fish_price"]')[globalIndex]?.value || "0";
//           const specVal = batchForm.querySelectorAll('[name^="fish_spec"]')[globalIndex]?.value || "";
//           const noticeVal = batchForm.querySelectorAll('[name^="fish_notice"]')[globalIndex]?.value || "";

//           // 所以我上面先把他數值找出來 然後在把他填入小貨車裡面
//           chunkFormData.append("fish_name[]", nameVal);
//           chunkFormData.append("fish_price[]", priceVal);
//           chunkFormData.append("fish_spec[]", specVal);
//           chunkFormData.append("fish_notice[]", noticeVal);

//           // 然後我就可以準備一下處理下一隻魚
//           const localSlotNum = localIndex + 1;
//           const globalSlotNum = globalIndex + 1;
//           // 他能精準抓出實體的那個魚的檔案然後塞入變數
//           const fileInput = batchForm.querySelector(`input[name="fish_image_${globalSlotNum}[]"], input[name="fish_image_${globalSlotNum}"]`);
//           // 我必須要有找到檔案 然後檔案要有東西才可以執行
//           if (fileInput && fileInput.files.length > 0) {
//             // 就算你只塞入一張照片也會變成filelist
//             // 我先抓出fileInput.files的第file個 然後裝車
//             for (let file of fileInput.files) {
//               // 我的file變成物件依序塞進去小資料庫裏面
//               chunkFormData.append(`fish_image_${localSlotNum}[]`, file);
//             }
//           }
//         });
//         // A.append(B, C) 命令a打開然後貼上標籤 把c丟進去
//         // const他是一個不可以改變的變數，只要定義了就不可以修改
//         // let就是可以替換的變數 因為for迴圈每一圈東西都不一樣所以要用他

//         //所以fetch其實是兩個動作 我把東西送出 並解等待回覆
//         try {
//           // 請等待等到fetch送出且收到貨才能繼續執行
//           // 左邊的batchForm.action會去看你的html上面有沒有action="/upload/" 這樣的目的地
//           // 如果沒有他就會去看「現在這個網頁的網址」然後直接送出
//           // fetch(位子，內容)
//           const response = await fetch(batchForm.action || window.location.href, {
//             method: "POST",
//             body: chunkFormData,
//             headers: { "X-CSRFToken": csrftoken },
//           });
//           // 如果回傳是ok的話
//           if (response.ok) {
//             // 我先把文字切下來給const 回來的目前還是txt我不能對txt做元素搜尋
//             const htmlResult = await response.text();
//             // 先創建一個解析器：parser是解析的意思
//             const parser = new DOMParser();
//             // 這裡的parse form string是從文字解析 請你用html解析這段text
//             const doc = parser.parseFromString(htmlResult, "text/html");
//             // 這裡的for不會執行兩次因為是<script></script>一組算一個
//             // 從doc裡面抓出script
//             // 然後每個script執行一次 所以他如果有其他非script標籤都會被忽略
//             doc.querySelectorAll("script").forEach((oldScript) => {
//               const newScript = document.createElement("script");
//               // 這裡的textContent很重要 因為他只令內部的文字相同外殼不會覆蓋過去
//               // 所以我上面的創建script元素才有用
//               newScript.textContent = oldScript.textContent;
//               document.body.appendChild(newScript); //把新的程式送進去網頁最下面
//               newScript.remove(); //最後清除我的變數下次要使用
//             });
//           }
//         } catch (err) {
//           console.error("傳輸中斷:", err);
//         }
//         // 我建立一個承諾物件
//         // 再reslove裡面藏著現在資料的處理進度
//         // 然後promise會看reslove裡面的東西放行
//         // 如果看到pending他會繼續等
//         // 如果Fulfilled 就會等待已完成就會往下走

//         await new Promise((resolve) => setTimeout(resolve, 500));
//       }

//       // 還原按鈕原本的文字
//       if (submitBtn) {
//         submitBtn.disabled = false;
//         submitBtn.style.opacity = "1";
//         submitBtn.style.cursor = "pointer";
//         submitBtn.innerHTML = "批次上架商品";
//       }

//       // 1. 清空數值
//       batchForm.reset();

//       // 2. 表單清空邏輯：還原照片預覽框
//       batchForm.querySelectorAll(".preview-img").forEach((img) => {
//         img.src = "";
//         img.style.display = "none";
//       });
//       // 我要把內部的小魚名子都清空
//       batchForm.querySelectorAll(".upload-placeholder").forEach((p) => {
//         p.style.display = "";
//       });
//       batchForm.querySelectorAll(".delete-prod-pic-btn").forEach((btn) => {
//         btn.style.display = "none";
//       });

//       // 🎯 最終一擊：在這裡才跳出總結彈窗，通知使用者大功告成！
//       alert(`總共 ${totalFilled} 隻商品已全部順利分批上架完畢！`);
//       console.log("%c[Fissh 保險安全線] 任務完美結束。", "color: #55bb00; font-weight: bold;");
//     });
//   }
// });

// 我發現我沒有初始化過我的快取 所以這跟上面是一對的 上面初始化的是其他東西
document.addEventListener("reset", (e) => {
  // 因：當任何表單執行 reset() 時（包含你那 200 行後端成功回傳後執行的 singleForm.reset()）
  // 過：撈出該表單內所有的檔案上傳欄位
  const fileInputs = e.target.querySelectorAll('input[type="file"]');

  fileInputs.forEach((input) => {
    // 果：無情抹除快取變數，徹底斷開記憶體連結，確保下一隻魚上傳時是純淨的真空狀態
    delete input._fissh_file_cache;
    input.dataset.isCompressed = "false";
    console.log(`%c[Fissh 記憶防線] 表單重設成功！已物理銷毀欄位 [${input.name}] 的圖片快取。`, "color: #ff9f00;");
  });
});

// 編輯表單切換邏輯
// function initTemplateState() {
//   const groups = document.querySelectorAll(".template-group");

//   groups.forEach((group, index) => {
//     const select = group.querySelector("select");
//     const buttons = group.querySelectorAll(".mini-tab");
//     if (!select || buttons.length < 2) return;

//     // 判定狀態：select 有值 = 引用模式 (on)，沒值 = 關閉模式 (off)
//     const hasValue = select.value && select.value.trim() !== "";

//     // 核心邏輯：根據 index 決定預設行為
//     let targetBtn;
//     let fieldName;

//     if (index === 0) {
//       // 規格範本：強制預設關閉 (關閉按鈕是 buttons[0])
//       targetBtn = buttons[0];
//       fieldName = "fish_spec";
//     } else {
//       // 提醒範本：有資料則引用 (buttons[1])，無資料則關閉 (buttons[0])
//       targetBtn = hasValue ? buttons[1] : buttons[0];
//       fieldName = "fish_notice";
//     }

//     // 觸發切換
//     const state = targetBtn.innerText.trim() === "引用" ? "on" : "off";

//     // 重要：只有在目前 active 狀態與目標不一致時才觸發，避免閃爍
//     if (!targetBtn.classList.contains("active")) {
//       toggleTemplate(targetBtn, state, fieldName);
//     }
//   });
// }

// 編輯表單收起來
document.body.addEventListener("htmx:afterSwap", (event) => {
  // 因：判斷這次完工的對象，是不是我們的小魚卡片？
  if (event.detail.target.id.startsWith("product-card-")) {
    // 果 1：呼叫你原本的關閉函數 (處理隱藏、動畫等)
    if (typeof closeEditModal === "function") {
      closeEditModal();
    }

    // 果 2：物理洗白！把容器裡的 HTML 徹底挖空
    // 這樣表單的舊資料就會跟著容器一起灰飛煙滅，完美達成「清空」
    const modalContainer = document.getElementById("edit-modal-container");
    if (modalContainer) {
      modalContainer.innerHTML = "";
    }

    console.log("✅ HTMX 替換成功：編輯彈窗已自動收起並物理清空！");
  }
});

// 🚀 監聽 HTMX 請求完成的廣播 (專門負責單獨新增表單的清空)
document.body.addEventListener("htmx:afterRequest", function (event) {
  // 因：判斷 1. 這次請求是否成功？ 2. 發起請求的是不是「單獨新增表單」？
  if (event.detail.successful && event.detail.elt.id === "singleUploadForm") {
    const form = event.detail.elt;

    // 果 1：觸發表單原生 reset！
    // (這會完美觸發你寫好的 document.addEventListener("reset")，把圖片快取徹底銷毀)
    form.reset();

    // 果 2：物理還原自訂的照片預覽 UI
    form.querySelectorAll(".preview-img").forEach((img) => {
      img.src = "";
      img.style.display = "none";
    });
    form.querySelectorAll(".upload-placeholder").forEach((p) => {
      p.style.display = ""; // 恢復顯示「+」號或上傳文字
    });
    // 這裡要注意：用逗號選取器同時抓兩種叉叉按鈕
    form.querySelectorAll(".delete-prod-pic-btn, .b-delete-prod-pic-btn").forEach((btn) => {
      btn.style.display = "none"; // 把叉叉隱藏
    });

    console.log("✅ 單獨新增表單已送出，並自動物理清空完畢！");
  }
});

// 🚀 1. 影片上傳的處理函數
