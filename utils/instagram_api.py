import requests
import os
import json
from datetime import datetime

class InstagramAPI:
    def __init__(self):
        self.access_token = os.getenv('INSTAGRAM_ACCESS_TOKEN', '')
        self.user_id = os.getenv('INSTAGRAM_USER_ID', '')
        self.base_url = "https://graph.instagram.com"
        self.config_file = "config/instagram_config.json"
        
        # Load saved configuration
        self._load_config()
    
    def _load_config(self):
        """Load Instagram API configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.access_token = config.get('access_token', self.access_token)
                    self.user_id = config.get('user_id', self.user_id)
        except Exception as e:
            print(f"Error loading Instagram config: {str(e)}")
    
    def configure(self, access_token, user_id):
        """Configure Instagram API credentials"""
        self.access_token = access_token
        self.user_id = user_id
        
        # Save configuration
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            config = {
                'access_token': access_token,
                'user_id': user_id,
                'configured_at': datetime.now().isoformat()
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        
        except Exception as e:
            print(f"Error saving Instagram config: {str(e)}")
    
    def is_configured(self):
        """Check if Instagram API is properly configured"""
        return bool(self.access_token and self.user_id)
    
    def get_account_info(self):
        """Get basic account information"""
        if not self.is_configured():
            return None
        
        try:
            url = f"{self.base_url}/{self.user_id}"
            params = {
                'fields': 'id,username,account_type,media_count',
                'access_token': self.access_token
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            return response.json()
        
        except requests.exceptions.RequestException as e:
            print(f"Error fetching account info: {str(e)}")
            return None
    
    def get_recent_media(self, limit=10):
        """Get recent media posts"""
        if not self.is_configured():
            return None
        
        try:
            url = f"{self.base_url}/{self.user_id}/media"
            params = {
                'fields': 'id,caption,media_type,media_url,thumbnail_url,timestamp,permalink',
                'limit': limit,
                'access_token': self.access_token
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            return data.get('data', [])
        
        except requests.exceptions.RequestException as e:
            print(f"Error fetching recent media: {str(e)}")
            return None
    
    def get_media_insights(self, media_id):
        """Get insights for a specific media post"""
        if not self.is_configured():
            return None
        
        try:
            url = f"{self.base_url}/{media_id}/insights"
            params = {
                'metric': 'impressions,reach,likes,comments,saves,shares',
                'access_token': self.access_token
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            return response.json()
        
        except requests.exceptions.RequestException as e:
            print(f"Error fetching media insights: {str(e)}")
            return None
    
    def validate_token(self):
        """Validate the current access token"""
        if not self.access_token:
            return False
        
        try:
            url = f"{self.base_url}/me"
            params = {
                'access_token': self.access_token
            }
            
            response = requests.get(url, params=params)
            return response.status_code == 200
        
        except:
            return False
    
    def get_token_info(self):
        """Get information about the current token"""
        if not self.access_token:
            return None
        
        try:
            url = f"{self.base_url}/access_token"
            params = {
                'grant_type': 'ig_exchange_token',
                'client_secret': os.getenv('INSTAGRAM_CLIENT_SECRET', ''),
                'access_token': self.access_token
            }
            
            response = requests.get(url, params=params)
            if response.status_code == 200:
                return response.json()
        
        except:
            pass
        
        return None
    
    def refresh_token(self):
        """Refresh the long-lived access token"""
        if not self.access_token:
            return False
        
        try:
            url = f"{self.base_url}/refresh_access_token"
            params = {
                'grant_type': 'ig_refresh_token',
                'access_token': self.access_token
            }
            
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                new_token = data.get('access_token')
                
                if new_token:
                    self.access_token = new_token
                    # Update saved configuration
                    self.configure(new_token, self.user_id)
                    return True
        
        except Exception as e:
            print(f"Error refreshing token: {str(e)}")
        
        return False
    
    def get_hashtag_info(self, hashtag):
        """Get information about a hashtag (requires business account)"""
        if not self.is_configured():
            return None
        
        try:
            # First, search for the hashtag ID
            url = f"{self.base_url}/ig_hashtag_search"
            params = {
                'user_id': self.user_id,
                'q': hashtag,
                'access_token': self.access_token
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            hashtag_data = data.get('data', [])
            
            if hashtag_data:
                hashtag_id = hashtag_data[0]['id']
                
                # Get hashtag info
                url = f"{self.base_url}/{hashtag_id}"
                params = {
                    'fields': 'id,name',
                    'access_token': self.access_token
                }
                
                response = requests.get(url, params=params)
                response.raise_for_status()
                
                return response.json()
        
        except requests.exceptions.RequestException as e:
            print(f"Error fetching hashtag info: {str(e)}")
        
        return None
