import streamlit as st
import json
import os

st.set_page_config(page_title="VIDASS - ניהול חשבונות", page_icon="💳")

def load_vault():
    if os.path.exists("vidass_vault.json"):
        with open("vidass_vault.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {"household_accounts": []}

def save_vault(data):
    with open("vidass_vault.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

st.header("🏠 ניהול חשבונות והוצאות הבית")
st.markdown("כאן תוכלו לעקוב אחר ההוצאות השוטפות ולעדכן חשבונות חדשים בכספת המאובטחת.")

vault_data = load_vault()
accounts = vault_data.get("household_accounts", [])

if accounts:
    st.subheader("מעקב תשלומים חודשיים")
    st.table(accounts)
else:
    st.info("אין עדיין חשבונות רשומים במערכת.")

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