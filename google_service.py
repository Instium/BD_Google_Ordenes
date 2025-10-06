import gspread
import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials

def get_sheet():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    with st.spinner("🔄 Conectando con Google Sheets..."):
        creds_dict = dict(st.secrets["google"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        sheet = client.open("Ordenes_BackOffice").sheet1

    st.toast("✅ Conectado correctamente a Google Sheets", icon="🟢")
    return sheet
