# API Documentation

## Overview

The Tableau Dashboard Application provides a comprehensive RESTful API for programmatic access to dashboards, user preferences, and administrative functions.

**Base URL:** `http://localhost:5000/api`  
**Response Format:** JSON  
**Authentication:** Session-based (login required for most endpoints)

---

## API Endpoints

### Authentication Endpoints

All protected endpoints require the user to be logged in. Use the login form to establish a session.

---

### Dashboard Management

#### 1. Get All Dashboards
**Endpoint:** `GET /api/dashboards`

**Description:** Retrieve list of all available dashboards with user's favorite status.

**Authentication:** Required

**Response (Success):**
```json
{
    "success": true,
    "dashboards": [
        {
            "id": "dashboard_id_1",
            "name": "Sales Dashboard",
            "description": "Dashboard: Sales Dashboard",
            "thumbnail": "static/images/Sales Dashboard.jpg",
            "project": "default"
        }
    ],
    "favorites": ["dashboard_id_1"]
}
```

**Response (Error):**
```json
{
    "success": false,
    "error": "Error message"
}
```

**Status Codes:**
- `200` - Success
- `401` - Unauthorized
- `500` - Server error

**Example Request:**
```bash
curl -X GET http://localhost:5000/api/dashboards \
  -H "Cookie: session=your_session_id"
```

---

#### 2. Toggle Favorite Dashboard
**Endpoint:** `POST /api/dashboard/<dashboard_id>/favorite`

**Description:** Add or remove dashboard from user's favorites.

**Authentication:** Required

**Request Body:**
```json
{
    "favorite": true
}
```

**Parameters:**
- `dashboard_id` (path) - ID of the dashboard
- `favorite` (body) - Boolean, true to add, false to remove

**Response:**
```json
{
    "success": true,
    "favorites": ["dashboard_id_1", "dashboard_id_2"]
}
```

**Status Codes:**
- `200` - Success
- `400` - Bad request
- `401` - Unauthorized
- `500` - Server error

**Example Request:**
```bash
curl -X POST http://localhost:5000/api/dashboard/dashboard_id_1/favorite \
  -H "Content-Type: application/json" \
  -H "Cookie: session=your_session_id" \
  -d '{"favorite": true}'
```

---

#### 3. Track Dashboard View
**Endpoint:** `POST /api/dashboard/<dashboard_id>/view`

**Description:** Record dashboard view (adds to recent dashboards).

**Authentication:** Required

**Parameters:**
- `dashboard_id` (path) - ID of the dashboard

**Response:**
```json
{
    "success": true
}
```

**Status Codes:**
- `200` - Success
- `401` - Unauthorized
- `500` - Server error

**Example Request:**
```bash
curl -X POST http://localhost:5000/api/dashboard/dashboard_id_1/view \
  -H "Cookie: session=your_session_id"
```

---

### User Management

#### 4. Get User Preferences
**Endpoint:** `GET /api/user/preferences`

**Description:** Retrieve current user's preferences and settings.

**Authentication:** Required

**Response:**
```json
{
    "success": true,
    "user": {
        "id": 0,
        "username": "user1",
        "created_at": "2024-04-29T12:00:00",
        "last_login": "2024-04-29T14:30:00",
        "theme": "light",
        "favorites": ["dashboard_id_1"],
        "recent_dashboards": ["dashboard_id_1", "dashboard_id_2"]
    }
}
```

**Status Codes:**
- `200` - Success
- `401` - Unauthorized
- `500` - Server error

**Example Request:**
```bash
curl -X GET http://localhost:5000/api/user/preferences \
  -H "Cookie: session=your_session_id"
```

---

#### 5. Update User Preferences
**Endpoint:** `POST /api/user/preferences`

**Description:** Update user's preferences (theme, settings).

**Authentication:** Required

**Request Body:**
```json
{
    "theme": "dark"
}
```

**Response:**
```json
{
    "success": true,
    "user": {
        "id": 0,
        "username": "user1",
        "theme": "dark",
        "favorites": [],
        "recent_dashboards": []
    }
}
```

**Status Codes:**
- `200` - Success
- `400` - Bad request
- `401` - Unauthorized
- `500` - Server error

**Example Request:**
```bash
curl -X POST http://localhost:5000/api/user/preferences \
  -H "Content-Type: application/json" \
  -H "Cookie: session=your_session_id" \
  -d '{"theme": "dark"}'
```

---

### Export Functions

#### 6. Export Favorites
**Endpoint:** `GET /api/export/favorites`

**Description:** Export user's favorite dashboards as Excel file.

**Authentication:** Required

**Query Parameters:**
- None

**Response:**
```json
{
    "success": true,
    "file": "user_data/user1/favorites.xlsx"
}
```

**Status Codes:**
- `200` - Success
- `401` - Unauthorized
- `403` - Feature disabled
- `500` - Server error

**Example Request:**
```bash
curl -X GET http://localhost:5000/api/export/favorites \
  -H "Cookie: session=your_session_id"
```

---

### Health & Status

#### 7. Health Check
**Endpoint:** `GET /api/health`

**Description:** Check application health status.

**Authentication:** Not required

**Response:**
```json
{
    "status": "healthy",
    "uptime": "2h 45m",
    "timestamp": "2024-04-29T14:30:00",
    "version": "2.0.0"
}
```

**Status Codes:**
- `200` - Healthy
- `500` - Unhealthy

**Example Request:**
```bash
curl -X GET http://localhost:5000/api/health
```

---

## Error Responses

### Standard Error Response Format
```json
{
    "success": false,
    "error": "Error message description"
}
```

### Common Error Codes

| Code | Message | Cause |
|------|---------|-------|
| 400 | Bad Request | Invalid request format or missing required fields |
| 401 | Unauthorized | User not authenticated |
| 403 | Forbidden | User not authorized for this action |
| 404 | Not Found | Resource not found |
| 500 | Internal Server Error | Server error |

---

## Authentication

### Session-Based Authentication

1. **Login via Form**
   - POST `/login` with username and password
   - Receive session cookie
   - Include cookie in subsequent API requests

### Example Login Flow
```bash
# 1. Login
curl -X POST http://localhost:5000/login \
  -d "username=user1&password=mypassword" \
  -c cookies.txt

# 2. Use session cookie in API calls
curl -X GET http://localhost:5000/api/dashboards \
  -b cookies.txt
```

---

## Rate Limiting

Currently, the API does not implement rate limiting. Production deployments should implement:
- Per-user request limits
- IP-based rate limiting
- API key management

---

## CORS Headers

By default, CORS is not enabled. For cross-origin requests, enable in configuration:

```python
from flask_cors import CORS
CORS(app)
```

---

## Best Practices

### API Usage
1. **Cache Results** - Use HTTP caching where possible
2. **Error Handling** - Always check `success` field
3. **Rate Limiting** - Implement client-side rate limiting
4. **Authentication** - Maintain session security
5. **Validation** - Validate all input data

### Security
1. **HTTPS** - Always use HTTPS in production
2. **Session** - Keep session timeout reasonable
3. **Input** - Validate all user inputs
4. **Output** - Sanitize all outputs
5. **Logging** - Log all API access

### Performance
1. **Pagination** - Implement pagination for large datasets
2. **Filtering** - Allow filtering and search
3. **Caching** - Cache frequently accessed data
4. **Compression** - Enable Gzip compression
5. **CDN** - Use CDN for static assets

---

## Webhook Events

Planned for v3.0:
- Dashboard viewed
- Favorite added/removed
- User logged in/out
- System alerts

---

## SDK & Libraries

### Python Client Example
```python
import requests

# Login
session = requests.Session()
session.post('http://localhost:5000/login', 
    data={'username': 'user1', 'password': 'password'})

# Get dashboards
response = session.get('http://localhost:5000/api/dashboards')
dashboards = response.json()['dashboards']

# Add favorite
session.post(f'http://localhost:5000/api/dashboard/{dashboard_id}/favorite',
    json={'favorite': True})
```

### JavaScript/Node.js Client Example
```javascript
// Login
const loginResponse = await fetch('http://localhost:5000/login', {
    method: 'POST',
    credentials: 'include',
    body: new FormData(loginForm)
});

// Get dashboards
const dashboards = await fetch('http://localhost:5000/api/dashboards', {
    credentials: 'include'
}).then(r => r.json());

// Add favorite
await fetch(`http://localhost:5000/api/dashboard/${dashboardId}/favorite`, {
    method: 'POST',
    credentials: 'include',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({favorite: true})
});
```

---

## Versioning

- **Current API Version:** 1.0
- **Next Version:** 2.0 (planned)
- **Deprecation Policy:** 6 months notice before deprecating endpoints

---

## Support

For API issues or questions:
1. Check error logs in `logs/app.log`
2. Review health endpoint status
3. Verify authentication and permissions
4. Check API documentation

---

**Last Updated:** April 2024  
**Version:** 2.0.0
