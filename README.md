# Professional Tableau Dashboard Application

A modern, professional Flask-based web application for displaying and managing Tableau dashboards with advanced user preferences, favorites management, and comprehensive API endpoints.

**Version:** 2.0.0  
**Status:** Production Ready ✅

## 🌟 Features

### Core Features
- ✅ **User Authentication** - Secure login system with session management
- ✅ **Dashboard Management** - Browse, select, and view Tableau dashboards
- ✅ **Favorites System** - Save and organize favorite dashboards
- ✅ **Recent Dashboards** - Track and access recently viewed dashboards
- ✅ **User Preferences** - Customizable theme and settings per user
- ✅ **Dark Mode** - Professional dark theme support
- ✅ **Responsive Design** - Mobile-friendly interface

### Advanced Features
- ✅ **API Endpoints** - RESTful JSON API for programmatic access
- ✅ **Export Functionality** - Export dashboards and data to Excel
- ✅ **Audit Logging** - Complete user action tracking
- ✅ **Caching System** - Intelligent data caching for performance
- ✅ **Error Handling** - Comprehensive error pages and logging
- ✅ **Security** - CSRF protection, secure cookies, input validation

### Professional Features
- ✅ **Health Check API** - Application status monitoring
- ✅ **Logging System** - Rotating file logs with multiple levels
- ✅ **Configuration Management** - Environment-based configuration
- ✅ **User Data Persistence** - Local user preference storage
- ✅ **Tableau Integration** - Full Tableau Server Client support

---

## 📋 Requirements

- Python 3.8+
- Flask 3.0.0
- Tableau Server or Tableau Public
- Modern web browser (Chrome, Firefox, Safari, Edge)

---

## 🚀 Installation

### 1. Clone or Download the Repository
```bash
git clone <repository-url>
cd Tableau-with-Flask-BackEnd
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# On Linux/Mac
source venv/bin/activate

# On Windows
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
```bash
# Copy the example env file
cp .env.example .env

# Edit .env with your configuration
nano .env
```

### Required Environment Variables
```env
# Flask
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your-secure-secret-key-here-minimum-32-chars

# Tableau Server
TABLEAU_SERVER_URL=http://your-tableau-server:8000
TABLEAU_USERNAME=your-tableau-username
TABLEAU_PASSWORD=your-tableau-password
TABLEAU_PROJECT_NAME=your-project-name

# Application
APP_PASSWORD=your-app-password
ALLOWED_USERS=user1,user2,user3

# Session
SESSION_TIMEOUT=1800

# Features
ENABLE_DARK_MODE=True
ENABLE_FAVORITES=True
ENABLE_RECENT_DASHBOARDS=True
```

### 5. Create Required Directories
```bash
mkdir -p logs user_data static/images
```

### 6. Run Application
```bash
python main.py
```

The application will be available at `http://localhost:5000`

---

## 📁 Project Structure

```
Tableau-with-Flask-BackEnd/
├── main.py                 # Application entry point
├── config.py              # Configuration management
├── models.py              # Data models (User, Dashboard)
├── utils.py               # Utility functions
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variables template
│
├── templates/             # HTML templates
│   ├── login.html        # Login page
│   ├── select-dashboard.html  # Dashboard selection
│   ├── dashboard.html    # Dashboard viewer
│   ├── profile.html      # User profile
│   └── error.html        # Error pages
│
├── static/               # Static assets
│   ├── css/             # Stylesheets
│   │   ├── bootstrap.min.css
│   │   ├── login.css
│   │   ├── dashboard.css
│   │   ├── styles.css
│   │   └── util.css
│   ├── js/              # JavaScript files
│   │   ├── bootstrap.min.js
│   │   ├── jquery-3.4.1.min.js
│   │   └── mainScript.js
│   └── images/          # Image assets
│
├── logs/                # Application logs
├── user_data/           # User preferences storage
│
├── README.md            # This file
├── API.md               # API Documentation
├── CHANGELOG.md         # Version history
└── INSTALLATION.md      # Detailed installation guide
```

---

## 🔐 Security Features

### Authentication
- Secure password validation
- Session timeout (default: 30 minutes)
- CSRF protection on all forms
- Secure cookies (HttpOnly, SameSite)

### Input Validation
- Username and password validation
- File name sanitization
- Safe URL redirect validation
- SQL injection prevention

### Logging & Auditing
- User action tracking
- Failed login attempt logging
- Error logging with rotation
- Access logs for all API calls

### Data Protection
- User preferences encryption support
- Secure file handling
- Safe path operations
- XSS prevention in templates

---

## 🌐 API Documentation

### Authentication Required Endpoints

#### Get Dashboards
```bash
GET /api/dashboards

Response:
{
    "success": true,
    "dashboards": [...],
    "favorites": ["dashboard_id1", "dashboard_id2"]
}
```

#### Toggle Favorite
```bash
POST /api/dashboard/<dashboard_id>/favorite
Body: {"favorite": true}

Response:
{
    "success": true,
    "favorites": [...]
}
```

#### Track Dashboard View
```bash
POST /api/dashboard/<dashboard_id>/view

Response:
{
    "success": true
}
```

#### Get User Preferences
```bash
GET /api/user/preferences

Response:
{
    "success": true,
    "user": {
        "id": "...",
        "username": "...",
        "theme": "light",
        "favorites": [...],
        "recent_dashboards": [...]
    }
}
```

#### Update User Preferences
```bash
POST /api/user/preferences
Body: {"theme": "dark"}

Response:
{
    "success": true,
    "user": {...}
}
```

#### Export Favorites
```bash
GET /api/export/favorites

Response:
{
    "success": true,
    "file": "path/to/export.xlsx"
}
```

### Public Endpoints

#### Health Check
```bash
GET /api/health

Response:
{
    "status": "healthy",
    "uptime": "2h 45m",
    "timestamp": "2024-04-29T12:34:56",
    "version": "2.0.0"
}
```

---

## 🎨 UI/UX Features

### Theme System
- **Light Mode** (Default) - Clean white interface
- **Dark Mode** - Eye-friendly dark theme
- Persistent theme preference per user
- CSS variables for easy customization

### Responsive Design
- Mobile-first approach
- Tablet optimization
- Desktop enhancement
- Touch-friendly controls

### Visual Design
- Modern gradient accents
- Smooth animations
- Professional color scheme
- Clear typography hierarchy

### Accessibility
- Semantic HTML
- ARIA labels where needed
- Keyboard navigation support
- Color contrast compliance

---

## 🔧 Configuration

### Flask Settings
```python
FLASK_ENV          # 'production' or 'development'
FLASK_DEBUG        # True/False
SECRET_KEY         # Secret key for sessions
```

### Tableau Connection
```python
TABLEAU_SERVER_URL      # Tableau server address
TABLEAU_USERNAME        # Tableau login username
TABLEAU_PASSWORD        # Tableau login password
TABLEAU_PROJECT_NAME    # Project to display
```

### Application Settings
```python
SESSION_TIMEOUT        # Session timeout in seconds (default: 1800)
CACHE_TIMEOUT         # Cache duration in seconds (default: 300)
LOG_LEVEL             # Logging level (INFO, DEBUG, WARNING)
```

### Feature Flags
```python
ENABLE_DARK_MODE              # Enable dark mode
ENABLE_FAVORITES              # Enable favorites feature
ENABLE_RECENT_DASHBOARDS      # Enable recent dashboards
API_ENABLE_IMPORT_EXPORT      # Enable export functionality
```

---

## 📊 Logging

### Log Files
- **app.log** - Main application log
- **audit.log** - User action audit trail

### Log Levels
- **DEBUG** - Detailed information for debugging
- **INFO** - General information
- **WARNING** - Warning messages
- **ERROR** - Error messages

### Rotation
- Max file size: 10MB
- Backup count: 5 files
- Automatic cleanup of old logs

---

## 🚨 Troubleshooting

### Issue: Connection to Tableau Server Failed
**Solution:** 
- Verify Tableau server URL is correct
- Check username and password
- Ensure network connectivity
- Check firewall rules

### Issue: Users Can't Login
**Solution:**
- Verify ALLOWED_USERS in .env matches actual usernames
- Check APP_PASSWORD matches login attempt
- Check logs in `logs/app.log`

### Issue: Dashboards Not Loading
**Solution:**
- Verify Tableau project name is correct
- Check user has access to dashboards
- Clear cache: Delete cached files
- Check network connectivity

### Issue: Dark Mode Not Working
**Solution:**
- Clear browser cache
- Check ENABLE_DARK_MODE=True in .env
- Verify CSS file is loaded (check browser console)

---

## 📈 Performance Optimization

### Caching
- Dashboard data cached for 5 minutes
- Screenshot thumbnails cached
- User preferences cached

### Database Optimization
- Minimal database queries
- Efficient file operations
- Smart pagination

### Frontend Optimization
- Minified CSS and JavaScript
- Image optimization
- Lazy loading support

---

## 🔄 Deployment

### Development
```bash
python main.py
# Application runs at http://localhost:5000
```

### Production
```bash
# Using Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 main:app

# Using uWSGI
uwsgi --http :5000 --wsgi-file main.py --callable app
```

### Docker (Optional)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

---

## 📝 Version History

### v2.0.0 (Current)
- ✅ Complete redesign with modern UI
- ✅ API endpoints for programmatic access
- ✅ Dark mode theme
- ✅ Export functionality
- ✅ Comprehensive logging
- ✅ Professional code structure
- ✅ English-only interface
- ✅ CSS in separate files

### v1.0.0
- Initial release with basic functionality

---

## 📄 License

This project is provided as-is for professional use.

---

## 👥 Support

For issues, questions, or feature requests:
1. Check the troubleshooting section
2. Review logs in `logs/` directory
3. Check `.env` configuration
4. Verify Tableau connectivity

---

## 🎯 Future Enhancements

- [ ] Database support for user data
- [ ] Role-based access control (RBAC)
- [ ] Two-factor authentication (2FA)
- [ ] Dashboard search and filtering
- [ ] Advanced export formats (PDF, CSV)
- [ ] Email notifications
- [ ] Custom dashboard layouts
- [ ] Real-time dashboard updates

---

**Created with ❤️ for professional dashboard management**
