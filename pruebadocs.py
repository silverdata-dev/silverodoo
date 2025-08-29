import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

# El ID del Google Doc que quieres leer.
DOCUMENT_ID = "d/1H4bhP6c1lhuLS9_gA53UIGs0LlJKRnVsaWfsGwLdr44"

PARENT_FOLDER_ID = "1J8gChbYr7WzcqiDMq0ldzWBZQRRfH9aw"
SUBDIRECTORY_NAME = "2025"
EXCEL_FILE_NAME = "Agosto.xlsx"

# El archivo JSON de la cuenta de servicio que descargaste.
SERVICE_ACCOUNT_FILE = 'gen-lang-client-0353566026-e92bd9d19b8c.json'

# El scope de Drive para solo lectura.
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


def build_drive_service():
    """Crea y retorna el servicio de la API de Google Drive."""
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    return build("drive", "v3", credentials=creds)


def find_file_in_folder(service, parent_folder_id, folder_name, file_name):
    """
    Busca un archivo con un nombre específico dentro de un subdirectorio.
    Retorna el ID del archivo si lo encuentra, de lo contrario, None.
    """
    try:
        # 1. Busca el subdirectorio por su nombre dentro de la carpeta padre
        folder_query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and '{parent_folder_id}' in parents"
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

    except HttpError as error:
        print(f"Ocurrió un error en la búsqueda: {error}")
        return None


def main():
    service = build_drive_service()


    file_id = find_file_in_folder(service, PARENT_FOLDER_ID, SUBDIRECTORY_NAME, EXCEL_FILE_NAME)

    if file_id:
        print("\n¡Puedes descargar el archivo!")
        # Aquí puedes agregar la lógica para descargar el archivo si lo necesitas,
        # usando el mismo método que en la respuesta anterior, pero con el nuevo file_id.
    else:
        print("No se pudo encontrar el archivo. Revisa los nombres y los IDs.")



if __name__ == "__main__":
    main()