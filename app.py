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
    with st.form("form_crear"):
        # 🕓 Fecha y hora local de México
        mx_timezone = pytz.timezone("America/Mexico_City")
        fecha = datetime.now(mx_timezone).strftime("%Y-%m-%d")
        hora = datetime.now(mx_timezone).strftime("%H:%M")

        st.text_input("Supervisor", supervisor, disabled=True)
        st.text_input("Centro", centro, disabled=True)

        dn = st.text_input("DN")
        if dn and (not dn.isdigit() or len(dn) != 10):
            st.warning("⚠️ El DN debe tener exactamente 10 dígitos numéricos.")

        numero_orden = st.text_input("Número de Orden")
        entrega = st.selectbox("Entrega", ["", "DHL", "Tienda", "Domicilio"])
        status = st.selectbox("Status", ["", "Activada", "Perdida", "En tránsito"])
        fecha_activacion = st.text_input("Fecha de activación (vacío si nueva)")
        comentarios = st.text_area("Comentarios")

        if st.form_submit_button("✅ Crear orden"):
            if not agente or not numero_orden or not entrega or not status:
                st.toast("❌ Faltan campos obligatorios: Agente, Número de Orden, Entrega o Status.", icon="⚠️")
            elif not dn.isdigit() or len(dn) != 10:
                st.toast("❌ DN inválido. Debe tener exactamente 10 dígitos numéricos.", icon="⚠️")
            else:
                # --- Validación de duplicados ---
                sheet = get_sheet()
                registros = sheet.get_all_records()

                dn_clean = dn.strip().lower()
                no_clean = numero_orden.strip().lower()

                dups_dn = any(str(r["DN"]).strip().lower() == dn_clean for r in registros)
                dups_no = any(str(r["Número de Orden"]).strip().lower() == no_clean for r in registros)

                if dups_dn:
                    st.toast(f"❌ Ya existe una orden con el DN: {dn}", icon="⚠️")
                elif dups_no:
                    st.toast(f"❌ Ya existe una orden con el Número de Orden: {numero_orden}", icon="⚠️")
                else:
                    crear_orden([
                        fecha, hora, centro, supervisor, agente, dn,
                        numero_orden, entrega, status, fecha_activacion, comentarios
                    ])
                    st.toast("✅ Orden agregada correctamente.", icon="🎉")


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

        # --- Formulario de actualización ---
        with st.form("form_update", clear_on_submit=False):
            fecha = st.text_input("Fecha", reg["Fecha"])
            hora = st.text_input("Hora", reg["Hora"])
            st.text_input("Centro", centro, disabled=True)
            st.text_input("Supervisor", supervisor, disabled=True)

            dn = st.text_input("DN", str(reg["DN"]))
            if dn and (not dn.isdigit() or len(dn) != 10):
                st.warning("⚠️ El DN debe tener exactamente 10 dígitos numéricos.")

            no_orden_val = st.text_input("Número de Orden", reg["Numero de Orden"])
            entrega = st.selectbox("Entrega", entrega_opts, index=entrega_opts.index(reg["Entrega"]) if reg["Entrega"] in entrega_opts else 0)
            status = st.selectbox("Status", status_opts, index=status_opts.index(reg["Status"]) if reg["Status"] in status_opts else 0)
            fecha_activacion = st.text_input("Fecha de activación", reg["Fecha de activacion"])
            comentarios = st.text_area("Comentarios", reg["Comentarios"])

            if st.form_submit_button("✏️ Guardar cambios"):
                if not agente or not no_orden_val or not entrega or not status:
                    st.toast("❌ Faltan campos obligatorios: Agente, Número de Orden, Entrega o Status.", icon="⚠️")
                elif not dn.isdigit() or len(dn) != 10:
                    st.toast("❌ DN inválido. Debe tener exactamente 10 dígitos numéricos.", icon="⚠️")
                else:
                    nuevos = [
                        fecha, hora, centro, supervisor, agente, dn,
                        no_orden_val, entrega, status, fecha_activacion, comentarios
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

st.success(f"✅ {len(registros)} órdenes cargadas correctamente")
st.dataframe(registros)
