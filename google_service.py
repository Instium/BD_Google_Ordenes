import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def get_sheet():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    creds_env = os.getenv("google_service_account") or os.getenv("google.service_account")

    # 🔧 Manejar caso según tipo (str o dict)
    if isinstance(creds_env, str):
        creds_dict = json.loads(creds_env)
    elif isinstance(creds_env, dict):
        creds_dict = creds_env
    else:
        raise ValueError("No se encontraron credenciales válidas en los Secrets de Streamlit")

    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    sheet = client.open("Ordenes_BackOffice").sheet1
    return sheet
