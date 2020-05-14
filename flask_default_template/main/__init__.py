from flask import Blueprint

bp = Blueprint('main', __name__, template_folder='templates')

from flask_default_template.main import routes
