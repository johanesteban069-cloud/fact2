import os
import re
import pandas as pd
from datetime import datetime

# ================================
# CATEGORÍAS Y AGRUPACIONES
# ================================
categorias_fusion = {
    "A_JACUZZI_FETI": ["AMANECIDA-JACUZI F", "AMANECIDA JACUZZI", "AMANECIDA-jacuzzi", "AMANECIDA NACUZZI"],
    "R_SEN_PARQ": ["RATO-SENC-PARQ"],
    "A_SEN_PARQ": ["AMANECIDA-SENCI-PARQ", "Ananecida 10+"],
    "R_FETICH": ["RATO-FETICHE"],
    "A_FETICHE": ["AMANECIDA-FETICHE", "AMANECIDA  FETICHE"],
    "R_FETI_PARQ": ["RATO-FETICHE-PARQ"],
    "A_FETI_PARQ": ["AMANECIDA-FETICHE-PA"],
    "R_MANSION": ["RATO-MANSION"],
    "A_MANSION": ["AMANECIDA-MANSION"],
    "R_ROJA": ["RATO ROJA"],
    "A_ROJA": ["AMANECIDA ROJA", "Amanecida Roja A"],
    "H_ADC_MAN": ["HORA-ADI-MANSION"],
    "HORA_ADC": [
        "HORA-ADI-FETICHE-PAR",
        "HORA-ADI-SENCI-PARQ",
        "HORA-ADI-FETICHE",
        "HORA ADICIONAL"
    ],
    "JACUZZI_MAN": ["/JACUZI MANSION"],
    "JACUZZI": ["/JACUZZI"],
    "PER_ADC_ES": ["/PERSONA ADICIONAL E"],
    "PER_ADC": ["/PERSONA ADICIONAL"],
    "DECORA": ["/DECORACION"],
}

# ================================
# FUNCIONES AUXILIARES
# ================================
def limpiar_numero(texto):
    if not texto:
        return 0
    texto = texto.replace(".", "").replace(",", "").replace("$", "").strip()
    try:
        return int(texto)
    except ValueError:
        return 0

# ================================
# PROCESAR ARCHIVO INDIVIDUAL
# ================================
def procesar_archivo(ruta_archivo):
    """
    Procesa un archivo de texto (.txt) y devuelve un diccionario con los datos extraídos.
    Compatible con Flask/Render: no usa carpetas locales.
    """
    datos = {"archivo": os.path.basename(ruta_archivo)}

    try:
        # --- Leer el contenido directamente ---
        with open(ruta_archivo, "r", encoding="utf-8", errors="ignore") as f:
            texto = f.read()

        # --- Fecha y hora ---
        fecha = re.search(r"FECHA\s+(\d{2}[-/]\d{2}[-/]\d{4})", texto)
        hora = re.search(r"HORA\s+(\d{2}:\d{2}:\d{2})", texto)
        datos["fecha"] = fecha.group(1) if fecha else ""
        datos["hora"] = hora.group(1) if hora else ""

        # --- Totales ---
        total_hab = re.search(r"TOTAL POR HABITACIONES\s*\$?\s*([\d.,]+)", texto)
        total_prod = re.search(r"TOTAL POR PRODUCTOS\s*\$?\s*([\d.,]+)", texto)
        total_venta = re.search(r"VENTA TOTAL\s*\$?\s*([\d.,]+)", texto)

        datos["total_habitaciones"] = limpiar_numero(total_hab.group(1)) if total_hab else 0
        datos["total_productos"] = limpiar_numero(total_prod.group(1)) if total_prod else 0
        datos["total_ventas"] = limpiar_numero(total_venta.group(1)) if total_venta else 0

        # --- Inicializar categorías ---
        for cat in categorias_fusion.keys():
            datos[f"{cat}_cant"] = 0
            datos[f"{cat}_valor"] = 0

        # --- Buscar coincidencias ---
        for linea in texto.splitlines():
            for grupo, subcats in categorias_fusion.items():
                for subcat in subcats:
                    patron = rf"\b(\d+)\s+{re.escape(subcat)}\s+([\d.,]+)"
                    match = re.search(patron, linea, re.IGNORECASE)
                    if match:
                        cantidad = limpiar_numero(match.group(1))
                        valor = limpiar_numero(match.group(2))
                        datos[f"{grupo}_cant"] += cantidad
                        datos[f"{grupo}_valor"] += valor

        # ✅ Devuelve resultado limpio (sin escribir archivos)
        return datos, None

    except Exception as e:
        # ❌ Si falla, devuelve el error
        return datos, str(e)
