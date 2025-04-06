import os
import json
import time
import requests
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('CACHE_MANAGER')

class CacheManager:
    def __init__(self, cache_dir="cache"):
        """Initialize the cache manager."""
        self.cache_dir = cache_dir
        self.avatar_cache_file = os.path.join(cache_dir, "avatar_cache.json")
        self.thumbnails_dir = os.path.join(cache_dir, "thumbnails")
        self.avatar_cache = {}
        
        # Create cache directories if they don't exist
        os.makedirs(cache_dir, exist_ok=True)
        os.makedirs(self.thumbnails_dir, exist_ok=True)
        
        # Load existing cache
        self.load_cache()
    
    def load_cache(self):
        """Load the avatar cache from disk."""
        if os.path.exists(self.avatar_cache_file):
            try:
                with open(self.avatar_cache_file, 'r') as f:
                    self.avatar_cache = json.load(f)
                logger.info(f"Loaded {len(self.avatar_cache)} avatar entries from cache")
            except Exception as e:
                logger.error(f"Error loading cache: {str(e)}")
                self.avatar_cache = {}
    
    def save_cache(self):
        """Save the avatar cache to disk."""
        try:
            with open(self.avatar_cache_file, 'w') as f:
                json.dump(self.avatar_cache, f, indent=4)
            logger.info(f"Saved {len(self.avatar_cache)} avatar entries to cache")
        except Exception as e:
            logger.error(f"Error saving cache: {str(e)}")
    
    def get_avatar_data(self, avatar_id, api_client=None):
        """Get avatar data from cache or API."""
        # Define the required fields that should be in the cache
        required_fields = ["name", "imageUrl", "lastUpdated", "isPublished", "isSharedWithMe", "creatorName"]
        
        # Check if we have the data in cache
        if avatar_id in self.avatar_cache:
            cache_entry = self.avatar_cache[avatar_id]
            
            # Check if all required fields are present
            missing_fields = [field for field in required_fields if field not in cache_entry]
            
            if not missing_fields:
                logger.info(f"Avatar {avatar_id} found in cache with all required fields")
                return cache_entry
            else:
                logger.info(f"Avatar {avatar_id} found in cache but missing fields: {missing_fields}")
                # If we have an API client, fetch fresh data
                if api_client and api_client.authenticated:
                    logger.info(f"Updating cache for avatar {avatar_id} with missing fields")
                    # Continue to API fetch below
        
        # If not in cache, missing fields, or we need to update, fetch from API
        if api_client and api_client.authenticated:
            # Get avatar data from API
            avatar_data = api_client.get_avatar_by_id(avatar_id)
            if avatar_data:
                # Extract relevant fields
                cache_entry = {
                    "name": avatar_data.get("name", "Unknown Avatar"),
                    "imageUrl": avatar_data.get("imageUrl", ""),
                    "lastUpdated": time.time(),
                    "isPublished": avatar_data.get("isPublished", False),
                    "isSharedWithMe": avatar_data.get("isSharedWithMe", False),
                    "creatorName": avatar_data.get("user", {}).get("name", "Unknown Creator")
                }
                
                # Save to cache
                self.avatar_cache[avatar_id] = cache_entry
                self.save_cache()
                
                # Download thumbnail if we have an image URL
                if cache_entry["imageUrl"]:
                    self.download_thumbnail(avatar_id, cache_entry["imageUrl"])
                
                return cache_entry
        
        # Return a default entry if we couldn't get the data
        return {
            "name": "Unknown Avatar",
            "imageUrl": "",
            "lastUpdated": 0,
            "isPublished": False,
            "isSharedWithMe": False,
            "creatorName": "Unknown Creator"
        }
    
    def download_thumbnail(self, avatar_id, image_url):
        """Download and cache an avatar thumbnail."""
        if not image_url:
            return
        
        thumbnail_path = os.path.join(self.thumbnails_dir, f"{avatar_id}.jpg")
        
        # Skip if we already have the thumbnail
        if os.path.exists(thumbnail_path):
            return
        
        try:
            # Download the image
            response = requests.get(image_url, stream=True)
            if response.status_code == 200:
                with open(thumbnail_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                logger.info(f"Downloaded thumbnail for avatar {avatar_id}")
            else:
                logger.error(f"Failed to download thumbnail for avatar {avatar_id}: {response.status_code}")
        except Exception as e:
            logger.error(f"Error downloading thumbnail for avatar {avatar_id}: {str(e)}")
    
    def get_thumbnail_path(self, avatar_id):
        """Get the path to a cached thumbnail."""
        thumbnail_path = os.path.join(self.thumbnails_dir, f"{avatar_id}.jpg")
        if os.path.exists(thumbnail_path):
            return thumbnail_path
        return None 