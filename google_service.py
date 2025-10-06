import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def get_sheet():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    # 🔐 Cargar credenciales desde los Secrets de Streamlit Cloud
    creds_json = os.getenv("google_service_account") or os.getenv("google.service_account")
    creds_dict = json.loads(creds_json)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)

    # 🔗 Conexión con tu Google Sheet
    client = gspread.authorize(creds)
    sheet = client.open("Ordenes_BackOffice").sheet1  # 👈 usa el nombre exacto de tu hoja
    return sheet
