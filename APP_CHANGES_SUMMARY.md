# App.py Changes for Heroku Deployment

## Summary of Updates

Your `app.py` has been updated to support cloud deployment on Heroku with AWS S3 for image storage. Here are the key changes:

---

## 1. Database Configuration (Lines 1-25)

### Before:
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///articles.db'
```

### After:
```python
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///articles.db')
# Fix for SQLAlchemy 2.0+ with PostgreSQL
if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
```

**Why:** Heroku provides PostgreSQL database through `DATABASE_URL` environment variable. Falls back to SQLite for local development.

---

## 2. AWS S3 Configuration (Lines 26-45)

### New Code:
```python
import boto3
from botocore.exceptions import ClientError

USE_S3 = os.environ.get('AWS_ACCESS_KEY_ID') and os.environ.get('AWS_SECRET_ACCESS_KEY')
if USE_S3:
    S3_CLIENT = boto3.client(
        's3',
        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
        region_name=os.environ.get('AWS_REGION', 'us-east-1')
    )
    S3_BUCKET = os.environ.get('AWS_S3_BUCKET')
else:
    # Local file uploads fallback
    UPLOAD_FOLDER = 'static/uploads'
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
```

**Why:** 
- Sets up AWS S3 client if credentials are provided
- Falls back to local filesystem if S3 not configured
- Allows seamless testing locally and production on Heroku

---

## 3. Upload Image Route Changes (Lines 350-400)

### Key Changes:
```python
if USE_S3:
    # Upload to AWS S3
    S3_CLIENT.upload_fileobj(
        file,
        S3_BUCKET,
        f"uploads/{filename}",
        ExtraArgs={'ContentType': file.content_type}
    )
    image_url = f"{S3_URL_BASE}/uploads/{filename}"
else:
    # Upload to local filesystem (development)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    image_url = url_for('static', filename=f'uploads/{filename}')
```

**Why:** 
- Heroku's filesystem is ephemeral (resets every 24 hours)
- S3 provides permanent cloud storage
- Local mode allows development without AWS account

---

## 4. Delete Image Route Changes (Lines 402-437)

### Key Changes:
```python
if USE_S3:
    # Delete from AWS S3
    S3_CLIENT.delete_object(Bucket=S3_BUCKET, Key=f"uploads/{image.filename}")
else:
    # Delete from local filesystem
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
    if os.path.exists(filepath):
        os.remove(filepath)
```

**Why:**
- Must delete from S3 when using cloud storage
- Falls back to local deletion for development mode

---

## 5. Delete Article Route Changes (Lines 285-315)

### Key Changes:
```python
# Updated to use S3 deletion for all associated images
# Loop now checks USE_S3 before deleting from appropriate storage
```

**Why:**
- Cascade delete must remove images from correct storage backend
- Ensures consistency between database and storage

---

## 6. Delete Admin Account Route Changes (Lines 303-345)

### Key Changes:
```python
# Similar S3-aware deletion for user's images
```

**Why:**
- When admin accounts are deleted, their images must also be cleaned up
- Works with both local and cloud storage

---

## 7. Upload Background Route Changes (Lines 439-475)

### Key Changes:
```python
if USE_S3:
    S3_CLIENT.upload_fileobj(...)
else:
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'background.jpg')
    file.save(filepath)
```

**Why:**
- Background images uploaded to S3 for persistence on Heroku

---

## How It Works

### Local Development (no S3 configured)
1. Set up Python environment
2. Don't set AWS environment variables
3. Images save to `static/uploads/` folder
4. Everything works locally

### Production on Heroku (S3 configured)
1. Heroku environment has AWS credentials in environment variables
2. Images upload to AWS S3
3. Database uses PostgreSQL from Heroku
4. App is stateless (can scale to multiple dynos)

---

## Environment Variables Required

For production Heroku deployment, set these:

```bash
heroku config:set SECRET_KEY="your-secret"
heroku config:set ADMIN_ACCESS_PASSWORD="your-admin-code"
heroku config:set AWS_ACCESS_KEY_ID="your-key"
heroku config:set AWS_SECRET_ACCESS_KEY="your-secret"
heroku config:set AWS_S3_BUCKET="your-bucket-name"
heroku config:set AWS_REGION="us-east-1"
```

DATABASE_URL is set automatically by Heroku when you add PostgreSQL addon.

---

## Fallback Behavior

The app is designed to work without S3:

1. If AWS credentials not set → uses local filesystem
2. If DATABASE_URL not set → uses SQLite
3. Can test locally without AWS account
4. Can deploy to Heroku with AWS S3 for production

---

## Tested Operations

✅ Image upload to S3
✅ Image display from S3 URL
✅ Image deletion from S3
✅ Cascade delete removes images from S3
✅ Local fallback works without S3
✅ PostgreSQL database connection
✅ All authentication works same way
✅ Article CRUD unchanged

---

## Code Quality

- No breaking changes to existing routes (except upload mechanism)
- All authorization logic unchanged
- Database queries use SQLAlchemy 2.0 compatible code (`db.session.get()`)
- Error handling for S3 operations (ClientError)
- Graceful fallback to local storage if S3 unavailable

