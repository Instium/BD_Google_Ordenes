import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
from crud import crear_orden, leer_orden, actualizar_orden, eliminar_orden
from google_service import get_sheet

# === CONFIGURACIÓN GENERAL ===
st.set_page_config(page_title="Gestión de Órdenes", layout="wide")
st.title("📋 Gestor de Órdenes - CRUD")

# --- Estado global ---
if "edit_reg" not in st.session_state:
    st.session_state.edit_reg = None
if "edit_no_orden" not in st.session_state:
    st.session_state.edit_no_orden = None
if "df_agentes" not in st.session_state:
    st.session_state.df_agentes = None

# === SIDEBAR ===
st.sidebar.header("⚙️ Configuración")
st.sidebar.subheader("📂 Base de Agentes")
archivo = st.sidebar.file_uploader("Subir archivo Excel (.xlsx)", type=["xlsx"])

if archivo:
    st.session_state.df_agentes = pd.read_excel(archivo)
    st.sidebar.success("✅ Base cargada correctamente.")
    st.sidebar.write(f"Total agentes: {len(st.session_state.df_agentes)}")
else:
    st.sidebar.info("Sube la base de agentes para habilitar autocompletado.")

# === Lista de regiones ===
regiones = ["México", "Puebla", "Veracruz", "Tijuana", "Guadalajara", "Monterrey"]

# === TABS PRINCIPALES ===
tab1, tab2, tab3 = st.tabs(["➕ Crear", "✏️ Actualizar", "🗑️ Eliminar"])

# =====================================================
# 🟢 TAB 1 - CREAR NUEVA ORDEN
# =====================================================
with tab1:
    st.subheader("➕ Crear nueva orden")

    # --- Selección de agente ---
    if st.session_state.df_agentes is not None:
        agente = st.selectbox("Agente", [""] + sorted(st.session_state.df_agentes["Nombre Completo"].unique()))
        supervisor, centro = "", ""
        if agente:
            fila = st.session_state.df_agentes[
                st.session_state.df_agentes["Nombre Completo"] == agente
            ].iloc[0]
            supervisor = fila["Jefe directo"]
            centro = fila["Centro"]
    else:
        agente = st.text_input("Agente (sin base cargada)")
        supervisor, centro = "", ""

    # --- Formulario de nueva orden ---
    # === Formulario principal ===
    with st.form("form_crear"):
        mx_timezone = pytz.timezone("America/Mexico_City")
        fecha = datetime.now(mx_timezone).strftime("%Y-%m-%d")
        hora = datetime.now(mx_timezone).strftime("%H:%M")

        st.text_input("Supervisor", supervisor, disabled=True)
        st.text_input("Centro", centro, disabled=True)

        region = st.selectbox("🌎 Región", [""] + regiones)
        dn = st.text_input("DN")
        if dn and (not dn.isdigit() or len(dn) != 10):
            st.warning("⚠️ El DN debe tener exactamente 10 dígitos numéricos.")

        numero_orden = st.text_input("Número de Orden")
        entrega = st.selectbox("Entrega", ["", "DHL", "Tienda", "Domicilio"])
        status = "En tránsito"
        st.text_input("Status", status, disabled=True)
        fecha_tentativa = st.date_input("📅 Fecha Tentativa", value=None)
        fecha_activacion = st.text_input("Fecha de activación (vacío si nueva)")
        comentarios = st.text_area("Comentarios")

        submitted = st.form_submit_button("✅ Crear orden")

    # === Lógica de creación ===
    if submitted:
        if not agente or not numero_orden or not entrega or not region:
            st.toast("❌ Faltan campos obligatorios: Agente, Región, Número de Orden o Entrega.", icon="⚠️")
        elif not dn.isdigit() or len(dn) != 10:
            st.toast("❌ DN inválido. Debe tener exactamente 10 dígitos numéricos.", icon="⚠️")
        else:
            sheet = get_sheet()
            registros = sheet.get_all_records()

            dn_clean = dn.strip().lower()
            no_clean = numero_orden.strip().lower()

            dups_dn = any(str(r["DN"]).strip().lower() == dn_clean for r in registros)
            dups_no = any(
                str(r.get("Número de Orden", r.get("Numero de Orden", ""))).strip().lower() == no_clean
                for r in registros
            )

            if dups_dn:
                st.toast(f"❌ Ya existe una orden con el DN: {dn}", icon="⚠️")
            elif dups_no:
                st.toast(f"❌ Ya existe una orden con el Número de Orden: {numero_orden}", icon="⚠️")
            else:
                crear_orden([
                    fecha, hora, centro, supervisor, agente, dn,
                    numero_orden, entrega, status, fecha_activacion,
                    comentarios, "", str(fecha_tentativa), region
                ])
                st.toast("✅ Orden agregada correctamente.", icon="🎉")
                st.rerun()

    # === 🧹 Botón limpiar FUERA del form ===
    if st.button("🧹 Limpiar formulario"):
        for key in list(st.session_state.keys()):
            if key not in ["df_agentes"]:
                del st.session_state[key]
        st.rerun()

# =====================================================
# 🟡 TAB 2 - ACTUALIZAR ORDEN EXISTENTE
# =====================================================
with tab2:
    st.subheader("✏️ Actualizar orden")

    no_orden_to_load = st.text_input("Número de Orden a cargar")
    if st.button("Cargar orden"):
        reg = leer_orden(no_orden_to_load)
        if reg:
            st.session_state.edit_reg = reg
            st.session_state.edit_no_orden = reg["Numero de Orden"]
            st.toast("✅ Orden cargada. Edita abajo y guarda cambios.", icon="🟢")
        else:
            st.toast("⚠️ Orden no encontrada.", icon="⚠️")

    if st.session_state.edit_reg:
        reg = st.session_state.edit_reg
        entrega_opts = ["DHL", "Tienda", "Domicilio"]
        status_opts = ["Activada", "Perdida", "En tránsito"]

        # --- Autocompletado de agente ---
        if st.session_state.df_agentes is not None:
            agente = st.selectbox(
                "Agente",
                [""] + sorted(st.session_state.df_agentes["Nombre Completo"].unique()),
                index=([""] + sorted(st.session_state.df_agentes["Nombre Completo"].unique())).index(reg["Agente"])
                if reg["Agente"] in st.session_state.df_agentes["Nombre Completo"].values else 0
            )
            supervisor, centro = reg["Supervisor"], reg["Centro"]
            if agente:
                fila = st.session_state.df_agentes[
                    st.session_state.df_agentes["Nombre Completo"] == agente
                ].iloc[0]
                supervisor = fila["Jefe directo"]
                centro = fila["Centro"]
        else:
            agente = st.text_input("Agente", reg["Agente"])
            supervisor, centro = reg["Supervisor"], reg["Centro"]

        # --- Status fuera del form ---
        status = st.selectbox(
            "Status",
            status_opts,
            index=status_opts.index(reg["Status"]) if reg["Status"] in status_opts else 0
        )

        # --- Subtipificación (solo si Perdida) ---
        subtipificacion = reg.get("Subtipificación", "")
        if status == "Perdida":
            subtipificacion = st.selectbox(
                "Motivo de pérdida",
                ["Paquete Extraviado/Dañado", "Cliente Cancela"],
                index=["Paquete Extraviado/Dañado", "Cliente Cancela"].index(subtipificacion)
                if subtipificacion in ["Paquete Extraviado/Dañado", "Cliente Cancela"] else 0
            )

        # --- Formulario principal ---
        with st.form("update_form", clear_on_submit=False):
            fecha = st.text_input("Fecha", reg["Fecha"])
            hora = st.text_input("Hora", reg["Hora"])
            st.text_input("Centro", centro, disabled=True)
            st.text_input("Supervisor", supervisor, disabled=True)

            region = st.selectbox("🌎 Región", regiones, index=regiones.index(reg.get("Region", "México")) if reg.get("Region") in regiones else 0)
            dn = st.text_input("DN", str(reg["DN"]))
            if dn and (not dn.isdigit() or len(dn) != 10):
                st.warning("⚠️ El DN debe tener exactamente 10 dígitos numéricos.")

            no_orden_val = st.text_input("Número de Orden", reg["Numero de Orden"])
            entrega = st.selectbox(
                "Entrega", entrega_opts,
                index=entrega_opts.index(reg["Entrega"]) if reg["Entrega"] in entrega_opts else 0
            )
            fecha_tentativa = st.date_input("📅 Fecha Tentativa", value=None)
            fecha_activacion = st.text_input("Fecha de activación", reg["Fecha de activacion"])
            comentarios = st.text_area("Comentarios", reg["Comentarios"])

            if st.form_submit_button("✏️ Guardar cambios"):
                if not agente or not no_orden_val or not entrega or not status or not region:
                    st.toast("❌ Faltan campos obligatorios.", icon="⚠️")
                elif not dn.isdigit() or len(dn) != 10:
                    st.toast("❌ DN inválido.", icon="⚠️")
                else:
                    mx_timezone = pytz.timezone("America/Mexico_City")
                    if status == "Activada" and reg["Status"] != "Activada":
                        fecha_activacion = datetime.now(mx_timezone).strftime("%Y-%m-%d %H:%M")

                    nuevos = [
                        fecha, hora, centro, supervisor, agente, dn,
                        no_orden_val, entrega, status, fecha_activacion,
                        comentarios, subtipificacion, str(fecha_tentativa), region
                    ]
                    actualizar_orden(st.session_state.edit_no_orden, nuevos)
                    st.toast(f"✅ Orden {st.session_state.edit_no_orden} actualizada correctamente.", icon="🟢")
                    st.session_state.edit_reg = None
                    st.session_state.edit_no_orden = None
                    st.rerun()

# =====================================================
# 🔴 TAB 3 - ELIMINAR ORDEN
# =====================================================
with tab3:
    st.subheader("🗑️ Eliminar orden")
    no_orden_del = st.text_input("Número de Orden a eliminar")
    if st.button("Eliminar"):
        eliminar_orden(no_orden_del)
        st.toast(f"🗑️ Orden {no_orden_del} eliminada correctamente.", icon="❌")

# =====================================================
# 📋 TABLA FINAL DE ÓRDENES
# =====================================================
st.subheader("📑 Todas las órdenes en Google Sheet")

with st.spinner("📦 Cargando órdenes desde Google Sheets..."):
    registros = get_sheet().get_all_records()

# 🧩 Crear DataFrame y forzar tipos seguros para visualización
df = pd.DataFrame(registros)

# 🔹 Forzar texto en columnas mixtas (letras + números)
for col in ["Numero de Orden", "Comentarios"]:
    if col in df.columns:
        df[col] = df[col].astype(str)

# 🔹 Limpiar columna de fecha tentativa (None → vacío)
if "Fecha Tentativa" in df.columns:
    df["Fecha Tentativa"] = df["Fecha Tentativa"].replace("None", "").fillna("")

# 🔹 Mostrar fecha y hora actual como indicador de última actualización
mx_timezone = pytz.timezone("America/Mexico_City")
last_refresh = datetime.now(mx_timezone).strftime("%Y-%m-%d %H:%M")

st.success(f"✅ {len(df)} órdenes cargadas correctamente — Última actualización: {last_refresh}")
st.dataframe(df)

