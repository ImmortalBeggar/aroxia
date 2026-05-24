import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account

class Auth:
    def __init__(self, token_file='config/token.json', credentials_file='config/credentials.json', service_account_file='config/service_account.json'):
        self.token_file = token_file
        self.credentials_file = credentials_file
        self.service_account_file = service_account_file
        self.scopes = [
            'https://www.googleapis.com/auth/generative-language.retriever',
            'https://www.googleapis.com/auth/drive.file'
        ]

    def get_developer_key(self):
        # For Gemini API
        return os.environ.get("GEMINI_API_KEY")

    def get_developer_service_account(self):
        # For GDrive Sync in Dev Mode
        if os.path.exists(self.service_account_file):
            return service_account.Credentials.from_service_account_file(
                self.service_account_file, scopes=self.scopes)
        return None

    def get_user_credentials(self):
        # OAuth flow for both Gemini and GDrive
        creds = None
        if os.path.exists(self.token_file):
            creds = Credentials.from_authorized_user_file(self.token_file, self.scopes)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_file):
                    return None
                
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_file, self.scopes)
                creds = flow.run_local_server(port=0)
            
            with open(self.token_file, 'w') as token:
                token.write(creds.to_json())
        
        return creds

    def get_active_creds(self, mode="developer", service="gemini"):
        if mode == "user":
            return self.get_user_credentials()
        
        if service == "drive":
            return self.get_developer_service_account()
        return self.get_developer_key()
