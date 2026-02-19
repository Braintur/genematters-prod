# Heroku Deployment Checklist ✓

Follow these steps in order to deploy your article management system to Heroku with AWS S3 storage.

## Before You Start
- [ ] You have a Heroku account (free tier available)
- [ ] You have an AWS account (free tier available)
- [ ] You have Heroku CLI installed
- [ ] Your code is in Git
- [ ] All files are saved locally

---

## Phase 1: AWS S3 Setup (15 minutes)

### Create S3 Bucket
- [ ] Log in to AWS Console (https://console.aws.amazon.com)
- [ ] Go to S3 service
- [ ] Create new bucket named `article-uploads-prod-YOURNAME`
- [ ] Select region `us-east-1`
- [ ] Note the bucket name - you'll need it later

### Configure Bucket for Public Access
- [ ] Go to bucket Permissions tab
- [ ] Edit "Block Public Access" - uncheck all boxes, save
- [ ] Edit "Bucket policy" and paste this (replace `YOUR-BUCKET-NAME`):

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::YOUR-BUCKET-NAME/uploads/*"
        }
    ]
}
```

### Create IAM User (for Heroku App Access)
- [ ] Go to IAM service
- [ ] Create user `heroku-article-uploader`
- [ ] Attach policy `AmazonS3FullAccess`
- [ ] Go to Security credentials → Create access key
- [ ] **COPY AND SAVE:**
  - [ ] Access Key ID: `________________________`
  - [ ] Secret Access Key: `________________________`
  - [ ] Bucket Name: `________________________`

---

## Phase 2: Prepare Your Code (5 minutes)

### Initialize Git (if not already done)
```bash
cd c:\Users\mikha\OneDrive\Документы\python\geled
git init
git add .
git commit -m "Initial commit with S3 support"
```

### Verify Required Files Exist
- [ ] `app.py` - updated with S3 support
- [ ] `requirements.txt` - has boto3, gunicorn, psycopg2-binary
- [ ] `Procfile` - contains `web: gunicorn app:app`
- [ ] `runtime.txt` - contains `python-3.11.6`
- [ ] `.env.example` - has all environment variable templates
- [ ] `.gitignore` - excludes .env files

---

## Phase 3: Heroku Deployment (15 minutes)

### Login to Heroku
```bash
heroku login
```
- [ ] Opens browser - log in with your Heroku account

### Create Heroku App
```bash
heroku create your-app-name
```
**Example:** `heroku create article-manager-app`

- [ ] Note your app name: `________________________`
- [ ] Note your app URL: `________________________`

### Add PostgreSQL Database
```bash
heroku addons:create heroku-postgresql:hobby-dev -a your-app-name
```
- [ ] Wait for confirmation that database was created

### Set Environment Variables
```bash
heroku config:set SECRET_KEY="generateRandomKeyHere" -a your-app-name
heroku config:set ADMIN_ACCESS_PASSWORD="your-admin-password" -a your-app-name
heroku config:set AWS_ACCESS_KEY_ID="your-aws-access-key" -a your-app-name
heroku config:set AWS_SECRET_ACCESS_KEY="your-aws-secret-key" -a your-app-name
heroku config:set AWS_S3_BUCKET="your-bucket-name" -a your-app-name
heroku config:set AWS_REGION="us-east-1" -a your-app-name
```

- [ ] All environment variables set successfully

### Deploy Code to Heroku
```bash
git push heroku main
```
(or `git push heroku master` if your branch is named master)

- [ ] Wait for deployment to complete
- [ ] Should see "Verifying deploy... done" at the end

### Initialize Database
```bash
heroku run python -c "from app import db; db.create_all()" -a your-app-name
```

- [ ] Database tables created successfully

---

## Phase 4: Test Your App (10 minutes)

### Open App
```bash
heroku open -a your-app-name
```
- [ ] App opens in browser

### Test Registration
- [ ] Navigate to `/admin-access`
- [ ] Enter your `ADMIN_ACCESS_PASSWORD`
- [ ] Register account with username `mikhail`
- [ ] Account created successfully
- [ ] Logged in as mikhail

### Test Article Creation
- [ ] Go to `/article/new`
- [ ] Create test article with title and content
- [ ] Upload a test image
- [ ] Submit article

### Test Image Display
- [ ] View the created article
- [ ] Image displays correctly
- [ ] Image is served from AWS S3 (check URL in browser dev tools)

### Test Image Operations
- [ ] Edit article
- [ ] Upload another image
- [ ] Delete an image
- [ ] Images update correctly

---

## Phase 5: Production Checklist (Optional)

### Monitor Logs
```bash
heroku logs --tail -a your-app-name
```
- [ ] No error messages in logs
- [ ] App is running normally

### Test Admin Functions
- [ ] Create second admin account
- [ ] Go to Admin Panel (super_admin only)
- [ ] View list of admin accounts
- [ ] Verify both accounts are listed

### Backup Database
```bash
heroku pg:backups:capture -a your-app-name
```
- [ ] Database backup created

---

## Phase 6: Share Your App

- [ ] Share URL: `https://your-app-name.herokuapp.com/`
- [ ] Users can register with your admin code
- [ ] Users can create and share articles

---

## Common Issues & Solutions

### "App won't start"
```bash
heroku logs --tail -a your-app-name
```
Check logs for specific error. Common causes:
- Missing environment variables - verify all config:set commands ran
- DATABASE_URL not set - may need to re-create database addon
- Python version mismatch - verify runtime.txt has correct version

### "Image uploads fail"
- [ ] Verify AWS credentials are correct (typo in key?)
- [ ] Verify S3 bucket name exactly matches
- [ ] Verify bucket permissions allow public access
- [ ] Check IAM user has S3 permissions

### "Database queries fail"
```bash
heroku run python -c "from app import db; db.create_all()" -a your-app-name
```
- Recreate all tables

### "Can't log in after deployment"
- Verify user was created during registration
- Create new account to test registration works

---

## Useful Debugging Commands

```bash
# View all config variables
heroku config -a your-app-name

# View app logs in real-time
heroku logs --tail -a your-app-name

# Run Python code on Heroku
heroku run python -c "import app; print('App loaded')" -a your-app-name

# Access app shell (bash on Heroku dyno)
heroku run bash -a your-app-name

# Check database tables
heroku run python -c "from app import db; print(db.metadata.tables.keys())" -a your-app-name
```

---

## What's Now Working

✅ Secure article management platform deployed to Heroku
✅ User authentication with mandatory admin code
✅ Article CRUD operations (Create, Read, Update, Delete)
✅ Image uploads stored in AWS S3 (not server filesystem)
✅ Image gallery with insert/delete functionality
✅ Admin account management
✅ PostgreSQL database for persistent storage
✅ Automatic environment-based configuration (S3 credentials from env vars)

---

## What's Running On Heroku

- **Web Server**: Gunicorn (production WSGI server)
- **Database**: Heroku PostgreSQL (managed database service)
- **Storage**: AWS S3 (cloud object storage for images)
- **Framework**: Flask with SQLAlchemy ORM
- **Authentication**: Flask-Login with werkzeug password hashing

---

## Monthly Costs Breakdown

- Heroku Hobby Dyno: **$5/month** (your app runs here)
- PostgreSQL Database: **$9/month** (your data stored here)
- AWS S3: **~$0-1/month** (images stored here, free tier covers most usage)
- **Total: ~$14-15/month**

---

## Next Steps

1. **Celebrate!** 🎉 Your app is live
2. Create more user accounts for contributors
3. Encourage team members to create articles
4. Monitor app health: `heroku logs --tail`
5. Back up data regularly: `heroku pg:backups:capture`

---

## Need Help?

If something doesn't work:

1. Check logs: `heroku logs --tail -a your-app-name`
2. Verify environment variables: `heroku config -a your-app-name`
3. Test database connection: `heroku run python -c "from app import db; db.session.execute('SELECT 1')"` 
4. Check AWS S3 bucket name and permissions match exactly
5. Verify IAM user has S3 permissions

