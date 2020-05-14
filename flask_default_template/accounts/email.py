from flask_mail import Message
from flask_default_template import mail
from flask import render_template, current_app
from threading import Thread


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body):
    """
    Sends async email
    """
    msg = Message(
        subject,
        sender=sender,
        recipients=recipients
    )
    msg.body = text_body
    msg.html = html_body
    Thread(
        target=send_async_email,
        args=(current_app._get_current_object(), msg)
    ).start()


def send_password_reset_email(user):
    """
    Sends password reset email to the user
    """
    token = user.get_reset_password_token()
    send_email('[Flask SN] Reset Your Password',
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=None,
               html_body=render_template(
                   'emails/reset_password.html',
                   user=user,
                   token=token)
               )
