# OAuth Setup Guide

This guide explains how to set up OAuth authentication for GitHub and Google in the FastAPI Blog System.

## Overview

The system supports OAuth 2.0 authentication with:
- **GitHub OAuth**: For GitHub user authentication
- **Google OAuth**: For Google user authentication

Users can:
- Login directly with OAuth providers
- Bind multiple OAuth accounts to their local account
- Unbind OAuth accounts (if they have other authentication methods)

## Features

### OAuth Login Flow
1. User clicks OAuth login button
2. Redirected to OAuth provider (GitHub/Google)
3. User authorizes the application
4. OAuth provider redirects back with authorization code
5. System exchanges code for access token
6. System fetches user information from OAuth provider
7. System creates or finds existing user account
8. System creates JWT tokens and redirects to frontend

### Account Binding
- Existing users can bind OAuth accounts to their local account
- Users can have multiple OAuth providers bound to one account
- Users cannot unbind their last authentication method

### User Creation
- New users are automatically created when they first login via OAuth
- Username is generated from OAuth provider username (with uniqueness check)
- Email is fetched from OAuth provider
- Profile picture URL is stored if available

## Setup Instructions

### 1. GitHub OAuth Setup

1. Go to [GitHub Developer Settings](https://github.com/settings/developers)
2. Click "New OAuth App"
3. Fill in the form:
   - **Application name**: Your blog name
   - **Homepage URL**: `http://localhost:8000` (or your domain)
   - **Authorization callback URL**: `http://localhost:8000/api/v1/oauth/github/callback`
4. Click "Register application"
5. Copy the **Client ID** and **Client Secret**

### 2. Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the Google+ API
4. Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client IDs"
5. Choose "Web application"
6. Fill in the form:
   - **Name**: Your blog name
   - **Authorized redirect URIs**: `http://localhost:8000/api/v1/oauth/google/callback`
7. Click "Create"
8. Copy the **Client ID** and **Client Secret**

### 3. Environment Configuration

Add the OAuth credentials to your `.env` file:

```env
# GitHub OAuth
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# OAuth Base URL
OAUTH_BASE_URL=http://localhost:8000
```

### 4. Database Migration

The system automatically creates the necessary database tables for OAuth:
- `user` table updated with OAuth fields
- `oauthaccount` table for OAuth account bindings

## API Endpoints

### OAuth Login Endpoints

#### GitHub OAuth
- `GET /api/v1/oauth/github/login` - Initiate GitHub OAuth login
- `GET /api/v1/oauth/github/callback` - GitHub OAuth callback

#### Google OAuth
- `GET /api/v1/oauth/google/login` - Initiate Google OAuth login
- `GET /api/v1/oauth/google/callback` - Google OAuth callback

### OAuth Management Endpoints

#### Get Available Providers
```http
GET /api/v1/oauth/providers
```

Response:
```json
{
  "providers": [
    {
      "name": "github",
      "display_name": "GitHub",
      "login_url": "/api/v1/oauth/github/login"
    },
    {
      "name": "google",
      "display_name": "Google",
      "login_url": "/api/v1/oauth/google/login"
    }
  ]
}
```

#### Get User's OAuth Accounts
```http
GET /api/v1/oauth/accounts
Authorization: Bearer <access_token>
```

Response:
```json
{
  "accounts": [
    {
      "provider": "github",
      "provider_username": "johndoe",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

#### Bind OAuth Account
```http
POST /api/v1/oauth/bind/{provider}
Authorization: Bearer <access_token>
```

#### Unbind OAuth Account
```http
DELETE /api/v1/oauth/unbind/{provider}
Authorization: Bearer <access_token>
```

## Frontend Integration

### OAuth Login Flow

1. **Redirect to OAuth provider**:
```javascript
// For GitHub
window.location.href = '/api/v1/oauth/github/login';

// For Google
window.location.href = '/api/v1/oauth/google/login';
```

2. **Handle OAuth callback**:
```javascript
// Check for OAuth callback parameters
const urlParams = new URLSearchParams(window.location.search);
const accessToken = urlParams.get('access_token');
const refreshToken = urlParams.get('refresh_token');

if (accessToken && refreshToken) {
  // Store tokens
  localStorage.setItem('access_token', accessToken);
  localStorage.setItem('refresh_token', refreshToken);
  
  // Redirect to dashboard or home
  window.location.href = '/dashboard';
}
```

### OAuth Account Management

```javascript
// Get user's OAuth accounts
const response = await fetch('/api/v1/oauth/accounts', {
  headers: {
    'Authorization': `Bearer ${accessToken}`
  }
});
const accounts = await response.json();

// Bind OAuth account
const bindResponse = await fetch('/api/v1/oauth/bind/github', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${accessToken}`
  }
});

// Unbind OAuth account
const unbindResponse = await fetch('/api/v1/oauth/unbind/github', {
  method: 'DELETE',
  headers: {
    'Authorization': `Bearer ${accessToken}`
  }
});
```

## Security Considerations

### Token Security
- OAuth access tokens are not stored in the database
- Only refresh tokens are stored (encrypted)
- JWT tokens are used for session management

### Account Security
- Users cannot unbind their last authentication method
- OAuth accounts are validated on each login
- Email verification is handled by OAuth providers

### Rate Limiting
- OAuth endpoints should be rate-limited
- Consider implementing rate limiting for OAuth callbacks

## Troubleshooting

### Common Issues

1. **OAuth provider not configured**
   - Check that client ID and secret are set in environment
   - Verify OAuth app is properly configured in provider dashboard

2. **Callback URL mismatch**
   - Ensure callback URL in OAuth app matches exactly
   - Check for trailing slashes or protocol differences

3. **Scope issues**
   - GitHub: Ensure `user:email` scope is requested
   - Google: Ensure `openid email profile` scopes are requested

4. **Database errors**
   - Ensure database tables are created
   - Check for unique constraint violations

### Debug Mode

Enable debug mode to see detailed OAuth logs:

```env
DEBUG=true
```

## Testing

Use the provided test script to verify OAuth functionality:

```bash
python test_oauth.py
```

This will test:
- OAuth provider endpoints
- Login flows
- Account management
- Authentication requirements

## Production Deployment

### Environment Variables
- Use strong, unique client secrets
- Set `OAUTH_BASE_URL` to your production domain
- Ensure HTTPS is used in production

### Security Headers
- Set appropriate CORS headers
- Use secure cookies for session management
- Implement CSRF protection

### Monitoring
- Monitor OAuth callback success rates
- Log OAuth authentication events
- Set up alerts for authentication failures 