import streamlit as st
import pandas as pd
import datetime
import time

# ==========================================
# 💾 1. DATABASE & STATE MANAGEMENT
# ==========================================
@st.cache_resource
class FoodSystemDB:
    def __init__(self):
        # รายการอาหาร (Database)
        self.menu = {
            "m1": {
                "name": "ขนมจีนน้ำเงี้ยว",
                "price": 45,
                "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/62/Nam_ngiao.jpg/800px-Nam_ngiao.jpg",
                "active": True,
                "options": {"เพิ่มเส้น": 5, "เพิ่มเครื่อง": 10, "ไม่ผัก": 0}
            },
            "m2": {
                "name": "ข้าวซอยไก่",
                "price": 50,
                "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/15/Khao_Soi_Kai.jpg/800px-Khao_Soi_Kai.jpg",
                "active": True,
                "options": {"น่องลาย": 10, "พิเศษ": 10}
            },
            "m3": {
                "name": "แคบหมู",
                "price": 15,
                "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/23/Khaep_mu.jpg/800px-Khaep_mu.jpg",
                "active": True,
                "options": {} 
            },
            "m4": {
                "name": "น้ำพริกหนุ่ม+ผัก",
                "price": 40,
                "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a3/Nam_phrik_num.jpg/800px-Nam_phrik_num.jpg",
                "active": True,
                "options": {"ไข่ต้ม": 10}
            },
            "m5": {
                "name": "แกงฮังเล",
                "price": 60,
                "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/41/Kaeng_hang_le.jpg/800px-Kaeng_hang_le.jpg",
                "active": True,
                "options": {"ข้าวสวย": 10, "ข้าวเหนียว": 10}
            }
        }
        self.orders = []

    def add_order(self, order_data):
        self.orders.append(order_data)

    def update_order_status(self, order_index, new_status):
        self.orders[order_index]['status'] = new_status

    def update_menu(self, menu_id, field, value):
        self.menu[menu_id][field] = value

db = FoodSystemDB()

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="ร้านอาหารเหนือเจ้า", layout="centered")

# เตรียม Session State สำหรับตะกร้าสินค้า (เฉพาะลูกค้าคนนั้นๆ)
if 'cart' not in st.session_state:
    st.session_state.cart = []

# ==========================================
# 🛒 CUSTOMER SIDE (ฝั่งลูกค้า)
# ==========================================
def customer_page():
    st.title("🍜 สั่งอาหารเหนือออนไลน์")

    # --- Step 1: ข้อมูลลูกค้า (ย่อเก็บได้) ---
    with st.expander("👤 1. กรอกข้อมูลจัดส่ง (คลิกเพื่อแก้ไข)", expanded=not st.session_state.cart):
        c_name = st.text_input("ชื่อของคุณ:", key="c_name")
        c_address = st.text_area("ที่อยู่จัดส่ง / เบอร์โทร:", key="c_address")

    # --- Step 2: เลือกเมนู (Add to Cart) ---
    st.header("🍽️ 2. เลือกเมนู")
    
    for m_id, item in db.menu.items():
        if item['active']:
            with st.container(border=True):
                c1, c2 = st.columns([1, 2])
                with c1:
                    st.image(item['img'], use_column_width=True)
                with c2:
                    st.subheader(f"{item['name']}")
                    st.write(f"ราคาเริ่มต้น: **{item['price']}** บาท")
                    
                    # Form แยกแต่ละเมนู เพื่อไม่ให้ค่าตีกัน
                    with st.form(key=f"form_{m_id}"):
                        # เลือก Option
                        selected_opts = []
                        extra_price = 0
                        if item['options']:
                            opts = st.multiselect("ตัวเลือกเสริม:", list(item['options'].keys()), key=f"opt_{m_id}")
                            for o in opts:
                                extra_price += item['options'][o]
                                selected_opts.append(f"{o} (+{item['options'][o]})")
                        
                        # เลือกจำนวน
                        qty = st.number_input("จำนวน", min_value=1, max_value=20, value=1, key=f"qty_{m_id}")
                        
                        # ปุ่ม Add
                        submitted = st.form_submit_button("➕ เพิ่มลงตะกร้า")
                        if submitted:
                            total_item_price = (item['price'] + extra_price) * qty
                            st.session_state.cart.append({
                                "id": m_id,
                                "name": item['name'],
                                "options": selected_opts, # เก็บเป็น List รายชื่อ option
                                "qty": qty,
                                "price": total_item_price
                            })
                            st.success(f"เพิ่ม {item['name']} แล้ว!")
                            time.sleep(0.5)
                            st.rerun()

    # --- Step 3: ตะกร้าสินค้า & ชำระเงิน ---
    st.divider()
    st.header("🛒 3. ตะกร้าของฉัน")

    if not st.session_state.cart:
        st.info("ตะกร้ายังว่างอยู่ครับ เลือกเมนูด้านบนได้เลย")
    else:
        # แสดงรายการในตะกร้า
        total_order_price = 0
        for i, cart_item in enumerate(st.session_state.cart):
            col_name, col_price, col_del = st.columns([3, 1, 1])
            with col_name:
                st.write(f"**{i+1}. {cart_item['name']}** x{cart_item['qty']}")
                if cart_item['options']:
                    st.caption(f"เสริม: {', '.join(cart_item['options'])}")
            with col_price:
                st.write(f"{cart_item['price']} บ.")
            with col_del:
                if st.button("❌ ลบ", key=f"del_{i}"):
                    st.session_state.cart.pop(i)
                    st.rerun()
            
            total_order_price += cart_item['price']
            st.divider()

        st.subheader(f"💰 ยอดรวมทั้งสิ้น: {total_order_price} บาท")

        # ส่วนชำระเงิน
        if c_name and c_address:
            with st.expander("💸 จ่ายเงินและยืนยันออเดอร์", expanded=True):
                # QR Code (ใช้ API สร้าง QR PromptPay ได้ถ้าต้องการ)
                st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=PromptPay_{total_order_price}", 
                         caption=f"สแกน {total_order_price} บาท", width=150)
                
                uploaded_slip = st.file_uploader("แนบสลิปโอนเงิน:", type=['jpg', 'png', 'jpeg'])
                
                if st.button("✅ ยืนยันการสั่งซื้อ"):
                    if not uploaded_slip:
                        st.error("กรุณาแนบสลิปก่อนครับ")
                    else:
                        # สร้าง Order ID
                        order_id = f"ORD-{int(time.time())}"
                        new_order = {
                            "id": order_id,
                            "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "customer": c_name,
                            "address": c_address,
                            "items": st.session_state.cart, # เอาทั้งตะกร้าไปบันทึก
                            "total": total_order_price,
                            "status": "รอตรวจสอบ",
                            "slip": "uploaded"
                        }
                        db.add_order(new_order)
                        # เคลียร์ตะกร้า
                        st.session_state.cart = []
                        st.success(f"ขอบคุณครับ! รหัสออเดอร์: {order_id}")
                        st.balloons()
        else:
            st.warning("⚠️ กรุณากรอก 'ชื่อ' และ 'ที่อยู่' ด้านบนให้ครบก่อนชำระเงินครับ")

    # --- Step 4: เช็คสถานะ (เหมือนเดิม) ---
    with st.expander("🔎 ติดตามสถานะออเดอร์"):
        search_name = st.text_input("พิมพ์ชื่อเพื่อค้นหา:")
        if search_name:
            for order in reversed(db.orders):
                if search_name in order['customer']:
                    st.write(f"**Order {order['id']}**: {order['status']} ({order['time']})")

# ==========================================
# 👨‍🍳 ADMIN SIDE (ฝั่งเจ้าของร้าน)
# ==========================================
def admin_page():
    st.title("👨‍🍳 จัดการร้านค้า")
    
    tab1, tab2, tab3 = st.tabs(["📦 ออเดอร์เข้าใหม่", "🛠️ แก้ไขเมนู", "📊 รายได้"])

    with tab1:
        if not db.orders:
            st.info("ยังไม่มีรายการสั่งซื้อ")
        else:
            for i, order in enumerate(reversed(db.orders)):
                real_idx = len(db.orders) - 1 - i
                with st.container(border=True):
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        st.subheader(f"#{order['id']} | คุณ {order['customer']}")
                        st.write(f"📍 {order['address']}")
                        st.write("---")
                        for item in order['items']:
                            opts = f" ({', '.join(item['options'])})" if item['options'] else ""
                            st.write(f"- {item['name']} x{item['qty']} {opts}")
                        st.write("---")
                        st.write(f"💰 **ยอดโอน: {order['total']} บาท**")
                    
                    with c2:
                        st.write(f"สถานะ: **{order['status']}**")
                        status_list = ["รอตรวจสอบ", "กำลังปรุง", "กำลังส่ง", "ส่งสำเร็จ", "ยกเลิก"]
                        new_stat = st.selectbox("เปลี่ยนสถานะ", status_list, index=status_list.index(order['status']), key=f"s_{order['id']}")
                        if new_stat != order['status']:
                            db.update_order_status(real_idx, new_stat)
                            st.rerun()

    with tab2: # จัดการเมนู (เหมือนเดิมแต่เพิ่มเมนู)
        st.write("รายการเมนูอาหาร")
        for m_id, item in db.menu.items():
            with st.expander(f"✏️ {item['name']}", expanded=False):
                new_p = st.number_input("ราคา", value=item['price'], key=f"p_{m_id}")
                new_active = st.checkbox("เปิดขาย", value=item['active'], key=f"a_{m_id}")
                if new_p != item['price'] or new_active != item['active']:
                    db.update_menu(m_id, 'price', new_p)
                    db.update_menu(m_id, 'active', new_active)
                    st.rerun()

    with tab3: # สรุปยอด
        if db.orders:
            total = sum(o['total'] for o in db.orders if o['status'] != 'ยกเลิก')
            st.metric("รายได้รวมทั้งหมด", f"{total} บาท")
            df = pd.DataFrame(db.orders)
            st.dataframe(df[['time', 'customer', 'total', 'status']])

# ==========================================
# MAIN APP
# ==========================================
# Sidebar ซ่อนเมนู Admin ไว้เนียนๆ
menu = st.sidebar.selectbox("Menu", ["ลูกค้าสั่งอาหาร", "Admin Login"])

if menu == "ลูกค้าสั่งอาหาร":
    customer_page()
elif menu == "Admin Login":
    pwd = st.sidebar.text_input("Password", type="password")
    if pwd == "1234":
        admin_page()
    else:
        st.warning("กรุณาใส่รหัสผ่าน")
