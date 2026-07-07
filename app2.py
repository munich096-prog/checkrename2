import streamlit as st
import re
import cv2
import numpy as np
from PIL import Image
import pytesseract
import pdfplumber

st.set_page_config(page_title="HAWB File Renamer", layout="centered")
st.title("📦 ระบบเปลี่ยนชื่อไฟล์ใบขนสินค้าด้วย HAWB")
st.write("อัปโหลดไฟล์ใบขนสินค้า (PDF, PNG, JPG) เพื่อเปลี่ยนชื่อไฟล์อัตโนมัติ")

uploaded_file = st.file_uploader("ลากและวางไฟล์ที่นี่ (PDF, PNG, JPG)", type=["pdf", "png", "jpg", "jpeg"])

if uploaded_file is not None:
    file_type = uploaded_file.name.rsplit('.', 1)[1].lower()
    text = ""
    
    with st.spinner("กำลังอ่านข้อมูลจากไฟล์..."):
        if file_type == "pdf":
            # อ่านข้อความจากไฟล์ PDF โดยตรง
            with pdfplumber.open(uploaded_file) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        else:
            # อ่านจากรูปภาพด้วย OCR
            image = Image.open(uploaded_file)
            st.image(image, caption="ไฟล์ที่อัปโหลด", use_container_width=True)
            img_np = np.array(image)
            gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
            text = pytesseract.image_to_string(gray, lang='tha+eng')
        
        # --- ส่วนการค้นหาเลข HAWB ---
        hawb_number = None
        
        # รูปแบบที่ 1: หาเลขในวงเล็บ (สำหรับไฟล์รูปแบบแรก)
        match1 = re.search(r'\(\s*(\d+)\s*\)', text)
        if match1:
            hawb_number = match1.group(1)
            
        # รูปแบบที่ 2: หาเลขหลังคำว่า House (สำหรับไฟล์รูปแบบใหม่ที่เป็นตาราง PDF)
        if not hawb_number:
            match2 = re.search(r'House\s*[\n\r,:]*\s*(\d+)', text, re.IGNORECASE)
            if match2:
                hawb_number = match2.group(1)
        
        # --- ส่วนการเปลี่ยนชื่อไฟล์ตามเงื่อนไข Output ---
        if hawb_number:
            st.success(f"🔍 ตรวจพบเลข HAWB: {hawb_number}")
            
            original_name = uploaded_file.name.rsplit('.', 1)[0]
            extension = uploaded_file.name.rsplit('.', 1)[1].lower()
            
            # เช็กเงื่อนไขการใช้ตัวเชื่อม (_ หรือ -)
            if original_name.endswith("_AIR"):
                new_filename = f"{original_name}_{hawb_number}.{extension}"
            else:
                new_filename = f"{original_name}-{hawb_number}.{extension}"
            
            st.info(f"💾 ชื่อไฟล์ใหม่จะเป็น: {new_filename}")
            
            uploaded_file.seek(0)
            file_bytes = uploaded_file.read()
            
            st.download_button(
                label="📥 กดดาวน์โหลดไฟล์ที่เปลี่ยนชื่อแล้ว",
                data=file_bytes,
                file_name=new_filename,
                mime=uploaded_file.type
            )
        else:
            st.error("❌ ไม่พบเลข HAWB ในไฟล์นี้ กรุณาตรวจสอบความถูกต้องของไฟล์อีกครั้ง")