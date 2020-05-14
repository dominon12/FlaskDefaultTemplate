from flask import Blueprint

bp = Blueprint('accounts', __name__, template_folder='templates')

from flask_default_template.accounts import routes
