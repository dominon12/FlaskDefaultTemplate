from flask_default_template import create_app, db
from flask_default_template.accounts.models import User


app = create_app()


@app.shell_context_processor
def make_shell_context():
    """
    Adds vars to flask shell
    """
    return {'db': db, 'User': User}


if __name__ == '__main__':
    app.run(debug=True)
