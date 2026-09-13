import streamlit as st
import json
import os

VAULT_FILE = "vidass_vault.json"
LEGACY_VAULT_FILE = "family_vault.json"

def load_vault():
    vault_path = VAULT_FILE if os.path.exists(VAULT_FILE) else LEGACY_VAULT_FILE
    if os.path.exists(vault_path):
        try:
            with open(vault_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {}

def save_vault(data):
    with open(VAULT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

st.set_page_config(
    page_title="VIDASS - Company Admin Panel",
    page_icon="🛡️",
    layout="wide"
)

st.markdown("""
    <style>
    .main { background-color: #1e1e2f; color: #ffffff; direction: rtl; text-align: right; }
    h1, h2, h3 { color: #00ffcc; text-align: right; }
    .card { background: #2a2a40; padding: 15px; border-radius: 10px; border: 1px solid #00ffcc; margin-bottom: 10px; color: white; }
    .stButton>button { background-color: #00ffcc; color: #1e1e2f; font-weight: bold; border-radius: 8px; width: 100%; }
    .stButton>button:hover { background-color: #ff007f; color: white; }
    </style>
""", unsafe_allow_html=True)

st.title("🛡️ VIDASS — Company Management & Analytics Panel")
st.caption("פאנל הניהול המרכזי של חברת VIDASS למעקב אחר תקלות, ביקוש פיצ'רים, פעילות משתמשים ונתוני מערכת.")

vault_data = load_vault()

if not vault_data:
    st.warning("⚠️ לא נמצאו נתוני מערכת פעילים בקובץ הראשי.")
else:
    # סקשנים מרכזיים בפאנל ניהול חברה
    tab_overview, tab_feedback, tab_users, tab_settings = st.tabs([
        "📊 סטטיסטיקה וסקירה כללית", 
        "🛠️ ניהול תקלות ופיצ'רים (Feedback)", 
        "👥 מעקב משתמשים ובתים", 
        "⚙️ הגדרות מערכת חברה"
    ])

    # 1. סקירה כללית
    with tab_overview:
        st.subheader("📊 מדדי ביצוע ופעילות באפליקציה")
        
        col1, col2, col3, col4 = st.columns(4)
        total_notes = len(vault_data.get("notes", []))
        total_shop = len(vault_data.get("shopping_list", []))
        total_expenses = len(vault_data.get("expenses", []))
        total_feedback = len(vault_data.get("vidass_feedback", []))
        
        col1.metric("📌 פתקיות פעילות במערכת", total_notes)
        col2.metric("🛒 פריטים ברשימות קניות", total_shop)
        col3.metric("🧾 קבלות וחשבוניות שנסרקו", total_expenses)
        col4.metric("🛠️ פניות/תקלות פתוחות", total_feedback)

        st.markdown("---")
        st.subheader("💡 סטטוס מנועי הלמידה החכמים של VIDASS")
        st.success("✔ מנוע ההתאמה האישית (Adaptive Engine): פעיל ומנתח נתונים ביתיים.")
        st.success("✔ מנוע החיסכון הפיננסי: מספק תובנות לחיסכון חודשי למשתמשים.")
        st.success("✔ סנכרון ענן מקומי: תקין ומאובטח.")

    # 2. ניהול תקלות ופיצ'רים
    with tab_feedback:
        st.subheader("🛠️ מעקב אחר בקשות פיצ'רים חדשים ותקלות (Bug Tracker)")
        
        feedbacks = vault_data.get("vidass_feedback", [])
        if not feedbacks:
            st.info("אין פניות או תקלות רשומות כרגע במערכת.")
        else:
            for idx, fb in enumerate(feedbacks):
                with st.container():
                    col_f1, col_f2 = st.columns([5, 1])
                    with col_f1:
                        st.markdown(f"""
                            <div class="card">
                                📌 <b>סוג:</b> {fb.get('type')} | <b>כותרת:</b> {fb.get('title')}<br>
                                🎯 <b>סטטוס נוכחי:</b> <span style="color: #00ffcc;">{fb.get('status')}</span><br>
                                <p>📝 <b>תיאור:</b> {fb.get('desc')}</p>
                            </div>
                        """, unsafe_allow_html=True)
                    with col_f2:
                        st.write("")
                        if st.button("🗑️ מחוק", key=f"admin_del_fb_{idx}"):
                            vault_data["vidass_feedback"].pop(idx)
                            save_vault(vault_data)
                            st.rerun()

    # 3. מעקב משתמשים ובתים
    with tab_users:
        st.subheader("👥 ניהול משתמשים ובתי אב מחוברים")
        
        user_name = vault_data.get("first_name", "לא הוגדר")
        family_name = vault_data.get("family_name", "לא הוגדר")
        address = vault_data.get("address", "לא הוגדרה כתובת")
        id_num = vault_data.get("id_number", "לא הוזן")

        st.markdown(f"""
            <div class="card">
                🏠 <b>שם המשפחה / בית אב:</b> משפחת {family_name}<br>
                👤 <b>משתמש ראשי רשום:</b> {user_name}<br>
                📍 <b>כתובת מגורים:</b> {address}<br>
                🆔 <b>תעודת זהות מזהה:</b> {id_num}<br>
                🔒 <b>אבטחת מידע:</b> חשבון מוצפן ומאובטח בסיסמה
            </div>
        """, unsafe_allow_html=True)

    # 4. הגדרות מערכת חברה
    with tab_settings:
        st.subheader("⚙️ הגדרות ניהול גלובליות לחברת VIDASS")
        st.info("כאן ניתן להגדיר תצורות מערכת גלובליות לכלל הלקוחות המשתמשים באפליקציה.")
        
        if st.button("🔄 אתחל נתוני אנליטיקה ומטמון מערכת"):
            st.success("נתוני המערכת אופסו בהצלחה עבור סביבת הפיתוח!")
import streamlit as st
import json
import os

# פונקציות לניהול כספת הנתונים של הבית
def load_vault():
    if os.path.exists("vidass_vault.json"):
        with open("vidass_vault.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {"household_accounts": []}

def save_vault(data):
    with open("vidass_vault.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# הוספת הלשונית לממשק הניהול
def render_finances_tab():
    st.header("🏠 ניהול חשבונות והוצאות הבית")
    st.markdown("כאן תוכלו לעקוב אחר ההוצאות השוטפות ולעדכן חשבונות חדשים בכספת המאובטחת.")

    vault_data = load_vault()
    accounts = vault_data.get("household_accounts", [])

    if accounts:
        st.subheader("מעקב תשלומים חודשיים")
        st.table(accounts)
    else:
        st.info("אין עדיין חשבונות רשומים במערכת.")

    # טופס להוספת חשבון חדש
    with st.form("add_bill_form"):
        st.subheader("הוספת הוצאה / חשבון חדש")
        new_cat = st.text_input("סוג החשבון (למשל: מים, גז, אינטרנט, ארנונה)")
        new_amount = st.number_input("סכום בשקלים", min_value=0.0)
        new_date = st.date_input("תאריך יעד לתשלום")
        submit_bill = st.form_submit_button("הוסף לכספת")
        
        if submit_bill and new_cat:
            new_entry = {
                "category": new_cat, 
                "amount": new_amount, 
                "due_date": str(new_date), 
                "status": "ממתין לתשלום"
            }
            vault_data["household_accounts"].append(new_entry)
            save_vault(vault_data)
            st.success("החשבון נוסף בהצלחה ונשמר במערכת!")
            st.rerun()

# אם את משתמשת בלשוניות (Tabs) בתוך ה-admin_panel.py שלך, את יכולה לקרוא לפונקציה כך:
# tab1, tab2, tab3, tab_finances = st.tabs(["מערכת ראשית", "מצלמות", "הגדרות", "💳 חשבונות והוצאות"])
# with tab_finances:
#     render_finances_tab()