from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app import db 

# make sure this import works inside app context

login_manager = LoginManager()

# ---------------------------
# USER MODEL
# ---------------------------
class User(UserMixin, db.Model):
    __tablename__ = 'user'  # optional, but helps avoid naming confusion

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)

    # Relationship with todos
    todos = db.relationship('Todo', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

# ---------------------------
# TODO MODEL
# ---------------------------
class Todo(db.Model):
    __tablename__ = 'todo'  # optional for clarity

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    completed = db.Column(db.Boolean, default=False)
    priority = db.Column(db.String(20), default='medium')  # low, medium, high
    category = db.Column(db.String(50), default='personal')  # personal, work, etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime)

    # Foreign key to User
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<Todo {self.title}>'

# ---------------------------
# USER LOADER FUNCTION
# ---------------------------
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
