# Heroku Deployment - Quick Start

## Prerequisites
- Heroku CLI: `choco install heroku-cli` (Windows) or `brew tap heroku/brew && brew install heroku` (Mac)
- AWS Account: https://aws.amazon.com/
- Git installed

## Step 1: Set Up AWS S3 for Image Storage

### 1.1 Create S3 Bucket
1. Log in to AWS Console: https://console.aws.amazon.com/
2. Go to S3 service
3. Click "Create bucket"
4. Name: `article-uploads-prod-YOURNAME` (must be globally unique)
5. Region: `us-east-1` (or your preferred region)
6. Click "Create bucket"

### 1.2 Enable Public Access (for image viewing)
1. Select your bucket
2. Go to "Permissions" tab
3. Block Public Access: Click "Edit"
4. Uncheck all boxes (allow public access)
5. Save

### 1.3 Set Bucket Policy (for public read-only access)
1. Still in Permissions tab
2. Scroll to "Bucket policy"
3. Click "Edit"
4. Replace with this policy (change `YOUR-BUCKET-NAME`):

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

5. Click "Save changes"

### 1.4 Create IAM User for Heroku App
1. Go to IAM service in AWS Console
2. Click "Users" → "Create user"
3. Name: `heroku-article-uploader`
4. Click "Next"
5. Click "Attach policies directly"
6. Search for `AmazonS3FullAccess` and select it
7. Click "Next" → "Create user"
8. Click on the user name
9. Go to "Security credentials" tab
10. Click "Create access key"
11. Select "Application running outside AWS"
12. Accept terms and click "Create access key"
13. **SAVE THESE VALUES:**
    - Access Key ID
    - Secret Access Key

## Step 2: Deploy to Heroku

### 2.1 Initialize Git (if not already done)
```bash
cd c:\Users\mikha\OneDrive\Документы\python\gened
git init
git add .
git commit -m "Initial commit with S3 support"
```

### 2.2 Create and Login to Heroku
```bash
heroku login
# Opens browser to authenticate - log in with your Heroku account

# Or use: heroku login -i
# Enter email and password when prompted
```

### 2.3 Create Heroku App
```bash
heroku create your-app-name
# Example: heroku create article-manager-app

# You should see something like:
# Creating ⬢ article-manager-app... done
# https://article-manager-app.herokuapp.com/ | https://git.heroku.com/article-manager-app.git
```

### 2.4 Add PostgreSQL Database
```bash
heroku addons:create heroku-postgresql:hobby-dev -a your-app-name
# Wait a few seconds for the database to be created
```

### 2.5 Set Environment Variables
```bash
# Generate a secure SECRET_KEY (use an online generator or this command)
# On Windows PowerShell: [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes((New-Guid).Guid))

heroku config:set SECRET_KEY="your-very-secure-random-key-here" -a your-app-name
heroku config:set ADMIN_ACCESS_PASSWORD="your-admin-password" -a your-app-name
heroku config:set AWS_ACCESS_KEY_ID="your-aws-access-key" -a your-app-name
heroku config:set AWS_SECRET_ACCESS_KEY="your-aws-secret-key" -a your-app-name
heroku config:set AWS_S3_BUCKET="your-bucket-name" -a your-app-name
heroku config:set AWS_REGION="us-east-1" -a your-app-name
```

### 2.6 Deploy Your Code
```bash
git push heroku main
# or if your main branch is named 'master':
git push heroku master
```

### 2.7 Initialize Database
```bash
heroku run python -c "from app import db; db.create_all()" -a your-app-name
```

### 2.8 Open Your App
```bash
heroku open -a your-app-name
```

## Step 3: First Use

1. Your app is now live at: `https://your-app-name.herokuapp.com/`
2. Go to `/admin-access`
3. Enter your `ADMIN_ACCESS_PASSWORD`
4. Register with username `mikhail` (to get super_admin)
5. Start creating articles!

## Troubleshooting

### Check App Status
```bash
heroku ps -a your-app-name
```

### View Logs
```bash
heroku logs --tail -a your-app-name
```

### Database Connection Issues
```bash
# Check if DATABASE_URL is set
heroku config:get DATABASE_URL -a your-app-name

# Reset the database
heroku run python -c "from app import db; db.drop_all(); db.create_all()" -a your-app-name
```

### Image Upload Not Working
1. Check AWS credentials: `heroku config -a your-app-name`
2. Verify S3 bucket name matches exactly
3. Check bucket permissions (public read access enabled)
4. View logs: `heroku logs --tail -a your-app-name`

### App Won't Start
```bash
# View detailed logs to see the error
heroku logs --tail -a your-app-name

# Common issues:
# - Missing environment variables
# - Database connection string invalid
# - Python dependencies not installed
```

## Updating Your App

After making changes locally:

```bash
git add .
git commit -m "Your commit message"
git push heroku main
```

## Monitoring Costs

### AWS Costs
- Free tier includes: 5 GB of S3 storage, 20,000 GET requests, 2,000 PUT requests per month
- Typical cost: $0.00 for small usage

### Heroku Costs
- Hobby dyno: $5/month
- PostgreSQL: $9/month
- Total: $14/month

## Useful Commands

```bash
# View all config variables
heroku config -a your-app-name

# Update a variable
heroku config:set KEY=VALUE -a your-app-name

# Remove a variable
heroku config:unset KEY -a your-app-name

# Run Python code
heroku run python -c "your code here" -a your-app-name

# Create database backup
heroku pg:backups:capture -a your-app-name
heroku pg:backups:download -a your-app-name

# Scale dynos (increase power)
heroku ps:scale web=2 -a your-app-name

# Access app bash shell
heroku run bash -a your-app-name
```

## Next Steps

1. Test image uploads work
2. Test image deletions work
3. Create backup of database: `heroku pg:backups:capture -a your-app-name`
4. Share app URL with others!

