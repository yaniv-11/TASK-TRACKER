from app import create_app, db
from app.models import User, Todo

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Todo': Todo}

if __name__ == '__main__':
    app.run()