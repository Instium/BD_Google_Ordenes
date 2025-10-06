from crud import crear_orden, leer_orden, actualizar_orden, eliminar_orden

if __name__ == "__main__":
    # Crear orden de prueba
    crear_orden([
        "2025-10-03", "14:00", "Centro X", "Supervisor Y", "Agente 1",
        "DN123", "ORD001", "Entrega Sí", "En tránsito", "", "Sin comentarios"
    ])

    # Leer orden
    leer_orden("ORD001")

    # Actualizar orden
    actualizar_orden("ORD001", [
        "2025-10-03", "14:00", "Centro X", "Supervisor Y",
        "Agente 1", "DN123", "ORD001", "Entrega No",
        "Entregado", "2025-10-04", "Entrega confirmada"
    ])

    # Eliminar orden
    eliminar_orden("ORD001")
