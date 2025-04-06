import os
import json
import xml.etree.ElementTree as ET
import requests
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('CVR_API')

class CVRApi:
    def __init__(self):
        self.api_base_url = "https://api.abinteractive.net/1"
        self.username = None
        self.access_key = None
        self.authenticated = False
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'CVR-Profile-Manager/1.0',
            'MatureContentDlc': 'true',
            'Platform': 'pc_standalone',
            'CompatibleVersions': '0,1,2',
        })
    
    def load_credentials_from_file(self, file_path):
        """Load credentials from the autologin.profile file."""
        try:
            if not os.path.exists(file_path):
                logger.error(f"Autologin profile file not found: {file_path}")
                return False
            
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            username_elem = root.find('Username')
            access_key_elem = root.find('AccessKey')
            
            if username_elem is None or access_key_elem is None:
                logger.error("Autologin profile file is missing Username or AccessKey")
                return False
            
            self.username = username_elem.text
            self.access_key = access_key_elem.text
            
            # Update session headers with authentication
            self.session.headers.update({
                'Username': self.username,
                'AccessKey': self.access_key,
            })
            
            self.authenticated = True
            logger.info(f"Successfully loaded credentials for user: {self.username}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading credentials: {str(e)}")
            return False
    
    def get_avatar_by_id(self, avatar_id):
        """Get avatar information by ID."""
        if not self.authenticated:
            logger.error("Not authenticated. Please load credentials first.")
            return None
        
        try:
            url = f"{self.api_base_url}/avatars/{avatar_id}"
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Successfully retrieved avatar data for ID: {avatar_id}")
                # Return the entire data object to allow access to all fields
                return data.get('data')
            else:
                logger.error(f"Failed to get avatar data. Status code: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting avatar data: {str(e)}")
            return None 