const MAX_VIDEO_SIZE = 20 * 1024 * 1024;

/**
 * 取得影片上傳區內的元素。
 */
function getVideoElements(root) {
  return {
    input: root.querySelector("#fish-video-input"),
    video: root.querySelector(".viewport-video"),
    placeholder: root.querySelector(".viewport-placeholder"),
    deleteButton: root.querySelector(".delete-prod-pic-btn"),
  };
}

/**
 * 釋放瀏覽器為影片預覽建立的暫存 URL。
 */
function releaseVideoObjectUrl(video) {
  const objectUrl = video?.dataset.objectUrl;

  if (objectUrl) {
    URL.revokeObjectURL(objectUrl);
    delete video.dataset.objectUrl;
  }
}

/**
 * 點擊影片區時，觸發隱藏的 file input。
 */
function triggerActiveInput(event) {
  if (event.target.closest(".delete-prod-pic-btn")) {
    return;
  }

  const input = event.currentTarget.querySelector("#fish-video-input");
  input?.click();
}

/**
 * 選擇影片後顯示預覽。
 */
function handleVideoUpload(input) {
  const file = input.files?.[0];

  if (!file) {
    return;
  }

  if (file.size > MAX_VIDEO_SIZE) {
    alert("影片請限制在 20MB 以內。");
    input.value = "";
    return;
  }

  const uploadBox = input.closest(".custom-upload-box");

  if (!uploadBox) {
    return;
  }

  const { video, placeholder, deleteButton } = getVideoElements(uploadBox);

  if (!video) {
    return;
  }

  // 避免重複選擇影片時，舊的 Object URL 留在記憶體。
  releaseVideoObjectUrl(video);

  const objectUrl = URL.createObjectURL(file);

  video.dataset.objectUrl = objectUrl;
  video.src = objectUrl;
  video.style.display = "block";

  placeholder?.style.setProperty("display", "none", "important");
  deleteButton?.style.setProperty("display", "flex", "important");

  video.play().catch(() => {
    // 瀏覽器禁止自動播放時不影響上傳。
  });
}

/**
 * 清除影片 input 與預覽。
 */
function resetVideoUpload(root) {
  const { input, video, placeholder, deleteButton } = getVideoElements(root);

  if (input) {
    input.value = "";
  }

  if (video) {
    video.pause();
    releaseVideoObjectUrl(video);
    video.removeAttribute("src");
    video.load();
    video.style.display = "none";
  }

  placeholder?.style.setProperty("display", "flex", "important");
  deleteButton?.style.setProperty("display", "none", "important");
}

/**
 * 點擊叉叉移除已選影片。
 *
 * 函數名稱暫時保留 removeActivePhoto，
 * 避免你還要同步修改現有 HTML onclick。
 */
function removeActivePhoto(event) {
  event.preventDefault();
  event.stopPropagation();

  const uploadBox = event.currentTarget.closest(".custom-upload-box");

  if (uploadBox) {
    resetVideoUpload(uploadBox);
  }
}

/**
 * 顯示目前選擇的封面檔名。
 */
function updateCoverFilename(input) {
  const form = input.closest("form");
  const display = form?.querySelector("#cover-filename-display");

  if (!display) {
    return;
  }

  const file = input.files?.[0];

  if (file) {
    display.textContent = file.name;
    display.style.color = "var(--primary)";
  } else {
    display.textContent = "尚未選擇封面檔案";
    display.style.color = "var(--secondary)";
  }
}

/**
 * 成功上架後，清空整個新增商品表單及媒體預覽。
 */
function resetSingleUploadForm(form) {
  form.reset();

  form.querySelectorAll("textarea.input-content-area").forEach((textarea) => {
    textarea.style.height = "auto";
  });

  const coverDisplay = form.querySelector("#cover-filename-display");

  if (coverDisplay) {
    coverDisplay.textContent = "尚未選擇封面檔案";
    coverDisplay.style.color = "var(--secondary)";
  }

  const uploadBox = form.querySelector(".custom-upload-box");

  if (uploadBox) {
    resetVideoUpload(uploadBox);
  }
}

/**
 * 只在 singleUploadForm 成功送出後重置。
 * 不再影響其他 HTMX 請求。
 */
document.body.addEventListener("htmx:afterRequest", (event) => {
  if (!event.detail.successful) {
    return;
  }

  const requestElement = event.detail.elt;

  const form = requestElement?.id === "singleUploadForm" ? requestElement : requestElement?.closest?.("#singleUploadForm");

  if (!form) {
    return;
  }

  resetSingleUploadForm(form);
});
