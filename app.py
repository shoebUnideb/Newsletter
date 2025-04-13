import os
from dotenv import load_dotenv
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from PIL import Image
import io

#check if the .env file exists already
if not os.path.exists('.env'):
    raise RuntimeError(
        "Missing .env file - please create one based on .env.example\n"
        "Required variables: SECRET_KEY, ADMIN_USERNAME, ADMIN_PASSWORD, DATABASE_URI"
    )
# Loading environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback-secret-key-for-dev')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'sqlite:///database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_IMAGE_SIZE'] = (800, 600)
app.config['THUMBNAIL_SIZE'] = (400, 300)
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(100))
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author = db.relationship('User', backref=db.backref('posts', lazy=True))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)

# Initialize database with fresh admin credentials
with app.app_context():
    db.create_all()
    
    # Remove all existing admin users
    User.query.filter_by(is_admin=True).delete()
    
    # Create new admin with current credentials
    admin_username = os.getenv('ADMIN_USERNAME', 'admin')
    admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
    
    if not User.query.filter_by(username=admin_username).first():
        new_admin = User(
            username=admin_username,
            password=generate_password_hash(admin_password),
            is_admin=True
        )
        db.session.add(new_admin)
        db.session.commit()

# Helper Functions
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def resize_image(image_data, max_size):
    img = Image.open(io.BytesIO(image_data))
    img.thumbnail(max_size, Image.LANCZOS)
    return img

def save_image(file, filename):
    image_data = file.read()
    img = resize_image(image_data, app.config['MAX_IMAGE_SIZE'])
    
    # Save main image
    img_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    img.save(img_path)
    
    # Save thumbnail
    thumb = resize_image(image_data, app.config['THUMBNAIL_SIZE'])
    thumb_path = os.path.join(app.config['UPLOAD_FOLDER'], 'thumbs', filename)
    os.makedirs(os.path.dirname(thumb_path), exist_ok=True)
    thumb.save(thumb_path)
    
    return filename

# Routes
@app.route('/')
def home():
    posts = Post.query.order_by(Post.date_posted.desc()).all()
    return render_template('index.html', posts=posts)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        # Get current admin credentials from env
        admin_user = os.getenv('ADMIN_USERNAME', 'admin')
        admin_pass = os.getenv('ADMIN_PASSWORD', 'admin123')
        
        # Special check for admin credentials
        if username == admin_user:
            if not (user and check_password_hash(user.password, admin_pass)):
                flash('Admin credentials have been updated. Please use current credentials.', 'error')
                return redirect(url_for('login'))
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            flash('Logged in successfully!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('home'))

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('is_admin'):
        flash('You do not have permission to access this page', 'error')
        return redirect(url_for('home'))
    
    posts = Post.query.order_by(Post.date_posted.desc()).all()
    return render_template('admin/dashboard.html', posts=posts)

@app.route('/admin/post/new', methods=['GET', 'POST'])
def new_post():
    if not session.get('is_admin'):
        flash('You do not have permission to access this page', 'error')
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        author_id = session['user_id']
        
        image = None
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filename = save_image(file, filename)
                image = filename
        
        post = Post(title=title, content=content, image=image, author_id=author_id)
        db.session.add(post)
        db.session.commit()
        flash('Post created successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin/edit_post.html')

@app.route('/admin/post/edit/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    if not session.get('is_admin'):
        flash('You do not have permission to access this page', 'error')
        return redirect(url_for('home'))
    
    post = Post.query.get_or_404(post_id)
    
    if request.method == 'POST':
        post.title = request.form['title']
        post.content = request.form['content']
        
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                # Delete old images
                if post.image:
                    try:
                        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], post.image))
                        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], 'thumbs', post.image))
                    except OSError:
                        pass
                
                # Save new image
                filename = secure_filename(file.filename)
                filename = save_image(file, filename)
                post.image = filename
        
        db.session.commit()
        flash('Post updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin/edit_post.html', post=post)

@app.route('/admin/post/delete/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    if not session.get('is_admin'):
        flash('You do not have permission to access this page', 'error')
        return redirect(url_for('home'))
    
    post = Post.query.get_or_404(post_id)
    
    if post.image:
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], post.image))
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], 'thumbs', post.image))
        except OSError:
            pass
    
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/post/<int:post_id>')
def view_post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('user/view_post.html', post=post)

@app.route('/user/posts')
def user_posts():
    posts = Post.query.order_by(Post.date_posted.desc()).all()
    return render_template('user/posts.html', posts=posts)

if __name__ == '__main__':
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'thumbs'), exist_ok=True)
    app.run(debug=os.getenv('FLASK_DEBUG', 'False') == 'True')