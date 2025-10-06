import gspread
import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials

def get_sheet():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    # ✅ Streamlit ya devuelve el JSON como diccionario, no lo vuelvas a cargar
    creds_dict = st.secrets["google"]["service_account"]

    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    sheet = client.open("Ordenes_BackOffice").sheet1
    return sheet
