from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_moment import Moment
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os


db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'accounts.login'
login.login_message = 'Please log in to access this page'
mail = Mail()
moment = Moment()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)
    moment.init_app(app)

    from flask_default_template.main import bp as main_bp
    app.register_blueprint(main_bp)

    from flask_default_template.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from flask_default_template.accounts import bp as accounts_bp
    app.register_blueprint(accounts_bp, url_prefix='/accounts')

    from flask_default_template.default import bp as default_bp
    app.register_blueprint(default_bp, url_prefix='/default')

    if not app.debug:
        if app.config['MAIL_SERVER']:
            auth = None
            if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
                auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            secure = None
            if app.config['MAIL_USE_TLS']:
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr='no-reply@' + app.config['MAIL_SERVER'],
                toaddrs=app.config['ADMINS'], subject='Server Failure',
                credentials=auth, secure=secure)
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)
        if not os.path.exists('flask_default_template/errors/logs'):
            os.mkdir('flask_default_template/errors/logs')
        file_handler = RotatingFileHandler('flask_default_template/errors/logs/flask_default_template.log', maxBytes=10240,
                                           backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Flask example project template')

    return app
