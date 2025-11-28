

import os
from typing import BinaryIO
import requests
import json
from typing import Optional 
from dotenv import load_dotenv
load_dotenv()

class WhatsappSender:
    def __init__(self):
        self.ACCESS_TOKEN = os.getenv("META_TOKEN")
        self.PHONE_NUMBER_ID = os.getenv("PHONE_ID")
        self.VERSION = "v22.0"
    
    def upload_file(self, filename, file: BinaryIO):
        print(f"Uploading {filename} to WhatsApp...")

        if hasattr(file, 'seek'):
            file.seek(0)
    
        upload_url = f"https://graph.facebook.com/{self.VERSION}/{self.PHONE_NUMBER_ID}/media"
        
        headers = {
            "Authorization": f"Bearer {self.ACCESS_TOKEN}"
        }
        
        
        files = {
            'file': (filename, file, 'application/pdf'),
            'type': (None, 'application/pdf'),
            'messaging_product': (None, 'whatsapp')
        }

        try:
            response = requests.post(upload_url, headers=headers, files=files)
            response.raise_for_status() 

            media_id = response.json().get('id')
            print(f"File uploaded! Media ID: {media_id}")
            return media_id
            
        except requests.exceptions.RequestException as e:
            print(f"Upload Failed: {e}")
            if 'response' in locals():
                print(f"Response details: {response.text}")
            return -1
    
    def send_bill(self, filename, bill: BinaryIO, date: Optional[str], recipient_number: Optional[str] = os.getenv("RECIPIENT_PHONE")):
        media_id = self.upload_file(filename, bill)
        if media_id == -1:
            return "Error: Could not upload bill to WhatsApp.", -1
        else:
            send_url = f"https://graph.facebook.com/{self.VERSION}/{self.PHONE_NUMBER_ID}/messages"
    
            payload = {
                "messaging_product": "whatsapp",
                "to": recipient_number,
                "type": "document",
                "document": {
                    "id": media_id,  
                    "filename": filename,
                    "caption": f"Hello! Here is your bill for {date}."
                }
            }
            
            headers_send = {
                "Authorization": f"Bearer {self.ACCESS_TOKEN}",
                "Content-Type": "application/json"
            }

            try:
                response = requests.post(send_url, headers=headers_send, json=payload)
                response.raise_for_status()
                return "Bill sent successfully.", 0
            except requests.exceptions.RequestException as e:
                return f"Error sending message: {e}", -1


