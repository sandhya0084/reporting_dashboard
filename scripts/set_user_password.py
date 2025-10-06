"""
Set a user's password to a known value (development use only).
Usage:
  python scripts/set_user_password.py user@example.com newpassword
"""
import sys, os
if len(sys.argv) < 3:
    print('Usage: set_user_password.py email newpassword')
    sys.exit(2)
email = sys.argv[1]
newpw = sys.argv[2]
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from importlib import import_module
mod = import_module('api.index')
app = mod.flask_app
from models import db, User

with app.app_context():
    user = User.query.filter_by(email=email).first()
    if not user:
        print('User not found')
        sys.exit(1)
    user.set_password(newpw)
    db.session.commit()
    print(f'Password for {email} set to {newpw}')
