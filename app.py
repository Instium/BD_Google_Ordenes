import streamlit as st
import pandas as pd
from datetime import datetime
from crud import crear_orden, leer_orden, actualizar_orden, eliminar_orden
from google_service import get_sheet

st.set_page_config(page_title="Gestión de Órdenes", layout="wide")
st.title("📋 Gestor de Órdenes - CRUD")

# --- Estado global ---
if "edit_reg" not in st.session_state:
    st.session_state.edit_reg = None
if "edit_no_orden" not in st.session_state:
    st.session_state.edit_no_orden = None
if "df_agentes" not in st.session_state:
    st.session_state.df_agentes = None

# === CARGAR BASE DE AGENTES ===
st.sidebar.header("⚙️ Configuración")
st.sidebar.subheader("📂 Base de Agentes")
archivo = st.sidebar.file_uploader("Subir archivo Excel (.xlsx)", type=["xlsx"])
if archivo:
    st.session_state.df_agentes = pd.read_excel(archivo)
    st.sidebar.success("✅ Base cargada correctamente.")
    st.sidebar.write(f"Total agentes: {len(st.session_state.df_agentes)}")
else:
    st.sidebar.info("Sube la base de agentes para habilitar autocompletado.")

# === TABS ===
tab1, tab2, tab3 = st.tabs(["➕ Crear", "✏️ Actualizar", "🗑️ Eliminar"])

# ============ CREAR ============
with tab1:
    st.subheader("➕ Crear nueva orden")

    # === Selección de agente (fuera del form para actualizar en vivo) ===
    if st.session_state.df_agentes is not None:
        agente = st.selectbox("Agente", [""] + sorted(st.session_state.df_agentes["Nombre Completo"].unique()))
        supervisor, centro = "", ""
        if agente:
            fila = st.session_state.df_agentes[st.session_state.df_agentes["Nombre Completo"] == agente].iloc[0]
            supervisor = fila["Jefe directo"]
            centro = fila["Centro"]
    else:
        agente = st.text_input("Agente (sin base cargada)")
        supervisor, centro = "", ""

    # === Formulario principal ===
    with st.form("form_crear"):
        fecha = datetime.now().strftime("%Y-%m-%d")
        hora = datetime.now().strftime("%H:%M")

        # Campos autocompletados
        st.text_input("Supervisor", supervisor, disabled=True)
        st.text_input("Centro", centro, disabled=True)

        dn = st.text_input("DN")
        if dn and (not dn.isdigit() or len(dn) != 10):
            st.warning("⚠️ El DN debe tener exactamente 10 dígitos numéricos.")

        no_orden = st.text_input("Número de Orden")
        entrega = st.selectbox("Entrega", ["", "DHL", "Tienda", "Domicilio"])
        status = st.selectbox("Status", ["", "Activada", "Perdida", "En tránsito"])
        fecha_activacion = st.text_input("Fecha de activacion (vacío si nueva)")
        comentarios = st.text_area("Comentarios")

        if st.form_submit_button("✅ Crear orden"):
            if not agente or not no_orden or not entrega or not status:
                st.error("❌ Faltan campos obligatorios: Agente, Número de Orden, Entrega o Status.")
            elif not dn.isdigit() or len(dn) != 10:
                st.error("❌ DN inválido. Debe tener exactamente 10 dígitos numéricos.")
            else:
                crear_orden([
                    fecha, hora, centro, supervisor, agente, dn,
                    no_orden, entrega, status, fecha_activacion, comentarios
                ])
                st.success(f"✅ Orden {no_orden} creada correctamente.")


# ============ ACTUALIZAR ============
with tab2:
    st.subheader("✏️ Actualizar orden")

    no_orden_to_load = st.text_input("Número de Orden a cargar")
    if st.button("Cargar orden"):
        reg = leer_orden(no_orden_to_load)
        if reg:
            st.session_state.edit_reg = reg
            st.session_state.edit_no_orden = reg["Numero de Orden"]
            st.success("✅ Orden cargada. Edita abajo y guarda cambios.")
        else:
            st.warning("⚠️ Orden no encontrada.")

    if st.session_state.edit_reg:
        reg = st.session_state.edit_reg
        entrega_opts = ["DHL", "Tienda", "Domicilio"]
        entrega_idx = entrega_opts.index(reg["Entrega"]) if reg["Entrega"] in entrega_opts else 0
        status_opts = ["Activada", "Perdida", "En tránsito"]
        status_idx = status_opts.index(reg["Status"]) if reg["Status"] in status_opts else 0

        # === Agente y autocompletado (fuera del form para actualizar en vivo) ===
        if st.session_state.df_agentes is not None:
            agente = st.selectbox(
                "Agente",
                [""] + sorted(st.session_state.df_agentes["Nombre Completo"].unique()),
                index=([""] + sorted(st.session_state.df_agentes["Nombre Completo"].unique())).index(reg["Agente"]) if reg["Agente"] in st.session_state.df_agentes["Nombre Completo"].values else 0
            )
            supervisor, centro = reg["Supervisor"], reg["Centro"]
            if agente:
                fila = st.session_state.df_agentes[st.session_state.df_agentes["Nombre Completo"] == agente].iloc[0]
                supervisor = fila["Jefe directo"]
                centro = fila["Centro"]
        else:
            agente = st.text_input("Agente", reg["Agente"])
            supervisor, centro = reg["Supervisor"], reg["Centro"]

        # === Formulario de actualización ===
        with st.form("form_update", clear_on_submit=False):
            fecha = st.text_input("Fecha", reg["Fecha"])
            hora = st.text_input("Hora", reg["Hora"])
            st.text_input("Centro", centro, disabled=True)
            st.text_input("Supervisor", supervisor, disabled=True)

            dn = st.text_input("DN", str(reg["DN"]))
            if dn and (not dn.isdigit() or len(dn) != 10):
                st.warning("⚠️ El DN debe tener exactamente 10 dígitos numéricos.")

            no_orden_val = st.text_input("Numero de Orden", reg["Numero de Orden"])
            entrega = st.selectbox("Entrega", entrega_opts, index=entrega_idx)
            status = st.selectbox("Status", status_opts, index=status_idx)
            fecha_activacion = st.text_input("Fecha de activacion", reg["Fecha de activacion"])
            comentarios = st.text_area("Comentarios", reg["Comentarios"])

            if st.form_submit_button("✏️ Guardar cambios"):
                if not agente or not no_orden_val or not entrega or not status:
                    st.error("❌ Faltan campos obligatorios: Agente, Número de Orden, Entrega o Status.")
                elif not dn.isdigit() or len(dn) != 10:
                    st.error("❌ DN inválido. Debe tener exactamente 10 dígitos numéricos.")
                else:
                    nuevos = [
                        fecha, hora, centro, supervisor, agente, dn,
                        no_orden_val, entrega, status, fecha_activacion, comentarios
                    ]
                    actualizar_orden(st.session_state.edit_no_orden, nuevos)
                    st.success(f"✅ Orden {st.session_state.edit_no_orden} actualizada correctamente.")
                    st.session_state.edit_reg = None
                    st.session_state.edit_no_orden = None
                    st.rerun()


# ============ ELIMINAR ============
with tab3:
    st.subheader("🗑️ Eliminar orden")
    no_orden_del = st.text_input("Número de Orden a eliminar")
    if st.button("Eliminar"):
        eliminar_orden(no_orden_del)
        st.success(f"🗑️ Orden {no_orden_del} eliminada correctamente.")

# ============ Tabla final ============
st.subheader("📑 Todas las órdenes en Google Sheet")
registros = get_sheet().get_all_records()
st.dataframe(registros)
