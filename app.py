import streamlit as st
from PIL import Image , ImageFilter
import numpy as np
import io
import requests as r


st.title("image app")

api_key = st.text_input("Enter your API from remove.bg")

imagefile = st.file_uploader("upload file",type= ["png","jpg","jpeg"])

bg_file = st.file_uploader("choose the place", type=['png' ,'jpg' , ])

def filter_vintage (image):
    arr = np.array (image,dtype=np.float32)
    arr[:, :, 0] = np.clip(arr[:, :, 0]*1.1+20, 0,255)
    arr[:, :, 1] = np.clip(arr[:, :, 1]*0.9+10, 0,255)
    arr[:, :, 2] = np.clip(arr[:, :, 2]*0.75 , 0,255)
    return Image.fromarray(arr.astype(np.uint8))

def filter_cinema (image): 
    arr = np.array (image,dtype=np.float32)
    arr[:, :, 0] = np.clip(arr[:, :, 0]*0.9, 0, 255)
    arr[:, :, 1] = np.clip(arr[:, :, 1]*1.0, 0, 255)
    arr[:, :, 2] = np.clip(arr[:, :, 2]*1.15,0, 255)
    return Image.fromarray(arr.astype(np.uint8))

def filter_warm (image):
    arr = np.array (image,dtype=np.float32)
    arr[:, :, 0] = np.clip(arr[:, :, 0]+ 40, 0, 255)
    arr[:, :, 1] = np.clip(arr[:, :, 1]+ 10, 0, 255 )
    arr[:, :, 2] = np.clip(arr[:,:,2]-  40, 0, 255 )
    return Image.fromarray(arr.astype(np.uint8))
    
    
def filter_bw(img):
    return img.convert('L').convert ("RGB")
def filter_sharp(img):
    return img.filter(ImageFilter.SHARPEN)

filters = {
"NO filters" : None,
"vintage" : filter_vintage,
"black&white" : filter_bw,
"sharp" : filter_sharp,
"cinema" : filter_cinema,
"warm" : filter_warm
}

if imagefile and bg_file and api_key:
    img = Image.open(imagefile).convert("RGBA")
    bg_img = Image.open(bg_file).convert("RGBA")

    st.write("the orignal image")
    col1 , col2 = st.columns(2)
    col1.image(img)
    col2.image(bg_img)

    with st.spinner("removing bg......"):
        imagefile.seek(0)
        response = r.post(
        "https://api.remove.bg/v1.0/removebg" , 
        files={"image_file": imagefile },
        data={"size" : "atuo"},
        headers={"X-API-key" : api_key})


    if response.status_code == 200:
        person_no_bg = Image.open(io.BytesIO(response.content)).convert("RGBA")


        st.subheader("Scale and Position")
        scale = st.slider("Person Scale", 10, 100, 50)
        pos_x = st.slider("Position X", 0, 100, 50)
        pos_y = st.slider("Position Y", 0, 100, 50)

        bg_w, bg_h = bg_img.size
        new_h = int(bg_h * scale / 100)
        ratio = new_h / person_no_bg.size[1]
        new_w = int(person_no_bg.size[0] * ratio)

        person_resized = person_no_bg.resize((new_w, new_h), Image.LANCZOS)

        x = int((bg_w - new_w)) * pos_x / 100
        y = int((bg_h - new_h)) * pos_y / 100

        result = bg_img.copy()   
        result.paste(person_resized , (y,x) , person_resized)


        
        st.subheader('choose filter')
        choice = st.radio('', list(filters.keys()))
        filtered = result.convert("RGB")

        if filters[choice]:
            filtered = filters[choice](filtered)

        st.write("the copy image")
        st.image(filtered)

        download_img = io.BytesIO()
        filtered.save(download_img,format="PNG")
        download_img.seek(0)
        st.download_button("download" , download_img, file_name= 'img.png', mime="image/png")

    else:
        st.error(f"Make sure your api is working,")


elif imagefile and bg_file and not api_key:
     st.warning("Enter your api key")