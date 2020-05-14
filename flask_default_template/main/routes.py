from flask_default_template import db
from flask_default_template.main import bp
from flask import render_template
from flask_login import current_user
from datetime import datetime


@bp.before_app_request
def before_request():
    """
    What to do before every request
    """
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@bp.route('/')
def index():
    """
    Returns index page
    """
    return render_template(
        'main/index.html',
        title='Main page',
    )
