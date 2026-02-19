# Heroku Deployment Guide

## Overview
This guide explains how to deploy the Article Management System to Heroku with persistent database storage and cloud file uploads.

## Prerequisites
- Heroku CLI installed: https://devcenter.heroku.com/articles/heroku-cli
- Heroku account: https://signup.heroku.com/
- Git installed
- AWS S3 account (for file uploads) OR Cloudinary account

## Step 1: Prepare Your Local Environment

### 1.1 Create `.env` file (for local testing)
```bash
DATABASE_URL=postgresql://localhost/articles_dev
SECRET_KEY=your-secret-key-here
ADMIN_ACCESS_PASSWORD=your-admin-password
```

### 1.2 Ensure files are in your Git repo
```bash
cd c:\Users\mikha\OneDrive\Документы\python\gened
git init
git add .
git commit -m "Initial commit"
```

## Step 2: Set Up PostgreSQL (Heroku Database)

Once deployed, Heroku provides `DATABASE_URL` automatically. For local development:
```bash
# Install PostgreSQL locally
# Create a local database:
createdb articles_dev
```

## Step 3: Update Your App Configuration

Your `app.py` needs to be updated to:
1. Use PostgreSQL from `DATABASE_URL` environment variable
2. Download uploaded files from storage instead of saving locally

Replace the database configuration in app.py:
```python
import os

# Get DATABASE_URL from environment (Heroku sets this)
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///articles.db')

# Fix for SQLAlchemy 2.0+ with PostgreSQL
if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
```

## Step 4: Set Up Cloud File Storage (AWS S3)

Since Heroku has ephemeral storage, uploaded files must be stored in AWS S3.

### 4.1 Create AWS S3 Bucket
1. Log in to AWS Console
2. Go to S3
3. Create a new bucket (e.g., `article-uploads-prod`)
4. Enable public read access for images
5. Create an IAM user with S3 permissions

### 4.2 Get AWS Credentials
- Access Key ID
- Secret Access Key
- Bucket Name

### 4.3 Modify Upload Route (See updated_app_s3.py below)

## Step 5: Deploy to Heroku

### 5.1 Create Heroku App
```bash
heroku login
heroku create your-app-name
```

### 5.2 Set Environment Variables
```bash
heroku config:set SECRET_KEY="your-secret-key-here"
heroku config:set ADMIN_ACCESS_PASSWORD="your-admin-password"
heroku config:set AWS_ACCESS_KEY_ID="your-aws-key"
heroku config:set AWS_SECRET_ACCESS_KEY="your-aws-secret"
heroku config:set AWS_S3_BUCKET="your-bucket-name"
heroku config:set AWS_REGION="us-east-1"
```

### 5.3 Deploy Code
```bash
git push heroku main
# or
git push heroku master
```

### 5.4 Run Database Migrations
```bash
heroku run python -c "from app import db; db.create_all()"
```

### 5.5 View Logs
```bash
heroku logs --tail
```

## Step 6: Test the App
```bash
heroku open
```

Navigate to `/admin-access` to register with your admin code.

## Troubleshooting

### Database Connection Issues
```bash
# Check the DATABASE_URL is set
heroku config:get DATABASE_URL

# Rebuild the database
heroku run python -c "from app import db; db.drop_all(); db.create_all()"
```

### Image Upload Not Working
- Verify AWS credentials in `heroku config`
- Check AWS S3 bucket permissions
- View logs: `heroku logs --tail`

### App Won't Start
```bash
heroku logs --tail
# Look for error messages
```

## File Structure Expected
```
gened/
├── app.py                  (main Flask app)
├── requirements.txt        (Python dependencies)
├── Procfile                (Heroku run command)
├── runtime.txt             (Python version)
├── .env.example            (environment variables template)
├── templates/              (HTML templates)
├── static/                 (CSS, JS, fonts)
└── .gitignore             (must exclude .env and __pycache__)
```

## Important: .gitignore File

Create `.gitignore`:
```
.env
__pycache__/
*.pyc
*.db
.venv
node_modules/
```

## Optional: Add Custom Domain
```bash
heroku domains:add www.yourdomain.com
```

## Monitoring

### View App Logs
```bash
heroku logs --tail
```

### Check Current Config
```bash
heroku config
```

### Scale Dynos
```bash
heroku ps:scale web=1
```

## Backup Database

### Export Database
```bash
heroku pg:backups:capture
heroku pg:backups:download
```

### Restore Database
```bash
heroku pg:backups:restore [BACKUP_ID]
```

## Notes

- **First registration**: Use the admin code to create the first account (mikhail)
  - This account will be super_admin automatically
  
- **Images storage**: All uploaded images are stored in AWS S3, not on Heroku
  - Make sure AWS S3 bucket is set to public read access
  
- **Database**: PostgreSQL is used instead of SQLite for reliability

- **Cost considerations**:
  - Heroku free tier is discontinued (paid plans start at $5/month)
  - AWS S3: Very cheap for small usage (~$0.023/GB/month)
