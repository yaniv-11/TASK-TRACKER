from flask import Flask,render_template,request,redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
from dotenv import load_dotenv
load_dotenv()  
db_url = os.environ.get('DATABASE_URL', 'sqlite:///todos.db')

if db_url.startswith('postgres://'):
    db_url = db_url.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Todo(db.Model):
    no = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    desc = db.Column(db.String(500), nullable=False)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __repr__(self) -> str:
        return f"{self.no} - {self.title}"

@app.route('/', methods=['GET', 'POST'])
def hello_world():
    if request.method == 'POST':
        title = request.form.get('title')
        desc = request.form.get('desc')
        todo = Todo(title=title, desc=desc)
        db.session.add(todo)
        db.session.commit()
    allTodo = Todo.query.all()
    return render_template('index.html', allTodo=allTodo)

@app.route('/show')
def show():
    allTodo = Todo.query.all()
    return render_template('show.html', allTodo=allTodo)

@app.route('/update/<int:no>', methods=['GET', 'POST'])
def update(no):
    if request.method == 'POST':
        title = request.form.get('title')
        desc = request.form.get('desc')
        todo = Todo.query.filter_by(no=no).first()
        todo.title = title
        todo.desc = desc    
        db.session.commit()
        return redirect('/')
    todo = Todo.query.filter_by(no=no).first()
    return render_template('update.html', todo=todo)

@app.route('/delete/<int:no>')
def delete(no):
    todo = Todo.query.filter_by(no=no).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect('/')    

# Initialize database
with app.app_context():
    db.create_all()

# This is required for Vercel
app = app

if __name__ == '__main__':
    app.run(debug=True, port=8000)

