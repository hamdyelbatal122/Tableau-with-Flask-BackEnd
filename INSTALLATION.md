# Installation Guide

Complete step-by-step guide for installing and configuring the Professional Tableau Dashboard Application.

**Estimated Time:** 15-20 minutes

---

## Prerequisites

### System Requirements
- **OS:** Linux, macOS, or Windows
- **Python:** 3.8 or higher
- **RAM:** Minimum 512MB
- **Disk Space:** 500MB
- **Network:** Access to Tableau Server

### Software Requirements
```bash
# Check Python version
python --version  # Should be 3.8 or higher

# Check pip is installed
pip --version
```

---

## Installation Steps

### Step 1: Get the Code

#### Option A: Clone from Git
```bash
git clone https://github.com/yourusername/Tableau-Dashboard.git
cd Tableau-with-Flask-BackEnd
```

#### Option B: Download ZIP
```bash
wget https://github.com/yourusername/Tableau-Dashboard/archive/main.zip
unzip main.zip
cd Tableau-with-Flask-BackEnd-main
```

---

### Step 2: Create Virtual Environment

**Why?** Virtual environments isolate Python packages per project.

#### On Linux/macOS
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

#### On Windows (PowerShell)
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\Activate.ps1
```

#### On Windows (Command Prompt)
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate.bat
```

**Verification:** Your terminal should show `(venv)` prefix.

---

### Step 3: Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install all requirements
pip install -r requirements.txt
```

**Expected Output:**
```
Successfully installed Flask-3.0.0 Flask-Login-0.6.3 ...
```

### Step 4: Configure Environment

#### Create .env File
```bash
# Copy example file
cp .env.example .env

# Edit with your settings
nano .env  # Linux/macOS
# or
notepad .env  # Windows
```

#### Fill Required Variables

```env
# ===========================================
# FLASK CONFIGURATION
# ===========================================
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your-secure-secret-key-here-change-this

# ===========================================
# TABLEAU SERVER CONFIGURATION
# ===========================================
TABLEAU_SERVER_URL=http://your-tableau-server:8000
TABLEAU_USERNAME=your-username
TABLEAU_PASSWORD=your-password
TABLEAU_PROJECT_NAME=your-project

# ===========================================
# APPLICATION SECURITY
# ===========================================
APP_PASSWORD=your-app-password
ALLOWED_USERS=user1,user2,user3

# ===========================================
# SESSION & FEATURES
# ===========================================
SESSION_TIMEOUT=1800
ENABLE_DARK_MODE=True
ENABLE_FAVORITES=True
ENABLE_RECENT_DASHBOARDS=True
```

**Important:** Keep your `.env` file secure and never commit to version control.

---

### Step 5: Create Required Directories

```bash
# Create logs directory
mkdir -p logs

# Create user data directory
mkdir -p user_data

# Create thumbnails directory
mkdir -p static/images
```

---

### Step 6: Run the Application

```bash
# Make sure virtual environment is activated
# (venv) should appear in your terminal

# Run the application
python main.py
```

**Expected Output:**
```
 * Running on http://0.0.0.0:5000
 * Debug mode: off
```

---

### Step 7: Verify Installation

1. **Open Browser:** `http://localhost:5000`
2. **Should See:** Login page
3. **Try Login:** Use credentials from `.env` (ALLOWED_USERS and APP_PASSWORD)
4. **Expected:** Redirect to dashboard selection page

---

## Configuration Details

### Tableau Server Connection

```env
TABLEAU_SERVER_URL=http://10.0.55.1:8000
TABLEAU_USERNAME=admin@tableau
TABLEAU_PASSWORD=YourSecurePassword
TABLEAU_PROJECT_NAME=Sales
```

**Tips:**
- Use full URL with port number
- Test connection before deployment
- User account must have Tableau Server access

### Security Settings

```env
SECRET_KEY=generate-secure-key-minimum-32-characters
APP_PASSWORD=use-strong-password-minimum-8-chars
SESSION_TIMEOUT=1800  # 30 minutes
```

**Generate Secure Key:**
```python
import secrets
print(secrets.token_hex(32))
```

### User Management

```env
ALLOWED_USERS=john,sarah,michael,emma
```

- Comma-separated list of allowed usernames
- Case-sensitive
- Must match your login attempts

---

## Troubleshooting Installation

### Issue: ModuleNotFoundError

**Error:** `ModuleNotFoundError: No module named 'flask'`

**Solution:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows

# Reinstall requirements
pip install -r requirements.txt
```

---

### Issue: Permission Denied

**Error:** `PermissionError: [Errno 13] Permission denied: 'logs'`

**Solution:**
```bash
# Fix directory permissions
chmod -R 755 logs
chmod -R 755 user_data
chmod -R 755 static/images
```

---

### Issue: Port Already in Use

**Error:** `Address already in use`

**Solution (Option 1):** Kill existing process
```bash
# Linux/macOS
lsof -i :5000
kill -9 <PID>

# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

**Solution (Option 2):** Use different port
```python
# In main.py, change:
app.run(host='0.0.0.0', port=5001)
```

---

### Issue: Tableau Connection Failed

**Error:** `Error connecting to Tableau Server`

**Diagnostic Steps:**
```bash
# Test connectivity
ping your-tableau-server

# Test specific port
telnet your-tableau-server 8000

# Verify credentials
# Login to Tableau Server manually first
```

**Solutions:**
- Verify Tableau server URL
- Check firewall rules
- Confirm user credentials
- Test network connectivity

---

## Production Deployment

### Using Gunicorn

```bash
# Install Gunicorn
pip install gunicorn

# Run with 4 workers
gunicorn -w 4 -b 0.0.0.0:5000 main:app

# Run with auto-reload (development)
gunicorn -w 4 -b 0.0.0.0:5000 --reload main:app
```

### Using Docker

**Dockerfile:**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV FLASK_APP=main.py
ENV PYTHONUNBUFFERED=1

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "main:app"]
```

**Build and Run:**
```bash
# Build image
docker build -t tableau-dashboard .

# Run container
docker run -p 5000:5000 \
  --env-file .env \
  tableau-dashboard
```

---

### Using Supervisor (Linux)

**File:** `/etc/supervisor/conf.d/tableau.conf`
```ini
[program:tableau_dashboard]
command=/home/user/Tableau-Dashboard/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 main:app
directory=/home/user/Tableau-Dashboard
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/tableau_dashboard.log
```

**Commands:**
```bash
# Reload configuration
sudo supervisorctl reread
sudo supervisorctl update

# Start/Stop service
sudo supervisorctl start tableau_dashboard
sudo supervisorctl stop tableau_dashboard
```

---

## Security Hardening

### 1. Enable HTTPS

```bash
# Generate self-signed certificate (development)
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365

# Use in Flask
app.run(
    ssl_context=('cert.pem', 'key.pem'),
    host='0.0.0.0',
    port=5000
)
```

### 2. Set Secure Environment

```env
FLASK_ENV=production
FLASK_DEBUG=False
SESSION_COOKIE_SECURE=True
```

### 3. Restrict File Permissions

```bash
# Make .env readable by owner only
chmod 600 .env

# Set logs directory permissions
chmod 755 logs
chmod 644 logs/*.log
```

### 4. Setup Firewall

```bash
# Allow application port only
sudo ufw allow 5000
sudo ufw deny from any to any port 22  # Restrict SSH if needed
```

---

## Post-Installation

### 1. Create Initial Users

Edit `.env`:
```env
ALLOWED_USERS=admin,user1,user2
APP_PASSWORD=InitialPassword123
```

### 2. Test All Features

- [ ] Login page loads
- [ ] Can login with credentials
- [ ] Dashboard list appears
- [ ] Can switch to dark mode
- [ ] Can add/remove favorites
- [ ] Can view dashboard
- [ ] API health endpoint works

### 3. Check Logs

```bash
# View application logs
tail -f logs/app.log

# View audit logs
tail -f logs/audit.log
```

### 4. Monitor Performance

```bash
# Check disk usage
df -h

# Check Python memory usage
top -p $(pgrep -f "python main.py")
```

---

## Maintenance

### Regular Tasks

**Weekly:**
- [ ] Check logs for errors
- [ ] Monitor disk space
- [ ] Verify backups

**Monthly:**
- [ ] Update dependencies: `pip list --outdated`
- [ ] Review security settings
- [ ] Test disaster recovery

**Quarterly:**
- [ ] Review and rotate logs
- [ ] Update documentation
- [ ] Security audit

---

## Uninstallation

```bash
# Deactivate virtual environment
deactivate

# Remove virtual environment
rm -rf venv

# Optional: Remove application directory
rm -rf Tableau-with-Flask-BackEnd
```

---

## Next Steps

1. ✅ Read [README.md](README.md) for overview
2. ✅ Review [API.md](API.md) for API documentation
3. ✅ Check [CHANGELOG.md](CHANGELOG.md) for version history
4. ✅ Configure your Tableau Server connection
5. ✅ Set up user accounts
6. ✅ Deploy to production

---

**Installation Complete!** 🎉

For support or issues, refer to the troubleshooting section or check the logs.
