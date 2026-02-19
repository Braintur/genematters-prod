# Article Management System with Authentication

## Features Implemented

✅ **User Authentication**
- Registration with username and password (6+ chars)
- Secure password hashing using werkzeug
- Login/logout functionality
- Session management with Flask-Login

✅ **Authorization & Security**
- CSRF protection on all forms
- Users can only edit/delete their own articles
- Admin role for future expansion
- 403 Forbidden errors for unauthorized access

✅ **Article Management**
- Create articles (requires login)
- Edit own articles
- Delete own articles
- View all articles publicly
- View personal article list with timestamps

✅ **Database**
- SQLite database (`articles.db`)
- User model with username and hashed passwords
- Article model with title, content, author reference, and timestamps
- Automatic database creation on first run

## Installation

1. Install required packages:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Visit `http://localhost:5000` in your browser

## Usage

### First Time Setup
- The database (`articles.db`) is created automatically on first run
- Navigate to `/register` to create an account
- Log in with your credentials

### Creating Articles
1. After logging in, click "+ New Article" in the navbar
2. Enter title and content
3. Click "Create Article"

### Managing Articles
- View all articles: Navigate to "/articles"
- View your articles: Click "My Articles" (after login)
- Edit an article: Click "Edit" on article card or in My Articles table
- Delete an article: Click "Delete" in My Articles table (with confirmation)

### Admin Features (To Enable)
To make a user admin:
```bash
python
>>> from app import app, db, User
>>> with app.app_context():
...     user = User.query.filter_by(username='your_username').first()
...     user.is_admin = True
...     db.commit()
```

Admins can edit/delete any article.

## Security Notes

✅ Implemented:
- Password hashing (Werkzeug)
- CSRF protection
- SQL injection prevention (SQLAlchemy ORM)
- Authorization checks on sensitive operations
- Session-based authentication

⚠️ Production Recommendations:
- Change `SECRET_KEY` in app.py to a strong random string
- Use environment variables for configuration
- Enable HTTPS in production
- Regularly backup the `articles.db` file
- Consider adding email verification for registration
- Add rate limiting to prevent brute force attacks

## File Structure

```
app.py                          # Main Flask application
requirements.txt                # Python dependencies

templates/
├── base.html                   # Base template with navbar
├── login.html                  # Login page
├── register.html               # Registration page
├── article_form.html           # Create/edit article form
├── articles_list.html          # View all articles
├── my_articles.html            # User's personal articles
├── error.html                  # Error pages
├── index.html                  # Home page (existing)
└── ... (other existing files)

static/
├── styles/                     # CSS files
└── js/                         # JavaScript files
```

## Database Schema

### User Table
- `id`: Primary key
- `username`: Unique username (string)
- `password_hash`: Hashed password (string)
- `is_admin`: Admin flag (boolean)
- `created_at`: Account creation timestamp

### Article Table
- `id`: Primary key
- `title`: Article title (string)
- `content`: Article content (text)
- `user_id`: Reference to User (foreign key)
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

## Future Enhancements

- Add email notifications
- Implement article comments/discussions
- Add article search functionality
- Create admin dashboard
- Add article categories/tags
- Implement article drafts
- Add user profiles
- Enable two-factor authentication
