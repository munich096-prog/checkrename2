import streamlit as st
import re
import cv2
import numpy as np
from PIL import Image
import pytesseract
import pdfplumber

st.set_page_config(page_title="HAWB File Renamer", page_icon="📦", layout="centered")

st.markdown("""
<style>
.main{background:#f4f7fb;}
.block-container{padding-top:2rem;max-width:820px;}
.card{background:#fff;padding:28px;border-radius:16px;box-shadow:0 4px 16px rgba(0,0,0,.08);}
h1{text-align:center;color:#0F4C81;}
.small{text-align:center;color:#666;}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>📦 HAWB File Renamer</h1>", unsafe_allow_html=True)
st.markdown("<div class='small'>Upload PDF / PNG / JPG เพื่อเปลี่ยนชื่อไฟล์อัตโนมัติ</div>", unsafe_allow_html=True)

st.markdown("<div class='card'>", unsafe_allow_html=True)
uploaded_file = st.file_uploader("📂 เลือกไฟล์", type=["pdf","png","jpg","jpeg"])
st.markdown("</div>", unsafe_allow_html=True)

def extract_hawb(text:str):
    patterns=[
        r'HAWB\s*No\.?\s*[:\-]?\s*([A-Za-z0-9\-]+)',
        r'House\s*AWB\s*[:\-]?\s*([A-Za-z0-9\-]+)',
        r'House\s*Air\s*Waybill\s*[:\-]?\s*([A-Za-z0-9\-]+)',
        r'House\s*[\n\r,: ]+\s*([A-Za-z0-9\-]+)',
        r'\(\s*([A-Za-z0-9\-]+)\s*\)'
    ]
    for p in patterns:
        m=re.search(p,text,re.I)
        if m:
            return m.group(1)
    return None

if uploaded_file:
    text=""
    ext=uploaded_file.name.rsplit(".",1)[1].lower()
    progress=st.progress(0,text="กำลังประมวลผล...")
    try:
        if ext=="pdf":
            with pdfplumber.open(uploaded_file) as pdf:
                for p in pdf.pages:
                    t=p.extract_text()
                    if t:
                        text+=t+"\n"
        else:
            image=Image.open(uploaded_file).convert("RGB")
            st.image(image,caption="Preview",use_container_width=True)
            gray=cv2.cvtColor(np.array(image),cv2.COLOR_RGB2GRAY)
            gray=cv2.GaussianBlur(gray,(3,3),0)
            gray=cv2.threshold(gray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)[1]
            text=pytesseract.image_to_string(gray,lang="tha+eng")
        progress.progress(70,text="ค้นหา HAWB...")
        hawb=extract_hawb(text)
        progress.progress(100,text="เสร็จสิ้น")
        with st.expander("ข้อความที่อ่านได้ (OCR/Text)"):
            st.text(text[:5000])
        if hawb:
            st.success(f"พบ HAWB: {hawb}")
            base=uploaded_file.name.rsplit(".",1)[0]
            new=f"{base}_{hawb}.{ext}" if base.endswith("_AIR") else f"{base}-{hawb}.{ext}"
            st.info(f"ชื่อใหม่: {new}")
            uploaded_file.seek(0)
            st.download_button("📥 ดาวน์โหลดไฟล์",uploaded_file.read(),file_name=new,mime=uploaded_file.type,use_container_width=True)
        else:
            st.error("ไม่พบเลข HAWB")
    except Exception as e:
        st.exception(e)
