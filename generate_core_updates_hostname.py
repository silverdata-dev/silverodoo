import csv
import os

# --- Configuración ---
CSV_FILE_PATH = './recuro/Equipo Core (isp.core).csv'
# Mapeo de nombres de columnas en el CSV a los datos que necesitamos.
CSV_HOSTNAME_COLUMN = 'Hostname'
CSV_IP_COLUMN = 'IP de Conexion'
CSV_PORT_COLUMN = 'Puerto de Conexion'
# --- Fin de la Configuración ---

def generate_sql_updates_by_hostname():
    """
    Lee el archivo CSV y genera sentencias SQL UPDATE usando el hostname.
    """
    if not os.path.exists(CSV_FILE_PATH):
        print(f"-- ERROR: No se pudo encontrar el archivo CSV en la ruta: {CSV_FILE_PATH}")
        return

    print("-- Script para actualizar IP y Puerto de Equipos Core (silver.core) por Hostname")
    print("-- Generado por el Asistente Gemini.")
    print("-- Por favor, revisa las sentencias antes de ejecutarlas en producción.\n")

    try:
        with open(CSV_FILE_PATH, mode='r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            # Validar que las columnas existan
            if not all(key in reader.fieldnames for key in [CSV_HOSTNAME_COLUMN, CSV_IP_COLUMN, CSV_PORT_COLUMN]):
                print(f"-- ERROR: El archivo CSV debe contener las columnas '{CSV_HOSTNAME_COLUMN}', '{CSV_IP_COLUMN}', y '{CSV_PORT_COLUMN}'.")
                print(f"-- Columnas encontradas: {reader.fieldnames}")
                return

            for row in reader:
                hostname = row.get(CSV_HOSTNAME_COLUMN, '').strip()
                ip_address = row.get(CSV_IP_COLUMN, '').strip()
                port = row.get(CSV_PORT_COLUMN, '').strip()

                if not hostname:
                    continue # Omitir filas sin hostname

                # Construir la subconsulta para encontrar el netdev_id correcto
                # Esta vez, la consulta es más simple porque hostname_core está en silver_core
                subquery = (
                    f"SELECT netdev_id FROM silver_core WHERE hostname_core = '{hostname}'"
                )

                # Generar la sentencia UPDATE
                update_statement = (
                    f"UPDATE silver_netdev SET "
                    f"ip = '{ip_address}', "
                    f"port = '{port}' "
                    f"WHERE id = ({subquery});"
                )
                
                print(update_statement)

    except Exception as e:
        print(f"-- Ha ocurrido un error al procesar el archivo: {e}")

if __name__ == "__main__":
    generate_sql_updates_by_hostname()
