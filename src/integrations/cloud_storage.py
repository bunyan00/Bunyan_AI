"""
Cloud Storage Integration Module
Handles Google Drive and OneDrive integration for file management
"""

import os
import json
import pickle
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import tempfile

# Google Drive imports
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import io

# OneDrive imports (using Microsoft Graph API)
import requests
from msal import ConfidentialClientApplication

@dataclass
class CloudFile:
    id: str
    name: str
    size: int
    modified_time: datetime
    mime_type: str
    download_url: Optional[str] = None
    parent_folder: Optional[str] = None

@dataclass
class UploadResult:
    success: bool
    file_id: str
    file_name: str
    error_message: Optional[str] = None

class GoogleDriveIntegration:
    """Google Drive integration for file storage and retrieval"""
    
    SCOPES = ['https://www.googleapis.com/auth/drive']
    
    def __init__(self, credentials_file: str = 'credentials.json'):
        self.credentials_file = credentials_file
        self.token_file = 'token.pickle'
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Drive API"""
        creds = None
        
        # Load existing token
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)
        
        # If no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_file):
                    raise FileNotFoundError(f"Google Drive credentials file not found: {self.credentials_file}")
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save credentials for next run
            with open(self.token_file, 'wb') as token:
                pickle.dump(creds, token)
        
        self.service = build('drive', 'v3', credentials=creds)
    
    def create_bunyan_folder(self) -> str:
        """Create Bunyan AI folder in Google Drive"""
        try:
            # Check if folder already exists
            results = self.service.files().list(
                q="name='Bunyan AI' and mimeType='application/vnd.google-apps.folder'",
                fields="files(id, name)"
            ).execute()
            
            folders = results.get('files', [])
            if folders:
                return folders[0]['id']
            
            # Create new folder
            folder_metadata = {
                'name': 'Bunyan AI',
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            folder = self.service.files().create(
                body=folder_metadata,
                fields='id'
            ).execute()
            
            return folder.get('id')
            
        except Exception as e:
            print(f"Error creating Bunyan folder: {e}")
            return None
    
    def upload_file(self, file_path: str, file_name: str = None, 
                   parent_folder_id: str = None) -> UploadResult:
        """Upload file to Google Drive"""
        try:
            if not file_name:
                file_name = os.path.basename(file_path)
            
            if not parent_folder_id:
                parent_folder_id = self.create_bunyan_folder()
            
            file_metadata = {
                'name': file_name,
                'parents': [parent_folder_id] if parent_folder_id else []
            }
            
            media = MediaFileUpload(file_path, resumable=True)
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            
            return UploadResult(
                success=True,
                file_id=file.get('id'),
                file_name=file_name
            )
            
        except Exception as e:
            return UploadResult(
                success=False,
                file_id='',
                file_name=file_name or '',
                error_message=str(e)
            )
    
    def download_file(self, file_id: str, download_path: str = None) -> Optional[str]:
        """Download file from Google Drive"""
        try:
            # Get file metadata
            file_metadata = self.service.files().get(fileId=file_id).execute()
            file_name = file_metadata['name']
            
            if not download_path:
                download_path = os.path.join(tempfile.gettempdir(), file_name)
            
            # Download file
            request = self.service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            
            done = False
            while done is False:
                status, done = downloader.next_chunk()
            
            # Save to file
            with open(download_path, 'wb') as f:
                f.write(fh.getvalue())
            
            return download_path
            
        except Exception as e:
            print(f"Error downloading file: {e}")
            return None
    
    def list_files(self, folder_id: str = None, file_type: str = None) -> List[CloudFile]:
        """List files in Google Drive"""
        try:
            query_parts = []
            
            if folder_id:
                query_parts.append(f"'{folder_id}' in parents")
            
            if file_type:
                if file_type == 'audio':
                    query_parts.append("mimeType contains 'audio/'")
                elif file_type == 'document':
                    query_parts.append("mimeType contains 'text/' or mimeType contains 'document'")
            
            query = " and ".join(query_parts) if query_parts else None
            
            results = self.service.files().list(
                q=query,
                fields="files(id, name, size, modifiedTime, mimeType, parents)",
                orderBy="modifiedTime desc"
            ).execute()
            
            files = []
            for file_data in results.get('files', []):
                cloud_file = CloudFile(
                    id=file_data['id'],
                    name=file_data['name'],
                    size=int(file_data.get('size', 0)),
                    modified_time=datetime.fromisoformat(file_data['modifiedTime'].replace('Z', '+00:00')),
                    mime_type=file_data['mimeType'],
                    parent_folder=file_data.get('parents', [None])[0]
                )
                files.append(cloud_file)
            
            return files
            
        except Exception as e:
            print(f"Error listing files: {e}")
            return []
    
    def delete_file(self, file_id: str) -> bool:
        """Delete file from Google Drive"""
        try:
            self.service.files().delete(fileId=file_id).execute()
            return True
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False

class OneDriveIntegration:
    """OneDrive integration using Microsoft Graph API"""
    
    def __init__(self, client_id: str, client_secret: str, tenant_id: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id
        self.access_token = None
        self.app = ConfidentialClientApplication(
            client_id=client_id,
            client_credential=client_secret,
            authority=f"https://login.microsoftonline.com/{tenant_id}"
        )
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Microsoft Graph API"""
        try:
            # Get access token
            result = self.app.acquire_token_for_client(
                scopes=["https://graph.microsoft.com/.default"]
            )
            
            if "access_token" in result:
                self.access_token = result["access_token"]
            else:
                raise Exception(f"Authentication failed: {result.get('error_description', 'Unknown error')}")
                
        except Exception as e:
            print(f"OneDrive authentication error: {e}")
            raise
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests"""
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
    
    def create_bunyan_folder(self) -> Optional[str]:
        """Create Bunyan AI folder in OneDrive"""
        try:
            # Check if folder exists
            search_url = "https://graph.microsoft.com/v1.0/me/drive/root/children"
            response = requests.get(search_url, headers=self._get_headers())
            
            if response.status_code == 200:
                items = response.json().get('value', [])
                for item in items:
                    if item['name'] == 'Bunyan AI' and 'folder' in item:
                        return item['id']
            
            # Create folder
            folder_data = {
                'name': 'Bunyan AI',
                'folder': {}
            }
            
            create_url = "https://graph.microsoft.com/v1.0/me/drive/root/children"
            response = requests.post(create_url, headers=self._get_headers(), json=folder_data)
            
            if response.status_code == 201:
                return response.json()['id']
            else:
                print(f"Error creating folder: {response.text}")
                return None
                
        except Exception as e:
            print(f"Error creating OneDrive folder: {e}")
            return None
    
    def upload_file(self, file_path: str, file_name: str = None, 
                   parent_folder_id: str = None) -> UploadResult:
        """Upload file to OneDrive"""
        try:
            if not file_name:
                file_name = os.path.basename(file_path)
            
            if not parent_folder_id:
                parent_folder_id = self.create_bunyan_folder()
            
            # For small files (< 4MB), use simple upload
            file_size = os.path.getsize(file_path)
            
            if file_size < 4 * 1024 * 1024:  # 4MB
                return self._simple_upload(file_path, file_name, parent_folder_id)
            else:
                return self._resumable_upload(file_path, file_name, parent_folder_id)
                
        except Exception as e:
            return UploadResult(
                success=False,
                file_id='',
                file_name=file_name or '',
                error_message=str(e)
            )
    
    def _simple_upload(self, file_path: str, file_name: str, parent_folder_id: str) -> UploadResult:
        """Simple upload for small files"""
        upload_url = f"https://graph.microsoft.com/v1.0/me/drive/items/{parent_folder_id}:/{file_name}:/content"
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/octet-stream'
        }
        
        with open(file_path, 'rb') as file_data:
            response = requests.put(upload_url, headers=headers, data=file_data)
        
        if response.status_code in [200, 201]:
            file_info = response.json()
            return UploadResult(
                success=True,
                file_id=file_info['id'],
                file_name=file_name
            )
        else:
            return UploadResult(
                success=False,
                file_id='',
                file_name=file_name,
                error_message=f"Upload failed: {response.text}"
            )
    
    def _resumable_upload(self, file_path: str, file_name: str, parent_folder_id: str) -> UploadResult:
        """Resumable upload for large files"""
        # Create upload session
        session_url = f"https://graph.microsoft.com/v1.0/me/drive/items/{parent_folder_id}:/{file_name}:/createUploadSession"
        
        session_data = {
            "item": {
                "@microsoft.graph.conflictBehavior": "replace",
                "name": file_name
            }
        }
        
        response = requests.post(session_url, headers=self._get_headers(), json=session_data)
        
        if response.status_code != 200:
            return UploadResult(
                success=False,
                file_id='',
                file_name=file_name,
                error_message=f"Failed to create upload session: {response.text}"
            )
        
        upload_url = response.json()['uploadUrl']
        
        # Upload file in chunks
        chunk_size = 320 * 1024  # 320KB chunks
        file_size = os.path.getsize(file_path)
        
        with open(file_path, 'rb') as file_data:
            bytes_uploaded = 0
            
            while bytes_uploaded < file_size:
                chunk = file_data.read(chunk_size)
                chunk_size_actual = len(chunk)
                
                headers = {
                    'Content-Range': f'bytes {bytes_uploaded}-{bytes_uploaded + chunk_size_actual - 1}/{file_size}',
                    'Content-Length': str(chunk_size_actual)
                }
                
                response = requests.put(upload_url, headers=headers, data=chunk)
                
                if response.status_code in [200, 201, 202]:
                    bytes_uploaded += chunk_size_actual
                    if response.status_code in [200, 201]:
                        # Upload complete
                        file_info = response.json()
                        return UploadResult(
                            success=True,
                            file_id=file_info['id'],
                            file_name=file_name
                        )
                else:
                    return UploadResult(
                        success=False,
                        file_id='',
                        file_name=file_name,
                        error_message=f"Upload failed at chunk {bytes_uploaded}: {response.text}"
                    )
        
        return UploadResult(
            success=False,
            file_id='',
            file_name=file_name,
            error_message="Upload completed but no response received"
        )
    
    def download_file(self, file_id: str, download_path: str = None) -> Optional[str]:
        """Download file from OneDrive"""
        try:
            # Get file metadata
            metadata_url = f"https://graph.microsoft.com/v1.0/me/drive/items/{file_id}"
            response = requests.get(metadata_url, headers=self._get_headers())
            
            if response.status_code != 200:
                print(f"Error getting file metadata: {response.text}")
                return None
            
            file_info = response.json()
            file_name = file_info['name']
            
            if not download_path:
                download_path = os.path.join(tempfile.gettempdir(), file_name)
            
            # Download file content
            download_url = f"https://graph.microsoft.com/v1.0/me/drive/items/{file_id}/content"
            response = requests.get(download_url, headers=self._get_headers())
            
            if response.status_code == 200:
                with open(download_path, 'wb') as f:
                    f.write(response.content)
                return download_path
            else:
                print(f"Error downloading file: {response.text}")
                return None
                
        except Exception as e:
            print(f"Error downloading file: {e}")
            return None
    
    def list_files(self, folder_id: str = None, file_type: str = None) -> List[CloudFile]:
        """List files in OneDrive"""
        try:
            if folder_id:
                list_url = f"https://graph.microsoft.com/v1.0/me/drive/items/{folder_id}/children"
            else:
                list_url = "https://graph.microsoft.com/v1.0/me/drive/root/children"
            
            response = requests.get(list_url, headers=self._get_headers())
            
            if response.status_code != 200:
                print(f"Error listing files: {response.text}")
                return []
            
            files = []
            for item in response.json().get('value', []):
                # Skip folders unless specifically requested
                if 'folder' in item and file_type != 'folder':
                    continue
                
                # Filter by file type if specified
                if file_type and file_type != 'folder':
                    mime_type = item.get('file', {}).get('mimeType', '')
                    if file_type == 'audio' and not mime_type.startswith('audio/'):
                        continue
                    elif file_type == 'document' and not (mime_type.startswith('text/') or 'document' in mime_type):
                        continue
                
                cloud_file = CloudFile(
                    id=item['id'],
                    name=item['name'],
                    size=item.get('size', 0),
                    modified_time=datetime.fromisoformat(item['lastModifiedDateTime'].replace('Z', '+00:00')),
                    mime_type=item.get('file', {}).get('mimeType', 'application/octet-stream'),
                    download_url=item.get('@microsoft.graph.downloadUrl')
                )
                files.append(cloud_file)
            
            return files
            
        except Exception as e:
            print(f"Error listing files: {e}")
            return []
    
    def delete_file(self, file_id: str) -> bool:
        """Delete file from OneDrive"""
        try:
            delete_url = f"https://graph.microsoft.com/v1.0/me/drive/items/{file_id}"
            response = requests.delete(delete_url, headers=self._get_headers())
            
            return response.status_code == 204
            
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False

class CloudStorageManager:
    """Unified manager for multiple cloud storage providers"""
    
    def __init__(self):
        self.providers = {}
        self.default_provider = None
    
    def add_google_drive(self, credentials_file: str):
        """Add Google Drive as a storage provider"""
        try:
            provider = GoogleDriveIntegration(credentials_file)
            self.providers['google_drive'] = provider
            if not self.default_provider:
                self.default_provider = 'google_drive'
            return True
        except Exception as e:
            print(f"Error adding Google Drive: {e}")
            return False
    
    def add_onedrive(self, client_id: str, client_secret: str, tenant_id: str):
        """Add OneDrive as a storage provider"""
        try:
            provider = OneDriveIntegration(client_id, client_secret, tenant_id)
            self.providers['onedrive'] = provider
            if not self.default_provider:
                self.default_provider = 'onedrive'
            return True
        except Exception as e:
            print(f"Error adding OneDrive: {e}")
            return False
    
    def upload_session_backup(self, session_data: Dict[str, Any], 
                            provider: str = None) -> UploadResult:
        """Upload session backup to cloud storage"""
        if not provider:
            provider = self.default_provider
        
        if provider not in self.providers:
            return UploadResult(
                success=False,
                file_id='',
                file_name='',
                error_message=f"Provider {provider} not configured"
            )
        
        # Create backup file
        backup_filename = f"bunyan_session_{session_data['session_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        backup_path = os.path.join(tempfile.gettempdir(), backup_filename)
        
        try:
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, default=str)
            
            # Upload to cloud
            result = self.providers[provider].upload_file(backup_path, backup_filename)
            
            # Clean up local file
            os.remove(backup_path)
            
            return result
            
        except Exception as e:
            return UploadResult(
                success=False,
                file_id='',
                file_name=backup_filename,
                error_message=str(e)
            )
    
    def list_session_backups(self, provider: str = None) -> List[CloudFile]:
        """List session backup files"""
        if not provider:
            provider = self.default_provider
        
        if provider not in self.providers:
            return []
        
        all_files = self.providers[provider].list_files()
        backup_files = [f for f in all_files if f.name.startswith('bunyan_session_')]
        
        return sorted(backup_files, key=lambda x: x.modified_time, reverse=True)
    
    def restore_session_backup(self, file_id: str, provider: str = None) -> Optional[Dict[str, Any]]:
        """Restore session from backup file"""
        if not provider:
            provider = self.default_provider
        
        if provider not in self.providers:
            return None
        
        # Download backup file
        download_path = self.providers[provider].download_file(file_id)
        
        if not download_path:
            return None
        
        try:
            with open(download_path, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            # Clean up downloaded file
            os.remove(download_path)
            
            return session_data
            
        except Exception as e:
            print(f"Error restoring backup: {e}")
            return None