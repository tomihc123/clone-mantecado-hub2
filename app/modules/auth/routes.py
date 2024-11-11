from flask import render_template, redirect, url_for, request, session
from flask_login import current_user, login_user, logout_user
from app.modules.auth import auth_bp
from app.modules.auth.forms import SignupForm, LoginForm
from app.modules.auth.services import AuthenticationService
from app.modules.profile.services import UserProfileService

authentication_service = AuthenticationService()
user_profile_service = UserProfileService()

@auth_bp.route("/signup/", methods=["GET", "POST"])
def show_signup_form():
    if current_user.is_authenticated:
        return redirect(url_for('public.index'))

    form = SignupForm()
    if form.validate_on_submit():
        email = form.email.data
        if not authentication_service.is_email_available(email):
            return render_template("auth/signup_form.html", form=form, error=f'Email {email} in use')

        try:
            user = authentication_service.create_with_profile(**form.data)
            session['confirm_email_user_id'] = user.id  # Set session for confirmation page
            return redirect(url_for('auth.confirm_email'))
        except Exception as exc:
            return render_template("auth/signup_form.html", form=form, error=f'Error creating user: {exc}')

    return render_template("auth/signup_form.html", form=form)

@auth_bp.route('/confirm-email', methods=['GET', 'POST'])
def confirm_email():
    user_id = session.get('confirm_email_user_id')
    if not user_id:
        return redirect(url_for('auth.login'))  # Redirect to login if no user is in session

    if request.method == 'POST':
        # Simulate email confirmation
        user = authentication_service.confirm_user_email(user_id)
        login_user(user, remember=True)
        session.pop('confirm_email_user_id', None)
        return redirect(url_for('public.index'))
    
    return render_template('auth/confirm_email.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('public.index'))

    form = LoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        result = authentication_service.login(form.email.data, form.password.data)
        if result is True:
            return redirect(url_for('public.index'))
        elif result == "unconfirmed":
            # Redirect to confirmation page if email is not confirmed
            user = authentication_service.find_user_by_email(form.email.data)
            session['confirm_email_user_id'] = user.id
            return redirect(url_for('auth.confirm_email'))
        
        return render_template("auth/login_form.html", form=form, error='Invalid credentials')

    return render_template('auth/login_form.html', form=form)

@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('public.index'))
