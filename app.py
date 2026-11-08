import streamlit as st
from PIL import Image, ImageFilter
import requests
import io
import numpy as np

def filter_vintage(img):
    arr = np.array(img, dtype=np.float32)
    arr[:, :, 0] = np.clip(arr[:, :, 0] * 1.1 + 20, 0, 255)
    arr[:, :, 1] = np.clip(arr[:, :, 1] * 0.9 + 10, 0, 255)  
    arr[:, :, 2] = np.clip(arr[:, :, 2] * 0.75,      0, 255)  
    return Image.fromarray(arr.astype(np.uint8))

def filter_bw(img):
    return img.convert("L").convert("RGB")  

def filter_cinema(img):
    arr = np.array(img, dtype=np.float32)
    arr[:, :, 0] = np.clip(arr[:, :, 0] * 0.9,  0, 255)  
    arr[:, :, 2] = np.clip(arr[:, :, 2] * 1.15, 0, 255)  
    bar = int(arr.shape[0] * 0.08)                      
    arr[:bar, :, :] = 0
    arr[-bar:, :, :] = 0
    return Image.fromarray(arr.astype(np.uint8))

def filter_warm(img):
    arr = np.array(img, dtype=np.float32)
    arr[:, :, 0] = np.clip(arr[:, :, 0] + 40, 0, 255)  
    arr[:, :, 2] = np.clip(arr[:, :, 2] - 40, 0, 255)  
    return Image.fromarray(arr.astype(np.uint8))

def filter_sharp(img):
    return img.filter(ImageFilter.SHARPEN)  

FILTERS = {
    "بدون ":       None,
    "Vintage ":    filter_vintage,
    "أبيض وأسود ": filter_bw,
    "Cinema ":     filter_cinema,
    "دافئ ":       filter_warm,
    "حاد ":        filter_sharp,
}
# ──────────────────────────────

st.title(" ضع نفسك في أي مكان!")
 
api_key = st.text_input(" أدخل API Key من remove.bg:", type="password")
 
person_file = st.file_uploader("اختر صورة الشخص", type=["png", "jpg"])
bg_file = st.file_uploader("اختر صورة المكان (تركيا، باريس...)", type=["png", "jpg"])
 
if person_file and bg_file and api_key:
    person_img = Image.open(person_file).convert("RGBA")
    bg_img = Image.open(bg_file).convert("RGBA")
 
    st.subheader("الصور الأصلية")
    col1, col2 = st.columns(2)
    col1.image(person_img, caption="الشخص")
    col2.image(bg_img, caption="المكان")
 
    with st.spinner(" جاري إزالة الخلفية..."):
        person_file.seek(0)
        response = requests.post(
            "https://api.remove.bg/v1.0/removebg",
            files={"image_file": person_file},
            data={"size": "auto"},
            headers={"X-Api-Key": api_key},
        )
 
    if response.status_code == 200:
        person_no_bg = Image.open(io.BytesIO(response.content)).convert("RGBA")
 
        st.subheader(" ضبط الحجم والموضع")
        scale = st.slider("حجم الشخص", 10, 100, 50)
        pos_x = st.slider("الموضع أفقي", 0, 100, 50)
        pos_y = st.slider("الموضع عمودي", 0, 100, 70)
 
        bg_w, bg_h = bg_img.size
        new_h = int(bg_h * scale / 100)
        ratio = new_h / person_no_bg.size[1]
        new_w = int(person_no_bg.size[0] * ratio)
        person_resized = person_no_bg.resize((new_w, new_h), Image.LANCZOS)
 
        x = int((bg_w - new_w) * pos_x / 100)
        y = int((bg_h - new_h) * pos_y / 100)
 
        result = bg_img.copy()
        result.paste(person_resized, (x, y), person_resized)

        st.subheader(" اختر فلتراً")
        choice = st.radio("", list(FILTERS.keys()), horizontal=True)
        filtered = result.convert("RGB")
        if FILTERS[choice]:
            filtered = FILTERS[choice](filtered)
 
        st.subheader("الصورة الناتجة")
        st.image(filtered)
 
        buf = io.BytesIO()
        result.convert("RGB").save(buf, format="PNG")
        buf.seek(0)
        st.download_button(" تحميل الصورة", buf, file_name="result.png", mime="image/png")
    else:
        st.error(f" خطأ: {response.status_code} - تأكد من صحة الـ API Key")
 
elif person_file and bg_file and not api_key:
    st.warning(" أدخل الـ API Key أولاً!")
