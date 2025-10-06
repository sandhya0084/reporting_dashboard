from importlib import import_module
import sys
sys.path.insert(0, r'c:/Users/Gouse Basha/OneDrive/Desktop/sandhya/reporting paltform/reporting_dashboard-1')
mod = import_module('index')
app = mod.app
from models import db, User

with app.app_context():
    db.create_all()
    if not User.query.filter_by(email='localtest@example.com').first():
        u = User(username='localtest', email='localtest@example.com')
        u.set_password('testpass')
        u.verified = True
        db.session.add(u)
        db.session.commit()
        print('Created user localtest@example.com / testpass')
    else:
        print('User already exists')
