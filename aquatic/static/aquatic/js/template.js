// 加上 window. 強制掛在全域，並加上 log 測電
window.openEditModal = function () {
  console.log("⚡ 開窗電路接通！準備呼叫 CSS 顯示...");
  const modal = document.getElementById("edit-modal-container");
  if (modal) {
    modal.classList.add("show");
    document.body.style.overflow = "hidden"; // 鎖住背景滾動
    console.log("✅ 成功加上 .show class！");
  } else {
    console.error("❌ 慘了，畫面上找不到 #edit-modal-container 空殼！");
  }
};

// 負責接收 HTML 按鈕傳來的 4 個包裹
window.openEditForm = function (id, title, content, btnElement) {
  console.log(`⚡ 準備編輯卡片 ID: ${id}`);

  // 1. 抓出這張卡片的最外層容器 (用來告訴 uiShowForm 要取代誰)
  const itemCard = btnElement.closest(".accordion-item");

  // 2. 抓出你準備好的編輯表單實體 (請確認你的表單 ID 叫什麼，這裡假設是 add-notice-form)
  const formContainer = document.getElementById("add-notice-form");

  if (!formContainer) {
    console.error("❌ 找不到表單 #add-notice-form！");
    return;
  }

  // 3. 物理填入舊資料
  const idInput = formContainer.querySelector("#editTempId");
  const titleInput = formContainer.querySelector("#newNoticeTitle");
  const contentInput = formContainer.querySelector("#newNoticeContent");

  if (idInput) idInput.value = id;
  if (titleInput) titleInput.value = title;
  if (contentInput) contentInput.value = content;

  // 4. 呼叫你之前寫好的「表單替換與動畫」引擎
  if (typeof window.uiShowForm === "function") {
    window.uiShowForm(itemCard, formContainer);
  } else {
    console.error("❌ 找不到 uiShowForm 引擎！");
  }
};

function closeEditModal() {
  const modal = document.getElementById("edit-modal-container");
  if (modal) {
    modal.classList.remove("show");
    document.body.style.overflow = ""; // 解除背景鎖定

    // 物理超渡：等關窗動畫播完後，燒毀 HTML 渣滓
    setTimeout(() => {
      modal.innerHTML = "";
    }, 200);
  }
}

// 監聽後端傳來的 HX-Trigger 訊號
document.body.addEventListener("closeEditModal", function () {
  console.log("⚡ 接收到後端成功訊號，自動關閉彈窗！");
  if (typeof closeEditModal === "function") {
    closeEditModal();
  }
});
