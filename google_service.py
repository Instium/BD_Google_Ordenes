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

    # 🧩 Si es texto -> convertir a dict
    if isinstance(creds_data, str):
        creds_dict = json.loads(creds_data)
    else:
        creds_dict = creds_data

    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    sheet = client.open("Ordenes_BackOffice").sheet1
    return sheet
