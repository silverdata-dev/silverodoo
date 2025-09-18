#!/bin/bash

# --- Configuración ---
# Directorio local a monitorear
LOCAL_DIR="/home/sergio/Documents/Proyectos/silverdata/silverodoo/silver_isp"

# Configuración del servidor remoto SFTP
REMOTE_USER="root"
REMOTE_HOST="10.0.0.198"
REMOTE_DIR="/var/lib/odoo/silverodoo/silver_isp"

# Opciones de exclusión para rsync
# Agrega aquí los archivos o directorios que no quieres sincronizar
# Separados por espacios. Por ejemplo: ".git .DS_Store node_modules"
EXCLUDE_PATTERNS=".git"

# --- Lógica del script ---

# Función para sincronizar los archivos
sync_files() {
  echo "$(date): Iniciando sincronización..."
  
  # Usa rsync con la bandera -a para modo archivo, -v para ser más verboso
  # --delete para eliminar archivos en el destino que ya no están en el origen
  # --exclude para usar los patrones de exclusión
  # -e "ssh" para forzar el uso de SSH, que rsync necesita para SFTP
  rsync -avz --delete \
    --exclude-from=<(printf "%s" "$EXCLUDE_PATTERNS") \
    -e "ssh" -i ~/odooprueba \
    "$LOCAL_DIR/" "$REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR/"
  
  # Chequea si el comando rsync fue exitoso
  if [ $? -eq 0 ]; then
    echo "$(date): Sincronización completada con éxito."
  else
    echo "$(date): ERROR: La sincronización falló. Revisa la configuración y la conexión."
  fi
}

# Bucle principal que usa inotifywait para detectar cambios
echo "$(date): Monitoreando cambios en $LOCAL_DIR..."

inotifywait -m -r -e create,delete,modify,move "$LOCAL_DIR" --format '%w%f' | while read FILE
do
  echo "$(date): Cambio detectado en $FILE. Sincronizando..."
  sync_files
done
