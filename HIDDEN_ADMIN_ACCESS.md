# Hidden Admin Access System

## How It Works

The login and registration system is now **completely hidden** from public view:

### For Common Users
- No login/register links appear in the navbar
- They can only browse articles publicly
- They cannot find the login system through the website

### For Admins
- A hidden access point exists at: `http://localhost:5000/admin-access`
- This page is **not indexed** by search engines (meta robots tag)
- Requires a special password to access
- After entering the correct password, they're redirected to the login page
- Then they can log in with their account credentials

## Configuration

### Default Admin Access Password
```
admin-secret-password
```

⚠️ **CHANGE THIS IMMEDIATELY IN PRODUCTION!**

### How to Set Custom Admin Password

**Option 1: Environment Variable (Recommended)**
```bash
set ADMIN_ACCESS_PASSWORD=your-new-secret-password
python app.py
```

**Option 2: Edit app.py directly**
```python
app.config['ADMIN_ACCESS_PASSWORD'] = 'your-new-secret-password'
```

## Usage Flow for Admins

1. Navigate to: `http://localhost:5000/admin-access`
2. Enter the admin access password
3. You'll be redirected to `/login`
4. Log in with your username and password
5. Access article management features

## Security Features

✅ **Multi-layer Access Control**
- Hidden `/admin-access` endpoint not linked anywhere
- Requires password to access login page
- Session-based authentication after login
- Logout available only when authenticated

✅ **Non-Indexable Pages**
- Admin access page has `meta robots: noindex, nofollow`
- Won't appear in search engines

✅ **No Public Links**
- Login/Register completely removed from navbar
- No discoverable links to authentication pages
- Only authenticated users see management features

## URL Reference

| Route | Visibility | Purpose |
|-------|-----------|---------|
| `/` | Public | Home page |
| `/articles` | Public | Browse all articles |
| `/article/<id>` | Public | Read article |
| `/admin-access` | Hidden | Admin password gateway |
| `/login` | Hidden (no links) | User login |
| `/register` | Hidden (no links) | User registration |
| `/article/new` | Login required | Create article |
| `/article/<id>/edit` | Owner only | Edit article |
| `/article/<id>/delete` | Owner only | Delete article |
| `/my-articles` | Login required | Manage user's articles |
| `/logout` | Login required | Log out |

## Creating Admin Accounts

Since registration is hidden, you need to manually create admin accounts:

```bash
python
>>> from app import app, db, User
>>> with app.app_context():
...     user = User(username='admin', is_admin=True)
...     user.set_password('admin-password')
...     db.session.add(user)
...     db.session.commit()
...     print("Admin user created!")
```

Or create a normal user first (via hidden `/register` page), then promote them:

```bash
python
>>> from app import app, db, User
>>> with app.app_context():
...     user = User.query.filter_by(username='your_username').first()
...     user.is_admin = True
...     db.session.commit()
```

## Accessing Hidden Pages

Normal users can only access through the navbar when logged in. To access hidden pages directly:

| What | URL | Notes |
|------|-----|-------|
| Admin gateway | `http://localhost:5000/admin-access` | Enter password |
| Login | `http://localhost:5000/login` | Direct URL access (no navbar link) |
| Register | `http://localhost:5000/register` | Direct URL access (no navbar link) |

⚠️ Direct URL access bypasses the password check. To prevent this, add protective logic as needed.

## Production Recommendations

1. **Change the admin access password** to something strong and random
2. **Use environment variables** for sensitive configuration
3. **Change the SECRET_KEY** to a strong random string
4. **Enable HTTPS** to encrypt all traffic
5. **Consider changing the `/admin-access` URL** to something custom
6. **Add request logging** to monitor access attempts
7. **Implement rate limiting** to prevent brute force attacks on `/admin-access`

## Articles Remain Public

✅ All articles are still visible to anyone
- Browse at `/articles`
- Read individual articles at `/article/<id>`
- No login required for viewing

Only creating, editing, and deleting articles requires authentication.
