import streamlit as st
import pandas as pd
import datetime
import time

# ==========================================
# 🎨 0. CUSTOM CSS & CONFIG (Modern UI)
# ==========================================
st.set_page_config(page_title="EasyEats App", layout="centered", page_icon="🍜")

# CSS เพื่อปรับแต่งหน้าตาให้เหมือน App มือถือ
st.markdown("""
<style>
    /* ปรับปุ่มกดให้โค้งมนและสวยงาม */
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        font-weight: bold;
        border: 1px solid #FF4B4B;
    }
    /* ปรับระยะห่างของ Container */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    /* สร้าง Card Effect */
    div[data-testid="stVerticalBlock"] > div[style*="flex-direction: column;"] > div[data-testid="stVerticalBlock"] {
        background-color: #f9f9f9;
        border-radius: 10px;
        padding: 10px;
    }
    /* หัวข้อสินค้า */
    h3 {
        font-size: 1.2rem !important;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 💾 1. DATABASE & STATE
# ==========================================
@st.cache_resource
class FoodSystemDB:
    def __init__(self):
        self.menu = {
            "m1": {"name": "ขนมจีนน้ำเงี้ยว", "price": 45, "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/62/Nam_ngiao.jpg/800px-Nam_ngiao.jpg", "active": True, "options": {"เพิ่มเส้น": 5, "เพิ่มเครื่อง": 10}},
#            "m2": {"name": "ข้าวซอยไก่", "price": 50, "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/15/Khao_Soi_Kai.jpg/800px-Khao_Soi_Kai.jpg", "active": True, "options": {"น่องลาย": 10}},
            "m3": {"name": "แคบหมูไร้มัน", "price": 15, "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/23/Khaep_mu.jpg/800px-Khaep_mu.jpg", "active": True, "options": {}},
#            "m4": {"name": "ไส้อั่วสมุนไพร", "price": 60, "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/89/Sai_ua_สมุนไพร.jpg/800px-Sai_ua_สมุนไพร.jpg", "active": True, "options": {"ข้าวเหนียว": 10}},
#            "m5": {"name": "น้ำพริกหนุ่ม", "price": 40, "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a3/Nam_phrik_num.jpg/800px-Nam_phrik_num.jpg", "active": True, "options": {"ไข่ต้ม": 10}},
        }
        self.orders = []

    def add_order(self, order_data):
        self.orders.append(order_data)

    def update_order_status(self, order_index, new_status):
        self.orders[order_index]['status'] = new_status

db = FoodSystemDB()

if 'cart' not in st.session_state:
    st.session_state.cart = []

# ==========================================
# 🛍️ UI COMPONENTS (ส่วนประกอบหน้าจอ)
# ==========================================
def render_header():
    # Banner ร้านค้า
    st.image("https://images.unsplash.com/photo-1555126634-323283e090fa?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80", use_column_width=True)
    st.title("น้ำเงี้ยววีคเอน")
    st.caption("อาหารเหนือแท้ๆ ส่งตรงถึงหน้าบ้านคุณ")

def cart_summary():
    # แถบสรุปยอดเงินด้านบน (Sticky แบบบ้านๆ)
    if st.session_state.cart:
        total = sum(item['price'] for item in st.session_state.cart)
        count = sum(item['qty'] for item in st.session_state.cart)
        st.info(f"🛒 ในตะกร้า: **{count} รายการ** | รวม: **{total} บาท**")

# ==========================================
# 🛒 CUSTOMER FLOW
# ==========================================
def customer_page():
    render_header()
    cart_summary()

    tab_menu, tab_cart, tab_status = st.tabs(["🍽️ เมนูอาหาร", "🛍️ ตะกร้า & จ่ายเงิน", "🚚 เช็คสถานะ"])

    # --- TAB 1: MENU (GRID LAYOUT) ---
    with tab_menu:
        # ใช้ Grid Layout 2 คอลัมน์เพื่อให้ดูเหมือนแอปมือถือ
        col1, col2 = st.columns(2)
        cols = [col1, col2]
        
        # กรองเฉพาะเมนูที่ Active
        active_items = [(k, v) for k, v in db.menu.items() if v['active']]
        
        for index, (m_id, item) in enumerate(active_items):
            # เลือกคอลัมน์ซ้ายหรือขวาตามลำดับ
            with cols[index % 2]:
                with st.container(border=True): # สร้าง Card
                    # รูปภาพเต็มกรอบ
                    st.image(item['img'], use_column_width=True)
                    st.markdown(f"### {item['name']}")
                    st.markdown(f"**{item['price']} บาท**")
                    
                    # ตัวเลือก (ย่อใน Popover เพื่อความสะอาดตา)
                    with st.expander("เลือกเพิ่มเติม"):
                        selected_opts = []
                        extra_price = 0
                        if item['options']:
                            opts = st.multiselect("ออปชัน:", list(item['options'].keys()), key=f"opt_{m_id}")
                            for o in opts:
                                extra_price += item['options'][o]
                                selected_opts.append(o)
                        
                        qty = st.number_input("จำนวน", 1, 10, 1, key=f"qty_{m_id}")
                    
                    # ปุ่ม Add (Full Width จาก CSS)
                    if st.button("➕ ใส่ตะกร้า", key=f"btn_{m_id}"):
                        final_price = (item['price'] + extra_price) * qty
                        st.session_state.cart.append({
                            "id": m_id, "name": item['name'], "options": selected_opts,
                            "qty": qty, "price": final_price
                        })
                        st.toast(f"เพิ่ม {item['name']} แล้ว!", icon="✅")
                        time.sleep(0.5)
                        st.rerun()

    # --- TAB 2: CART ---
    with tab_cart:
        if not st.session_state.cart:
            st.empty()
            st.info("ตะกร้ายังว่างอยู่ครับ ไปเลือกเมนูอร่อยๆ กันเลย!")
            st.button("กลับไปเลือกเมนู", on_click=lambda: st.rerun())
        else:
            st.subheader("รายการที่เลือก")
            total_price = 0
            
            for i, item in enumerate(st.session_state.cart):
                with st.container(border=True):
                    c1, c2, c3 = st.columns([4, 2, 1])
                    with c1:
                        st.markdown(f"**{item['name']}** x{item['qty']}")
                        if item['options']:
                            st.caption(f"+ {', '.join(item['options'])}")
                    with c2:
                        st.markdown(f"**{item['price']} บ.**")
                    with c3:
                        if st.button("🗑️", key=f"del_{i}"):
                            st.session_state.cart.pop(i)
                            st.rerun()
                total_price += item['price']
            
            st.divider()
            st.markdown(f"### 💰 ยอดรวม: <span style='color:green'>{total_price} บาท</span>", unsafe_allow_html=True)

            # Form Checkout
            with st.form("checkout_form"):
                st.write("**ข้อมูลจัดส่ง**")
                c_name = st.text_input("ชื่อผู้รับ")
                c_addr = st.text_area("ที่อยู่ / เบอร์โทร")
                
                st.write("**การชำระเงิน**")
                # QR Code แบบ Modern (ใช้ API QR จริง)
                col_qr, col_upload = st.columns(2)
                with col_qr:
                    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=PromptPay_{total_price}"
                    st.image(qr_url, caption="สแกนจ่ายได้เลย")
                with col_upload:
                    uploaded_slip = st.file_uploader("อัปโหลดสลิป", type=['jpg', 'png'])

                submitted = st.form_submit_button("✅ ยืนยันการสั่งซื้อ", type="primary")
                
                if submitted:
                    if not c_name or not c_addr:
                        st.error("กรุณากรอกชื่อและที่อยู่ครับ")
                    elif not uploaded_slip:
                        st.error("กรุณาแนบสลิปโอนเงินครับ")
                    else:
                        order_id = f"ORD-{int(time.time())}"
                        new_order = {
                            "id": order_id,
                            "time": datetime.datetime.now().strftime("%H:%M"),
                            "customer": c_name,
                            "address": c_addr,
                            "items": st.session_state.cart,
                            "total": total_price,
                            "status": "รอตรวจสอบ", # สถานะแรก
                            "slip_img": uploaded_slip
                        }
                        db.add_order(new_order)
                        st.session_state.cart = [] # Clear cart
                        st.balloons()
                        st.success(f"สั่งซื้อสำเร็จ! รหัสของคุณ: {order_id}")

    # --- TAB 3: STATUS ---
    with tab_status:
        st.write("ตรวจสอบสถานะอาหารของคุณ")
        search = st.text_input("กรอกชื่อ หรือ รหัสออเดอร์", placeholder="เช่น สมชาย")
        if search:
            found = False
            for order in reversed(db.orders):
                if search in order['customer'] or search in order['id']:
                    found = True
                    with st.container(border=True):
                        st.markdown(f"### 🧾 ออเดอร์ {order['id']}")
                        
                        # Progress Bar ตามสถานะ
                        status_map = {"รอตรวจสอบ": 10, "กำลังปรุง": 40, "กำลังส่ง": 70, "ส่งสำเร็จ": 100, "ยกเลิก": 0}
                        progress = status_map.get(order['status'], 0)
                        
                        if order['status'] == "ยกเลิก":
                            st.error("❌ ออเดอร์ถูกยกเลิก")
                        else:
                            st.progress(progress)
                            st.caption(f"สถานะปัจจุบัน: **{order['status']}**")
                        
                        with st.expander("ดูรายการอาหาร"):
                            for item in order['items']:
                                st.write(f"- {item['name']} x{item['qty']}")
            if not found:
                st.warning("ไม่พบข้อมูลออเดอร์ครับ")

# ==========================================
# 👨‍🍳 ADMIN SIDE (Back Office)
# ==========================================
def admin_page():
    st.title("👨‍🍳 ระบบหลังบ้าน")
    st.markdown("---")
    
    # Dashboard สรุปยอด
    if db.orders:
        today_total = sum(o['total'] for o in db.orders if o['status'] != 'ยกเลิก')
        pending_orders = sum(1 for o in db.orders if o['status'] == 'รอตรวจสอบ')
        
        c1, c2, c3 = st.columns(3)
        c1.metric("ยอดขายวันนี้", f"{today_total:,} บ.")
        c2.metric("ออเดอร์รอตรวจ", f"{pending_orders} รายการ", delta_color="inverse")
        c3.metric("ออเดอร์ทั้งหมด", len(db.orders))
    
    tab_orders, tab_menu = st.tabs(["📦 จัดการออเดอร์", "✏️ แก้ไขเมนู"])
    
    with tab_orders:
        if not db.orders:
            st.info("ยังไม่มีออเดอร์เข้า")
        else:
            for i, order in enumerate(reversed(db.orders)):
                real_idx = len(db.orders) - 1 - i
                
                # การ์ดออเดอร์ Admin
                with st.container(border=True):
                    c1, c2 = st.columns([2, 1])
                    with c1:
                        st.markdown(f"**#{order['id']}** | {order['time']} น.")
                        st.markdown(f"👤 **{order['customer']}**")
                        st.caption(f"🏠 {order['address']}")
                        st.markdown(f"💰 **ยอดโอน: {order['total']} บาท**")
                        
                        with st.expander("ดูรายการอาหาร & สลิป"):
                            for item in order['items']:
                                st.write(f"- {item['name']} x{item['qty']}")
                            if order.get('slip_img'):
                                st.image(order['slip_img'], caption="สลิปโอนเงิน", width=200)

                    with c2:
                        st.write("สถานะ:")
                        current_stat = order['status']
                        opts = ["รอตรวจสอบ", "กำลังปรุง", "กำลังส่ง", "ส่งสำเร็จ", "ยกเลิก"]
                        new_stat = st.selectbox("Update", opts, index=opts.index(current_stat), key=f"st_{order['id']}", label_visibility="collapsed")
                        
                        if new_stat != current_stat:
                            db.update_order_status(real_idx, new_stat)
                            st.rerun()

    with tab_menu:
        for m_id, item in db.menu.items():
            with st.expander(f"🍔 {item['name']}", expanded=False):
                col1, col2 = st.columns(2)
                with col1:
                    new_price = st.number_input(f"ราคา ({item['name']})", value=item['price'], key=f"p_{m_id}")
                with col2:
                    new_active = st.toggle("เปิดขาย", value=item['active'], key=f"a_{m_id}")
                
                if new_price != item['price'] or new_active != item['active']:
                    db.update_menu(m_id, 'price', new_price)
                    db.update_menu(m_id, 'active', new_active)
                    st.toast("บันทึกการแก้ไขแล้ว!")
                    time.sleep(1)
                    st.rerun()

# ==========================================
# 🧭 NAVIGATION
# ==========================================
# ใช้ Sidebar แบบซ่อนเนียนๆ
with st.sidebar:
    st.header("EasyEats System")
    mode = st.radio("Menu", ["ลูกค้า", "ผู้ดูแลร้าน"])
    st.divider()
    st.caption("Developed with Streamlit")

if mode == "ลูกค้า":
    customer_page()
else:
    pwd = st.sidebar.text_input("รหัสผ่าน Admin", type="password")
    if pwd == "1234":
        admin_page()
    elif pwd:
        st.error("รหัสผ่านผิด")
