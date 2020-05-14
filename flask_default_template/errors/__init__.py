from flask import Blueprint

bp = Blueprint('errors', __name__, template_folder='templates')

from flask_default_template.errors import handlers
