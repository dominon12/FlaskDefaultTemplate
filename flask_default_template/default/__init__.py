from flask import Blueprint

bp = Blueprint('default', __name__, template_folder='templates')

from flask_default_template.default import routes, forms, models
