import os
import time
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, Response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import uuid
import json

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-secret-key'
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

# --- MODELS MUST BE DEFINED BEFORE THEY'RE USED IN ROUTES ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(512), nullable=False)
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
# --- END MODELS ---

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create tables and admin user
with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='TR4N5P4R3NT').first():
        admin_password = os.environ.get('ADMIN_PASSWORD') or 'admin_password'
        admin = User(
            username='TR4N5P4R3NT',
            password=generate_password_hash(admin_password, method='pbkdf2:sha256', salt_length=8),
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()

# --- ROUTES ---
@app.route('/')
def index():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('index.html', posts=posts or [])

@app.route('/stream')
def stream():
    def event_stream():
        last_id = Post.query.order_by(Post.id.desc()).first().id if Post.query.count() > 0 else 0
        while True:
            new_posts = Post.query.filter(Post.id > last_id).order_by(Post.created_at.asc()).all()
            for post in new_posts:
                last_id = post.id
                data = {
                    'id': post.id,
                    'title': post.title,
                    'content': post.content,
                    'image': post.image,
                    'username': post.author.username,
                    'user_id': post.user_id,
                    'created_at': post.created_at.strftime('%Y-%m-%d %H:%M'),
                    'views': post.views,
                    'comments_count': len(post.comments)
                }
                yield f"data: {json.dumps(data)}\n\n"
            time.sleep(1)
    return Response(event_stream(), mimetype="text/event-stream")

# [Keep all your other routes exactly as they were]

if __name__ == '__main__':
    app.run(debug=True)
