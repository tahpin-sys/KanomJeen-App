import streamlit as st
import pandas as pd
import datetime
import time

# ==========================================
# 🎨 0. CONFIG & CSS
# ==========================================
st.set_page_config(page_title="KanomJeen App", layout="centered", page_icon="🍜")

st.markdown("""
<style>
    /* ปรับ Font และ Button */
    .stButton>button { border-radius: 10px; font-weight: 600; }
    
    /* Card สินค้า */
    div[data-testid="stVerticalBlock"] > div[style*="flex-direction: column;"] > div[data-testid="stVerticalBlock"] {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    /* Highlight สถานะ */
    .status-badge {
        padding: 5px 10px;
        border-radius: 15px;
        font-size: 0.8em;
        font-weight: bold;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 🕒 1. HELPER FUNCTIONS (TIMEZONE)
# ==========================================
def get_thai_now():
    """แปลงเวลา Server (UTC) เป็นเวลาไทย (UTC+7)"""
    return datetime.datetime.utcnow() + datetime.timedelta(hours=7)

def get_thai_time_str():
    """คืนค่าเวลาไทยแบบ String สวยๆ"""
    return get_thai_now().strftime("%d/%m/%Y %H:%M")

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

    # ฟังก์ชันจัดการ Option
    def add_option(self, menu_id, opt_name, opt_price):
        self.menu[menu_id]['options'][opt_name] = opt_price

    def remove_option(self, menu_id, opt_name):
        if opt_name in self.menu[menu_id]['options']:
            del self.menu[menu_id]['options'][opt_name]

db = FoodSystemDB()

if 'cart' not in st.session_state:
    st.session_state.cart = []

# ==========================================
# 🛍️ UI COMPONENTS
# ==========================================
def render_header():
    st.image("https://i.postimg.cc/637Jz9Zs/Gemini_Generated_Image_bcsz82bcsz82bcsz.png", use_column_width=True)
    st.title("🍜 KanomJeen Weekend")
    st.caption(f"อร่อยเหมือนกินที่เชียงใหม่ (เวลาปัจจุบัน: {get_thai_time_str()} น.)")

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
                        # Show Options Dynamically
                        selected_opts = []
                        extra_price = 0
                        if item['options']:
                            st.caption("เลือกเพิ่มเติม:")
                            # ใช้ Multiselect เพื่อเลือกหลาย option
                            # Format: "ชื่อ (+ราคา)"
                            opt_choices = [f"{k} (+{v})" for k,v in item['options'].items()]
                            selection = st.multiselect("Option", opt_choices, label_visibility="collapsed", key=f"sel_{m_id}")
                            
                            for s in selection:
                                # แกะชื่อและราคาออกจาก String เช่น "เพิ่มเส้น (+5)"
                                raw_name = s.split(" (+")[0]
                                price_val = int(s.split(" (+")[1].replace(")", ""))
                                selected_opts.append(raw_name)
                                extra_price += price_val
                        
                        qty = st.number_input("จำนวน", 1, 20, 1, key=f"qty_{m_id}")
                        
                        if st.form_submit_button("➕ ใส่ตะกร้า", type="primary", use_container_width=True):
                            final_price = (item['price'] + extra_price) * qty
                            st.session_state.cart.append({
                                "id": m_id, 
                                "name": item['name'], 
                                "options": selected_opts, # เก็บเป็น List ชื่อ Option
                                "qty": qty, 
                                "price": final_price,
                                "unit_price": item['price'] + extra_price
                            })
                            st.toast(f"เพิ่ม {item['name']} ลงตะกร้าแล้ว", icon="✅")
                            time.sleep(0.5)
                            st.rerun()

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
                    st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=PromptPay_{total_price}", caption="QR แม่มณี / PromptPay")
                with col_upl:
                    uploaded_slip = st.file_uploader("แนบสลิปโอนเงิน", type=['jpg', 'png'])

                if st.form_submit_button("✅ สั่งซื้อทันที", type="primary", use_container_width=True):
                    if c_name and c_addr and uploaded_slip:
                        # สร้าง Order Object
                        order_id = f"ORD-{int(time.time())}"
                        new_order = {
                            "id": order_id,
                            "timestamp": get_thai_now(), # เก็บเป็น Object เพื่อ sort ง่าย
                            "time_str": get_thai_time_str(), # เก็บ String ไว้โชว์
                            "customer": c_name,
                            "address": c_addr,
                            "items": st.session_state.cart,
                            "total": total_price,
                            "status": "รอการตรวจสอบ",
                            "slip_img": uploaded_slip
                        }
                        db.orders.append(new_order)
                        st.session_state.cart = [] # Clear
                        st.balloons()
                        st.success(f"สั่งซื้อสำเร็จ! รหัสออเดอร์: {order_id}")
                    else:
                        st.error("กรุณากรอกข้อมูลให้ครบถ้วน")

    # --- TAB 3: STATUS ---
    with tab_status:
        st.subheader("🔍 ติดตามพัสดุ / อาหาร")
        search = st.text_input("ค้นหา (ชื่อ หรือ รหัสออเดอร์)")
        if search:
            found = False
            for order in reversed(db.orders):
                if search in order['customer'] or search in order['id']:
                    found = True
                    with st.container(border=True):
                        st.markdown(f"##### ออเดอร์ {order['id']}")
                        st.caption(f"สั่งเมื่อ: {order['time_str']}")
                        
                        # Logic Status Bar
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
    st.caption(f"Login Time: {get_thai_time_str()}")
    
    tab_orders, tab_menu, tab_analytics = st.tabs(["📦 จัดการออเดอร์", "🛠️ แก้ไขเมนู & Option", "📊 สรุปยอดขายละเอียด"])
    
    # --- ADMIN: ORDERS ---
    with tab_orders:
        status_opts = ["รอการตรวจสอบ", "กำลังทำอาหาร", "กำลังจัดส่ง", "จัดส่งสำเร็จ", "ยกเลิก"]
        
        if not db.orders:
            st.info("ยังไม่มีออเดอร์เข้ามาวันนี้")
        
        # วนลูปแสดงออเดอร์
        for i, order in enumerate(reversed(db.orders)):
            real_idx = len(db.orders) - 1 - i
            
            # การ์ดออเดอร์
            with st.container(border=True):
                c1, c2 = st.columns([2, 1])
                with c1:
                    st.markdown(f"#### #{order['id']} | คุณ {order['customer']}")
                    st.caption(f"🕒 {order['time_str']} | 🏠 {order['address']}")
                    
                    # แสดงรายการอาหาร พร้อม Option (Requirement: Admin ต้องเห็น Option)
                    st.markdown("---")
                    for item in order['items']:
                        opt_str = f" (+ {', '.join(item['options'])})" if item['options'] else ""
                        st.write(f"• **{item['name']}** x{item['qty']} {opt_str}")
                    st.markdown("---")
                    st.markdown(f"💰 ยอดรวม: **{order['total']} บาท**")
                    
                    if order.get('slip_img'):
                        with st.expander("ดูสลิปโอนเงิน"):
                            st.image(order['slip_img'], width=250)
                
                with c2:
                    st.write("สถานะปัจจุบัน:")
                    curr_stat = order['status']
                    # Selectbox เปลี่ยนสถานะ
                    idx = status_opts.index(curr_stat) if curr_stat in status_opts else 0
                    new_stat = st.selectbox("Update Status", status_opts, index=idx, key=f"st_{order['id']}", label_visibility="collapsed")
                    
                    if new_stat != curr_stat:
                        db.update_order_status(real_idx, new_stat)
                        st.toast(f"อัปเดตออเดอร์ {order['id']} แล้ว!")
                        time.sleep(1)
                        st.rerun()

    # --- ADMIN: MENU & OPTIONS ---
    with tab_menu:
        st.info("💡 Tip: คุณสามารถ เพิ่ม/ลบ Option ของแต่ละเมนูได้ที่นี่")
        for m_id, item in db.menu.items():
            with st.expander(f"⚙️ แก้ไข: {item['name']}", expanded=False):
                # 1. แก้ไขข้อมูลพื้นฐาน
                c1, c2, c3 = st.columns([2, 1, 1])
                new_price = c1.number_input("ราคาหลัก", value=item['price'], key=f"p_{m_id}")
                new_active = c2.toggle("เปิดขาย", value=item['active'], key=f"a_{m_id}")
                new_img = c3.text_input("URL รูป", value=item['img'], key=f"i_{m_id}")
                
                # Update พื้นฐานทันที
                if new_price != item['price'] or new_active != item['active'] or new_img != item['img']:
                    db.update_menu(m_id, 'price', new_price)
                    db.update_menu(m_id, 'active', new_active)
                    db.update_menu(m_id, 'img', new_img)
                    st.rerun()

                st.markdown("---")
                st.markdown("**จัดการ Option (ตัวเลือกเสริม)**")
                
                # 2. แสดง Option ที่มีอยู่
                if item['options']:
                    for opt_name, opt_val in item['options'].items():
                        oc1, oc2, oc3 = st.columns([3, 2, 1])
                        oc1.text(f"• {opt_name}")
                        oc2.text(f"+{opt_val} บาท")
                        if oc3.button("ลบ", key=f"del_opt_{m_id}_{opt_name}"):
                            db.remove_option(m_id, opt_name)
                            st.rerun()
                else:
                    st.caption("เมนูนี้ยังไม่มีตัวเลือกเสริม")

                # 3. เพิ่ม Option ใหม่
                with st.form(key=f"add_opt_{m_id}"):
                    ac1, ac2 = st.columns([3, 2])
                    new_opt_name = ac1.text_input("ชื่อตัวเลือก (เช่น ไข่ต้ม)", key=f"nopt_{m_id}")
                    new_opt_price = ac2.number_input("ราคาบวกเพิ่ม", min_value=0, value=5, key=f"popt_{m_id}")
                    
                    if st.form_submit_button("เพิ่ม Option"):
                        if new_opt_name:
                            db.add_option(m_id, new_opt_name, new_opt_price)
                            st.success("เพิ่มเรียบร้อย")
                            st.rerun()

    # --- ADMIN: ANALYTICS ---
    with tab_analytics:
        if not db.orders:
            st.warning("ยังไม่มีข้อมูลการขาย")
        else:
            # เตรียมข้อมูล (Data Preparation)
            valid_orders = [o for o in db.orders if o['status'] != 'ยกเลิก']
            
            # 1. KPI Cards
            total_rev = sum(o['total'] for o in valid_orders)
            total_ord = len(valid_orders)
            if total_ord > 0:
                avg_ticket = total_rev / total_ord
            else:
                avg_ticket = 0
                
            k1, k2, k3 = st.columns(3)
            k1.metric("💰 รายได้รวม", f"{total_rev:,} บาท")
            k2.metric("🧾 ออเดอร์สำเร็จ", f"{total_ord} รายการ")
            k3.metric("📈 เฉลี่ยต่อบิล", f"{avg_ticket:.0f} บาท")
            
            st.markdown("---")

            # 2. แยกรายละเอียดรายเมนู (Item Breakdown)
            st.subheader("🏆 เมนูขายดี (Best Sellers)")
            
            # ระเบิด Data (Explode) จาก Order -> Items
            all_sold_items = []
            for o in valid_orders:
                for item in o['items']:
                    all_sold_items.append({
                        "Menu": item['name'],
                        "Qty": item['qty'],
                        "Total": item['price']
                    })
            
            if all_sold_items:
                df_items = pd.DataFrame(all_sold_items)
                
                # Group By Menu
                df_grouped = df_items.groupby("Menu").sum().reset_index()
                df_grouped = df_grouped.sort_values(by="Qty", ascending=False)
                
                # แสดงเป็น Bar Chart
                st.bar_chart(df_grouped.set_index("Menu")["Qty"])
                
                # แสดงเป็นตาราง
                st.dataframe(df_grouped, use_container_width=True)
            
            st.markdown("---")
            
            # 3. ช่วงเวลาขายดี (Time Analysis)
            st.subheader("⏰ ช่วงเวลาที่มีการสั่งซื้อ")
            order_times = [o['timestamp'].hour for o in valid_orders]
            df_time = pd.DataFrame(order_times, columns=["Hour"])
            hour_counts = df_time['Hour'].value_counts().sort_index()
            st.bar_chart(hour_counts)
            st.caption("แกน X: ชั่วโมง (0-23) | แกน Y: จำนวนออเดอร์")

# ==========================================
# 🧭 MAIN NAVIGATION
# ==========================================
with st.sidebar:
    st.header("KanomJeen App")
    st.caption(f"Current Time (TH): {get_thai_time_str()}")
    page = st.radio("เลือกโหมดใช้งาน", ["ลูกค้าสั่งอาหาร", "เจ้าของร้าน (Admin)"])

if page == "ลูกค้าสั่งอาหาร":
    customer_page()
else:
    pwd = st.sidebar.text_input("รหัสผ่าน Admin", type="password")
    if pwd == "1234":
        admin_page()
    elif pwd:
        st.error("รหัสผ่านไม่ถูกต้อง")
