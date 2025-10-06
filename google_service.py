import os
import json
import gspread
import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials

def get_sheet():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    creds_data = st.secrets["google"]["service_account"]

    # 🧠 Si es texto plano con saltos reales, no lo conviertas con json.loads
    if isinstance(creds_data, str) and creds_data.strip().startswith("{"):
        try:
            creds_dict = json.loads(creds_data)
        except Exception:
            # Si ya no es JSON sino un dict directo
            creds_dict = st.secrets["google"]["service_account"]
    else:
        creds_dict = creds_data

    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    sheet = client.open("Ordenes_BackOffice").sheet1

    st.success("✅ Conectado correctamente a Google Sheets")
    return sheet
