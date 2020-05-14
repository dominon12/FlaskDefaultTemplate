from flask_default_template.default import bp
from flask import render_template


@bp.route('/')
def index():
    return render_template('default/default.html', title='Default')
