
import streamlit as st
import os

st.set_page_config(page_title="מרכז השליטה הביתי שלי", layout="wide")

# עיצוב מותאם אישית עם יישור טקסט נכון לימין בעברית
st.markdown("""
    <style>
    .stApp {
        background-color: #fff5f8;
        direction: rtl;
        text-align: right;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        font-weight: bold;
        background-color: #ffb6c1;
        color: #5c1d2e;
        border: 1px solid #ff91a4;
    }
    .stButton>button:hover {
        background-color: #ff91a4;
        color: white;
    }
    h1, h2, h3 {
        color: #d1496b;
        text-align: right;
    }
    p, label, div {
        text-align: right;
    }
    .weather-card {
        background-color: white;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #ffb6c1;
        text-align: center;
        box-shadow: 0 2px 8px rgba(255, 182, 193, 0.3);
    }
    </style>
""", unsafe_allow_html=True)

# אתחול מצב אימות והגנה
if "is_registered" not in st.session_state:
    st.session_state.is_registered = False
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# שלב 1: אם המערכת עדיין לא הוגדרה במכשיר/סשן, נעשה תהליך הרשמה חד פעמי
if not st.session_state.is_registered:
    st.title("🛡️ הגדרת אבטחה ראשונית למרכז השליטה")
    st.write("זו הפעם הראשונה שאת מגדירה את המערכת. אנא קבעי את פרטי הזיהוי וההגנה שלך:")

    reg_tz = st.text_input("הקלידי מספר תעודת זהות:", max_chars=9)
    reg_pass = st.text_input("צרי סיסמה חדשה למערכת:", type="password")
    
    st.markdown("---")
    st.subheader("שאלת אבטחה אישית נגד בוטים")
    reg_question = st.text_input("כתבי שאלה אישית משלך (למשל: מה שם החיה הראשונה שלי?):", placeholder="הקלידי שאלה כאן...")
    reg_answer = st.text_input("הקלידי את התשובה הנכונה לשאלה:", type="password")

    if st.button("שמור הגדרות והתחל"):
        if reg_tz and reg_pass and reg_question and reg_answer:
            st.session_state.saved_tz = reg_tz.strip()
            st.session_state.saved_pass = reg_pass.strip()
            st.session_state.saved_question = reg_question.strip()
            st.session_state.saved_answer = reg_answer.strip().lower()
            st.session_state.is_registered = True
            st.success("ההגדרות נשמרו בהצלחה! מעבר למסך כניסה...")
            st.rerun()
        else:
            st.error("נא למלא את כל השדות כדי להמשיך.")
    st.stop()

# שלב 2: מסך כניסה מאובטח (למי שכבר רשום)
if not st.session_state.authenticated:
    st.title("🔒 מרכז השליטה נעול")
    st.write("נא להזדהות כדי להיגיש למרכז השליטה האישי שלך:")

    login_tz = st.text_input("תעודת זהות:", max_chars=9, key="login_tz")
    login_pass = st.text_input("סיסמה:", type="password", key="login_pass")
    
    st.markdown(f"**שאלת אבטחה:** {st.session_state.saved_question}")
    login_answer = st.text_input("תשובה לשאלת האבטחה:", type="password", key="login_ans")

    if st.button("כניסה למערכת"):
        if (login_tz.strip() == st.session_state.saved_tz and 
            login_pass.strip() == st.session_state.saved_pass and 
            login_answer.strip().lower() == st.session_state.saved_answer):
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("אחד או יותר מהפרטים שגויים. הגישה חסומה.")
    st.stop()

# --- מכאן והלאה: המערכת פתוחה ומאובטחת ---

# אתחול נתונים
if "tasks" not in st.session_state:
    st.session_state.tasks = {
        "משמרת / זמן עבודה במעון": "טרם בוצע",
        "טיול עם ג'ולי הכלבה": "טרם בוצע",
        "תור רפואי / בדיקה": "טרם בוצע",
        "חוג (זומבה / פעילות)": "טרם בוצע",
        "זמן קפה עם דוד": "טרם בוצע",
        "לסדר את הבית": "טרם בוצע"
    }

if "shopping" not in st.session_state:
    st.session_state.shopping = {
        "מים מינרלים / סודה": False,
        "ביצים": False,
        "לחם אחיד": True,
        "ירקות טריים": False
    }

if "events" not in st.session_state:
    st.session_state.events = [
        {"time": "08:00 - 13:00", "title": "עבודה במעון (משמרת בוקר)"},
        {"time": "17:00 - 18:00", "title": "חוג זומבה"},
        {"time": "19:30", "title": "טיול ערב עם ג'ולי והסרת חום אספלט"}
    ]

# ניהול תיקיות וידע אישי ל-AI
if "ai_knowledge_folders" not in st.session_state:
    st.session_state.ai_knowledge_folders = {
        "כללי הבית באילת": "שמירה על ג'ולי מחום האספלט, ניהול קניות מים וסודה.",
        "עבודה במעון": "הפעלת הילדים, שירים של ויקטוריה השועלה ואריאל החתולה."
    }

if "ai_messages" not in st.session_state:
    st.session_state.ai_messages = [
        {"role": "assistant", "content": "היי! אני העוזרת האישית שלך. המערכת מוכנה ומאובטחת. איך אוכל לעזור לך היום?"}
    ]

st.title("💖 מרכז השליטה הדיגיטלי של הבית (אילת)")
st.write("ניהול משימות, יומן, קניות, תיקיות ידע ל-AI ועוזרת אישית מאובטחת.")

# חלוקה ללשוניות כולל ניהול תיקיות וידע ל-AI
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📅 יומן ומזג אוויר", 
    "📌 משימות ותורים", 
    "🛒 רשימת קניות", 
    "📁 תיקיות וידע ל-AI", 
    "🤖 עוזרת AI אישית"
])

with tab1:
    st.subheader("☀️ מזג האוויר כרגע באילת")
    col_w1, col_w2, col_w3 = st.columns(3)
    with col_w1:
        st.markdown('<div class="weather-card"><h3>🌡️ טמפרטורה</h3><p><b>38°C - חם מאוד</b></p></div>', unsafe_allow_html=True)
    with col_w2:
        st.markdown('<div class="weather-card"><h3>☀️ מצב שמיים</h3><p><b>בהיר ושמש מלאה</b></p></div>', unsafe_allow_html=True)
    with col_w3:
        st.markdown('<div class="weather-card"><h3>🐕 טיפ לג\'ולי</h3><p><b>לצאת רק בערב כשהאספלט קריר!</b></p></div>', unsafe_allow_html=True)

    st.divider()
    st.subheader("🕒 יומן שעות ולוח זמנים יומי")
    
    col_e1, col_e2, col_e3 = st.columns([1, 2, 1])
    with col_e1:
        event_time = st.text_input("שעה:", placeholder="למשל: 16:00", key="new_event_time")
    with col_e2:
        event_title = st.text_input("תיאור אירוע / תור / חוג:", placeholder="למשל: תור לרופא...", key="new_event_title")
    with col_e3:
        st.write("") 
        if st.button("➕ הוסף ליומן", use_container_width=True):
            if event_time and event_title:
                st.session_state.events.append({"time": event_time, "title": event_title})
                st.rerun()

    st.divider()

    for i, ev in enumerate(st.session_state.events):
        col_ev1, col_ev2, col_ev3 = st.columns([1, 3, 1])
        with col_ev1:
            st.markdown(f"**⏰ {ev['time']}**")
        with col_ev2:
            st.markdown(f"📌 {ev['title']}")
        with col_ev3:
            if st.button("🗑️ מחיקה", key=f"del_event_{i}"):
                st.session_state.events.pop(i)
                st.rerun()

with tab2:
    st.subheader("מעקב שוטף: עבודה, תורים, חוגים ובדיקות")
    
    col_input1, col_input2 = st.columns([3, 1])
    with col_input1:
        new_task = st.text_input("הוסיפי משימה חדשה:", label_visibility="collapsed", placeholder="הקלידי כאן...", key="new_task_input")
    with col_input2:
        if st.button("➕ הוסף משימה", use_container_width=True):
            if new_task and new_task not in st.session_state.tasks:
                st.session_state.tasks[new_task] = "טרם בוצע"
                st.rerun()

    st.divider()

    for task, status in list(st.session_state.tasks.items()):
        c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
        with c1:
            edited_task = st.text_input("ערוך", value=task, key=f"edit_task_{task}", label_visibility="collapsed")
            if edited_task != task and edited_task:
                st.session_state.tasks[edited_task] = st.session_state.tasks.pop(task)
                st.rerun()
        with c2:
            if status == "בוצע":
                st.success("בוצע")
            else:
                st.error("לטיפול")
        with c3:
            button_label = "🔄 בטל" if status == "בוצע" else "✔️ בוצע"
            if st.button(button_label, key=f"task_btn_{task}"):
                st.session_state.tasks[task] = "בוצע" if status == "טרם בוצע" else "טרם בוצע"
                st.rerun()
        with c4:
            if st.button("🗑️ מחיקה", key=f"del_task_{task}"):
                del st.session_state.tasks[task]
                st.rerun()

with tab3:
    st.subheader("ניהול רשימת קניות לסופר")
    
    col_s1, col_s2 = st.columns([3, 1])
    with col_s1:
        new_item = st.text_input("הוסיפי מוצר לקניות:", label_visibility="collapsed", placeholder="הקלידי מוצר כאן...", key="new_item_input")
    with col_s2:
        if st.button("➕ הוסף מוצר", use_container_width=True):
            if new_item and new_item not in st.session_state.shopping:
                st.session_state.shopping[new_item] = False
                st.rerun()

    st.divider()

    for item, bought in list(st.session_state.shopping.items()):
        col_item1, col_item2, col_item3 = st.columns([3, 1, 1])
        with col_item1:
            edited_item = st.text_input("ערוך מוצר", value=item, key=f"edit_shop_{item}", label_visibility="collapsed")
            if edited_item != item and edited_item:
                st.session_state.shopping[edited_item] = st.session_state.shopping.pop(item)
                st.rerun()
        with col_item2:
            new_state = st.checkbox("נקנה", value=bought, key=f"shop_cb_{item}")
            if new_state != bought:
                st.session_state.shopping[item] = new_state
                st.rerun()
        with col_item3:
            if st.button("🗑️ מחיקה", key=f"del_shop_{item}"):
                del st.session_state.shopping[item]
                st.rerun()

with tab4:
    st.subheader("📁 ניהול תיקיות והוספת מידע ל-AI")
    st.write("כאן את יכולה ליצור תיקיות חדשות ולהוסיף לתוכן מידע אישי, כדי שהעוזרת הביתית תכיר את ההרגלים שלך לעומק.")

    folder_name = st.text_input("שם התיקייה החדשה (למשל: רעיונות לסיפורים, מתכונים):")
    folder_content = st.text_area("תוכן / מידע אישי לתוך התיקייה:")
    
    if st.button("➕ צור תיקייה והוסף ל-AI"):
        if folder_name and folder_content:
            st.session_state.ai_knowledge_folders[folder_name] = folder_content
            st.success(f"התיקייה '{folder_name}' נוספה בהצלחה למאגר הידע של ה-AI!")
            st.rerun()
        else:
            st.warning("נא למלא גם שם לתיקייה וגם תוכן.")

    st.divider()
    st.subheader("התיקיות הקיימות במערכת שלך:")
    for f_name, f_val in list(st.session_state.ai_knowledge_folders.items()):
        with st.expander(f"📁 {f_name}"):
            st.write(f"**מידע שמור:** {f_val}")
            if st.button("🗑️ מחוק תיקייה", key=f"del_folder_{f_name}"):
                del st.session_state.ai_knowledge_folders[f_name]
                st.rerun()

with tab5:
    st.subheader("🤖 העוזרת הביתית החכמה שלך")
    st.write("העוזרת קוראת את המידע מתוך התיקיות שיצרת ויודעת לענות על הכל.")

    for message in st.session_state.ai_messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    if user_prompt := st.chat_input("כתבי כאן משהו לעוזרת..."):
        st.session_state.ai_messages.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.write(user_prompt)

        # יצירת תשובה חכמה המשלבת את הידע מתוך התיקיות שהמשתמשת יצרה
        knowledge_summary = " | ".join([f"[{k}: {v}]" for k, v in st.session_state.ai_knowledge_folders.items()])

        if "תור" in user_prompt or "בדיקה" in user_prompt:
            ai_reply = "רשמתי לפניי! תדאגי להוסיף את שעת התור המדויקת ללשונית היומן."
        elif "עבודה" in user_prompt or "מעון" in user_prompt:
            ai_reply = "זמני העבודה במעון חשובים מאוד. זכרי לקחת רגע לעצמך בסיום המשמרת!"
        elif "חוג" in user_prompt:
            ai_reply = "מעולה לשלב חוגים בלו'ז השבועי כדי ליהנות ולהישאר באנרגיות מעולות!"
        else:
            ai_reply = f"בדקתי בתיקיות האישיות שלך ({knowledge_summary}), ואני כאן כדי לעזור לך לנהל הכל ביד רמה באילת!"

        st.session_state.ai_messages.append({"role": "assistant", "content": ai_reply})
        with st.chat_message("assistant"):
            st.write(ai_reply)