import streamlit as st
import json
import os
import hmac
import hashlib
import secrets

VAULT_FILE = "vidass_vault.json"
LEGACY_VAULT_FILE = "family_vault.json"

def _default_vault():
    return {
        "first_name": "",
        "family_name": "",
        "id_number": "",
        "address": "",
        "password_hash": "",
        "password_salt": "",
        "security_question": "",
        "security_answer_hash": "",
        "security_answer_salt": "",
        "notes": [],
        "shopping_list": [],
        "expenses": [],
        "inventory": [],
        "bills": [],
        "community_tips": [],
        "music_links": [],
        "home_cameras": [],
        "smart_devices": [],
        "calendar_events": [],
        "locations": [{"city": "אזור הבית", "transport": "רכב פרטי (דלק)"}],
        "active_city": "אזור הבית",
        "theme_color": "ורוד"
    }

def load_vault():
    vault_path = VAULT_FILE if os.path.exists(VAULT_FILE) else LEGACY_VAULT_FILE
    if os.path.exists(vault_path):
        try:
            with open(vault_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            defaults = _default_vault()
            for key, default_value in defaults.items():
                data.setdefault(key, default_value)
            data.pop("children", None)
            return data
        except (OSError, json.JSONDecodeError):
            pass
    return _default_vault()

def save_vault(data):
    data.pop("children", None)
    with open(VAULT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def _hash_secret(secret, salt=None):
    salt_bytes = bytes.fromhex(salt) if salt else secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", str(secret).encode("utf-8"), salt_bytes, 310000)
    return salt_bytes.hex(), digest.hex()

def _secret_matches(secret, stored_hash, stored_salt):
    if not stored_hash or not stored_salt:
        return False
    try:
        _, calculated_hash = _hash_secret(secret, stored_salt)
        return hmac.compare_digest(str(calculated_hash), str(stored_hash))
    except Exception:
        return False

def _set_authenticated(user_data):
    st.session_state.authenticated = True
    st.session_state.user_name = user_data.get("first_name", "משתמש")
    st.session_state.family_name = user_data.get("family_name", "הבית")
    st.session_state.address = user_data.get("address", "כתובת הבית")

def _greeting(first_name):
    from datetime import datetime
    name_to_show = first_name if first_name else "משתמש"
    hour = datetime.now().hour
    if hour < 12:
        period = "בוקר טוב"
    elif hour < 18:
        period = "צהריים טובים"
    else:
        period = "ערב טוב"
    return f"שלום {period}, {name_to_show}"

def _registration_form(vault_data):
    st.subheader("הרשמה ראשונית ל־VIDASS-HomeCommand")
    st.caption("ההרשמה מתבצעת פעם אחת בלבד. לאחר מכן המערכת תזהה אתכם אוטומטית.")
    with st.form("registration_form"):
        first_name = st.text_input("שם פרטי", placeholder="לדוגמה: ישראל")
        family_name = st.text_input("שם משפחה", placeholder="לדוגמה: ישראלי")
        id_number = st.text_input("תעודת זהות", placeholder="מספר תעודת זהות")
        address = st.text_input("כתובת הבית המדויקת", placeholder="כתובת מגורים")
        password = st.text_input("סיסמה אישית", type="password", placeholder="לפחות 8 תווים")
        password_confirmation = st.text_input("אימות סיסמה", type="password")
        security_question = st.text_input("שאלת אבטחה לשחזור", placeholder="לדוגמה: מהו המאכל האהוב עליי?")
        security_answer = st.text_input("תשובה לשאלת האבטחה", type="password")

        if st.form_submit_button("יצירת חשבון ביתי"):
            required_values = [first_name, family_name, id_number, address, password, security_question, security_answer]
            if not all(str(val).strip() for val in required_values):
                st.warning("נא למלא את כל השדות.")
            elif len(password) < 8:
                st.warning("הסיסמה חייבת להכיל לפחות 8 תווים.")
            elif password != password_confirmation:
                st.warning("אימות הסיסמה אינו תואם לסיסמה.")
            else:
                password_salt, password_hash = _hash_secret(password)
                answer_salt, answer_hash = _hash_secret(security_answer.strip().casefold())
                vault_data.update({
                    "first_name": first_name.strip(),
                    "family_name": family_name.strip(),
                    "id_number": id_number.strip(),
                    "address": address.strip(),
                    "password_hash": password_hash,
                    "password_salt": password_salt,
                    "security_question": security_question.strip(),
                    "security_answer_hash": answer_hash,
                    "security_answer_salt": answer_salt
                })
                save_vault(vault_data)
                _set_authenticated(vault_data)
                st.success("החשבון נוצר ונשמר בהצלחה!")
                st.rerun()

def _login_form(vault_data):
    first_name = vault_data.get("first_name", "")
    st.subheader(_greeting(first_name))
    st.caption("ברוכים הבאים ל־VIDASS-HomeCommand. הכניסו את הסיסמה האישית כדי להיכנס.")
    with st.form("login_form"):
        password = st.text_input("סיסמה אישית", type="password")
        submitted = st.form_submit_button("כניסה למערכת")
        if submitted:
            pass_str = str(password) if password else ""
            password_hash = vault_data.get("password_hash")
            password_salt = vault_data.get("password_salt")
            
            if password_hash and password_salt and _secret_matches(pass_str, password_hash, password_salt):
                _set_authenticated(vault_data)
                st.rerun()
            else:
                st.warning("הסיסמה אינה נכונה.")

def _recovery_form(vault_data):
    with st.expander("שכחתי את הסיסמה"):
        st.write(f"<b>שאלת אבטחה:</b> {vault_data.get('security_question', 'לא הוגדרה שאלה')}", unsafe_allow_html=True)
        with st.form("recovery_form"):
            answer = st.text_input("תשובה לשאלת האבטחה", type="password")
            new_password = st.text_input("סיסמה חדשה", type="password")
            new_password_confirmation = st.text_input("אימות הסיסמה החדשה", type="password")
            submitted = st.form_submit_button("איפוס סיסמה")
            if submitted:
                ans_str = str(answer).strip().casefold() if answer else ""
                answer_hash = vault_data.get("security_answer_hash")
                answer_salt = vault_data.get("security_answer_salt")
                
                answer_is_valid = False
                if answer_hash and answer_salt:
                    answer_is_valid = _secret_matches(ans_str, answer_hash, answer_salt)

                if not answer_is_valid:
                    st.warning("תשובת האבטחה אינה נכונה.")
                elif len(str(new_password)) < 8:
                    st.warning("הסיסמה החדשה חייבת להכיל לפחות 8 תווים.")
                elif new_password != new_password_confirmation:
                    st.warning("אימות הסיסמה החדשה אינו תואם.")
                else:
                    new_pass_str = str(new_password)
                    password_salt, password_hash = _hash_secret(new_pass_str)
                    answer_salt, answer_hash = _hash_secret(ans_str)
                    vault_data["password_salt"] = password_salt
                    vault_data["password_hash"] = password_hash
                    vault_data["security_answer_salt"] = answer_salt
                    vault_data["security_answer_hash"] = answer_hash
                    save_vault(vault_data)
                    st.success("הסיסמה אופסה בהצלחה! אפשר להתחבר כעת.")

def check_authentication():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        vault_data = load_vault()
        st.markdown("""
            <div style="text-align: center; padding: 20px;">
                <h2>🏠 VIDASS-HomeCommand</h2>
                <p>ניהול ביתי, משפחתי ואישי במקום אחד</p>
            </div>
        """, unsafe_allow_html=True)

        if vault_data.get("password_hash") and vault_data.get("password_salt"):
            _login_form(vault_data)
            _recovery_form(vault_data)
        else:
            _registration_form(vault_data)
        return False
    return True