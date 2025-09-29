from flask import Flask
from flask_mail import Mail, Message

app = Flask(__name__)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'sandhyachirumamilla6@gmail.com'
app.config['MAIL_PASSWORD'] = 'wdwxvjbvqnydbibp'  # <-- App Password (no spaces)

mail = Mail(app)

with app.app_context():
    msg = Message("Test Email",
                  sender=app.config['MAIL_USERNAME'],
                  recipients=["sandhyachirumamilla6@gmail.com"])
    msg.body = "This is a test email from Flask."
    mail.send(msg)
    print("✅ Test email sent!")

