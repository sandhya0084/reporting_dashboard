import sys, os
sys.path.insert(0, os.path.abspath(r'c:/Users/Gouse Basha/OneDrive/Desktop/sandhya/reporting paltform/reporting_dashboard-1'))
from importlib import import_module
mod = import_module('index')
app = getattr(mod, 'app', mod.flask_app)
from models import User
with app.app_context():
    users = User.query.filter(User.password.like('scrypt:%')).all()
    if not users:
        print('No scrypt-hashed users found.')
    else:
        print(f'Found {len(users)} scrypt-hashed users:')
        for u in users:
            print(f' - id={u.id}, email={u.email}')
