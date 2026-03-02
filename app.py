import streamlit as st
import pandas as pd
import datetime
import time

# ==========================================
# 🎨 0. CONFIG & CSS
# ==========================================
st.set_page_config(page_title="KanomJeen Manager", layout="centered", page_icon="🍜")

st.markdown("""
<style>
    /* Global Font & Button */
    .stButton>button { border-radius: 12px; font-weight: 600; }
    
    /* Card สินค้า */
    div[data-testid="stVerticalBlock"] > div[style*="flex-direction: column;"] > div[data-testid="stVerticalBlock"] {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    /* 🛒 Sticky Footer (แถบตะกร้าลอยด้านล่าง) */
    .sticky-footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #FF4B4B;
        color: white;
        text-align: center;
        padding: 15px 10px;
        font-size: 18px;
        font-weight: bold;
        z-index: 9999;
        box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
        border-top-left-radius: 15px;
        border-top-right-radius: 15px;
    }
    .sticky-footer a {
        color: white; 
        text-decoration: none;
    }
    
    /* ซ่อน Footer เดิมของ Streamlit เพื่อความเนียน */
    footer {visibility: hidden;}
    
</style>
""", unsafe_allow_html=True)

# ==========================================
# 🕒 1. HELPER FUNCTIONS
# ==========================================
def get_thai_now():
    return datetime.datetime.utcnow() + datetime.timedelta(hours=7)

def get_thai_time_str():
    return get_thai_now().strftime("%d/%m/%Y %H:%M")

def play_notification_sound():
    # ฝัง HTML5 Audio เพื่อเล่นเสียงแจ้งเตือน
    audio_html = """
        <audio autoplay>
        <source src="https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3" type="audio/mpeg">
        </audio>
    """
    st.markdown(audio_html, unsafe_allow_html=True)

# ==========================================
# 💾 2. DATABASE & STATE
# ==========================================
@st.cache_resource
class FoodSystemDB:
    def __init__(self):
        self.menu = {
            "m1": {"name": "ขนมจีนน้ำเงี้ยว", "price": 45, "img": "https://i.postimg.cc/637Jz9Zs/Gemini_Generated_Image_bcsz82bcsz82bcsz.png", "active": True, "options": {"เพิ่มเส้น": 5, "เพิ่มเครื่อง": 10}},
#            "m2": {"name": "ข้าวซอยไก่", "price": 50, "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/15/Khao_Soi_Kai.jpg/800px-Khao_Soi_Kai.jpg", "active": True, "options": {"น่องลาย": 10, "พิเศษ": 10}},
            "m3": {"name": "แคบหมูไร้มัน", "price": 15, "img": "https://i.postimg.cc/1z71pg8h/Gemini_Generated_Image_kjdzbkjdzbkjdzbk.png", "active": True, "options": {}},
#            "m4": {"name": "ไส้อั่วสมุนไพร", "price": 60, "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/89/Sai_ua_สมุนไพร.jpg/800px-Sai_ua_สมุนไพร.jpg", "active": True, "options": {"ข้าวเหนียว": 10}},
#            "m5": {"name": "น้ำพริกหนุ่ม", "price": 40, "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a3/Nam_phrik_num.jpg/800px-Nam_phrik_num.jpg", "active": True, "options": {"ไข่ต้ม": 10}},
        }
        self.orders = []

    def update_order_status(self, order_index, new_status):
        self.orders[order_index]['status'] = new_status
        
    def update_menu(self, menu_id, field, value):
        self.menu[menu_id][field] = value

    def add_option(self, menu_id, opt_name, opt_price):
        self.menu[menu_id]['options'][opt_name] = opt_price

    def remove_option(self, menu_id, opt_name):
        if opt_name in self.menu[menu_id]['options']:
            del self.menu[menu_id]['options'][opt_name]

db = FoodSystemDB()

# State สำหรับลูกค้า
if 'cart' not in st.session_state:
    st.session_state.cart = []

# State สำหรับ Admin (เพื่อจำจำนวนออเดอร์เก่า ไว้เทียบกับอันใหม่)
if 'last_order_count' not in st.session_state:
    st.session_state.last_order_count = 0

# ==========================================
# 🛍️ UI COMPONENTS
# ==========================================
def render_header():
    st.image("https://i.postimg.cc/637Jz9Zs/Gemini_Generated_Image_bcsz82bcsz82bcsz.png", use_column_width=True)
    st.title("🍜 KanomJeen Weekend")
    st.caption(f"เวลาปัจจุบัน: {get_thai_time_str()} น.")

def render_sticky_footer():
    """แสดงแถบสรุปยอดเงินด้านล่างสุด"""
    if st.session_state.cart:
        total = sum(item['price'] for item in st.session_state.cart)
        count = sum(item['qty'] for item in st.session_state.cart)
        # HTML Injection สำหรับ Sticky Footer
        st.markdown(f"""
            <div class="sticky-footer">
                🛒 ในตะกร้า {count} ชิ้น | รวม <b>{total}</b> บาท <br>
                <span style="font-size:0.8em; font-weight:normal;">(กดที่ Tab 'ตะกร้าสินค้า' ด้านบนเพื่อชำระเงิน)</span>
            </div>
        """, unsafe_allow_html=True)

# ==========================================
# 🛒 CUSTOMER FLOW
# ==========================================
def customer_page():
    render_header()

    tab_menu, tab_cart, tab_status = st.tabs(["📋 เมนูอาหาร", "🛒 ตะกร้าสินค้า", "🚚 เช็คสถานะ"])

    # --- TAB 1: MENU ---
    with tab_menu:
        # Layout 2 Column
        col1, col2 = st.columns(2)
        cols = [col1, col2]
        active_items = [(k, v) for k, v in db.menu.items() if v['active']]
        
        for index, (m_id, item) in enumerate(active_items):
            with cols[index % 2]:
                with st.container(border=True):
                    st.image(item['img'], use_column_width=True)
                    st.markdown(f"**{item['name']}**")
                    st.markdown(f":red[**{item['price']} บาท**]")
                    
                    with st.form(key=f"form_{m_id}", border=False):
                        selected_opts = []
                        extra_price = 0
                        if item['options']:
                            st.caption("เลือกเพิ่มเติม:")
                            opt_choices = [f"{k} (+{v})" for k,v in item['options'].items()]
                            selection = st.multiselect("Option", opt_choices, label_visibility="collapsed", key=f"sel_{m_id}")
                            
                            for s in selection:
                                raw_name = s.split(" (+")[0]
                                price_val = int(s.split(" (+")[1].replace(")", ""))
                                selected_opts.append(raw_name)
                                extra_price += price_val
                        
                        qty = st.number_input("จำนวน", 1, 20, 1, key=f"qty_{m_id}")
                        
                        # ปุ่มเพิ่มลงตะกร้า
                        if st.form_submit_button("➕ ใส่ตะกร้า", type="primary", use_container_width=True):
                            final_price = (item['price'] + extra_price) * qty
                            st.session_state.cart.append({
                                "id": m_id, 
                                "name": item['name'], 
                                "options": selected_opts,
                                "qty": qty, 
                                "price": final_price,
                                "unit_price": item['price'] + extra_price
                            })
                            st.toast(f"เพิ่ม {item['name']} แล้ว", icon="✅")
                            time.sleep(0.5)
                            st.rerun()
        
        # เรียกใช้ Sticky Footer (จะทำงานเมื่อมีของในตะกร้า)
        render_sticky_footer()

    # --- TAB 2: CART ---
    with tab_cart:
        if not st.session_state.cart:
            st.info("ตะกร้ายังว่างอยู่ครับ")
        else:
            total_price = sum(i['price'] for i in st.session_state.cart)
            st.markdown(f"### รวมทั้งหมด: :green[{total_price} บาท]")
            
            for i, item in enumerate(st.session_state.cart):
                with st.container(border=True):
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        st.markdown(f"**{item['name']}** x{item['qty']}")
                        if item['options']:
                            st.caption(f"เสริม: {', '.join(item['options'])}")
                    with c2:
                        st.markdown(f"**{item['price']} บ.**")
                        if st.button("ลบ", key=f"del_{i}"):
                            st.session_state.cart.pop(i)
                            st.rerun()
            
            st.divider()
            with st.form("checkout"):
                st.subheader("ยืนยันคำสั่งซื้อ")
                c_name = st.text_input("ชื่อลูกค้า")
                c_addr = st.text_area("ที่อยู่จัดส่ง / เบอร์โทร")
                
                col_qr, col_upl = st.columns(2)
                with col_qr:
                    st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=PromptPay_{total_price}", caption="QR PromptPay")
                with col_upl:
                    uploaded_slip = st.file_uploader("แนบสลิปโอนเงิน", type=['jpg', 'png'])

                if st.form_submit_button("✅ สั่งซื้อทันที", type="primary", use_container_width=True):
                    if c_name and c_addr and uploaded_slip:
                        order_id = f"ORD-{int(time.time())}"
                        new_order = {
                            "id": order_id,
                            "timestamp": get_thai_now(),
                            "time_str": get_thai_time_str(),
                            "customer": c_name,
                            "address": c_addr,
                            "items": st.session_state.cart,
                            "total": total_price,
                            "status": "รอการตรวจสอบ",
                            "slip_img": uploaded_slip
                        }
                        db.orders.append(new_order)
                        st.session_state.cart = []
                        st.balloons()
                        st.success(f"สั่งซื้อสำเร็จ! รหัสออเดอร์: {order_id}")
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error("กรุณากรอกข้อมูลให้ครบถ้วน")

    # --- TAB 3: STATUS ---
    with tab_status:
        st.subheader("🔍 ติดตามพัสดุ")
        search = st.text_input("ค้นหา (ชื่อ หรือ รหัสออเดอร์)")
        if search:
            found = False
            for order in reversed(db.orders):
                if search in order['customer'] or search in order['id']:
                    found = True
                    with st.container(border=True):
                        st.markdown(f"##### ออเดอร์ {order['id']}")
                        st.caption(f"สั่งเมื่อ: {order['time_str']}")
                        
                        flow = ["รอการตรวจสอบ", "กำลังทำอาหาร", "กำลังจัดส่ง", "จัดส่งสำเร็จ"]
                        curr = order['status']
                        if curr == "ยกเลิก":
                            st.error("❌ ออเดอร์นี้ถูกยกเลิก")
                        else:
                            try:
                                pct = int(((flow.index(curr) + 1) / len(flow)) * 100)
                            except: pct = 0
                            st.progress(pct)
                            st.info(f"สถานะ: **{curr}**")

# ==========================================
# 👨‍🍳 ADMIN SIDE
# ==========================================
def admin_page():
    st.title("👨‍🍳 KanomJeen Manager")
    
    # --- Notification Logic ---
    # ตรวจสอบว่ามีออเดอร์เพิ่มขึ้นหรือไม่
    current_order_count = len(db.orders)
    if current_order_count > st.session_state.last_order_count:
        # มีออเดอร์ใหม่!
        st.toast(f"🔔 มีออเดอร์ใหม่เข้ามา! (รวม {current_order_count})", icon="🔥")
        play_notification_sound()
        st.session_state.last_order_count = current_order_count # อัปเดตตัวนับ

    # Toggle สำหรับ Auto-refresh
    col_head, col_toggle = st.columns([3, 1])
    with col_head:
        st.caption(f"Last Update: {get_thai_time_str()}")
    with col_toggle:
        auto_refresh = st.toggle("🔴 โหมดรับออเดอร์ (Live)", value=False)
    
    if auto_refresh:
        time.sleep(10) # รีเฟรชทุก 10 วินาที
        st.rerun()

    # Tabs
    tab_orders, tab_menu, tab_analytics = st.tabs(["📦 ออเดอร์", "🛠️ เมนู/Option", "📊 สรุปยอด"])
    
    # --- ADMIN: ORDERS ---
    with tab_orders:
        status_opts = ["รอการตรวจสอบ", "กำลังทำอาหาร", "กำลังจัดส่ง", "จัดส่งสำเร็จ", "ยกเลิก"]
        
        if not db.orders:
            st.info("ยังไม่มีออเดอร์")
        
        for i, order in enumerate(reversed(db.orders)):
            real_idx = len(db.orders) - 1 - i
            with st.container(border=True):
                c1, c2 = st.columns([2, 1])
                with c1:
                    st.markdown(f"#### #{order['id']} | {order['customer']}")
                    st.caption(f"🕒 {order['time_str']} | 🏠 {order['address']}")
                    st.markdown("---")
                    for item in order['items']:
                        opt_str = f" (+ {', '.join(item['options'])})" if item['options'] else ""
                        st.write(f"• **{item['name']}** x{item['qty']} {opt_str}")
                    st.markdown(f"💰 ยอดรวม: **{order['total']} บาท**")
                    if order.get('slip_img'):
                        st.expander("ดูสลิป").image(order['slip_img'])
                
                with c2:
                    curr_stat = order['status']
                    idx = status_opts.index(curr_stat) if curr_stat in status_opts else 0
                    new_stat = st.selectbox("Status", status_opts, index=idx, key=f"st_{order['id']}", label_visibility="collapsed")
                    if new_stat != curr_stat:
                        db.update_order_status(real_idx, new_stat)
                        st.rerun()

    # --- ADMIN: MENU ---
    with tab_menu:
        for m_id, item in db.menu.items():
            with st.expander(f"⚙️ {item['name']}", expanded=False):
                c1, c2 = st.columns([2, 1])
                np = c1.number_input("ราคา", value=item['price'], key=f"p_{m_id}")
                na = c2.toggle("Active", value=item['active'], key=f"a_{m_id}")
                ni = st.text_input("IMG URL", value=item['img'], key=f"i_{m_id}")
                
                if np != item['price'] or na != item['active'] or ni != item['img']:
                    db.update_menu(m_id, 'price', np)
                    db.update_menu(m_id, 'active', na)
                    db.update_menu(m_id, 'img', ni)
                    st.rerun()
                
                st.write("**Options:**")
                if item['options']:
                    for oname, oval in item['options'].items():
                        oc1, oc2 = st.columns([3, 1])
                        oc1.text(f"{oname} (+{oval})")
                        if oc2.button("ลบ", key=f"d_{m_id}_{oname}"):
                            db.remove_option(m_id, oname)
                            st.rerun()
                
                with st.form(key=f"add_opt_{m_id}"):
                    c_n, c_p = st.columns(2)
                    new_n = c_n.text_input("ชื่อ Option")
                    new_p = c_p.number_input("ราคาบวก", 0)
                    if st.form_submit_button("เพิ่ม"):
                        if new_n:
                            db.add_option(m_id, new_n, new_p)
                            st.rerun()

    # --- ADMIN: ANALYTICS ---
    with tab_analytics:
        if db.orders:
            valid = [o for o in db.orders if o['status'] != 'ยกเลิก']
            rev = sum(o['total'] for o in valid)
            st.metric("ยอดขายรวม", f"{rev:,} บาท")
            
            # Best Seller
            items = []
            for o in valid:
                for i in o['items']: items.append(i['name'])
            if items:
                st.write("สินค้าขายดี:")
                st.bar_chart(pd.Series(items).value_counts())

# ==========================================
# 🧭 MAIN NAVIGATION
# ==========================================
with st.sidebar:
    st.header("KanomJeen App")
    st.caption(f"Current Time: {get_thai_time_str()}")
    page = st.radio("Mode", ["ลูกค้า", "Admin"])

if page == "ลูกค้า":
    customer_page()
else:
    pwd = st.sidebar.text_input("Password", type="password")
    if pwd == "1234":
        admin_page()
