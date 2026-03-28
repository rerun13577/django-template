import os
from io import BytesIO

import requests
from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image


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
    if uploaded_image.size <= threshold_kb * 1024:
        return uploaded_image
    img = Image.open(uploaded_image)
    max_width = 1200
    if img.width > max_width:
        img = img.resize(
            (max_width, int(img.height * (max_width / img.width))), Image.LANCZOS
        )
    if img.mode != "RGB":
        img = img.convert("RGB")
    output = BytesIO()
    img.save(output, format="WEBP", quality=80)
    output.seek(0)
    new_filename = f"{uploaded_image.name.rsplit('.', 1)[0]}.webp"
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
