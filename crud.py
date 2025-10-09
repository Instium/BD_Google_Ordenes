from google_service import get_sheet

# CREATE
def crear_orden(datos):
    hoja = get_sheet()
    hoja.append_row(datos)
    print("✅ Orden creada:", datos)

# READ
def leer_orden(no_orden):
    hoja = get_sheet()
    registros = hoja.get_all_records()
    for reg in registros:
        if str(reg["Numero de Orden"]) == str(no_orden):
            print("🔎 Orden encontrada:", reg)
            return reg
    print("⚠️ Orden no encontrada:", no_orden)
    return None

# UPDATE
def actualizar_orden(no_orden, nuevos_datos):
    hoja = get_sheet()
    celdas = hoja.findall(str(no_orden))
    if not celdas:
        print("⚠️ Orden no encontrada:", no_orden)
        return
    fila = celdas[0].row
    hoja.update([nuevos_datos], f"A{fila}:O{fila}")  # 👈 Ajusta rango a tus columnas
    print(f"✏️ Orden {no_orden} actualizada:", nuevos_datos)

# DELETE
def eliminar_orden(no_orden):
    hoja = get_sheet()
    celdas = hoja.findall(str(no_orden))
    if not celdas:
        print("⚠️ Orden no encontrada:", no_orden)
        return
    fila = celdas[0].row
    hoja.delete_rows(fila)
    print(f"🗑️ Orden {no_orden} eliminada")
