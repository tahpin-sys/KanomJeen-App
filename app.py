import streamlit as st
import pandas as pd
import datetime
import time

# ==========================================
# 🎨 0. CONFIG & CSS Styling
# ==========================================
st.set_page_config(page_title="KanomJeen", layout="centered", page_icon="🍜")

# CSS ปรับแต่งความสวยงาม
st.markdown("""
<style>
    /* 1. ปรับแต่ง Tabs ให้ใหญ่และชัดเจน */
    button[data-baseweb="tab"] {
        font-size: 18px !important;
        font-weight: bold !important;
        padding: 10px 20px !important;
    }
    
    /* 2. ปรับปุ่มกดทั่วไป */
    .stButton>button {
        border-radius: 12px;
        font-weight: 600;
    }

    /* 3. ปรับแต่ง Card สินค้า */
    div[data-testid="stVerticalBlock"] > div[style*="flex-direction: column;"] > div[data-testid="stVerticalBlock"] {
        background-color: #ffffff;
        border: 1px solid #f0f2f6;
        border-radius: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        padding: 15px;
    }
    
    /* หัวข้อสินค้า */
    h3 {
        font-size: 1.1rem !important;
        margin-bottom: 0.2rem;
        color: #333;
    }
    
    /* สีราคา */
    .price-tag {
        color: #FF4B4B;
        font-weight: bold;
        font-size: 1.1rem;
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
            "m2": {"name": "ข้าวซอยไก่", "price": 50, "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/15/Khao_Soi_Kai.jpg/800px-Khao_Soi_Kai.jpg", "active": True, "options": {"น่องลาย": 10, "พิเศษ": 10}},
            "m3": {"name": "แคบหมูไร้มัน", "price": 15, "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/23/Khaep_mu.jpg/800px-Khaep_mu.jpg", "active": True, "options": {}},
            "m4": {"name": "ไส้อั่วสมุนไพร", "price": 60, "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/89/Sai_ua_สมุนไพร.jpg/800px-Sai_ua_สมุนไพร.jpg", "active": True, "options": {"ข้าวเหนียว": 10}},
            "m5": {"name": "น้ำพริกหนุ่ม", "price": 40, "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a3/Nam_phrik_num.jpg/800px-Nam_phrik_num.jpg", "active": True, "options": {"ไข่ต้ม": 10}},
        }
        self.orders = []

    def update_order_status(self, order_index, new_status):
        self.orders[order_index]['status'] = new_status
        
    def update_menu(self, menu_id, field, value):
        self.menu[menu_id][field] = value

db = FoodSystemDB()

if 'cart' not in st.session_state:
    st.session_state.cart = []

# ==========================================
# 🛍️ UI COMPONENTS
# ==========================================
def render_header():
    # Banner
    st.image("https://images.unsplash.com/photo-1593560708920-61dd98c46a4e?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80", use_column_width=True)
    st.title("🍜 KanomJeen Weekend")
    st.caption("อร่อยเหมือนกินที่บ้าน สะอาด ปลอดภัย")

def cart_summary():
    if st.session_state.cart:
        total = sum(item['price'] for item in st.session_state.cart)
        count = sum(item['qty'] for item in st.session_state.cart)
        st.warning(f"🛒 ตะกร้า: **{count} รายการ** | รวม: **{total} บาท**")

# ==========================================
# 🛒 CUSTOMER FLOW
# ==========================================
def customer_page():
    render_header()
    cart_summary()

    # Tabs ที่ปรับปรุงใหม่ ชัดเจนขึ้น
    tab_menu, tab_cart, tab_status = st.tabs(["📋 เมนูอาหาร", "🛒 ตะกร้า & จ่ายเงิน", "🚚 สถานะ"])

    # --- TAB 1: MENU ---
    with tab_menu:
        st.write("เลือกเมนูที่ต้องการ")
        col1, col2 = st.columns(2)
        cols = [col1, col2]
        
        active_items = [(k, v) for k, v in db.menu.items() if v['active']]
        
        for index, (m_id, item) in enumerate(active_items):
            with cols[index % 2]:
                with st.container(border=True): 
                    st.image(item['img'], use_column_width=True)
                    st.markdown(f"### {item['name']}")
                    st.markdown(f"<div class='price-tag'>{item['price']} บาท</div>", unsafe_allow_html=True)
                    
                    # Form แยกแต่ละเมนู
                    with st.form(key=f"form_{m_id}", border=False):
                        selected_opts = []
                        extra_price = 0
                        if item['options']:
                            opts = st.multiselect("เลือกเพิ่ม:", list(item['options'].keys()), key=f"opt_{m_id}")
                            for o in opts:
                                extra_price += item['options'][o]
                                selected_opts.append(o)
                        
                        qty = st.number_input("จำนวน", 1, 10, 1, key=f"qty_{m_id}")
                        st.markdown("---")
                        # ปุ่ม Add to Cart เด่นชัด (Primary Color)
                        if st.form_submit_button("➕ ใส่ตะกร้า", type="primary", use_container_width=True):
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
            st.info("ยังไม่มีสินค้าในตะกร้า")
        else:
            st.subheader("รายการที่เลือก")
            total_price = 0
            for i, item in enumerate(st.session_state.cart):
                with st.container(border=True):
                    c1, c2, c3 = st.columns([4, 2, 1])
                    with c1:
                        st.markdown(f"**{item['name']}** x{item['qty']}")
                        if item['options']: st.caption(f"+ {', '.join(item['options'])}")
                    with c2:
                        st.markdown(f"**{item['price']} บ.**")
                    with c3:
                        if st.button("❌", key=f"del_{i}"):
                            st.session_state.cart.pop(i)
                            st.rerun()
                total_price += item['price']
            
            st.markdown(f"### รวมทั้งสิ้น: :green[{total_price} บาท]")
            
            # Checkout Form
            with st.container(border=True):
                st.subheader("ข้อมูลจัดส่ง & ชำระเงิน")
                with st.form("checkout"):
                    c_name = st.text_input("ชื่อผู้รับ")
                    c_addr = st.text_area("ที่อยู่ / เบอร์โทร")
                    
                    st.write("---")
                    col_qr, col_up = st.columns(2)
                    with col_qr:
                        st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=PromptPay_{total_price}", caption="สแกนจ่ายได้เลย")
                    with col_up:
                        uploaded_slip = st.file_uploader("แนบสลิป", type=['jpg', 'png'])
                    
                    if st.form_submit_button("✅ ยืนยันการสั่งซื้อ", type="primary", use_container_width=True):
                        if c_name and c_addr and uploaded_slip:
                            order_id = f"ORD-{int(time.time())}"
                            new_order = {
                                "id": order_id,
                                "time": datetime.datetime.now().strftime("%H:%M"),
                                "customer": c_name,
                                "address": c_addr,
                                "items": st.session_state.cart,
                                "total": total_price,
                                "status": "รอการตรวจสอบ", # เริ่มต้นสถานะนี้
                                "slip_img": uploaded_slip
                            }
                            db.orders.append(new_order)
                            st.session_state.cart = []
                            st.balloons()
                            st.success(f"สั่งซื้อสำเร็จ! รหัสของคุณ: {order_id}")
                        else:
                            st.error("กรุณากรอกข้อมูลและแนบสลิปให้ครบถ้วน")

    # --- TAB 3: STATUS ---
    with tab_status:
        st.subheader("ติดตามสถานะ")
        search = st.text_input("ค้นหา (ชื่อ หรือ รหัสออเดอร์)")
        if search:
            found = False
            for order in reversed(db.orders):
                if search in order['customer'] or search in order['id']:
                    found = True
                    with st.container(border=True):
                        st.markdown(f"##### ออเดอร์ {order['id']}")
                        
                        # Logic Progress Bar ตามสถานะใหม่
                        status_flow = ["รอการตรวจสอบ", "กำลังทำอาหาร", "กำลังจัดส่ง", "จัดส่งสำเร็จ"]
                        current = order['status']
                        
                        if current == "ยกเลิก":
                            st.error("❌ ออเดอร์ถูกยกเลิก")
                        else:
                            # คำนวณ % Progress
                            try:
                                prog_index = status_flow.index(current)
                                prog_value = int(((prog_index + 1) / len(status_flow)) * 100)
                            except:
                                prog_value = 0
                            
                            st.progress(prog_value)
                            st.info(f"สถานะ: **{current}**")
                            
                        with st.expander("รายละเอียด"):
                             for item in order['items']:
                                st.write(f"- {item['name']} x{item['qty']}")
            if not found:
                st.warning("ไม่พบออเดอร์")

# ==========================================
# 👨‍🍳 ADMIN SIDE
# ==========================================
def admin_page():
    st.title("👨‍🍳 KanomJeen Manager")
    
    # Status List ใหม่ (สำหรับการเปลี่ยนสถานะ)
    status_options = ["รอการตรวจสอบ", "กำลังทำอาหาร", "กำลังจัดส่ง", "จัดส่งสำเร็จ", "ยกเลิก"]
    
    tab_orders, tab_menu, tab_dash = st.tabs(["📦 ออเดอร์", "✏️ เมนู", "📊 ยอดขาย"])
    
    with tab_orders:
        if not db.orders:
            st.info("ไม่มีออเดอร์ใหม่")
        else:
            for i, order in enumerate(reversed(db.orders)):
                real_idx = len(db.orders) - 1 - i
                with st.container(border=True):
                    c1, c2 = st.columns([2, 1])
                    with c1:
                        st.markdown(f"**#{order['id']}** | {order['time']} น.")
                        st.markdown(f"👤 **{order['customer']}**")
                        st.caption(f"🏠 {order['address']}")
                        st.markdown(f"💰 ยอด: **{order['total']} บาท**")
                        with st.expander("ดูสลิป & รายการ"):
                            if order.get('slip_img'): st.image(order['slip_img'], width=200)
                            for item in order['items']: st.write(f"- {item['name']} x{item['qty']}")
                    
                    with c2:
                        st.write("สถานะ:")
                        current = order['status']
                        # ป้องกัน error กรณีสถานะเก่าไม่ตรงกับ list ใหม่
                        idx = status_options.index(current) if current in status_options else 0
                        
                        new_stat = st.selectbox("เลือกสถานะ", status_options, index=idx, key=f"s_{order['id']}", label_visibility="collapsed")
                        
                        if new_stat != current:
                            db.update_order_status(real_idx, new_stat)
                            st.toast("อัปเดตสถานะแล้ว!")
                            time.sleep(1)
                            st.rerun()

    with tab_menu:
        for m_id, item in db.menu.items():
            with st.expander(f"⚙️ {item['name']}", expanded=False):
                c1, c2 = st.columns(2)
                np = c1.number_input(f"ราคา", value=item['price'], key=f"p_{m_id}")
                na = c2.toggle("เปิดขาย", value=item['active'], key=f"a_{m_id}")
                if np != item['price'] or na != item['active']:
                    db.update_menu(m_id, 'price', np)
                    db.update_menu(m_id, 'active', na)
                    st.rerun()
                    
    with tab_dash:
         if db.orders:
            total = sum(o['total'] for o in db.orders if o['status'] != 'ยกเลิก')
            st.metric("ยอดขายรวม", f"{total:,} บาท")
            st.dataframe(pd.DataFrame(db.orders)[['time','customer','total','status']])

# ==========================================
# 🧭 MAIN NAV
# ==========================================
with st.sidebar:
    st.header("KanomJeen App")
    page = st.radio("ไปที่", ["ลูกค้า", "ผู้จัดการร้าน"])

if page == "ลูกค้า":
    customer_page()
else:
    pwd = st.sidebar.text_input("Password", type="password")
    if pwd == "1234":
        admin_page()
