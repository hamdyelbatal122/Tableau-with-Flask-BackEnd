"""
Professional Tableau Dashboard Application
A Flask-based application to display and manage Tableau dashboards with user preferences.
"""

import os
import logging
from flask import Flask, render_template, redirect, url_for, request, jsonify, abort
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv
import tableauserverclient as TSC

from config import get_config, setup_logging
from models import User, Dashboard
from utils import (
    is_safe_url, log_user_action, validate_username, validate_password,
    sanitize_filename, CacheManager, get_user_file_path, export_to_excel
)

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__)

# Load configuration
config = get_config()
app.config.from_object(config)

# Setup logging
logger = setup_logging(app)

# Setup CSRF protection
csrf = CSRFProtect(app)

# Setup Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please sign in to access this page.'

# Application start time for uptime tracking
from datetime import datetime
app_start_time = datetime.now()


# ============================================================================
# INITIALIZATION & ERROR HANDLERS
# ============================================================================

@app.before_request
def before_request():
    """Before each request"""
    if current_user.is_authenticated:
        current_user.update_last_login()


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template('error.html', 
        error_code=404,
        error_message='Page Not Found',
        error_description='The page you are looking for does not exist.'
    ), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f'Internal server error: {str(error)}')
    return render_template('error.html',
        error_code=500,
        error_message='Internal Server Error',
        error_description='An unexpected error occurred.'
    ), 500


@app.errorhandler(403)
def forbidden(error):
    """Handle 403 errors"""
    return render_template('error.html',
        error_code=403,
        error_message='Access Forbidden',
        error_description='You do not have permission to access this resource.'
    ), 403


# ============================================================================
# USER LOADER
# ============================================================================

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    return User.get(user_id)


# ============================================================================
# AUTHENTICATION ROUTES
# ============================================================================

@app.route('/')
def index():
    """Redirect to login or dashboard based on auth status"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard_select'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        # Input validation
        if not username or not password:
            return render_template('login.html', 
                error='Username and password are required.')
        
        if not validate_username(username):
            logger.warning(f'Invalid username format attempt: {username}')
            return render_template('login.html',
                error='Invalid username format.')
        
        # Verify credentials
        if username not in config.ALLOWED_USERS:
            logger.warning(f'Login attempt with unknown user: {username}')
            log_user_action(username, 'LOGIN_FAILED', {'reason': 'unknown_user'})
            return render_template('login.html',
                error='Invalid credentials.')
        
        if password != config.APP_PASSWORD:
            logger.warning(f'Failed login attempt for user: {username}')
            log_user_action(username, 'LOGIN_FAILED', {'reason': 'invalid_password'})
            return render_template('login.html',
                error='Invalid credentials.')
        
        # Authentication successful
        try:
            user = User.get_by_username(username)
            if user:
                user.load_preferences()
                login_user(user, remember=request.form.get('rememberMe') is not None)
                
                logger.info(f'User logged in successfully: {username}')
                log_user_action(username, 'LOGIN_SUCCESS', {'ip': request.remote_addr})
                
                next_page = request.args.get('next')
                if not next_page or not is_safe_url(next_page, request):
                    next_page = url_for('dashboard_select')
                
                return redirect(next_page)
        except Exception as e:
            logger.error(f'Login error for {username}: {str(e)}')
            return render_template('login.html',
                error='An error occurred during login. Please try again.')
    
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    """Handle user logout"""
    username = current_user.username
    logout_user()
    
    logger.info(f'User logged out: {username}')
    log_user_action(username, 'LOGOUT', {})
    
    return redirect(url_for('login'))


@app.route('/profile')
@login_required
def profile():
    """User profile page"""
    try:
        user_data = current_user.to_dict()
        return render_template('profile.html', user=user_data)
    except Exception as e:
        logger.error(f'Error loading profile: {str(e)}')
        return render_template('error.html',
            error_code=500,
            error_message='Error',
            error_description='Could not load profile.'
        ), 500


# ============================================================================
# DASHBOARD ROUTES
# ============================================================================

@app.route('/dashboard-select')
@login_required
def dashboard_select():
    """Display available dashboards for selection"""
    try:
        return render_template('select-dashboard.html')
    except Exception as e:
        logger.error(f'Error loading dashboard selection: {str(e)}')
        return render_template('error.html',
            error_code=500,
            error_message='Error',
            error_description='Could not load dashboards.'
        ), 500


@app.route('/dashboard/<dashboard_id>')
@login_required
def view_dashboard(dashboard_id):
    """Display specific dashboard"""
    try:
        # Add to recent dashboards
        current_user.add_to_recent(dashboard_id)
        
        # Log dashboard view
        log_user_action(current_user.username, 'VIEW_DASHBOARD', {'dashboard_id': dashboard_id})
        
        return render_template('dashboard.html', dashboard_id=dashboard_id)
    except Exception as e:
        logger.error(f'Error viewing dashboard: {str(e)}')
        return render_template('error.html',
            error_code=500,
            error_message='Error',
            error_description='Could not load dashboard.'
        ), 500


# ============================================================================
# API ROUTES - JSON ENDPOINTS
# ============================================================================

@app.route('/api/dashboards')
@login_required
def api_get_dashboards():
    """Get list of available dashboards (API)"""
    try:
        cache_key = f'dashboards_{config.TABLEAU_PROJECT}'
        dashboards = CacheManager.get(cache_key)
        
        if dashboards is None:
            dashboards = []
            
            try:
                server = TSC.Server(config.TABLEAU_SERVER_URL)
                auth = TSC.TableauAuth(config.TABLEAU_USERNAME, config.TABLEAU_PASSWORD)
                
                with server.auth.sign_in(auth):
                    workbooks, _ = server.workbooks.get()
                    
                    os.makedirs(config.THUMBNAILS_PATH, exist_ok=True)
                    
                    for wb in workbooks:
                        if wb.project_name == config.TABLEAU_PROJECT:
                            try:
                                server.workbooks.populate_preview_image(wb)
                                thumbnail_path = os.path.join(
                                    config.THUMBNAILS_PATH,
                                    f"{sanitize_filename(wb.name)}.jpg"
                                )
                                with open(thumbnail_path, "wb") as f:
                                    f.write(wb.preview_image)
                                
                                dashboard = {
                                    'id': wb.id,
                                    'name': wb.name,
                                    'description': f"Dashboard: {wb.name}",
                                    'thumbnail': thumbnail_path,
                                    'project': wb.project_name
                                }
                                dashboards.append(dashboard)
                            except Exception as e:
                                logger.warning(f'Error processing workbook {wb.name}: {str(e)}')
                
                # Cache the result
                CacheManager.set(cache_key, dashboards, config.CACHE_TIMEOUT)
                
            except Exception as e:
                logger.error(f'Error fetching dashboards from Tableau: {str(e)}')
        
        return jsonify({
            'success': True,
            'dashboards': dashboards,
            'favorites': current_user.favorites
        })
    except Exception as e:
        logger.error(f'API Error: {str(e)}')
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/dashboard/<dashboard_id>/favorite', methods=['POST'])
@login_required
def api_toggle_favorite(dashboard_id):
    """Toggle dashboard as favorite (API)"""
    try:
        data = request.get_json() or {}
        is_favorite = data.get('favorite', False)
        
        if is_favorite:
            current_user.add_favorite(dashboard_id)
            log_user_action(current_user.username, 'ADD_FAVORITE', {'dashboard_id': dashboard_id})
        else:
            current_user.remove_favorite(dashboard_id)
            log_user_action(current_user.username, 'REMOVE_FAVORITE', {'dashboard_id': dashboard_id})
        
        return jsonify({
            'success': True,
            'favorites': current_user.favorites
        })
    except Exception as e:
        logger.error(f'Error toggling favorite: {str(e)}')
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/dashboard/<dashboard_id>/view', methods=['POST'])
@login_required
def api_track_dashboard_view(dashboard_id):
    """Track dashboard view (API)"""
    try:
        current_user.add_to_recent(dashboard_id)
        log_user_action(current_user.username, 'VIEW_DASHBOARD', {'dashboard_id': dashboard_id})
        
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f'Error tracking view: {str(e)}')
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/user/preferences')
@login_required
def api_get_user_preferences():
    """Get user preferences (API)"""
    try:
        return jsonify({
            'success': True,
            'user': current_user.to_dict()
        })
    except Exception as e:
        logger.error(f'Error getting preferences: {str(e)}')
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/user/preferences', methods=['POST'])
@login_required
def api_update_user_preferences():
    """Update user preferences (API)"""
    try:
        data = request.get_json() or {}
        
        if 'theme' in data:
            current_user.theme = data['theme']
        
        current_user.save_preferences()
        
        log_user_action(current_user.username, 'UPDATE_PREFERENCES', {'changes': data})
        
        return jsonify({
            'success': True,
            'user': current_user.to_dict()
        })
    except Exception as e:
        logger.error(f'Error updating preferences: {str(e)}')
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/health')
def api_health():
    """Health check endpoint"""
    from utils import get_uptime
    
    return jsonify({
        'status': 'healthy',
        'uptime': get_uptime(app_start_time),
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.0'
    })


# ============================================================================
# EXPORT ROUTES
# ============================================================================

@app.route('/api/export/favorites')
@login_required
def api_export_favorites():
    """Export user's favorite dashboards as Excel"""
    try:
        if not config.API_ENABLE_IMPORT_EXPORT:
            return jsonify({'error': 'Export functionality is disabled'}), 403
        
        export_file = get_user_file_path(current_user.username, 'favorites.xlsx')
        
        data = [{'dashboard_id': fav} for fav in current_user.favorites]
        
        if export_to_excel(data, export_file):
            log_user_action(current_user.username, 'EXPORT_FAVORITES', {})
            return jsonify({
                'success': True,
                'file': export_file
            })
        else:
            return jsonify({'error': 'Export failed'}), 500
    except Exception as e:
        logger.error(f'Export error: {str(e)}')
        return jsonify({'error': str(e)}), 500


# ============================================================================
# CLEANUP & CONTEXT PROCESSORS
# ============================================================================

@app.context_processor
def inject_config():
    """Inject config into templates"""
    return dict(
        config=config,
        app_version='2.0.0',
        current_year=datetime.now().year
    )


@app.teardown_appcontext
def cleanup(error):
    """Cleanup on app teardown"""
    if error:
        logger.error(f'App error: {str(error)}')


# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs(config.THUMBNAILS_PATH, exist_ok=True)
    os.makedirs(config.LOGS_PATH, exist_ok=True)
    os.makedirs(config.USER_DATA_PATH, exist_ok=True)
    
    logger.info('Starting Tableau Dashboard Application')
    logger.info(f'Environment: {config.FLASK_ENV}')
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=config.DEBUG,
        use_reloader=False if config.FLASK_ENV == 'production' else True
    )
