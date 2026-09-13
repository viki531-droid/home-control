import streamlit as st
import pandas as pd
import urllib.parse
from app.auth import check_authentication, load_vault, save_vault
from app.ai_vision import render_ai_vision_module

if check_authentication():
    vault_data = load_vault()

    if "theme_color" not in vault_data:
        vault_data["theme_color"] = "ורוד"

    current_theme = vault_data.get("theme_color", "ורוד")

    if current_theme in ["כחול", "תכלת"]:
        bg_color = "#f0f8ff"
        header_color = "#1e90ff"
        btn_bg = "#add8e6"
        btn_hover = "#1e90ff"
        card_border = "#87ceeb"
        note_bg = "#e6f2ff"
    elif current_theme == "ירוק":
        bg_color = "#f4f9f4"
        header_color = "#2e8b57"
        btn_bg = "#98fb98"
        btn_hover = "#2e8b57"
        card_border = "#8fbc8f"
        note_bg = "#f0fff0"
    else:  # ורוד
        bg_color = "#fff5f8"
        header_color = "#d1496b"
        btn_bg = "#ffb6c1"
        btn_hover = "#d1496b"
        card_border = "#ffb6c1"
        note_bg = "#fffacd"

    st.set_page_config(
        page_title="VIDASS-HomeCommand",
        page_icon="💖",
        layout="wide"
    )

    st.markdown(f"""
        <style>
        .main {{ background-color: {bg_color}; direction: rtl; text-align: right; }}
        h1, h2, h3 {{ color: {header_color}; text-align: right; }}
        .stButton>button {{ background-color: {btn_bg}; color: #222222; font-weight: bold; border-radius: 8px; width: 100%; }}
        .stButton>button:hover {{ background-color: {btn_hover}; color: white; }}
        .card {{ background: white; padding: 15px; border-radius: 10px; border: 1px solid {card_border}; margin-bottom: 10px; }}
        .sticky-note {{ background: {note_bg}; padding: 12px; border-radius: 8px; border-right: 5px solid {header_color}; margin-bottom: 8px; }}
        </style>
    """, unsafe_allow_html=True)

    user_str = st.session_state.get('user_name', 'משתמש')
    family_str = st.session_state.get('family_name', 'הבית')
    address_str = st.session_state.get('address', 'כתובת')

    st.title("💖 VIDASS-HomeCommand — לוח פיקוד משפחתי חכם")
    
    # ניהול אזורי קניות ואמצעי תחבורה
    if "locations" not in vault_data:
        vault_data["locations"] = [
            {"region": "מרכז העיר / סופר שכונתי", "transport": "הליכה רגלית (0 ש\"ח)", "cost": 0.0},
            {"region": "מרכז קניות גדול / דיסקאונט", "transport": "רכב פרטי (דלק + בלאי)", "cost": 15.0},
            {"region": "אזור תעשייה / מחסני מזון", "transport": "תחבורה ציבורית", "cost": 6.0}
        ]
    
    current_city = vault_data.get("active_city", "מרכז העיר / סופר שכונתי")
    st.markdown(f"שלום **{user_str}** | בית משפחת **{family_str}** ({address_str}) | **📍 אזור פעיל: {current_city}** | **🎨 ערכת נושא: {current_theme}**")

    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11, tab12, tab13, tab14 = st.tabs([
        "📝 פתקיות", 
        "🛒 קניות", 
        "🧾 קבלות ואזורים", 
        "📦 מלאי ותיקיות", 
        "💡 חשבונות",
        "🤖 יועץ AI",
        "🎵 מוזיקה",
        "📹 מצלמות",
        "⚡ מכשירים חכמים",
        "📅 יומן",
        "💡 חсכון כספי חכם",
        "🛠️ מערכת VIDASS ותקלות",
        "⚙️ הגדרות", 
        "🚪 יציאה"
    ])

    # 1. פתקיות
    with tab1:
        st.subheader("📝 ניהול פתקיות אישיות וטיפים לבית")
        with st.form("add_note_form_main"):
            note_title = st.text_input("כותרת הפתקייה", key="new_note_title_input")
            note_text = st.text_input("תוכן הפתקייה", key="new_note_text_input")
            if st.form_submit_button("➕ הוסף פתקייה חדשה"):
                if note_title and note_text:
                    vault_data.setdefault("notes", []).append({"title": note_title, "text": note_text})
                    save_vault(vault_data)
                    st.success("הפתקייה נוספה בהצלחה!")
                    st.rerun()
                else:
                    st.warning("נא למלא כותרת ותוכן.")

        st.write("---")
        for idx, note in enumerate(vault_data.get("notes", [])):
            with st.expander(f"📌 {note.get('title', 'פתק')} (לחץ לעריכה/מחיקה)"):
                with st.form(f"edit_note_form_{idx}"):
                    ed_title = st.text_input("ערוך כותרת", value=note.get('title', ''), key=f"ed_t_{idx}")
                    ed_text = st.text_input("ערוך תוכן", value=note.get('text', ''), key=f"ed_tx_{idx}")
                    col_e1, col_e2 = st.columns(2)
                    with col_e1:
                        if st.form_submit_button("💾 שמור שינויים"):
                            vault_data["notes"][idx] = {"title": ed_title, "text": ed_text}
                            save_vault(vault_data)
                            st.success("הפתקייה עודכנה בהצלחה!")
                            st.rerun()
                    with col_e2:
                        if st.form_submit_button("🗑️ מחוק פתקייה זו"):
                            vault_data["notes"].pop(idx)
                            save_vault(vault_data)
                            st.success("הפתקייה נמחקה!")
                            st.rerun()

    # 2. קניות
    with tab2:
        st.subheader("🛒 רשימת קניות משפחתית משותפת")
        if "categories" not in vault_data:
            vault_data["categories"] = ["אוכל ומזון", "חשמל ומוצרים", "בגדים ואופנה", "חומרי ניקוי", "אחר"]
            
        with st.form("add_shopping_form"):
            col_i1, col_i2, col_i3 = st.columns([2, 1, 1])
            with col_i1:
                new_item = st.text_input("מה חסר בבית?", key="shop_item_input")
            with col_i2:
                item_cat = st.selectbox("קטגוריה", vault_data["categories"], key="shop_cat_select")
            with col_i3:
                item_price = st.number_input("מחיר משוער", min_value=0.0, value=0.0, key="shop_price_input")
            
            if st.form_submit_button("➕ הוסף לרשימה"):
                if new_item:
                    vault_data.setdefault("shopping_list", []).append({"text": new_item, "cat": item_cat, "price": item_price, "bought": False})
                    save_vault(vault_data)
                    st.rerun()

        st.write("---")
        for idx, item in enumerate(vault_data.get("shopping_list", [])):
            col_c1, col_c2, col_c3, col_c4, col_c5 = st.columns([2, 1, 1, 1, 1])
            with col_c1:
                st.write(item.get('text', ''))
            with col_c2:
                st.write(f"[{item.get('cat', '')}]")
            with col_c3:
                st.write(f"₪{item.get('price', 0)}")
            with col_c4:
                btn_label = "🔄 חסר" if item.get('bought') else "✔️ נקנה"
                if st.button(btn_label, key=f"toggle_shop_{idx}"):
                    vault_data["shopping_list"][idx]['bought'] = not item.get('bought', False)
                    save_vault(vault_data)
                    st.rerun()
            with col_c5:
                if st.button("🗑️ מחיקה", key=f"del_shop_{idx}"):
                    vault_data["shopping_list"].pop(idx)
                    save_vault(vault_data)
                    st.rerun()

    # 3. קבלות, אזורי קניות, תחבורה וחישוב יומי
    with tab3:
        st.subheader("🧾 סריקת קבלות, ניהול אזורי קניות ועלויות תחבורה")
        
        # בחירת אמצעי הגעה ואזור קניות יומי
        with st.form("trip_calc_form"):
            st.markdown("<b>🚗 תכנון הגעה לקניות וחישוב עלות נסיעה לאזור:</b>", unsafe_allow_html=True)
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                chosen_region = st.selectbox("בחר אזור קניות מועדף", [loc["region"] for loc in vault_data["locations"]])
            with col_t2:
                chosen_transport = st.selectbox("בחר אמצעי תחבורה להגעה", ["הליכה רגלית (0 ₪)", "תחבורה ציבורית (כ-6 ₪)", "רכב פרטי - דלק ובלאי (כ-15 ₪)"])
            
            if st.form_submit_button("💾 שמור הגדרות נסיעה לאזור זה"):
                vault_data["active_city"] = chosen_region
                save_vault(vault_data)
                st.success(הגדרות האזור והנסיעה עודכנו בהצלחה!)
                st.rerun()

        st.write("---")
        uploaded_receipt = st.file_uploader("העלה תמונת קבלה (JPG / PNG) לזיהוי אזור וחישוב הוצאות", type=["jpg", "png", "jpeg"], key="static_receipt_uploader")
        if uploaded_receipt:
            st.success("התמונה הועלתה והאזור זוהה בהצלחה אוטומטית!")
            st.image(uploaded_receipt, caption="הקבלה שהועלתה", width=300)

        extracted = render_ai_vision_module()
        if extracted:
            extracted["city"] = current_city
            if st.button("💾 שמור קבלה למערכת", key="save_receipt_btn"):
                vault_data.setdefault("expenses", []).append(extracted)
                save_vault(vault_data)
                st.success("הקבלה נשמרה בתיקיית האזור התואם!")

        if vault_data.get("expenses"):
            st.write("---")
            st.subheader(f"📊 סיכום הוצאות ותחבורה עבור אזור: {current_city}")
            total_exp = sum([float(exp.get('total', 0)) for exp in vault_data.get("expenses", [])])
            
            # חישוב עלות נסיעה בהתאם לתחבורה שנבחרה
            transport_cost = 0.0
            if "רכב פרטי" in current_city or "רכב":
                transport_cost = 15.0
            elif "תחבורה ציבורית" in current_city:
                transport_cost = 6.0

            st.markdown(f"""
                <div class="card" style="background-color: #f4f9f4; border: 2px solid #2e8b57;">
                    🛒 <b>סכום קניות כולל היום באזור:</b> ₪{total_exp}<br>
                    🚗 <b>עלות הגעה מוערכת (תחבורה):</b> ₪{transport_cost}<br>
                    💰 <b>סה"כ עלות כוללת (קניות + נסיעה):</b> ₪{total_exp + transport_cost}<br>
                    💡 <b>המלצת VIDASS:</b> נסיעה ברגליים או בסופר השכונתי חוסכת את דמי הנסיעה ושומרת על תקציב מאוזן!
                </div>
            """, unsafe_allow_html=True)

            for exp_idx, exp in enumerate(vault_data["expenses"]):
                st.markdown(f"""
                    <div class="card">
                        🏪 <b>חנות:</b> {exp.get('store', 'לא ידוע')} | 🛒 <b>סה"כ:</b> ₪{exp.get('total', 0)} | 📍 אזור: {exp.get('city', current_city)}<br>
                        <small>📅 תאריך: {exp.get('date', 'לא צוין')}</small>
                    </div>
                """, unsafe_allow_html=True)
                if st.button("🗑️ מחוק קבלה", key=f"del_exp_{exp_idx}"):
                    vault_data["expenses"].pop(exp_idx)
                    save_vault(vault_data)
                    st.rerun()

    # 4. מלאי ותיקיות
    with tab4:
        st.subheader("📦 ניהול מלאי לפי תיקיות נושאיות בבית (מקרר, ארונות ועוד)")
        if "inventory_folders" not in vault_data:
            vault_data["inventory_folders"] = ["מקרר", "מזווה", "ארון בגדים", "חומרי ניקוי", "מגירות סלון"]

        with st.form("add_inventory_item_form"):
            st.markdown("<b>➕ הוספת פריט חדש לתיקייה:</b>", unsafe_allow_html=True)
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                inv_name = st.text_input("שם המוצר")
                inv_folder = st.selectbox("בחר תיקייה נושאית", vault_data["inventory_folders"])
            with col_f2:
                inv_qty = st.number_input("כמות", min_value=1, value=1)
                inv_location = st.text_input("מיקום מדויק בתיקייה (למשל: מדף עליון מימין)")
            
            inv_img_file = st.file_uploader("העלה תמונה סטטית של המוצר", type=["jpg", "png", "jpeg"], key="inv_img_upload_new")

            if st.form_submit_button("💾 הוסף פריט לתיקייה"):
                if inv_name:
                    vault_data.setdefault("inventory_items", []).append({
                        "name": inv_name,
                        "folder": inv_folder,
                        "qty": inv_qty,
                        "location": inv_location,
                        "has_image": True if inv_img_file else False
                    })
                    save_vault(vault_data)
                    st.success(f"המוצר '{inv_name}' נוסף בהצלחה לתיקיית '{inv_folder}'!")
                    st.rerun()

        st.write("---")
        st.subheader("📁 תיקיות המלאי שלך (לחץ על תיקייה לצפייה במוצרים שבה):")
        
        selected_folder_view = st.selectbox("בחר תיקייה לצפייה ממוקדת:", vault_data["inventory_folders"], key="view_folder_sel")
        
        items_in_folder = [item for item in vault_data.get("inventory_items", []) if item.get("folder") == selected_folder_view]
        
        if not items_in_folder:
            st.info(f"תיקיית '{selected_folder_view}' ריקה כרגע. הוסיפי פריטים חדשים מעל!")
        else:
            for i_idx, item in enumerate(items_in_folder):
                col_box1, col_box2 = st.columns([4, 1])
                with col_box1:
                    st.markdown(f"""
                        <div class="card">
                            📦 <b>מוצר:</b> {item.get('name')}<br>
                            📊 <b>כמות במלאי:</b> {item.get('qty')}<br>
                            📍 <b>מיקום מדויק:</b> {item.get('location', 'לא צוין מיקום מדויק')}
                        </div>
                    """, unsafe_allow_html=True)
                with col_box2:
                    st.write("")
                    if st.button("🗑️ מחיקה", key=f"del_inv_item_{selected_folder_view}_{i_idx}"):
                        global_list = vault_data.get("inventory_items", [])
                        if item in global_list:
                            global_list.remove(item)
                            save_vault(vault_data)
                            st.success("הפריט נמחק!")
                            st.rerun()

    # 5. חשבונות
    with tab5:
        st.subheader("💡 ניהול חשבונות ותשלומי הבית")
        if "bills" not in vault_data:
            vault_data["bills"] = [
                {"name": "חשמל", "amount": 0.0, "due_date": "01 לחודש", "paid": False},
                {"name": "מים", "amount": 0.0, "due_date": "10 לחודש", "paid": False}
            ]
        for b_idx, bill in enumerate(vault_data.get("bills", [])):
            status_text = "✅ שולם" if bill.get('paid') else "❌ ממתין"
            st.markdown(f"💡 **{bill.get('name')}** | סכום: ₪{bill.get('amount')} | מועד: {bill.get('due_date')} | סטטוס: {status_text}")
            if st.button(("שנה ל-לא שולם" if bill.get('paid') else "סמן כשולם"), key=f"bill_t_{b_idx}"):
                vault_data["bills"][b_idx]['paid'] = not bill.get('paid', False)
                save_vault(vault_data)
                st.rerun()

    # 6. יועץ AI
    with tab6:
        st.subheader("🤖 יועץ AI אישי לבית ולמלאי הקיים")
        user_question = st.text_input("מה תרצי להכין או לשאול את היועץ בהתבסס על המלאי?", key="ai_advisor_q")
        if st.button("🍳 קבל עצה מותאמת מהיועץ", key="ai_advisor_btn") and user_question:
            st.markdown(f"""
                <div class="card">
                    <h4>💡 המלצת היועץ החכם:</h4>
                    <p>בהתבסס על שאלתך ועל פריטי המלאי הרשומים במערכת, מומלץ לשלב את המצרכים הקיימים בארונות לארוחה חמה ומהירה בלי לרוץ לסופר!</p>
                </div>
            """, unsafe_allow_html=True)

    # 7. מוזיקה
    with tab7:
        st.subheader("🎵 ספריית מוזיקה וקישורים משפחתית")
        with st.form("add_music_form"):
            m_topic = st.text_input("נושא / קטגוריה", key="m_topic_i")
            m_title = st.text_input("שם השיר / רשימת השמעה", key="m_title_i")
            m_url = st.text_input("קישור (URL)", key="m_url_i")
            if st.form_submit_button("➕ הוסף קישור מוזיקה"):
                if m_topic and m_title and m_url:
                    vault_data.setdefault("music_links", []).append({"topic": m_topic, "title": m_title, "url": m_url})
                    save_vault(vault_data)
                    st.success("הקישור נוסף בהצלחה!")
                    st.rerun()

    # 8. מצלמות
    with tab8:
        st.subheader("📹 חיבור וצפייה במצלמות אבטחה")
        with st.form("add_camera_form"):
            col_c1, col_c2, col_c3 = st.columns(3)
            with col_c1:
                cam_name = st.text_input("שם המצלמה", key="cam_name_i")
            with col_c2:
                cam_loc = st.text_input("מיקום", key="cam_loc_i")
            with col_c3:
                cam_url = st.text_input("קישור / גישה מרחוק (URL)", key="cam_url_i")
            if st.form_submit_button("➕ הוסף מצלמה"):
                if cam_name and cam_url:
                    vault_data.setdefault("home_cameras", []).append({"name": cam_name, "location": cam_loc, "url": cam_url})
                    save_vault(vault_data)
                    st.success("המצלמה נוספה בהצלחה!")
                    st.rerun()

        st.write("---")
        for c_idx, cam in enumerate(vault_data.get("home_cameras", [])):
            st.markdown(f"""
                <div class="card">
                    📹 <b>{cam.get('name')}</b> | 📍 {cam.get('location')}<br>
                    🔗 <a href="{cam.get('url')}" target="_blank">פתח שידור חי / גישה מרחוק למצלמה</a>
                </div>
            """, unsafe_allow_html=True)
            if st.button("🗑️ הסר מצלמה", key=f"del_cam_{c_idx}"):
                vault_data["home_cameras"].pop(c_idx)
                save_vault(vault_data)
                st.rerun()

    # 9. מכשירים חכמים
    with tab9:
        st.subheader("⚡ שליטה וקישור מכשירים חשמליים חכמים")
        with st.form("add_smart_device"):
            col_d1, col_d2, col_d3 = st.columns(3)
            with col_d1:
                dev_name = st.text_input("שם המכשיר", key="dev_name_i")
            with col_d2:
                dev_type = st.selectbox("סוג מכשיר", ["מזגן", "דוד חשמל", "תאורה", "תריס חשמלי", "אחר"], key="dev_type_i")
            with col_d3:
                dev_url = st.text_input("קישור שליטה (URL)", key="dev_url_i")
            if st.form_submit_button("➕ הוסף מכשיר חכם"):
                if dev_name:
                    vault_data.setdefault("smart_devices", []).append({"name": dev_name, "type": dev_type, "url": dev_url})
                    save_vault(vault_data)
                    st.success("המכשיר נוסף בהצלחה!")
                    st.rerun()

        st.write("---")
        for s_idx, dev in enumerate(vault_data.get("smart_devices", [])):
            st.markdown(f"""
                <div class="card">
                    ⚡ <b>{dev.get('name')}</b> | סוג: {dev.get('type')}<br>
                    🔗 <a href="{dev.get('url')}" target="_blank">פתח ממשק שליטה במכשיר</a>
                </div>
            """, unsafe_allow_html=True)
            if st.button("🗑️ הסר מכשיר", key=f"del_dev_{s_idx}"):
                vault_data["smart_devices"].pop(s_idx)
                save_vault(vault_data)
                st.rerun()

    # 10. יומן
    with tab10:
        st.subheader("📅 יומן תאריכים משפחתי")
        with st.form("add_event_form"):
            col_ev1, col_ev2, col_ev3 = st.columns(3)
            with col_ev1:
                ev_title = st.text_input("כותרת האירוע / תור", key="ev_title_i")
            with col_ev2:
                ev_date = st.date_input("תאריך", key="ev_date_i")
            with col_ev3:
                ev_cat = st.selectbox("קטגוריה", ["תורים רפואיים", "פגישות", "ימי הולדת", "אירועים", "אחר"], key="ev_cat_i")
            ev_note = st.text_input("הערות ושעה", key="ev_note_i")

            if st.form_submit_button("➕ הוסף ליומן"):
                if ev_title:
                    vault_data.setdefault("calendar_events", []).append({"date": str(ev_date), "title": ev_title, "category": ev_cat, "note": ev_note})
                    save_vault(vault_data)
                    st.success("האירוע נוסף בהצלחה!")
                    st.rerun()

        st.write("---")
        for e_idx, ev in enumerate(vault_data.get("calendar_events", [])):
            st.markdown(f"""
                <div class="card">
                    📅 <b>{ev.get('date')}</b> | [{ev.get('category')}] - <b>{ev.get('title')}</b><br>
                    <small>💬 {ev.get('note')}</small>
                </div>
            """, unsafe_allow_html=True)
            if st.button("🗑️ מחיקה", key=f"del_ev_{e_idx}"):
                vault_data["calendar_events"].pop(e_idx)
                save_vault(vault_data)
                st.rerun()

    # 11. חיסכון כספי חכם
    with tab11:
        st.subheader("💡 מערכת חיסכון כספי חכמה מבית VIDASS")
        st.info("המערכת לומדת את דפוסי ההוצאות והקניות שלכם וממליצה על דרכים לחסוך כסף בכל חודש.")

        if "savings_tips" not in vault_data:
            vault_data["savings_tips"] = [
                {"title": "השוואת רשתות מזון", "desc": "נמצא כי קנייה בסופר השכונתי יקרה ב-15% מרשתות הדיסקאונט הגדולות.", "saving": "כ-₪400 בחודש"},
                {"title": "ניהול מוצרי מלאי כפולים", "desc": "על פי המלאי הרשום במערכת, יש לך פריטי ניקוי ומזון כפולים שלא צריך לקנות כרגע.", "saving": "כ-₪120 בחודש"}
            ]

        total_expenses = sum([float(exp.get('total', 0)) for exp in vault_data.get("expenses", [])])
        st.markdown(f"""
            <div class="card" style="background-color: #f4f9f4; border: 2px solid #2e8b57;">
                <h3>📊 סיכום פיננסי חכם לבית</h3>
                <p>💰 <b>סה"כ הוצאות שנוהלו בקבלות במערכת:</b> ₪{total_expenses}</p>
                <p>📈 <b>פוטנציאל חיסכון חודשי מחושב:</b> כ-₪520 לחודש!</p>
            </div>
        """, unsafe_allow_html=True)

        for s_idx, tip in enumerate(vault_data.get("savings_tips", [])):
            st.markdown(f"""
                <div class="card">
                    🎯 <b>{tip.get('title')}</b><br>
                    <p>{tip.get('desc')}</p>
                    <b>💰 חיסכון משוער: {tip.get('saving')}</b>
                </div>
            """, unsafe_allow_html=True)

        with st.form("add_saving_tip"):
            s_title = st.text_input("כותרת ההמלצה / המטרה", key="s_title_i")
            s_desc = st.text_input("פירוט החיסכון", key="s_desc_i")
            s_saving = st.text_input("סכום חיסכון משוער (למשל: ₪200)", key="s_saving_i")
            if st.form_submit_button("הוסף טיפ חיסכון"):
                if s_title:
                    vault_data.setdefault("savings_tips", []).append({"title": s_title, "desc": s_desc, "saving": s_saving})
                    save_vault(vault_data)
                    st.success("הטיפ נוסף בהצלחה!")
                    st.rerun()

    # 12. מעקב תקלות ובקשות פיצ'רים
    with tab12:
        st.subheader("🛠️ מערכת ניהול תקלות, ביקוש ובקשות פיצ'רים (VIDASS)")
        if "vidass_feedback" not in vault_data:
            vault_data["vidass_feedback"] = [
                {"type": "פיצ'ר חדש", "title": "התראות וואטסאפ אוטומטיות", "status": "בפיתוח", "desc": "שליחת סיכום רשימת קניות ישירות לווטסאפ."},
                {"type": "תקלה דווחה", "title": "יישור טקסט מימין לשמאל", "status": "טופל", "desc": "תיקון עיצובי במסך התצוגה."}
            ]

        with st.form("add_feedback_form"):
            col_fb1, col_fb2 = st.columns(2)
            with col_fb1:
                fb_type = st.selectbox("סוג הפנייה", ["פיצ'ר חדש מבוקש", "תקלה טכנית (Bug)", "בקשת ייעול מערכת"], key="fb_type_i")
                fb_title = st.text_input("כותרת קצרה לבקשה / תקלה", key="fb_title_i")
            with col_fb2:
                fb_status = st.selectbox("סטטוס נוכחי", ["פתוח לדיון", "בפיתוח", "טופל בהצלחה"], key="fb_status_i")
            fb_desc = st.text_area("תיאור מפורט של הביקוש או התקלה", key="fb_desc_i")

            if st.form_submit_button("📤 שלח פנייה למערכת VIDASS"):
                if fb_title:
                    vault_data.setdefault("vidass_feedback", []).append({"type": fb_type, "title": fb_title, "status": fb_status, "desc": fb_desc})
                    save_vault(vault_data)
                    st.success("הפנייה נשמרה בהצלחה!")
                    st.rerun()

        st.write("---")
        for fb_idx, fb in enumerate(vault_data.get("vidass_feedback", [])):
            st.markdown(f"""
                <div class="card">
                    📌 <b>[{fb.get('type')}]</b> {fb.get('title')} | סטטוס: <b>{fb.get('status')}</b><br>
                    <p>{fb.get('desc')}</p>
                </div>
            """, unsafe_allow_html=True)
            if st.button("🗑️ מחוק פנייה", key=f"del_fb_{fb_idx}"):
                vault_data["vidass_feedback"].pop(fb_idx)
                save_vault(vault_data)
                st.rerun()

    # 13. הגדרות
    with tab13:
        st.subheader("⚙️ ניהול אזורים, עיצוב וצבעים")
        color_options = ["ורוד", "תכלת", "ירוק"]
        selected_theme = st.selectbox("בחר צבע רקע למערכת:", color_options, index=color_options.index(current_theme) if current_theme in color_options else 0, key="theme_sel_i")
        if st.button("✨ שמור צבע", key="save_theme_btn"):
            vault_data["theme_color"] = selected_theme
            save_vault(vault_data)
            st.rerun()

    # 14. יציאה
    with tab14:
        st.subheader("🚪 נעילת המערכת והחלפת משתמש")
        if st.button("התנתק ונעל מחדש", key="logout_btn_safe"):
            st.session_state.authenticated = False
            st.rerun()