from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    verified = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        # Force a stable, widely-supported algorithm to avoid environment
        # incompatibilities (some Werkzeug/Python combos default to scrypt,
        # which can raise in certain stdlib configurations). pbkdf2:sha256 is
        # a safe, portable default.
        self.password = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        # Some deployments may have existing password hashes in a format
        # not supported by the runtime's hashlib (for example, newer
        # Werkzeug created scrypt-based hashes while the system's
        # hashlib doesn't expose scrypt as a hash name for HMAC). In that
        # case check_password_hash raises ValueError during comparison.
        #
        # We catch that error and return False so the app doesn't crash;
        # affected users should reset their passwords (or re-create
        # accounts) so passwords are re-hashed with the supported method.
        try:
            return check_password_hash(self.password, password)
        except ValueError as exc:
            # Log the issue to stdout (visible in many hosting logs)
            print(f"check_password: unsupported hash format for user {self.id}: {exc}")
            return False

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email_sent = db.Column(db.Integer, default=0)
    sms_sent = db.Column(db.Integer, default=0)
    voice_calls = db.Column(db.Integer, default=0)
    telemarketing_calls = db.Column(db.Integer, default=0)

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'))
    platform = db.Column(db.String(50))
    status = db.Column(db.String(50))
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    client = db.relationship('Client', backref='reports')
