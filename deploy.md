# 🚀 Barangay Portal Deployment Guide

## Quick Deployment Options

### Option 1: Railway (Recommended for Django)

1. Go to https://railway.app
2. Sign up/Login with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Railway will auto-detect Django and deploy

**Environment Variables to set in Railway:**
```
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=*.railway.app
```

### Option 2: PythonAnywhere

1. Go to https://www.pythonanywhere.com
2. Create free account
3. Upload your project files
4. Set up WSGI configuration
5. Configure database and static files

### Option 3: Heroku

1. Install Heroku CLI
2. Create Procfile:
   ```
   web: python manage.py runserver 0.0.0.0:$PORT
   ```
3. Deploy:
   ```
   heroku create barangay-burgos-portal
   git push heroku main
   ```

### Option 4: Local Network Deployment

Run locally and access from other devices:

```bash
python manage.py runserver 0.0.0.0:8000
```

Then access from other devices using your IP: `http://YOUR_IP:8000`

## Pre-Deployment Checklist

✅ Static files configured (WhiteNoise)
✅ Environment variables ready
✅ Database migrations applied
✅ Security settings configured
✅ Requirements.txt updated

## Production Settings

Your app is configured with:
- Environment variable support
- Static file serving
- Security headers
- Database ready
- Multi-language support

Choose the deployment option that works best for you!
