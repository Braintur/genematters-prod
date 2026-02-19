from flask import Flask, render_template, url_for, request, redirect, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import boto3
from botocore.exceptions import ClientError

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')

# Database Configuration - Support both SQLite (local) and PostgreSQL (Heroku)
database_url = os.environ.get('DATABASE_URL', 'sqlite:///articles.db')
# Fix PostgreSQL URL format for SQLAlchemy 2.0+
if database_url and database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['ADMIN_ACCESS_PASSWORD'] = os.environ.get('ADMIN_ACCESS_PASSWORD', 'admin-secret-password')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# AWS S3 Configuration
USE_S3 = os.environ.get('AWS_ACCESS_KEY_ID') and os.environ.get('AWS_SECRET_ACCESS_KEY')
if USE_S3:
    S3_CLIENT = boto3.client(
        's3',
        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
        region_name=os.environ.get('AWS_REGION', 'us-east-1')
    )
    S3_BUCKET = os.environ.get('AWS_S3_BUCKET')
    S3_URL_BASE = f"https://{S3_BUCKET}.s3.amazonaws.com"
else:
    # Local file uploads if no S3 configured
    UPLOAD_FOLDER = 'static/uploads'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
csrf = CSRFProtect(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

# ===== MODELS =====
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_super_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    articles = db.relationship('Article', backref='author', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    images = db.relationship('ArticleImage', backref='article', lazy=True, cascade='all, delete-orphan')

class ArticleImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'), nullable=True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True, index=True)  # Track who uploaded
    url = db.Column(db.String(500), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ===== HELPER FUNCTIONS =====
def is_article_owner_or_admin(article):
    """Check if current user owns article or is admin"""
    return current_user.is_admin or article.user_id == current_user.id

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# ===== PUBLIC ROUTES =====
@app.route("/")
def about_us():
    return render_template('index.html')

@app.route("/articles")
def list_articles():
    """List all articles"""
    page = request.args.get('page', 1, type=int)
    articles = Article.query.order_by(Article.created_at.desc()).paginate(page=page, per_page=10)
    return render_template('articles_list.html', articles=articles)

@app.route("/article/<int:article_id>")
def article(article_id):
    """View single article"""
    article_obj = db.session.get(Article, article_id)
    if not article_obj:
        abort(404)
    return render_template("article.html", article=article_obj)

@app.route("/form")
def form():
    return render_template("form.html")

# ===== AUTHENTICATION ROUTES =====
@app.route("/admin-access", methods=['GET', 'POST'])
def admin_access():
    """Hidden admin access point - requires special password"""
    if request.method == 'POST':
        password = request.form.get('password')
        
        if password == app.config['ADMIN_ACCESS_PASSWORD']:
            # Redirect to login after correct password
            return redirect(url_for('login'))
        else:
            return render_template('admin_access.html', error='Invalid password')
    
    return render_template('admin_access.html')

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('about_us'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('about_us'))
        else:
            return render_template('login.html', error='Invalid username or password')
    
    return render_template('login.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('about_us'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        admin_code = request.form.get('admin_code', '').strip()
        
        # Validation
        if not username or not password or not confirm_password or not admin_code:
            return render_template('register.html', error='All fields are required')
        
        if len(username) < 3:
            return render_template('register.html', error='Username must be at least 3 characters long')
        
        if len(password) < 6:
            return render_template('register.html', error='Password must be at least 6 characters long')
        
        if password != confirm_password:
            return render_template('register.html', error='Passwords do not match')
        
        if admin_code != app.config['ADMIN_ACCESS_PASSWORD']:
            return render_template('register.html', error='Invalid admin code')
        
        if User.query.filter_by(username=username).first():
            return render_template('register.html', error='Username already exists')
        
        # Admin code is valid, create new user with admin rights
        # mikhail gets super_admin access
        is_super_admin = (username.lower() == 'mikhail')
        user = User(username=username, is_admin=True, is_super_admin=is_super_admin)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        return redirect(url_for('about_us'))
    
    return render_template('register.html')

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('about_us'))

@app.route("/html-guide")
def html_guide():
    """Display HTML article guide"""
    guide_path = 'HTML_ARTICLE_GUIDE.md'
    if os.path.exists(guide_path):
        with open(guide_path, 'r', encoding='utf-8') as f:
            guide_content = f.read()
        return render_template('guide.html', content=guide_content)
    return render_template('error.html', message='Guide not found'), 404

# ===== ARTICLE MANAGEMENT ROUTES =====
@app.route("/article/new", methods=['GET', 'POST'])
@login_required
def create_article():
    """Create new article"""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        image_ids = request.form.get('image_ids', '').strip()  # Get image IDs from form
        
        if not title or not content:
            return render_template('article_form.html', error='Title and content are required')
        
        article = Article(title=title, content=content, user_id=current_user.id)
        db.session.add(article)
        db.session.commit()
        
        # Link any uploaded images to this article
        if image_ids:
            try:
                image_id_list = [int(id.strip()) for id in image_ids.split(',') if id.strip()]
                images = ArticleImage.query.filter(ArticleImage.id.in_(image_id_list), ArticleImage.article_id.is_(None)).all()
                for image in images:
                    image.article_id = article.id
                db.session.commit()
            except Exception as e:
                print(f"Error linking images to article: {e}")
        
        return redirect(url_for('article', article_id=article.id))
    
    return render_template('article_form.html')

@app.route("/article/<int:article_id>/edit", methods=['GET', 'POST'])
@login_required
def edit_article(article_id):
    """Edit article (only owner or admin)"""
    article_obj = db.session.get(Article, article_id)
    if not article_obj:
        abort(404)
    
    # Authorization check
    if not is_article_owner_or_admin(article_obj):
        return render_template('error.html', message='You do not have permission to edit this article'), 403
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        
        if not title or not content:
            return render_template('article_form.html', article=article_obj, error='Title and content are required')
        
        article_obj.title = title
        article_obj.content = content
        db.session.commit()
        
        return redirect(url_for('article', article_id=article_obj.id))
    
    return render_template('article_form.html', article=article_obj)

@app.route("/article/<int:article_id>/delete", methods=['POST'])
@login_required
def delete_article(article_id):
    """Delete article (only owner or admin)"""
    article_obj = db.session.get(Article, article_id)
    if not article_obj:
        abort(404)
    
    # Authorization check
    if not is_article_owner_or_admin(article_obj):
        return render_template('error.html', message='You do not have permission to delete this article'), 403
    
    # Delete all associated images
    images = ArticleImage.query.filter_by(article_id=article_id).all()
    for image in images:
        try:
            if USE_S3:
                # Delete from AWS S3
                try:
                    S3_CLIENT.delete_object(Bucket=S3_BUCKET, Key=f"uploads/{image.filename}")
                except ClientError as e:
                    print(f"Warning: Could not delete from S3: {e}")
            else:
                # Delete from local filesystem
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
                if os.path.exists(filepath):
                    os.remove(filepath)
        except Exception as e:
            print(f"Error deleting image file {image.filename}: {e}")
    
    # Delete article and its images (cascade delete)
    db.session.delete(article_obj)
    db.session.commit()
    
    return redirect(url_for('list_articles'))

@app.route("/my-articles")
@login_required
def my_articles():
    """View current user's articles"""
    page = request.args.get('page', 1, type=int)
    articles = Article.query.filter_by(user_id=current_user.id).order_by(Article.created_at.desc()).paginate(page=page, per_page=10)
    return render_template('my_articles.html', articles=articles)

@app.route("/admin-accounts")
@login_required
def admin_accounts():
    """View all admin accounts (super_admin only)"""
    if not current_user.is_super_admin:
        return render_template('error.html', message='You do not have permission to access this page'), 403
    
    page = request.args.get('page', 1, type=int)
    admins = User.query.filter_by(is_admin=True).order_by(User.created_at.desc()).paginate(page=page, per_page=20)
    return render_template('admin_accounts.html', admins=admins)

@app.route("/admin-accounts/<int:user_id>/delete", methods=['POST'])
@login_required
def delete_admin_account(user_id):
    """Delete admin account (super_admin only)"""
    if not current_user.is_super_admin:
        return render_template('error.html', message='You do not have permission to delete accounts'), 403
    
    user_to_delete = db.session.get(User, user_id)
    if not user_to_delete:
        abort(404)
    
    # Prevent deleting super_admin
    if user_to_delete.is_super_admin:
        return render_template('error.html', message='Cannot delete a super admin account'), 403
    
    # Prevent self-deletion
    if user_to_delete.id == current_user.id:
        return render_template('error.html', message='You cannot delete your own account'), 403
    
    username = user_to_delete.username
    
    # Delete all articles and associated images
    articles = Article.query.filter_by(user_id=user_id).all()
    for article in articles:
        images = ArticleImage.query.filter_by(article_id=article.id).all()
        for image in images:
            try:
                if USE_S3:
                    # Delete from AWS S3
                    try:
                        S3_CLIENT.delete_object(Bucket=S3_BUCKET, Key=f"uploads/{image.filename}")
                    except ClientError as e:
                        print(f"Warning: Could not delete from S3: {e}")
                else:
                    # Delete from local filesystem
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
                    if os.path.exists(filepath):
                        os.remove(filepath)
            except Exception as e:
                print(f"Error deleting image file {image.filename}: {e}")
        db.session.delete(article)
    
    # Delete user
    db.session.delete(user_to_delete)
    db.session.commit()
    
    return redirect(url_for('admin_accounts'))

# ===== IMAGE UPLOAD ROUTES =====
@app.route("/upload-image", methods=['POST'])
@login_required
def upload_image():
    """Upload image for articles - supports both local filesystem and AWS S3"""
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    
    file = request.files['image']
    
    if file.filename == '':
        return jsonify({'error': 'No image selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Allowed: png, jpg, jpeg, gif, webp'}), 400
    
    try:
        # Get article_id from request if editing
        article_id = request.form.get('article_id', type=int)
        
        filename = secure_filename(f"{datetime.utcnow().timestamp()}_{file.filename}")
        
        if USE_S3:
            # Upload to AWS S3
            try:
                S3_CLIENT.upload_fileobj(
                    file,
                    S3_BUCKET,
                    f"uploads/{filename}",
                    ExtraArgs={'ContentType': file.content_type}
                )
                image_url = f"{S3_URL_BASE}/uploads/{filename}"
            except ClientError as e:
                return jsonify({'error': f'S3 upload failed: {str(e)}'}), 500
        else:
            # Upload to local filesystem (development)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            image_url = url_for('static', filename=f'uploads/{filename}')
        
        # Save image info to database
        article_image = ArticleImage(
            article_id=article_id if article_id else None,
            user_id=current_user.id,  # Always track who uploaded
            url=image_url,
            filename=filename
        )
        db.session.add(article_image)
        db.session.commit()
        
        return jsonify({'url': image_url, 'success': True, 'id': article_image.id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/get-article-images/<int:article_id>", methods=['GET'])
@login_required
def get_article_images(article_id):
    """Get all images for an article"""
    article = db.session.get(Article, article_id)
    if not article:
        return jsonify({'error': 'Article not found'}), 404
    
    # Check if user has permission to view this article's images
    if article.user_id != current_user.id and not current_user.is_admin:
        return jsonify({'error': 'Permission denied'}), 403
    
    images = ArticleImage.query.filter_by(article_id=article_id).all()
    return jsonify({
        'success': True,
        'images': [
            {
                'id': img.id,
                'url': img.url,
                'code': f'<img src="{img.url}" alt="Article image">'
            }
            for img in images
        ]
    })

@app.route("/get-temp-images", methods=['GET'])
@login_required
def get_temp_images():
    """Get temporary unlinked images for current user"""
    # Fetch images that don't have an article_id (temporary uploads) from current user
    images = ArticleImage.query.filter_by(article_id=None, user_id=current_user.id).all()
    return jsonify({
        'success': True,
        'images': [
            {
                'id': img.id,
                'url': img.url,
                'code': f'<img src="{img.url}" alt="Article image">'
            }
            for img in images
        ]
    })

@app.route("/delete-article-image/<int:image_id>", methods=['POST'])
@login_required
def delete_article_image(image_id):
    """Delete an article image - supports both local filesystem and AWS S3"""
    image = db.session.get(ArticleImage, image_id)
    if not image:
        return jsonify({'error': 'Image not found'}), 404
    
    # Check permissions
    if image.article_id:
        # Image linked to article - check if user owns it
        article = db.session.get(Article, image.article_id)
        if article.user_id != current_user.id and not current_user.is_admin:
            return jsonify({'error': 'Permission denied'}), 403
    else:
        # Temporary image - only uploader can delete
        if image.user_id != current_user.id and not current_user.is_admin:
            return jsonify({'error': 'Permission denied'}), 403
    
    try:
        if USE_S3:
            # Delete from AWS S3
            try:
                S3_CLIENT.delete_object(Bucket=S3_BUCKET, Key=f"uploads/{image.filename}")
            except ClientError as e:
                print(f"Warning: Could not delete from S3: {e}")
        else:
            # Delete from local filesystem
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
            if os.path.exists(filepath):
                os.remove(filepath)
        
        # Delete from database
        db.session.delete(image)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/upload-background", methods=['POST'])
@login_required
def upload_background():
    """Upload background image (admin only)"""
    if not current_user.is_admin:
        return jsonify({'error': 'Only admins can change background'}), 403
    
    if 'background' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    
    file = request.files['background']
    
    if file.filename == '':
        return jsonify({'error': 'No image selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400
    
    try:
        if USE_S3:
            # Upload to AWS S3 with fixed filename
            try:
                S3_CLIENT.upload_fileobj(
                    file,
                    S3_BUCKET,
                    'uploads/background.jpg',
                    ExtraArgs={'ContentType': file.content_type}
                )
                return jsonify({'success': True, 'message': 'Background updated'})
            except ClientError as e:
                return jsonify({'error': f'S3 upload failed: {str(e)}'}), 500
        else:
            # Save to local filesystem with fixed filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'background.jpg')
            file.save(filepath)
            return jsonify({'success': True, 'message': 'Background updated'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ===== DNA CHECKING ROUTE (Original) =====
@app.route("/check_dna", methods=['POST'])
def check_dna():
    data = request.get_json()
    dna_sequence = data.get('dna_sequence', '')
    
    # Your DNA checking function here
    result = dna_id(dna_sequence)
    
    if result:
        return jsonify({'redirect_url': url_for('article')})
    else:
        return jsonify({'error': 'DNA analysis failed'})

def dna_id(dna_seq):
    return True

# ===== ERROR HANDLERS =====
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', message='Page not found'), 404

@app.errorhandler(403)
def forbidden(e):
    return render_template('error.html', message='Access denied'), 403

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        
        # Ensure mikhail is a super_admin (if exists)
        try:
            mikhail = User.query.filter_by(username='mikhail').first()
            if mikhail and not mikhail.is_super_admin:
                mikhail.is_super_admin = True
                mikhail.is_admin = True
                db.session.commit()
        except Exception as e:
            print(f"Note: Could not update mikhail account: {e}")
    
    app.run(debug=True)