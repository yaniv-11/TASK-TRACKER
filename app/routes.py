from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, DateTimeField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from app import db
from app.models import User, Todo
from datetime import datetime

# Create blueprint
main = Blueprint('main', __name__)

# Forms
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')
    
class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Choose a different one.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Choose a different one.')

class TodoForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description')
    priority = SelectField('Priority', choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')])
    category = SelectField('Category', choices=[('personal', 'Personal'), ('work', 'Work'), ('shopping', 'Shopping'), ('health', 'Health')])
    due_date = DateTimeField('Due Date', format='%Y-%m-%d %H:%M', validators=[])
    submit = SubmitField('Save Todo')

# Routes
@main.route('/')
def index():
    return render_template('base.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        print("✅ Form validated")
        user = User.query.filter_by(username=form.username.data).first()
        print("User from DB:", user)

        if user:
            print("Checking password hash...")
            result = user.check_password(form.password.data)
            print("Password match:", result)
        else:
            print("No such user found")

        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('login.html', form=form)


@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('main.login'))
    
    return render_template('register.html', form=form)

@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))

@main.route('/dashboard')
@login_required
def dashboard():
    todos = Todo.query.filter_by(user_id=current_user.id).order_by(Todo.created_at.desc()).all()
    return render_template('dashboard.html', todos=todos)


# API routes for managing todos

# api route to get all todos for the current user
from flask import jsonify
from app.models import Todo
@main.route('/api/todos', methods=['GET'])
@login_required
def get_todos():
    todos = Todo.query.filter_by(user_id=current_user.id).order_by(Todo.created_at.desc()).all()
    return {
        'todos': [
            {
                'id': todo.id,
                'title': todo.title,
                'description': todo.description,
                'completed': todo.completed,
                'priority': todo.priority,
                'category': todo.category,
                'due_date': todo.due_date.isoformat() if todo.due_date else None
,
                'created_at': todo.created_at.strftime('%Y-%m-%d %H:%M')
            } for todo in todos
        ]
    }
# API: Create a new todo
@main.route('/api/todos', methods=['POST'])
@login_required
def api_add_todo():
    data = request.get_json()

    if not data.get('title'):
        return jsonify({'error': 'Title is required'}), 400

    try:
        todo = Todo(
            title=data['title'],
            description=data.get('description'),
            category=data.get('category', 'personal'),
            priority=data.get('priority', 'medium'),
            due_date=datetime.strptime(data['due_date'], '%Y-%m-%dT%H:%M'),
            user_id=current_user.id
        )
        db.session.add(todo)
        db.session.commit()
        return jsonify({'message': 'Todo added successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API: Update an existing todo
@main.route('/api/todos/<int:id>', methods=['PUT'])
@login_required
def api_update_todo(id):
    todo = Todo.query.get_or_404(id)
    if todo.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()
    todo.title = data['title']
    todo.description = data.get('description')
    todo.category = data.get('category')
    todo.priority = data.get('priority')
    todo.due_date = datetime.strptime(data['due_date'], '%Y-%m-%dT%H:%M')

    db.session.commit()
    return jsonify({'message': 'Todo updated'})

# API: Toggle completion status
@main.route('/api/todos/<int:id>/toggle', methods=['PUT'])
@login_required
def api_toggle_todo(id):
    todo = Todo.query.get_or_404(id)
    if todo.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    todo.completed = not todo.completed
    db.session.commit()
    return jsonify({'message': 'Todo status updated'})

# API: Delete a todo
@main.route('/api/todos/<int:id>', methods=['DELETE'])
@login_required
def api_delete_todo(id):
    todo = Todo.query.get_or_404(id)
    if todo.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    db.session.delete(todo)
    db.session.commit()
    return jsonify({'message': 'Todo deleted'})