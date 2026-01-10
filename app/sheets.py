import asyncio
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from app.config import GOOGLE_CREDENTIALS_FILE, SCOPES

class SheetsService:
    def __init__(self):
        self.credentials = Credentials.from_service_account_file(GOOGLE_CREDENTIALS_FILE, scopes=SCOPES)
        self.service = build('sheets', 'v4', credentials=self.credentials)
    
    async def get_data(self, sheet_id: str, range_name: str):
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: self.service.spreadsheets().values().get(
                spreadsheetId=sheet_id, range=range_name
            ).execute()
        )
        return result.get('values', [])
    
    async def update_data(self, sheet_id: str, range_name: str, values):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: self.service.spreadsheets().values().update(
                spreadsheetId=sheet_id,
                range=range_name,
                valueInputOption='RAW',
                body={'values': values}
            ).execute()
        )