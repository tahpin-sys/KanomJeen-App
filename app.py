import streamlit as st
import pandas as pd
import time

# ตั้งค่าหน้าจอให้เหมาะกับมือถือ
st.set_page_config(page_title="EasyOrder App", layout="centered")

# --- ข้อมูลเมนู (Database จำลอง) ---
menu_data = {
    "ข้าวกะเพราไก่": {"price": 50, "condiments": ["ไข่ดาว (+10)", "ไข่เจียว (+10)", "เพิ่มข้าว (+5)", "เผ็ดมาก", "ไม่ใส่ผัก"]},
    "ก๋วยเตี๋ยวเรือ": {"price": 45, "condiments": ["เส้นเล็ก", "เส้นหมี่", "ตับหวาน (+10)", "แคบหมู (+7)", "พิเศษลูกชิ้น (+10)"]},
    "ข้าวผัดปู": {"price": 60, "condiments": ["พริกน้ำปลา", "มะนาวเพิ่ม", "ไข่เค็ม (+12)", "กุนเชียง (+15)", "ผักชี"]},
    "สเต็กหมู": {"price": 89, "condiments": ["ซอสพริกไทยดำ", "เฟรนช์ฟรายส์ (+20)", "สลัดเพิ่ม", "ขนมปังกระเทียม", "ไข่ดาว (+10)"]},
    "กาแฟอเมริกาโน่": {"price": 40, "condiments": ["หวานน้อย", "ไม่หวาน", "เพิ่มช็อต (+15)", "น้ำผึ้ง (+10)", "เย็น/ร้อน"]}
}

# --- ส่วนของ UI ---
st.title("🍴 ร้านอาหารสั่งง่าย (EasyOrder)")

# เลือกโหมดผู้ใช้งาน (จำลองการสลับหน้า)
user_mode = st.sidebar.radio("เลือกโหมดผู้ใช้งาน", ["ลูกค้า (Customer)", "เจ้าของร้าน (Owner)"])

if user_mode == "ลูกค้า (Customer)":
    st.subheader("เลือกเมนูอาหารของคุณ")
    
    # 1. เลือกเมนูหลัก
    selected_dish = st.selectbox("เลือกเมนูหลัก:", list(menu_data.keys()))
    
    # 2. เลือก Condiments (เลือกได้หลายอย่าง)
    st.write(f"ราคาเริ่มต้น: {menu_data[selected_dish]['price']} บาท")
    selected_extras = st.multiselect("เลือกเครื่องปรุง/ตัวเลือกเสริม:", menu_data[selected_dish]['condiments'])
    
    # 3. คำนวณราคา (จำลองการบวกราคาจากข้อความ)
    extra_price = 0
    for item in selected_extras:
        if "(+" in item:
            extra_price += int(item.split("(+")[1].split(")")[0])
    
    total = menu_data[selected_dish]['price'] + extra_price
    
    st.divider()
    st.write(f"### ยอดรวมทั้งหมด: {total} บาท")

    # 4. ส่วนการชำระเงิน
    if st.button("ยืนยันการสั่งซื้อและชำระเงิน"):
        st.info("กำลังสร้าง QR Code สำหรับชำระเงิน...")
        # จำลอง QR Code (ในระบบจริงจะใช้ PromptPay Library)
        st.image("https://upload.wikimedia.org/wikipedia/commons/d/d0/QR_code_for_mobile_English_Wikipedia.svg", caption="สแกนเพื่อจ่ายเงิน (ตัวอย่าง)", width=200)
        
        uploaded_file = st.file_uploader("อัปโหลดสลิปเพื่อยืนยัน (Verify)", type=['png', 'jpg', 'jpeg'])
        
        if uploaded_file is not None:
            with st.spinner('กำลังตรวจสอบสลิปด้วยระบบ AI...'):
                time.sleep(2) # จำลองกระบวนการตรวจเช็ค
                st.success("✅ ตรวจสอบสำเร็จ! ออเดอร์ส่งถึงร้านแล้ว")
                # บันทึกลง Session (จำลอง Database)
                if 'orders' not in st.session_state:
                    st.session_state.orders = []
                st.session_state.orders.append({"item": selected_dish, "extras": selected_extras, "total": total, "status": "กำลังปรุง"})

elif user_mode == "เจ้าของร้าน (Owner)":
    st.subheader("📋 รายการสั่งอาหารวันนี้")
    if 'orders' in st.session_state and len(st.session_state.orders) > 0:
        df = pd.DataFrame(st.session_state.orders)
        st.table(df)
        if st.button("ล้างคิวอาหาร"):
            st.session_state.orders = []
            st.rerun()
    else:
        st.write("ยังไม่มีออเดอร์ใหม่เข้ามา")