from flask_default_template import db
from flask_default_template.accounts import bp
from flask_default_template.accounts.models import User
from flask_default_template.accounts.email import send_password_reset_email, send_email
from flask_default_template.accounts.forms import SignUpForm, EditProfileForm, LoginForm, ChangePasswordForm, \
    ResetPasswordRequestForm,ResetPasswordForm
from flask import flash, url_for, redirect, render_template, request, current_app
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse


@bp.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    """
    Registers new user profiles
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = SignUpForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        new_user = User(username=username, email=email)
        new_user.set_password(form.password1.data)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user, remember=True)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        flash('You were successfully registered!')
        return redirect(next_page)
    return render_template(
        'registration/sign_up.html',
        title='Sign up',
        form=form,
    )


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Returns login page and authenticates user
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('accounts.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template(
        'registration/login.html',
        title='Sign In',
        form=form,
    )


@bp.route('/logout')
@login_required
def logout():
    """
    Logs out the user
    """
    logout_user()
    return redirect(url_for('main.index'))


@bp.route('/change-password/<username>', methods=['GET', 'POST'])
@login_required
def change_password(username):
    """
    Changes user password
    """
    user = User.query.filter_by(username=username).first_or_404()
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if user.check_password(form.old_password.data):
            user.set_password(form.new_password.data)
            db.session.commit()
            flash('Your password was successfully changed')
            return redirect(url_for('accounts.profile', username=username))
        else:
            flash("Old password didn't match")
            return redirect(url_for('accounts.change_password', username=username))
    return render_template(
        'registration/change_password.html',
        title='Change password',
        form=form,
    )


@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your emails for the instructions to reset your password')
        return redirect(url_for('accounts.login'))
    return render_template(
        'registration/reset_password_request.html',
        title='Reset Password',
        form=form
    )


@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('accounts.login'))
    return render_template(
        'registration/reset_password.html',
        title='Reset password',
        form=form
    )


@bp.route('/users')
def users():
    """
    List view for users
    """
    page = request.args.get('page', 1, type=int)
    users = User.query.paginate(page, current_app.config['OBJECTS_PER_PAGE'], False)
    next_url = url_for('accounts.users', page=users.next_num) \
        if users.has_next else None
    prev_url = url_for('accounts.users', page=users.prev_num) \
        if users.has_prev else None
    return render_template(
        'accounts/profiles.html',
        title='All users',
        users=users.items,
        next_url=next_url,
        prev_url=prev_url,
    )


@bp.route('/profile/<username>')
@login_required
def user(username):
    """
    Returns user's profile page
    """
    user = User.query.filter_by(username=username).first_or_404()
    return render_template(
        'accounts/profile.html',
        title='User profile',
        user=user,
    )


@bp.route('/edit-profile', methods=['GET', 'POST'])
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('accounts.user', username=current_user.username))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.about_me.data = current_user.about_me
    return render_template(
        'accounts/edit.html',
        title='Edit Profile',
        form=form,
    )


@bp.route('/send_security_info/<token>')
def send_security_info(token):
    user = User.verify_reset_password_token(token)
    send_email(
        'Security email',
        sender=current_app.config['ADMINS'][0],
        recipients=[current_app.config['ADMINS'][0]],
        text_body=None,
        html_body=render_template('emails/security_email.html', user=user)
    )
    flash('Message to admin was send!')
    return redirect(url_for('main.index'))

