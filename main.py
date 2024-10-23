# main.py
"""
Author: Abhisek Shrestha
"""

# Import of all required packages
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bootstrap import Bootstrap


# Initialize the Flask application
app = Flask(__name__)

# Configuration settings for the SQLite database and secret key for sessions
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy (ORM) and Bootstrap (CSS framework) extensions
db = SQLAlchemy(app)
Bootstrap(app)

# Database model for users (register and login)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)

# Database model for posts created by users
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Route for the home page
@app.route('/')
def home():
    return render_template('home.html')

# Route for the about page
@app.route('/about')
def about():
    return render_template('about.html')

# Route for the registration page, allows GET (view form) and POST (submit form)
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

# Route for the login page, allows GET (view form) and POST (submit form)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Login failed. Check your credentials.', 'danger')
    return render_template('login.html')

# Route for the user dashboard (accessible only after login)
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please log in first!', 'warning')
        return redirect(url_for('login'))
    posts = Post.query.filter_by(user_id=session['user_id']).all()
    return render_template('dashboard.html', posts=posts)

# Route for creating a new post, requires GET (view form) and POST (submit form)
@app.route('/new_post', methods=['GET', 'POST'])
def new_post():
    if 'user_id' not in session:
        flash('Please log in first!', 'warning')
        return redirect(url_for('login'))
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        post = Post(title=title, content=content, user_id=session['user_id'])
        db.session.add(post)
        db.session.commit()
        flash('Post created!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('new_post.html')

# Create all database tables before the first request
@app.before_request
def create_tables():
    db.create_all()

# Start the Flask application (debug mode on for development purposes)
if __name__ == '__main__':
    app.run(debug=True)