"""
Inspect user id=1 using the app exported from index.py and print password info.
"""
from index import app
from models import User

with app.app_context():
    u = User.query.get(1)
    if not u:
        print('No user with id=1')
    else:
        print('id=', u.id)
        print('email=', u.email)
        pwd = getattr(u, 'password', None)
        print('password repr=', repr(pwd))
        print('password length:', len(pwd) if pwd else 'None')
        try:
            print('password startswith scrypt?', isinstance(pwd, str) and pwd.startswith('scrypt:'))
        except Exception as e:
            print('error checking password start', e)
        print('is_verified=', getattr(u, 'verified', None) if hasattr(u, 'verified') else getattr(u, 'is_verified', None))
