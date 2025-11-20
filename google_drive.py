import os
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import json

class GoogleDriveUploader:
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/drive.file']
        self.CLIENT_SECRETS_FILE = os.getenv('GOOGLE_CLIENT_SECRETS_FILE', 'credentials.json')
        self.REDIRECT_URI = os.getenv('REDIRECT_URI', 'http://localhost:8080/')
        
    def get_auth_url(self, user_id):
        """Generate Google OAuth2 authorization URL"""
        flow = Flow.from_client_secrets_file(
            self.CLIENT_SECRETS_FILE,
            scopes=self.SCOPES,
            redirect_uri=self.REDIRECT_URI
        )
        
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent',
            state=str(user_id)
        )
        
        return authorization_url
    
    def get_credentials_from_code(self, code):
        """Exchange authorization code for credentials"""
        flow = Flow.from_client_secrets_file(
            self.CLIENT_SECRETS_FILE,
            scopes=self.SCOPES,
            redirect_uri=self.REDIRECT_URI
        )
        
        flow.fetch_token(code=code)
        credentials = flow.credentials
        
        return {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }
    
    def get_service(self, token_dict):
        """Get Google Drive service instance"""
        if isinstance(token_dict, str):
            token_dict = json.loads(token_dict)
        
        creds = Credentials(
            token=token_dict['token'],
            refresh_token=token_dict.get('refresh_token'),
            token_uri=token_dict['token_uri'],
            client_id=token_dict['client_id'],
            client_secret=token_dict['client_secret'],
            scopes=token_dict['scopes']
        )
        
        # Refresh token if expired
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
        
        service = build('drive', 'v3', credentials=creds)
        return service
    
    async def upload_file(self, file_path, file_name, token_dict):
        """Upload file to Google Drive"""
        try:
            service = self.get_service(token_dict)
            
            file_metadata = {
                'name': file_name,
                'mimeType': self.get_mime_type(file_name)
            }
            
            media = MediaFileUpload(
                file_path,
                mimetype=self.get_mime_type(file_name),
                resumable=True
            )
            
            file = service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, webViewLink, webContentLink'
            ).execute()
            
            # Make file shareable
            permission = {
                'type': 'anyone',
                'role': 'reader'
            }
            service.permissions().create(
                fileId=file['id'],
                body=permission
            ).execute()
            
            return file
            
        except Exception as e:
            raise Exception(f"Google Drive upload failed: {str(e)}")
    
    def get_mime_type(self, filename):
        """Get MIME type based on file extension"""
        extension = filename.split('.')[-1].lower()
        
        mime_types = {
            'pdf': 'application/pdf',
            'doc': 'application/msword',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'xls': 'application/vnd.ms-excel',
            'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'ppt': 'application/vnd.ms-powerpoint',
            'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            'txt': 'text/plain',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'mp4': 'video/mp4',
            'avi': 'video/x-msvideo',
            'mkv': 'video/x-matroska',
            'mp3': 'audio/mpeg',
            'wav': 'audio/wav',
            'zip': 'application/zip',
            'rar': 'application/x-rar-compressed',
            '7z': 'application/x-7z-compressed'
        }
        
        return mime_types.get(extension, 'application/octet-stream')
    
    def list_files(self, token_dict, page_size=10):
        """List files from Google Drive"""
        try:
            service = self.get_service(token_dict)
            
            results = service.files().list(
                pageSize=page_size,
                fields="nextPageToken, files(id, name, mimeType, size, createdTime)"
            ).execute()
            
            return results.get('files', [])
            
        except Exception as e:
            raise Exception(f"Failed to list files: {str(e)}")
    
    def delete_file(self, token_dict, file_id):
        """Delete file from Google Drive"""
        try:
            service = self.get_service(token_dict)
            service.files().delete(fileId=file_id).execute()
            return True
        except Exception as e:
            raise Exception(f"Failed to delete file: {str(e)}")