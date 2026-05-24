import os
import io
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload

class SyncManager:
    def __init__(self, auth_instance, mode="developer"):
        self.auth = auth_instance
        self.mode = mode
        self.drive_service = self._init_drive_service()

    def _init_drive_service(self):
        creds = self.auth.get_active_creds(mode=self.mode, service="drive")
        if creds:
            return build('drive', 'v3', credentials=creds)
        return None

    def upload_file(self, file_path, folder_id=None):
        if not self.drive_service: return False
        try:
            file_name = os.path.basename(file_path)
            file_metadata = {'name': file_name}
            if folder_id:
                file_metadata['parents'] = [folder_id]
                
            media = MediaFileUpload(file_path, resumable=True)
            
            results = self.drive_service.files().list(
                q=f"name='{file_name}' and trashed=false", fields="files(id)").execute()
            files = results.get('files', [])
            
            if files:
                file_id = files[0]['id']
                self.drive_service.files().update(fileId=file_id, media_body=media).execute()
            else:
                self.drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            return True
        except Exception as e:
            print(f"Sync Upload Error: {e}")
            return False

    def download_file(self, file_name, destination_path):
        if not self.drive_service: return False
        try:
            results = self.drive_service.files().list(
                q=f"name='{file_name}' and trashed=false", fields="files(id)").execute()
            files = results.get('files', [])
            
            if not files: return False
            
            file_id = files[0]['id']
            request = self.drive_service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
            
            with open(destination_path, 'wb') as f:
                f.write(fh.getvalue())
            return True
        except Exception as e:
            print(f"Sync Download Error: {e}")
            return False
