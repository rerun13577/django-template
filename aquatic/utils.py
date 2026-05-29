import os
from io import BytesIO

import requests
from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image, ImageOps

# 🚀 加上這兩行，讓 Pillow 瞬間學會看懂 HEIC
from pillow_heif import register_heif_opener

register_heif_opener()


def purge_cloudflare_cache(url_list):
    ZONE_ID = os.getenv("CF_ZONE_ID")
    API_TOKEN = os.getenv("CF_API_TOKEN")
    if not ZONE_ID or not API_TOKEN:
        return
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json",
    }
    try:
        requests.post(
            f"https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/purge_cache",
            headers=headers,
            json={"files": url_list},
        )
    except Exception as e:
        print(f"⚠️ [API 異常]：{e}")


def compress_image(uploaded_image, threshold_kb=500):
    print(
        f"\n[轉檔雷達] 📥 收到圖片: {uploaded_image.name}, 大小: {uploaded_image.size / 1024:.2f} KB"
    )

    # 🎯 物理防線 1：檢查是不是 HEIC 家族
    is_heic = uploaded_image.name.lower().endswith((".heic", ".heif"))
    if is_heic:
        print("[轉檔雷達] 🚨 偵測到 HEIC 格式，無視大小，準備強制絞肉轉檔！")

    # 🎯 物理防線 2：如果檔案小於 500KB，且「不是 HEIC」，才可以直接退回原檔
    if uploaded_image.size <= threshold_kb * 1024 and not is_heic:
        print(
            f"[轉檔雷達] ✅ 安全放行：檔案小於 {threshold_kb}KB 且非 HEIC，不壓縮直接退回原檔。"
        )
        return uploaded_image

    # 如果是 HEIC，或者檔案大於 500KB，就強迫進入轉檔器
    print("[轉檔雷達] ⚙️ 進入轉檔/壓縮程序...")
    try:
        img = Image.open(uploaded_image)
    except Exception as e:
        print(f"[轉檔雷達] ❌ 致命錯誤：Image.open 無法開啟檔案！原因: {e}")
        raise e  # 發生錯誤直接報出來，不要吞掉

    # 🚀 救命補丁：iPhone 照片自帶方向標籤，轉檔容易倒轉，這行能幫你強制轉正
    img = ImageOps.exif_transpose(img)
    print(f"[轉檔雷達] 🔄 EXIF 方向校正完成，原始尺寸: {img.width}x{img.height}")

    max_width = 1200
    if img.width > max_width:
        new_height = int(img.height * (max_width / img.width))
        print(
            f"[轉檔雷達] 📏 寬度 {img.width} 超過限制，開始縮放為 {max_width}x{new_height}"
        )
        img = img.resize((max_width, new_height), Image.LANCZOS)

    if img.mode != "RGB":
        print(f"[轉檔雷達] 🎨 偵測到非標準顏色模式 ({img.mode})，強制轉換為 RGB")
        img = img.convert("RGB")

    output = BytesIO()
    try:
        img.save(output, format="WEBP", quality=80)
    except Exception as e:
        print(f"[轉檔雷達] ❌ 致命錯誤：無法儲存為 WEBP！原因: {e}")
        raise e

    output.seek(0)
    new_filename = f"{uploaded_image.name.rsplit('.', 1)[0]}.webp"
    final_size_kb = output.getbuffer().nbytes / 1024

    print(
        f"[轉檔雷達] 💾 轉檔成功！新檔名: {new_filename}, 新大小: {final_size_kb:.2f} KB\n"
    )

    return InMemoryUploadedFile(
        output,
        "ImageField",
        new_filename,
        "image/webp",
        output.getbuffer().nbytes,
        None,
    )


def handle_model_image_upload(instance, field_name, threshold_kb=500):
    image_field = getattr(instance, field_name)
    if image_field:
        from django.core.files.uploadedfile import UploadedFile

        if hasattr(image_field, "file") and isinstance(image_field.file, UploadedFile):
            try:
                compressed_file = compress_image(image_field, threshold_kb=threshold_kb)
                setattr(instance, field_name, compressed_file)
            except Exception as e:
                print(f"❌ 壓縮失敗: {e}")
