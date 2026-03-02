import streamlit as st
import pandas as pd
import datetime
import time

# --- 1. จำลอง Database (Shared State) ---
# ใช้ cache_resource เพื่อให้ข้อมูลแชร์กันระหว่างเครื่องลูกค้าและเครื่องเจ้าของร้าน
@st.cache_resource
class FoodSystemDB:
    def __init__(self):
        # ข้อมูลเมนูเริ่มต้น
        self.menu = {
            "m1": {
                "name": "ขนมจีนน้ำเงี้ยว",
                "price": 45,
                "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/62/Nam_ngiao.jpg/800px-Nam_ngiao.jpg",
                "active": True,
                "options": {
                    "เพิ่มเส้น": 5,
                    "เพิ่มเครื่อง": 10
                }
            },
            "m2": {
                "name": "แคบหมู",
                "price": 15,
                "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/23/Khaep_mu.jpg/800px-Khaep_mu.jpg",
                "active": True,
                "options": {} # ไม่มี Option เสริม
            }
        }
        # รายการออเดอร์ทั้งหมด
        self.orders = []

    def add_order(self, order_data):
        self.orders.append(order_data)

    def update_order_status(self, order_index, new_status):
        self.orders[order_index]['status'] = new_status

    def update_menu(self, menu_id, field, value):
        self.menu[menu_id][field] = value

db = FoodSystemDB()

# --- ตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="ร้านขนมจีนน้ำเงี้ยว", layout="wide")

# --- Function สำหรับสร้าง QR Code (จำลอง) ---
def generate_qr(amount):
    # ในการใช้งานจริง ให้ใช้ Library 'promptpay' เพื่อ Gen QR Code จริง
    st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=PromptPay_{amount}", 
             caption=f"สแกนเพื่อจ่ายเงิน {amount} บาท", width=150)

# ==========================================
# 🛒 ส่วนของลูกค้า (Customer Side)
# ==========================================
def customer_page():
    st.header("🍜 สั่งขนมจีนออนไลน์")

    # --- Step 1: ข้อมูลลูกค้า ---
    with st.expander("📝 1. ข้อมูลจัดส่ง", expanded=True):
        c_name = st.text_input("ชื่อลูกค้า:")
        c_address = st.text_area("ที่อยู่ / บ้านเลขที่:")

    if c_name and c_address:
        # --- Step 2: เลือกเมนู ---
        st.subheader("🍽️ 2. เลือกเมนู")
        cart = []
        total_price = 0

        # วนลูปแสดงเมนู
        for m_id, item in db.menu.items():
            if item['active']: # แสดงเฉพาะเมนูที่เปิดขาย
                col1, col2 = st.columns([1, 3])
                with col1:
                    st.image(item['img'], width=100)
                with col2:
                    st.write(f"**{item['name']}** - {item['price']} บาท")
                    
                    # ตัวเลือกเสริม (Options)
                    selected_opts = []
                    extra_cost = 0
                    if item['options']:
                        opts = st.multiselect(f"เลือกออปชันเสริม ({item['name']})", 
                                            list(item['options'].keys()), 
                                            key=f"opt_{m_id}")
                        for o in opts:
                            extra_cost += item['options'][o]
                            selected_opts.append(f"{o} (+{item['options'][o]})")
                    
                    # จำนวน
                    qty = st.number_input(f"จำนวน", min_value=0, max_value=20, key=f"qty_{m_id}")
                    
                    if qty > 0:
                        item_total = (item['price'] + extra_cost) * qty
                        cart.append({
                            "item_name": item['name'],
                            "options": selected_opts,
                            "qty": qty,
                            "price": item_total
                        })
                        total_price += item_total
                st.divider()

        # --- Step 3: สรุปยอดและจ่ายเงิน ---
        if len(cart) > 0:
            st.subheader(f"💰 ยอดรวมทั้งหมด: {total_price} บาท")
            with st.expander("💸 3. ชำระเงิน"):
                st.write("รายการสั่งซื้อของคุณ:")
                for c in cart:
                    st.text(f"- {c['item_name']} x{c['qty']} ({', '.join(c['options'])}) = {c['price']} บ.")
                
                generate_qr(total_price)
                
                slip_file = st.file_uploader("แนบสลิปโอนเงิน", type=['jpg', 'png'])
                
                if st.button("✅ ยืนยันการสั่งซื้อ"):
                    if slip_file is None:
                        st.error("กรุณาแนบสลิปโอนเงินก่อนครับ")
                    else:
                        # บันทึกออเดอร์ลงระบบ
                        order_id = f"ORD-{int(time.time())}"
                        new_order = {
                            "id": order_id,
                            "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "customer": c_name,
                            "address": c_address,
                            "items": cart,
                            "total": total_price,
                            "status": "รอการตรวจสอบ", # สถานะเริ่มต้น
                            "slip": "uploaded" # (ในระบบจริงต้อง save ไฟล์)
                        }
                        db.add_order(new_order)
                        st.success(f"สั่งซื้อสำเร็จ! รหัสออเดอร์ของคุณคือ: {order_id}")
                        st.info("กรุณารอร้านค้าตรวจสอบสถานะ")

    # --- Step 4: เช็คสถานะ ---
    st.divider()
    st.subheader("🔎 เช็คสถานะคำสั่งซื้อ")
    check_name = st.text_input("ค้นหาด้วยชื่อของคุณ:")
    if check_name:
        found = False
        for order in db.orders:
            if check_name in order['customer']:
                st.info(f"📍 ออเดอร์ {order['id']}: สถานะ **{order['status']}**")
                found = True
        if not found:
            st.warning("ไม่พบออเดอร์ (หรือร้านยังไม่อัปเดต)")

# ==========================================
# 👨‍🍳 ส่วนของเจ้าของร้าน (Admin Side)
# ==========================================
def admin_page():
    st.title("👨‍🍳 ระบบจัดการร้าน (Admin)")
    
    tab1, tab2, tab3 = st.tabs(["📦 รายการสั่งซื้อ", "🛠️ จัดการเมนู", "📊 สรุปรายได้"])

    # --- Tab 1: รายการสั่งซื้อ ---
    with tab1:
        st.write("### รายการที่เข้ามาล่าสุด")
        if not db.orders:
            st.info("ยังไม่มีออเดอร์วันนี้")
        else:
            # แปลงเป็น DataFrame เพื่อแสดงผลรวมๆ ก่อน
            df = pd.DataFrame(db.orders)
            st.dataframe(df[['time', 'id', 'customer', 'status', 'total']])
            
            st.divider()
            st.write("### จัดการสถานะออเดอร์")
            
            # วนลูปจัดการทีละออเดอร์
            for i, order in enumerate(reversed(db.orders)): # เอาออเดอร์ล่าสุดขึ้นก่อน
                idx = len(db.orders) - 1 - i # หา index จริงใน list
                
                with st.container(border=True):
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.write(f"**#{order['id']}** | คุณ {order['customer']} ({order['time']})")
                        st.write(f"📍 ที่อยู่: {order['address']}")
                        st.write("รายการ:")
                        text_items = ""
                        for item in order['items']:
                            text_items += f"- {item['item_name']} x{item['qty']} {item['options']}\n"
                        st.text(text_items)
                        st.write(f"💰 ยอดโอน: **{order['total']} บาท** (มีสลิปแนบมา)")
                    
                    with col2:
                        current_status = order['status']
                        status_options = ["รอการตรวจสอบ", "กำลังทำอาหาร", "กำลังส่ง", "ส่งสำเร็จ", "ยกเลิก"]
                        new_status = st.selectbox("เปลี่ยนสถานะ:", status_options, index=status_options.index(current_status), key=f"st_{order['id']}")
                        
                        if new_status != current_status:
                            db.update_order_status(idx, new_status)
                            st.success("อัปเดตแล้ว!")
                            time.sleep(1)
                            st.rerun()

    # --- Tab 2: จัดการเมนู (แก้ไขราคา/รูป/เปิดปิด) ---
    with tab2:
        st.write("### แก้ไขข้อมูลเมนู")
        for m_id, item in db.menu.items():
            with st.expander(f"✏️ แก้ไข: {item['name']}", expanded=True):
                c1, c2, c3 = st.columns(3)
                
                # แก้ไขราคา
                new_price = c1.number_input("ราคา", value=item['price'], key=f"p_{m_id}")
                if new_price != item['price']:
                    db.update_menu(m_id, 'price', new_price)
                    st.rerun()
                
                # เปิด-ปิด เมนู
                is_active = c2.checkbox("เปิดขาย", value=item['active'], key=f"a_{m_id}")
                if is_active != item['active']:
                    db.update_menu(m_id, 'active', is_active)
                    st.rerun()
                
                # แก้ไขรูป (ใส่ URL)
                new_img = st.text_input("URL รูปภาพ", value=item['img'], key=f"i_{m_id}")
                if new_img != item['img']:
                    db.update_menu(m_id, 'img', new_img)
                    st.rerun()

    # --- Tab 3: สรุปรายได้ ---
    with tab3:
        st.write("### 📈 สรุปยอดขายวันนี้")
        if db.orders:
            total_sales = sum(o['total'] for o in db.orders if o['status'] != 'ยกเลิก')
            completed_orders = sum(1 for o in db.orders if o['status'] == 'ส่งสำเร็จ')
            
            col1, col2, col3 = st.columns(3)
            col1.metric("รายได้รวม", f"{total_sales} บาท")
            col2.metric("ออเดอร์ทั้งหมด", f"{len(db.orders)} รายการ")
            col3.metric("ส่งสำเร็จแล้ว", f"{completed_orders} รายการ")
            
            st.bar_chart(pd.DataFrame(db.orders).set_index('time')['total'])
        else:
            st.write("ยังไม่มีข้อมูลการขาย")

# ==========================================
# 🧭 Main Navigation (เลือกว่าเป็นใคร)
# ==========================================
# สร้าง Sidebar เพื่อสลับโหมด (ในความเป็นจริงอาจแยก URL กัน)
mode = st.sidebar.radio("เลือกโหมดการใช้งาน", ["ลูกค้า (Customer)", "เจ้าของร้าน (Admin)"])

if mode == "ลูกค้า (Customer)":
    customer_page()
else:
    # เพิ่มระบบ Login ง่ายๆ สำหรับ Admin
    password = st.sidebar.text_input("รหัสผ่าน Admin", type="password")
    if password == "1234": # รหัสผ่านคือ 1234
        admin_page()
    else:
        st.sidebar.warning("กรุณาใส่รหัสผ่าน (default: 1234)")