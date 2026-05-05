function openNoticeEdit(id, title, content, btn) {
  const item = btn.closest(".accordion-item");
  const form = document.getElementById("add-notice-form");

  // 1. 呼叫通用的 UI 動畫
  uiShowForm(item, form);

  // 2. 處理自己特有的資料填寫 (只要填兩格)
  document.getElementById("editTempId").value = id;
  document.getElementById("newNoticeTitle").value = title;
  document.getElementById("newNoticeContent").value = content;
}

function openEditNotice(id, title, content, btn) {
  const item = btn.closest(".accordion-item");
  const form = document.getElementById("add-notice-form");

  // 呼叫 manage.js 的顯示邏輯 (如果有寫通用 uiShowForm 的話)
  // 這裡暫時手動處理資料回填
  document.getElementById("editTempId").value = id;
  document.getElementById("newNoticeTitle").value = title;
  document.getElementById("newNoticeContent").value = content;

  // 觸發顯示
  toggleForm("add-notice-form");
}

// 🚀 購物須知：編輯按鈕點擊
window.openEditForm = function (id, title, content, btn) {
  const item = btn.closest(".accordion-item");
  const form = document.getElementById("add-notice-form");

  if (!form) return console.error("❌ 找不到新增範本的表單 ID");

  // 1. 先把資料填進表單
  document.getElementById("editTempId").value = id;
  document.getElementById("newNoticeTitle").value = title;
  document.getElementById("newNoticeContent").value = content;

  // 2. 呼叫你寫好的通用動畫
  uiShowForm(item, form);
};
