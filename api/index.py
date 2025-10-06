# ...existing code...
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
import traceback
import sys

load_dotenv()


# --- Startup environment validation (run at import-time so Vercel logs show results) ---
def _mask(val: str) -> str:
    if not val:
        return '<missing>'
    if len(val) <= 8:
        return val[0] + '***' + val[-1]
    return val[:4] + '...' + val[-4:]

def validate_startup_env():
    """Print (masked) environment variables and Vercel git metadata to stderr.

    This runs at import time intentionally so that platform logs (Vercel)
    immediately show missing configuration instead of a vague 500.
    """
    required = ['SECRET_KEY', 'DATABASE_URL']
    optional = ['MAIL_USERNAME', 'MAIL_PASSWORD', 'MAIL_SERVER', 'MAIL_PORT']

    missing = []
    print('\n[startup] environment summary:', file=sys.stderr)
    for k in required:
        v = os.environ.get(k)
        print(f"  {k} = {_mask(v)}", file=sys.stderr)
        if not v:
            missing.append(k)

    for k in optional:
        v = os.environ.get(k)
        if v:
            print(f"  {k} = {_mask(v)}", file=sys.stderr)

    # Vercel-provided metadata (helpful in logs)
    vercel_sha = os.environ.get('VERCEL_GIT_COMMIT_SHA') or os.environ.get('GIT_COMMIT')
    vercel_ref = os.environ.get('VERCEL_GIT_COMMIT_REF') or os.environ.get('GIT_BRANCH')
    if vercel_sha or vercel_ref:
        print(f"  VERCEL_GIT_COMMIT_REF={vercel_ref} VERCEL_GIT_COMMIT_SHA={vercel_sha}", file=sys.stderr)

    if missing:
        print('[startup] WARNING: missing required env vars: ' + ','.join(missing), file=sys.stderr)
    else:
        print('[startup] all required env vars present (masked)', file=sys.stderr)


# Run validation now so Vercel logs capture it when the function loads.
try:
    validate_startup_env()
except Exception as _exc:
    # Don't raise during import; just log so platform shows the issue.
    print('[startup] validate_startup_env failed:', repr(_exc), file=sys.stderr)

# -------------------- APP CONFIG --------------------
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# Ensure templates/static are resolved relative to the repository root so
# importing this module from the `api/` package finds the top-level templates.
flask_app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, 'templates'),
    static_folder=os.path.join(BASE_DIR, 'static'),
)
# Use env var for secret key in production; fall back to a local default for dev
flask_app.secret_key = os.environ.get('SECRET_KEY', 'supersecretkey')
# Allow configuring the DB via DATABASE_URL (set this in Vercel). Default to sqlite for local dev.
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
    # Show form on GET. On POST use POST-Redirect-GET for better UX.
    if request.method == "POST":
        email = (request.form.get("email") or "").strip()
        if not email:
            flash("Please enter an email address.", "warning")
            return render_template("resend_verification.html", email=email)

        user = User.query.filter_by(email=email).first()

        if user:
            if user.verified:
                # Already verified — send user back to login with an informative message
                flash("This email is already verified. Please login.", "info")
                return redirect(url_for('login'))

            # Not verified: attempt to resend verification email
            try:
                send_verification_email(flask_app, user, mail)
                flash("Verification email resent. Please check your inbox.", "success")
                return redirect(url_for('login'))
            except Exception as e:
                print(f"Resend failed: {str(e)}")
                flash("Failed to send verification email. Please try again later.", "danger")
                # fall through to re-render form so user can retry
                return render_template("resend_verification.html", email=email)

        # No user found with that email
        flash("Email not found. Would you like to register instead?", "warning")
        return redirect(url_for('register'))

    # GET: show form (allow pre-filling via query param)
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
            # Invalid credentials — render the login page with an inline error
            # so the message is visible immediately and the user doesn't have
            # to follow a redirect to see it.
            auth_error = 'Invalid email or password'
            prefill_email = form.email.data or ''
            return render_template('login.html', form=form, email=prefill_email, auth_error=auth_error)

    # Prefill the email field from query param if present (e.g., after redirect)
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


# Simple health endpoint for platform checks (useful for Vercel and monitoring)
@flask_app.route('/healthz')
def healthz():
    # Return a lightweight 200 response so Vercel or load balancers can verify the app is up.
    return ("OK", 200)


# -------------------- DATABASE INIT (guarded) --------------------
def init_db(create_sample_data: bool = False):
    """Create database tables and optional sample data.

    This is intentionally not run at import-time because platforms like Vercel
    import the module to load the app and may not permit filesystem writes or
    immediate schema creation during import. Call this manually when running
    locally or via a controlled deployment step.
    """
    try:
        db.create_all()
    except Exception as e:
        # Log the error but don't raise during import-time usage
        print(f"init_db: failed to create tables: {e}")
        return

    if create_sample_data:
        try:
            if not Client.query.first():
                sample_clients = [
                    Client(name="Acme Corp", email_sent=10, sms_sent=5, voice_calls=3, telemarketing_calls=2),
                    Client(name="Globex Inc", email_sent=15, sms_sent=7, voice_calls=4, telemarketing_calls=3)
                ]
                db.session.add_all(sample_clients)
                db.session.commit()
        except Exception as e:
            print(f"init_db: failed to add sample data: {e}")


# -------------------- VERCEL / ASGI ENTRYPOINT --------------------
# Wrap the Flask (WSGI) app with ASGI adapter and export as `app` so Vercel (and other ASGI hosts) can load it.
# Note: Do NOT run the Flask development server here. Vercel will invoke `app` as an ASGI callable.
app = WsgiToAsgi(flask_app)


# Global exception handler that logs full tracebacks to stderr/stdout.
# This helps capture the real server-side error in Vercel logs while
# keeping the HTTP response generic.
@flask_app.errorhandler(Exception)
def handle_unhandled_exception(exc):
    tb = traceback.format_exc()
    print("Unhandled exception in app:\n", tb, file=sys.stderr)
    # Return a generic 500 response to the client
    return ("Internal Server Error", 500)

# If this file is executed directly (local development), allow initializing the DB
# and running the dev server. For production deployments (like Vercel) this
# module will be imported and the ASGI `app` exported; import-time DB writes are
# avoided.
if __name__ == '__main__':
    # Optional: allow forcing DB init via env var for local convenience
    allow_init = os.environ.get('ALLOW_DB_INIT', '0')
    if allow_init == '1':
        with flask_app.app_context():
            init_db(create_sample_data=True)

    flask_app.run(debug=True)

# Note: Do NOT run the Flask development server here. Vercel will invoke `app` as an ASGI callable.
