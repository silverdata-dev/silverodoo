import os,sys,string


import pandas as pd
import csv
import os

# --- Configuración ---
ARCHIVO_ENTRADA = "Equipo Core (isp.core).csv"
ARCHIVO_SALIDA = "productos_import_odoo.csv"

# Nombres de las columnas en el archivo de entrada
COLUMNA_MARCA = "Marca"
COLUMNA_MODELO = "Modelo"

# Nombres de las columnas en el archivo de salida (para Odoo Product Template)
# Odoo usa 'name' como nombre principal, y el campo 'type' (product type) es obligatorio.
COLUMNAS_SALIDA = ['name', 'Marca', 'Modelo', 'type']


def generar_productos_odoo(archivo_entrada, archivo_salida):
    """
    Lee el archivo CSV de equipos, agrupa por Marca y Modelo, y genera
    un archivo CSV listo para importar plantillas de productos en Odoo.
    """
    if not os.path.exists(archivo_entrada):
        print(f"❌ Error: El archivo de entrada '{archivo_entrada}' no se encontró.")
        return

    print(f"⏳ Leyendo datos de: {archivo_entrada}...")

    try:
        # 1. Leer el archivo CSV completo
        df = pd.read_csv(archivo_entrada)

        # 2. Seleccionar solo las columnas de interés y eliminar duplicados
        #    Esto nos da las combinaciones únicas de Marca y Modelo.
        df_productos = df[[COLUMNA_MARCA, COLUMNA_MODELO]].drop_duplicates()

        # 3. Eliminar filas donde Marca o Modelo sean valores faltantes/vacíos
        df_productos.dropna(subset=[COLUMNA_MARCA, COLUMNA_MODELO], inplace=True)

        # 4. Crear la columna 'name' (Nombre del Producto)
        #    Combinamos Marca y Modelo como nombre (e.g., Mikrotik - CCR2116-12G-4S+)
        df_productos['name'] = df_productos[COLUMNA_MARCA] + ' - ' + df_productos[COLUMNA_MODELO]

        # 5. Agregar el campo 'type' (Tipo de Producto en Odoo)
        #    Asumimos que son productos almacenables ('product') o consumibles ('consu')
        #    Usaremos 'product' (almacenable/stockable) por ser hardware.
        df_productos['type'] = 'product'

        # 6. Reordenar las columnas para el formato de salida deseado
        df_final = df_productos[COLUMNAS_SALIDA]

        # 7. Escribir el DataFrame resultante a un nuevo archivo CSV
        df_final.to_csv(archivo_salida, index=False, quoting=csv.QUOTE_NONNUMERIC)

        print(f"✅ Proceso completado. Se generó el archivo de importación: {archivo_salida}")
        print("\n--- Vista Previa de los Datos Generados ---")
        print(df_final.head(10).to_markdown(index=False))
        print(f"\nTotal de productos únicos a importar: {len(df_final)}")

    except Exception as e:
        print(f"❌ Ocurrió un error durante el procesamiento de datos: {e}")


if __name__ == "__main__":
    generar_productos_odoo(ARCHIVO_ENTRADA, ARCHIVO_SALIDA)
