from flask_default_template import db, login
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5
from time import time
import jwt
from flask import current_app


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class User(UserMixin, db.Model):
    """
    User model
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    first_name = db.Column(db.String(64), nullable=True)
    last_name = db.Column(db.String(64), nullable=True)
    about_me = db.Column(db.String(140), nullable=True)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        """
        Sets password hash
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """
        Checks password hash
        """
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        """
        Assigns an avatar to the user
        """
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def is_online(self):
        """
        Checks if user is online
        """
        if self.last_seen is None:
            return False
        difference = datetime.utcnow() - self.last_seen
        seconds_in_day = 24 * 60 * 60
        div = divmod(difference.days * seconds_in_day + difference.seconds, 60)
        if div[0] < 3:
            return True
        return False

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)
