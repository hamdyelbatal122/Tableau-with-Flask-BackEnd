"""
User and Dashboard models for the application.
"""

import os
import json
import logging
from flask_login import UserMixin
from datetime import datetime

logger = logging.getLogger(__name__)


class User(UserMixin):
    """User model for Flask-Login"""
    
    def __init__(self, user_id, username):
        self.id = user_id
        self.username = username
        self.created_at = datetime.now().isoformat()
        self.last_login = None
        self.theme = 'light'
        self.favorites = []
        self.recent_dashboards = []
    
    @staticmethod
    def get(user_id):
        """Get user by ID"""
        from config import get_config
        config = get_config()
        
        try:
            user_id_int = int(user_id)
            if 0 <= user_id_int < len(config.ALLOWED_USERS):
                return User(user_id_int, config.ALLOWED_USERS[user_id_int])
        except (ValueError, TypeError):
            pass
        
        return None
    
    @staticmethod
    def get_by_username(username):
        """Get user by username"""
        from config import get_config
        config = get_config()
        
        if username in config.ALLOWED_USERS:
            user_id = config.ALLOWED_USERS.index(username)
            return User(user_id, username)
        return None
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'created_at': self.created_at,
            'last_login': self.last_login,
            'theme': self.theme,
            'favorites': self.favorites,
            'recent_dashboards': self.recent_dashboards
        }
    
    def load_preferences(self):
        """Load user preferences from file"""
        try:
            from config import get_config
            config = get_config()
            
            user_file = os.path.join(config.USER_DATA_PATH, self.username, 'preferences.json')
            
            if os.path.exists(user_file):
                with open(user_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.theme = data.get('theme', 'light')
                    self.favorites = data.get('favorites', [])
                    self.recent_dashboards = data.get('recent_dashboards', [])
                    self.last_login = data.get('last_login')
                    return True
            else:
                self.save_preferences()
                return True
        except Exception as e:
            logger.error(f"Error loading preferences for {self.username}: {str(e)}")
            return False
    
    def save_preferences(self):
        """Save user preferences to file"""
        try:
            from config import get_config
            config = get_config()
            
            user_dir = os.path.join(config.USER_DATA_PATH, self.username)
            os.makedirs(user_dir, exist_ok=True)
            
            user_file = os.path.join(user_dir, 'preferences.json')
            
            data = {
                'username': self.username,
                'theme': self.theme,
                'favorites': self.favorites,
                'recent_dashboards': self.recent_dashboards,
                'last_login': self.last_login,
                'last_updated': datetime.now().isoformat()
            }
            
            with open(user_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=True, indent=2)
            
            logger.info(f"Preferences saved for user: {self.username}")
            return True
        except Exception as e:
            logger.error(f"Error saving preferences for {self.username}: {str(e)}")
            return False
    
    def add_favorite(self, dashboard_id):
        """Add dashboard to favorites"""
        if dashboard_id not in self.favorites:
            self.favorites.append(dashboard_id)
            self.save_preferences()
            logger.info(f"Added {dashboard_id} to favorites for {self.username}")
            return True
        return False
    
    def remove_favorite(self, dashboard_id):
        """Remove dashboard from favorites"""
        if dashboard_id in self.favorites:
            self.favorites.remove(dashboard_id)
            self.save_preferences()
            logger.info(f"Removed {dashboard_id} from favorites for {self.username}")
            return True
        return False
    
    def add_to_recent(self, dashboard_id, max_items=10):
        """Add dashboard to recent list"""
        # Remove if already exists
        if dashboard_id in self.recent_dashboards:
            self.recent_dashboards.remove(dashboard_id)
        
        # Add to beginning
        self.recent_dashboards.insert(0, dashboard_id)
        
        # Keep only last N items
        self.recent_dashboards = self.recent_dashboards[:max_items]
        
        self.save_preferences()
        return True
    
    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login = datetime.now().isoformat()
        self.save_preferences()


class Dashboard:
    """Dashboard model"""
    
    def __init__(self, id, name, description=None, thumbnail=None, project=None):
        self.id = id
        self.name = name
        self.description = description or f"Dashboard: {name}"
        self.thumbnail = thumbnail
        self.project = project
        self.created_at = datetime.now().isoformat()
    
    def to_dict(self):
        """Convert dashboard to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'thumbnail': self.thumbnail,
            'project': self.project,
            'created_at': self.created_at
        }
