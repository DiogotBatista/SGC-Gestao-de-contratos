import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from io import BytesIO
from django.conf import settings

# Caminho absoluto para o arquivo de credenciais
SERVICE_ACCOUNT_FILE = os.path.join(settings.BASE_DIR, 'config', 'drive_service_account.json')

# ID da pasta principal das atas (definido no .env)
DRIVE_FOLDER_ID = settings.GOOGLE_DRIVE_FOLDER_ID

# Escopo de permissão
SCOPES = ['https://www.googleapis.com/auth/drive']

def get_drive_service():
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    return build('drive', 'v3', credentials=credentials)

def create_folder_for_ata(nome_pasta, parent_id=DRIVE_FOLDER_ID):
    service = get_drive_service()
    folder_metadata = {
        'name': nome_pasta,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent_id]
    }
    folder = service.files().create(
        body=folder_metadata,
        fields='id'
    ).execute()
    return folder.get('id')

def upload_file_to_drive(file, filename, folder_id):
    service = get_drive_service()
    file_metadata = {
        'name': filename,
        'parents': [folder_id]
    }
    media = MediaIoBaseUpload(file, mimetype=file.content_type, resumable=True)
    uploaded = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id, webViewLink'
    ).execute()
    return uploaded.get('webViewLink'), uploaded.get('id')

def delete_file_in_drive(file_id):
    service = get_drive_service()
    try:
        service.files().delete(fileId=file_id).execute()
    except Exception as e:
        print(f"Erro ao excluir arquivo {file_id}: {e}")

def delete_folder_in_drive(folder_id):
    service = get_drive_service()
    try:
        # Buscar todos os arquivos e subpastas dentro da pasta
        query = f"'{folder_id}' in parents"
        response = service.files().list(q=query, fields="files(id)").execute()
        files = response.get('files', [])
        for file in files:
            delete_file_in_drive(file['id'])
        # Excluir a própria pasta
        service.files().delete(fileId=folder_id).execute()
    except Exception as e:
        print(f"Erro ao excluir pasta {folder_id}: {e}")
