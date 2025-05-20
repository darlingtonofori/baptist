import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import uuid

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-secret-key'  # Change in production!
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or \
    'postgresql://lebron_user:Hl1Og0nZl15rXjknaywyI3Av92hMyBaJ@dpg-d0ma4ahr0fns73bip9sg-a.oregon-postgres.render.com/lebron'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/images'

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'auth'

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)  # Increased from 100 to 256
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    posts = db.relationship('Post', backref='author', lazy=True)
    comments = db.relationship('Comment', backref='author', lazy=True)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    content = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(100))
    views = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    comments = db.relationship('Comment', backref='post', lazy=True, cascade='all, delete-orphan')

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Tool(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    github_url = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(100))
    posted_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create tables and admin user
with app.app_context():
    db.create_all()
    # Create admin user if not exists
    if not User.query.filter_by(username='TR4N5P4R3NT').first():
        admin_password = os.environ.get('ADMIN_PASSWORD') or 'admin_password'  # Change in production!
        admin = User(
            username='TR4N5P4R3NT',
            password=generate_password_hash(admin_password, method='pbkdf2:sha256', salt_length=8),
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
# Add these routes if they're missing from your current app.py

@app.route('/')
def index():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('index.html', posts=posts)

@app.route('/auth', methods=['GET', 'POST'])
def auth():
    # [Keep your existing auth route implementation]
    pass

@app.route('/logout')
@login_required
def logout():
    # [Keep your existing logout route implementation]
    pass

# [Keep all your other existing routes]
# ... [keep all your existing route definitions exactly as they were] ...

if __name__ == '__main__':
    app.run(debug=True)
