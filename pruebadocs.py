import io, os
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload


import pandas as pd

meses_es = {
    "01": "Enero", "02": "Febrero", "03": "Marzo",
    "04": "Abril", "05": "Mayo", "06": "Junio",
    "07": "Julio", "08": "Agosto", "09": "Septiembre",
    "10": "Octubre", "11": "Noviembre", "12": "Diciembre"
}

# El ID del Google Doc que quieres leer.
DOCUMENT_ID = "d/1H4bhP6c1lhuLS9_gA53UIGs0LlJKRnVsaWfsGwLdr44"

PARENT_FOLDER_ID = "1J8gChbYr7WzcqiDMq0ldzWBZQRRfH9aw"
SUBDIRECTORY_NAME = "2025"
EXCEL_FILE_NAME = "Agosto.xlsx"

# El archivo JSON de la cuenta de servicio que descargaste.

SERVICE_ACCOUNT_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__),  'gen-lang-client-0353566026-e92bd9d19b8c.json'))


# El scope de Drive para solo lectura.
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


def build_drive_service():
    """Crea y retorna el servicio de la API de Google Drive."""
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    return build("drive", "v3", credentials=creds)


def find_item_by_name(service, name, parent_id, mimeType=None):
    q = f"'{parent_id}' in parents and name = '{name}' and trashed = false"
    if mimeType:
        q += f" and mimeType='{mimeType}'"
    results = service.files().list(q=q, fields="files(id, name)").execute()
    files = results.get('files', [])

    return files[0] if files else None

def find_file_in_folder(service, parent_folder_id, folder_name, file_name):
    """
    Busca un archivo con un nombre específico dentro de un subdirectorio.
    Retorna el ID del archivo si lo encuentra, de lo contrario, None.
    """
    #try:
    if 1:
        # 1. Busca el subdirectorio por su nombre dentro de la carpeta padre
        folder_query = f"name='{folder_name}' "
                       # and mimeType='application/vnd.google-apps.folder' and '{parent_folder_id}' in parents"

        print(("query", folder_query))

        response = service.files().list(q=folder_query, fields="files(id, name)").execute()
        folders = response.get('files', [])



        if not folders:
            print(f"No se encontró el subdirectorio '{folder_name}'.")
            return None

        subdirectory_id = folders[0]['id']
        print(f"Subdirectorio '{folder_name}' encontrado con ID: {subdirectory_id}")

        # 2. Busca el archivo Excel por su nombre dentro del subdirectorio
        file_query = f"name='{file_name}' and '{subdirectory_id}' in parents and mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'"
        response = service.files().list(q=file_query, fields="files(id, name)").execute()
        files = response.get('files', [])

        if not files:
            print(f"No se encontró el archivo '{file_name}' en el subdirectorio.")
            return None

        file_id = files[0]['id']
        print(f"Archivo '{file_name}' encontrado con ID: {file_id}")
        return file_id

    #except HttpError as error:
        print(f"Ocurrió un error en la búsqueda: {error}")
        return None

def download_sheet_as_excel(drive_service, file_id, dest_path):
    request = drive_service.files().export_media(
        fileId=file_id,
        mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    fh = io.FileIO(dest_path, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
        if status:
            print(f"Descargando... {int(status.progress() * 100)}%")
    print("Descarga completa:", dest_path)


def main(back):
    service = build_drive_service()

    about = service.about().get(fields="user").execute()
    print("Autenticado como:", about["user"])

    subdir = find_item_by_name(service, "%d"%datetime.now().year, PARENT_FOLDER_ID, mimeType="application/vnd.google-apps.folder")
    if not subdir:
        print(("Nosub "))

        #raise Exception("No encontré la subcarpeta")

    print(("subdir", subdir))

    mes_numerico = datetime.now().month
    nombre_mes_es = meses_es[str(mes_numerico).zfill(2)]  # zfill(2) asegura un número de dos dígitos
    print(nombre_mes_es)

    file = find_item_by_name(service, nombre_mes_es, subdir['id'])
    if not file:
        raise Exception("No encontré el archivo Excel")

    file_id = file['id']
    print(("file ", file_id))
    #return


    #file_id = find_file_in_folder(service, PARENT_FOLDER_ID, SUBDIRECTORY_NAME, EXCEL_FILE_NAME)

    if file_id:
        print("\n¡Puedes descargar el archivo!")
        # Aquí puedes agregar la lógica para descargar el archivo si lo necesitas,
        # usando el mismo método que en la respuesta anterior, pero con el nuevo file_id.
    else:
        print("No se pudo encontrar el archivo. Revisa los nombres y los IDs.")
        return

    download_sheet_as_excel(
        service,
        file_id,  # tu fileId
        "/tmp/%s.xlsx"%nombre_mes_es
    )

    fh = ( "/tmp/%s.xlsx"%nombre_mes_es)
# ==== 3. Descargar el archivo ====

    # ==== 4. Leer Excel con pandas ====
    today = datetime.now().strftime("%02d")
    df = pd.read_excel(fh, sheet_name=today)

    # ==== 5. Procesar cada fila ====
    for _, row in df.iterrows():
        back(row)
        #print(("row", row))
        continue

def filas(row):
    print(("row", row))

if __name__ == "__main__":
    main(filas)