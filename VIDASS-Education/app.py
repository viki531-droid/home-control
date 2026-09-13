import hashlib
import hmac
import secrets
import sqlite3
from datetime import date, datetime
from pathlib import Path

import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "vidass_education.db"


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def hash_secret(value, salt=None):
    salt_bytes = bytes.fromhex(salt) if salt else secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", value.encode("utf-8"), salt_bytes, 310000)
    return salt_bytes.hex(), digest.hex()


def verify_secret(value, salt, expected_hash):
    _, calculated_hash = hash_secret(value, salt)
    return hmac.compare_digest(calculated_hash, expected_hash)


def initialize_database():
    with get_connection() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS institutions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                institution_code TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                manager_name TEXT NOT NULL,
                manager_id TEXT NOT NULL,
                manager_password_hash TEXT NOT NULL,
                manager_password_salt TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS staff (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                institution_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                identity_number TEXT NOT NULL,
                role TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                password_salt TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'פעיל',
                FOREIGN KEY (institution_id) REFERENCES institutions(id)
            );
            CREATE TABLE IF NOT EXISTS children (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                institution_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                guardian_name TEXT NOT NULL,
                guardian_phone TEXT NOT NULL,
                medical_notes TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT 'פעיל',
                FOREIGN KEY (institution_id) REFERENCES institutions(id)
            );
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                child_id INTEGER NOT NULL,
                attendance_date TEXT NOT NULL,
                status TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                UNIQUE(child_id, attendance_date),
                FOREIGN KEY (child_id) REFERENCES children(id)
            );
            CREATE TABLE IF NOT EXISTS emergencies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                institution_id INTEGER NOT NULL,
                child_name TEXT NOT NULL,
                event_type TEXT NOT NULL,
                description TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'פתוח',
                created_at TEXT NOT NULL,
                FOREIGN KEY (institution_id) REFERENCES institutions(id)
            );
            """
        )


def query_all(sql, parameters=()):
    with get_connection() as connection:
        return connection.execute(sql, parameters).fetchall()


def query_one(sql, parameters=()):
    with get_connection() as connection:
        return connection.execute(sql, parameters).fetchone()


def execute(sql, parameters=()):
    with get_connection() as connection:
        cursor = connection.execute(sql, parameters)
        connection.commit()
        return cursor.lastrowid


def login_screen():
    st.title("VIDASS")
    st.caption("מערכת ניהול מוסדות חינוך ותינוקיות")
    login_type = st.selectbox(
        "סוג משתמש",
        ["חברת VIDASS", "מנהלת מוסד", "צוות שטח", "הורה"],
    )
    institution_code = st.text_input("מספר מוסד", disabled=login_type == "חברת VIDASS")
    identity_number = st.text_input("תעודת זהות")
    password = st.text_input("סיסמה", type="password")

    if st.button("כניסה למערכת", type="primary", use_container_width=True):
        if not identity_number or not password:
            st.error("נא למלא תעודת זהות וסיסמה.")
            return
        if login_type == "חברת VIDASS":
            if identity_number == "admin" and password == "admin":
                st.session_state.user = {"role": "company", "name": "חברת VIDASS"}
                st.rerun()
            st.error("פרטי הכניסה אינם תקינים.")
            return

        institution = query_one(
            "SELECT * FROM institutions WHERE institution_code = ?",
            (institution_code.strip(),),
        )
        if institution is None:
            st.error("מספר המוסד אינו קיים במערכת.")
            return

        if login_type == "מנהלת מוסד":
            valid = institution["manager_id"] == identity_number and verify_secret(
                password, institution["manager_password_salt"], institution["manager_password_hash"]
            )
            user = {"role": "manager", "name": institution["manager_name"], "institution_id": institution["id"]}
        elif login_type == "צוות שטח":
            staff_member = query_one(
                "SELECT * FROM staff WHERE institution_id = ? AND identity_number = ? AND status = 'פעיל'",
                (institution["id"], identity_number),
            )
            valid = staff_member is not None and verify_secret(
                password, staff_member["password_salt"], staff_member["password_hash"]
            )
            user = {"role": "staff", "name": staff_member["name"] if staff_member else "", "institution_id": institution["id"]}
        else:
            child = query_one(
                "SELECT * FROM children WHERE institution_id = ? AND guardian_phone = ?",
                (institution["id"], identity_number),
            )
            valid = child is not None and password == child["guardian_phone"]
            user = {"role": "parent", "name": child["guardian_name"] if child else "", "institution_id": institution["id"], "child_id": child["id"] if child else None}

        if valid:
            st.session_state.user = user
            st.rerun()
        st.error("פרטי הכניסה אינם תקינים.")


def institution_selector(institution_id):
    return query_one("SELECT * FROM institutions WHERE id = ?", (institution_id,))


def company_panel():
    st.header("פאנל חברת VIDASS")
    with st.form("new_institution"):
        name = st.text_input("שם המוסד")
        code = st.text_input("מספר מוסד")
        manager_name = st.text_input("שם המנהלת")
        manager_id = st.text_input("תעודת זהות מנהלת")
        initial_password = st.text_input("סיסמה ראשונית למנהלת", type="password")
        submitted = st.form_submit_button("פתח מוסד", use_container_width=True)
        if submitted:
            if not all([name, code, manager_name, manager_id, initial_password]):
                st.warning("נא למלא את כל השדות.")
            else:
                salt, password_hash = hash_secret(initial_password)
                try:
                    execute(
                        "INSERT INTO institutions (institution_code, name, manager_name, manager_id, manager_password_hash, manager_password_salt, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (code.strip(), name.strip(), manager_name.strip(), manager_id.strip(), password_hash, salt, datetime.now().isoformat()),
                    )
                    st.success("המוסד נפתח בהצלחה.")
                except sqlite3.IntegrityError:
                    st.error("מספר המוסד כבר קיים.")

    institutions = query_all("SELECT institution_code, name, manager_name, created_at FROM institutions ORDER BY id DESC")
    if institutions:
        st.dataframe(pd.DataFrame([dict(row) for row in institutions]), use_container_width=True, hide_index=True)
    else:
        st.info("עדיין לא נפתחו מוסדות.")


def manager_panel(institution):
    st.header(f"ניהול מוסד: {institution['name']}")
    tabs = st.tabs(["אישורי בטיחות", "צוות", "תיקי ילדים", "מוקד חירום"])
    with tabs[0]:
        st.info("מסך אישורי הבטיחות מוכן לחיבור למסמכים ותאריכי תוקף.")
    with tabs[1]:
        with st.form("new_staff"):
            name = st.text_input("שם עובד/ת")
            identity = st.text_input("תעודת זהות")
            role = st.selectbox("תפקיד", ["גננת מובילה", "מטפלת תינוקייה", "סייעת"])
            password = st.text_input("סיסמה", type="password")
            if st.form_submit_button("פתח תיק עובד", use_container_width=True):
                if not all([name, identity, password]):
                    st.warning("נא למלא שם, תעודת זהות וסיסמה.")
                else:
                    salt, password_hash = hash_secret(password)
                    execute(
                        "INSERT INTO staff (institution_id, name, identity_number, role, password_hash, password_salt) VALUES (?, ?, ?, ?, ?, ?)",
                        (institution["id"], name.strip(), identity.strip(), role, password_hash, salt),
                    )
                    st.success("תיק העובד נפתח.")
        staff = query_all("SELECT name, identity_number, role, status FROM staff WHERE institution_id = ?", (institution["id"],))
        if staff:
            st.dataframe(pd.DataFrame([dict(row) for row in staff]), use_container_width=True, hide_index=True)
    with tabs[2]:
        with st.form("new_child"):
            name = st.text_input("שם הילד/ה")
            guardian = st.text_input("שם הורה / איש קשר")
            phone = st.text_input("טלפון איש קשר")
            notes = st.text_area("דגשים רפואיים")
            if st.form_submit_button("שמור תיק ילד", use_container_width=True):
                if not all([name, guardian, phone]):
                    st.warning("נא למלא שם, איש קשר וטלפון.")
                else:
                    execute(
                        "INSERT INTO children (institution_id, name, guardian_name, guardian_phone, medical_notes) VALUES (?, ?, ?, ?, ?)",
                        (institution["id"], name.strip(), guardian.strip(), phone.strip(), notes.strip()),
                    )
                    st.success("תיק הילד נשמר.")
        children = query_all("SELECT name, guardian_name, guardian_phone, medical_notes, status FROM children WHERE institution_id = ?", (institution["id"],))
        if children:
            st.dataframe(pd.DataFrame([dict(row) for row in children]), use_container_width=True, hide_index=True)
    with tabs[3]:
        emergencies = query_all("SELECT child_name, event_type, description, status, created_at FROM emergencies WHERE institution_id = ? ORDER BY id DESC", (institution["id"],))
        if emergencies:
            st.dataframe(pd.DataFrame([dict(row) for row in emergencies]), use_container_width=True, hide_index=True)
        else:
            st.success("אין אירועי חירום פתוחים.")


def staff_panel(institution):
    st.header(f"טאבלט צוות: {institution['name']}")
    children = query_all("SELECT * FROM children WHERE institution_id = ? AND status = 'פעיל' ORDER BY name", (institution["id"],))
    if not children:
        st.info("לא קיימים ילדים פעילים במוסד.")
        return
    today = date.today().isoformat()
    for child in children:
        existing = query_one("SELECT status FROM attendance WHERE child_id = ? AND attendance_date = ?", (child["id"], today))
        current_status = existing["status"] if existing else "לא דווח"
        col1, col2, col3 = st.columns([3, 2, 2])
        col1.write(f"**{child['name']}**")
        col1.caption(child["medical_notes"] or "אין דגשים רפואיים")
        selected = col2.selectbox("נוכחות", ["לא דווח", "נוכח", "לא הגיע", "נאסף"], index=["לא דווח", "נוכח", "לא הגיע", "נאסף"].index(current_status), key=f"attendance_{child['id']}")
        if col3.button("שמור", key=f"save_attendance_{child['id']}"):
            execute(
                "INSERT INTO attendance (child_id, attendance_date, status, updated_at) VALUES (?, ?, ?, ?) ON CONFLICT(child_id, attendance_date) DO UPDATE SET status = excluded.status, updated_at = excluded.updated_at",
                (child["id"], today, selected, datetime.now().isoformat()),
            )
            st.success(f"הנוכחות של {child['name']} עודכנה.")
        st.divider()

    st.subheader("דיווח חריג")
    with st.form("emergency_report"):
        child_name = st.selectbox("שם הילד/ה", [child["name"] for child in children])
        event_type = st.selectbox("סוג האירוע", ["מכה", "חום", "נשיכה", "אירוע אחר"])
        description = st.text_area("תיאור האירוע")
        if st.form_submit_button("שלח דיווח חירום", use_container_width=True):
            if description.strip():
                execute(
                    "INSERT INTO emergencies (institution_id, child_name, event_type, description, created_at) VALUES (?, ?, ?, ?, ?)
",
                    (institution["id"], child_name, event_type, description.strip(), datetime.now().isoformat()),
                )
                st.success("הדיווח נשלח למנהלת.")
            else:
                st.warning("נא לתאר את האירוע.")


def parent_panel(user):
    child = query_one("SELECT * FROM children WHERE id = ?", (user["child_id"],))
    st.header(f"פורטל הורים: {child['name']}")
    attendance = query_one("SELECT status, attendance_date FROM attendance WHERE child_id = ? ORDER BY attendance_date DESC LIMIT 1", (child["id"],))
    if attendance and attendance["status"] == "נוכח":
        st.success(f"סטטוס נוכחות: {attendance['status']}")
    else:
        st.info(f"סטטוס נוכחות: {attendance['status'] if attendance else 'טרם דווח'}")
    if child["medical_notes"]:
        st.warning(f"דגשים רפואיים: {child['medical_notes']}")


def main():
    st.set_page_config(page_title="VIDASS", page_icon="🛡️", layout="wide")
    initialize_database()
    if "user" not in st.session_state:
        login_screen()
        return

    user = st.session_state.user
    st.sidebar.write(f"שלום, {user['name']}")
    if st.sidebar.button("התנתק", use_container_width=True):
        st.session_state.pop("user", None)
        st.rerun()

    if user["role"] == "company":
        company_panel()
    else:
        institution = institution_selector(user["institution_id"])
        if user["role"] == "manager":
            manager_panel(institution)
        elif user["role"] == "staff":
            staff_panel(institution)
        else:
            parent_panel(user)


if __name__ == "__main__":
    main()
