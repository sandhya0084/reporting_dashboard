from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_mail import Mail
from models import db, User, Client, Report
from forms import RegistrationForm, LoginForm
from email_utils import send_verification_email
from asgiref.wsgi import WsgiToAsgi

# -------------------- APP CONFIG --------------------
flask_app = Flask(__name__)
flask_app.secret_key = "supersecretkey"
flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///reporting.db'
flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# -------------------- MAIL CONFIG --------------------
flask_app.config['MAIL_SERVER'] = 'smtp.gmail.com'
flask_app.config['MAIL_PORT'] = 587
flask_app.config['MAIL_USE_TLS'] = True
flask_app.config['MAIL_USERNAME'] = 'sandhyachirumamilla6@gmail.com'       # Your Gmail
flask_app.config['MAIL_PASSWORD'] = 'wdwxvjbvqnydbibp'                      # Your Gmail App Password
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
    if request.method == "POST":
        email = request.form["email"]
        user = User.query.filter_by(email=email).first()

        if user and not user.verified:
            try:
                send_verification_email(flask_app, user, mail)
                flash("Verification email resent. Please check your inbox.", "success")
            except Exception as e:
                print(f" Resend failed: {str(e)}")
                flash("Failed to send verification email. Please try again later.", "danger")
        else:
            flash("Email not found or already verified.", "warning")

    return render_template("resend_verification.html")


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
            flash('Invalid email or password', 'danger')
            return redirect(url_for(resend_verification))

    return render_template('login.html', form=form)


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
if __name__ == '__main__':
    flask_app.run(debug=True)
