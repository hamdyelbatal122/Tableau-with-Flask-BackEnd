"""
Utility functions for the application.
Includes security checks, logging, cache management, and export functionality.
"""

import os
import json
import logging
from functools import wraps
from urllib.parse import urlparse, urljoin
from datetime import datetime
import openpyxl
from flask import session, abort, current_app, request

logger = logging.getLogger(__name__)


def is_safe_url(target, request):
    """Check if URL is safe for redirect"""
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    
    return (test_url.scheme in ('http', 'https') and 
            ref_url.netloc == test_url.netloc)


def log_user_action(username, action, details=None):
    """Log user action for audit trail"""
    try:
        from config import get_config
        config = get_config()
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'username': username,
            'action': action,
            'details': details or {},
            'ip_address': request.remote_addr if request else 'unknown'
        }
        
        logs_dir = config.LOGS_PATH
        os.makedirs(logs_dir, exist_ok=True)
        
        audit_file = os.path.join(logs_dir, 'audit.log')
        with open(audit_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=True) + '\n')
        
        logger.info(f"User action logged - {username}: {action}")
    except Exception as e:
        logger.error(f"Error logging user action: {str(e)}")


def require_login(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask_login import current_user
        if not current_user.is_authenticated:
            abort(401)
        return f(*args, **kwargs)
    return decorated_function


def validate_username(username):
    """Validate username format"""
    if not username or not isinstance(username, str):
        return False
    if len(username) < 3 or len(username) > 50:
        return False
    return username.isalnum() or '_' in username


def validate_password(password):
    """Validate password requirements"""
    if not password or len(password) < 6:
        return False
    return True


def sanitize_filename(filename):
    """Sanitize filename for safe file operations"""
    import re
    filename = re.sub(r'[^\w\s-]', '', filename)
    filename = re.sub(r'[-\s]+', '-', filename)
    return filename.strip('-')


def export_to_excel(data, filename):
    """Export data to Excel format"""
    try:
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = 'Data'
        
        # Add headers
        if data and len(data) > 0:
            headers = list(data[0].keys())
            ws.append(headers)
            
            # Add data rows
            for row in data:
                ws.append([row.get(header, '') for header in headers])
        
        # Save
        wb.save(filename)
        logger.info(f"Data exported to Excel: {filename}")
        return True
    except Exception as e:
        logger.error(f"Error exporting to Excel: {str(e)}")
        return False


def export_to_json(data, filename):
    """Export data to JSON format"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=True, indent=2)
        logger.info(f"Data exported to JSON: {filename}")
        return True
    except Exception as e:
        logger.error(f"Error exporting to JSON: {str(e)}")
        return False


def get_user_file_path(username, filename):
    """Get safe file path for user"""
    from config import get_config
    config = get_config()
    
    user_dir = os.path.join(config.USER_DATA_PATH, sanitize_filename(username))
    os.makedirs(user_dir, exist_ok=True)
    
    return os.path.join(user_dir, sanitize_filename(filename))


def get_file_size_readable(size_bytes):
    """Convert bytes to readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def get_uptime(start_time):
    """Calculate application uptime"""
    delta = datetime.now() - start_time
    days = delta.days
    hours = delta.seconds // 3600
    minutes = (delta.seconds % 3600) // 60
    
    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    
    return ' '.join(parts) if parts else "< 1m"


def parse_bearer_token(request):
    """Parse bearer token from request headers"""
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        return auth_header[7:]
    return None


class CacheManager:
    """Simple cache manager"""
    
    _cache = {}
    
    @classmethod
    def set(cls, key, value, ttl=300):
        """Set cache value with TTL"""
        cls._cache[key] = {
            'value': value,
            'expires': datetime.now().timestamp() + ttl
        }
    
    @classmethod
    def get(cls, key):
        """Get cache value if exists and not expired"""
        if key in cls._cache:
            cache_item = cls._cache[key]
            if cache_item['expires'] > datetime.now().timestamp():
                return cache_item['value']
            else:
                del cls._cache[key]
        return None
    
    @classmethod
    def clear(cls, key=None):
        """Clear cache"""
        if key:
            cls._cache.pop(key, None)
        else:
            cls._cache.clear()
    
    @classmethod
    def get_size(cls):
        """Get cache size"""
        return len(cls._cache)
