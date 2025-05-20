import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import uuid
import os


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this in production!
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://lebron_user:Hl1Og0nZl15rXjknaywyI3Av92hMyBaJ@dpg-d0ma4ahr0fns73bip9sg-a.oregon-postgres.render.com/lebron'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/images'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'auth'

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
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

# Create tables (run once)
with app.app_context():
    db.create_all()
    # Create admin user if not exists
    if not User.query.filter_by(username='TR4N5P4R3NT').first():
        admin = User(
            username='TR4N5P4R3NT',
            password=generate_password_hash('admin_password'),  # Change this!
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
@app.route('/auth', methods=['GET', 'POST'])
def auth():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form_type = 'login'  # Default to login form
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if 'register' in request.form:
            form_type = 'register'
            # Handle registration
            if User.query.filter_by(username=username).first():
                flash('Username already exists', 'error')
            else:
                hashed_password = generate_password_hash(password)
                new_user = User(username=username, password=hashed_password)
                db.session.add(new_user)
                db.session.commit()
                flash('Registration successful! Please login.', 'success')
                form_type = 'login'
        
        else:
            # Handle login
            user = User.query.filter_by(username=username).first()
            if user and check_password_hash(user.password, password):
                login_user(user)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('index'))
            else:
                flash('Invalid username or password', 'error')
    
    return render_template('auth.html', form_type=form_type)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/')
def index():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('index.html', posts=posts)

@app.route('/tools')
def tools():
    tools = Tool.query.order_by(Tool.created_at.desc()).all()
    return render_template('tools.html', tools=tools)

@app.route('/post', methods=['POST'])
@login_required
def create_post():
    title = request.form.get('title', '')
    content = request.form.get('content', '')
    image = None
    
    if 'image' in request.files:
        file = request.files['image']
        if file.filename != '':
            ext = file.filename.split('.')[-1]
            filename = f"{uuid.uuid4()}.{ext}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image = filename
    
    new_post = Post(
        title=title,
        content=content,
        image=image,
        user_id=current_user.id
    )
    db.session.add(new_post)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'post': {
            'id': new_post.id,
            'title': new_post.title,
            'content': new_post.content,
            'image': new_post.image,
            'username': current_user.username,
            'created_at': new_post.created_at.strftime('%Y-%m-%d %H:%M'),
            'views': new_post.views
        }
    })

@app.route('/comment', methods=['POST'])
@login_required
def create_comment():
    post_id = request.form.get('post_id')
    content = request.form.get('content')
    
    post = Post.query.get_or_404(post_id)
    new_comment = Comment(
        content=content,
        user_id=current_user.id,
        post_id=post.id
    )
    db.session.add(new_comment)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'comment': {
            'id': new_comment.id,
            'content': new_comment.content,
            'username': current_user.username,
            'created_at': new_comment.created_at.strftime('%Y-%m-%d %H:%M')
        }
    })

@app.route('/post/<int:post_id>')
def view_post(post_id):
    post = Post.query.get_or_404(post_id)
    post.views += 1
    db.session.commit()
    return render_template('post.html', post=post)

@app.route('/add_tool', methods=['POST'])
@login_required
def add_tool():
    name = request.form.get('name')
    github_url = request.form.get('github_url')
    description = request.form.get('description')
    image = None
    
    if 'image' in request.files:
        file = request.files['image']
        if file.filename != '':
            ext = file.filename.split('.')[-1]
            filename = f"{uuid.uuid4()}.{ext}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image = filename
    
    new_tool = Tool(
        name=name,
        github_url=github_url,
        description=description,
        image=image,
        posted_by=current_user.id
    )
    db.session.add(new_tool)
    db.session.commit()
    
    return redirect(url_for('tools'))

# Admin routes
@app.route('/delete_post/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if current_user.is_admin or current_user.id == post.user_id:
        db.session.delete(post)
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Unauthorized'}), 403

@app.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if current_user.is_admin:
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Unauthorized'}), 403

# API endpoint for live updates
@app.route('/api/posts')
def get_posts():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    posts_data = []
    for post in posts:
        posts_data.append({
            'id': post.id,
            'title': post.title,
            'content': post.content,
            'image': post.image,
            'username': post.author.username,
            'created_at': post.created_at.strftime('%Y-%m-%d %H:%M'),
            'views': post.views,
            'comments_count': len(post.comments)
        })
    return jsonify(posts_data)

if __name__ == '__main__':
    app.run(debug=True)
