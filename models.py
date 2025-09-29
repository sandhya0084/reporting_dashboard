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
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

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
