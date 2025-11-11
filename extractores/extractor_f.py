import os
import re
import pandas as pd
from datetime import datetime

# ================================
# CONFIGURACIÓN
# ================================
carpeta_entrada = "entrada"
carpeta_salida = "salida"
archivo_salida = os.path.join(carpeta_salida, "resultado_f.xlsx")
archivo_log = os.path.join(carpeta_salida, "log_errores.txt")

os.makedirs(carpeta_salida, exist_ok=True)

# ================================
# CATEGORÍAS Y AGRUPACIONES
# ================================
# Puedes modificar fácilmente estas agrupaciones en el futuro.
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
    "HORA_ADC": ["HORA-ADI-FETICHE-PAR", "HORA-ADI-SENCI-PARQ", "HORA-ADI-FETICHE", "HORA ADICIONAL"],
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


def sumar_categorias(datos, nombres):
    """Suma cantidad y valor de varias columnas."""
    total_cant = sum(datos.get(f"{n}_cant", 0) or 0 for n in nombres)
    total_valor = sum(datos.get(f"{n}_valor", 0) or 0 for n in nombres)
    return total_cant, total_valor

# ================================
# PROCESAR ARCHIVO INDIVIDUAL
# ================================
def procesar_archivo(ruta_archivo):
    datos = {"archivo": os.path.basename(ruta_archivo)}
    try:
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

        # --- Buscar coincidencias por cada subcategoría ---
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

        return datos, None  # None = sin error

    except Exception as e:
        return datos, str(e)

# ================================
# EJECUCIÓN PRINCIPAL
# ================================
resultados = []
errores = []

for archivo in os.listdir(carpeta_entrada):
    if archivo.lower().endswith(".txt"):
        ruta = os.path.join(carpeta_entrada, archivo)
        datos, error = procesar_archivo(ruta)
        resultados.append(datos)
        if error:
            errores.append(f"[{datetime.now()}] ERROR en {archivo}: {error}")
        else:
            errores.append(f"[{datetime.now()}] OK: {archivo} procesado correctamente.")

# ================================
# EXPORTAR RESULTADOS
# ================================
df = pd.DataFrame(resultados)
df.to_excel(archivo_salida, index=False)

# Guardar log
with open(archivo_log, "w", encoding="utf-8") as log:
    for linea in errores:
        log.write(linea + "\n")

# Mostrar resumen
print("=================================")
print(" PROCESO FINALIZADO")
print("=================================")
print(f"Archivos procesados: {len(resultados)}")
print(f"Archivo Excel generado: {archivo_salida}")
print(f"Log de errores: {archivo_log}")
print("=================================")
for e in errores:
    print(e)