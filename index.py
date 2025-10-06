from asgiref.wsgi import WsgiToAsgi

from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_mail import Mail
from models import db, User, Client, Report
from forms import RegistrationForm, LoginForm
from email_utils import send_verification_email
from asgiref.wsgi import WsgiToAsgi
from dotenv import load_dotenv
import os

load_dotenv()

# -------------------- APP CONFIG --------------------
flask_app = Flask(__name__)
flask_app.secret_key = os.environ.get('SECRET_KEY', 'supersecretkey')
flask_app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///reporting.db')
flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# -------------------- MAIL CONFIG --------------------
flask_app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
flask_app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
flask_app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True').lower() in ('1', 'true', 'yes')
flask_app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
flask_app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
mail = Mail(flask_app)

# -------------------- DATABASE & LOGIN --------------------
db.init_app(flask_app)
login_manager = LoginManager(flask_app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# -------------------- ROUTES --------------------

@flask_app.route('/')
def home():
    return render_template('home.html')


@flask_app.route('/register', methods=['GET','POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('register'))

        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        # Fail-safe email sending
        try:
            send_verification_email(flask_app, user, mail)
            flash('Account created! Check your email to verify.', 'success')
        except Exception as e:
            print("Email sending failed:", e)
            flash("Account created! Verification email failed. Please try resending.", "warning")

        return redirect(url_for('login'))

    return render_template('register.html', form=form)


@flask_app.route('/verify_email/<token>')
def verify_email(token):
    from itsdangerous import URLSafeTimedSerializer
    s = URLSafeTimedSerializer(flask_app.secret_key)
    try:
        email = s.loads(token, salt='email-confirm', max_age=3600)
    except:
        flash('Verification link expired or invalid.', 'danger')
        return redirect(url_for('login'))

    user = User.query.filter_by(email=email).first()
    if user and not user.verified:
        user.verified = True
        db.session.commit()
        flash('Email verified! You can now login.', 'success')
    else:
        flash('Email already verified.', 'info')
    return redirect(url_for('login'))


@flask_app.route("/resend_verification", methods=["GET", "POST"])
def resend_verification():
    # GET: show form. POST: handle resend then redirect (PRG pattern).
    if request.method == "POST":
        email = (request.form.get("email") or "").strip()
        if not email:
            flash("Please enter an email address.", "warning")
            return render_template("resend_verification.html", email=email)

        user = User.query.filter_by(email=email).first()

        if user:
            if user.verified:
                flash("This email is already verified. Please login.", "info")
                return redirect(url_for('login'))

            try:
                send_verification_email(flask_app, user, mail)
                flash("Verification email resent. Please check your inbox.", "success")
                return redirect(url_for('login'))
            except Exception as e:
                print(f"Resend failed: {str(e)}")
                flash("Failed to send verification email. Please try again later.", "danger")
                return render_template("resend_verification.html", email=email)

        # No matching user
        flash("Email not found. Would you like to register instead?", "warning")
        return redirect(url_for('register'))

    prefill_email = request.args.get('email', '')
    return render_template("resend_verification.html", email=prefill_email)


@flask_app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            if user.verified:
                login_user(user)
                flash('Logged in successfully', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Please verify your email first', 'warning')
        else:
            auth_error = 'Invalid email or password'
            prefill_email = form.email.data or ''
            return render_template('login.html', form=form, email=prefill_email, auth_error=auth_error)

    prefill_email = request.args.get('email', '')
    return render_template('login.html', form=form, email=prefill_email)


@flask_app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully', 'info')
    return redirect(url_for('login'))


@flask_app.route('/dashboard')
@login_required
def dashboard():
    clients = Client.query.all()
    return render_template('dashboard.html',
                           username=current_user.username,
                           total_users=User.query.count(),
                           total_email=sum(c.email_sent for c in clients),
                           total_sms=sum(c.sms_sent for c in clients),
                           total_voice=sum(c.voice_calls for c in clients),
                           total_tele=sum(c.telemarketing_calls for c in clients))


@flask_app.route('/reports')
@login_required
def reports():
    platform = request.args.get('platform')
    query = Report.query
    if platform and platform != "All":
        query = query.filter_by(platform=platform)
    reports = query.order_by(Report.generated_at.desc()).all()
    return render_template('reports.html', reports=reports, platform=platform)


# Simple health endpoint for local checks and parity with api/index.py
@flask_app.route('/healthz')
def healthz():
    return ("OK", 200)


# -------------------- DATABASE INIT --------------------
with flask_app.app_context():
    db.create_all()
    # Add sample clients if none exist
    if not Client.query.first():
        sample_clients = [
            Client(name="Acme Corp", email_sent=10, sms_sent=5, voice_calls=3, telemarketing_calls=2),
            Client(name="Globex Inc", email_sent=15, sms_sent=7, voice_calls=4, telemarketing_calls=3)
        ]
        db.session.add_all(sample_clients)
        db.session.commit()


# -------------------- RUN APP --------------------
# Export a top-level `app` name so WSGI servers can import this module
# (e.g., gunicorn index:app). This makes the application easier to run
# from different entrypoints.
app = flask_app

if __name__ == '__main__':
    # For local development only: disable CSRF to simplify testing with the
    # dev server and test clients. Do NOT enable this in production.
    flask_app.config.setdefault('WTF_CSRF_ENABLED', False)
    flask_app.run(debug=True)
