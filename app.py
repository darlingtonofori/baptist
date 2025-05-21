import os
import time
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, Response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import uuid
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or \
    'postgresql://lebron_user:Hl1Og0nZl15rXjknaywyI3Av92hMyBaJ@dpg-d0ma4ahr0fns73bip9sg-a.oregon-postgres.render.com/lebron'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/images'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'auth'

# Models (keep your existing models exactly as they were)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

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

# Keep all your other routes exactly as they were

if __name__ == '__main__':
    app.run(debug=True)
