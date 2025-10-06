import gspread
import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials

def get_sheet():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    # ✅ En Streamlit, el JSON ya viene listo como diccionario
    creds_dict = st.secrets["google"]["service_account"]

    # 🔗 Autorizar acceso con las credenciales
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)

    # 📄 Abrir la hoja de cálculo (ajusta el nombre si es distinto)
    sheet = client.open("Ordenes_BackOffice").sheet1
    return sheet
