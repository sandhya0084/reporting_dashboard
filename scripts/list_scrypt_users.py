"""
List users whose password field starts with 'scrypt:' so you can identify affected accounts.
Run with the project's venv: 

"C:/.../venv/Scripts/python.exe" scripts/list_scrypt_users.py
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from importlib import import_module
mod = import_module('api.index')
app = mod.flask_app
from models import User

with app.app_context():
    users = User.query.filter(User.password.like('scrypt:%')).all()
    if not users:
        print('No scrypt-hashed users found.')
    else:
        print(f'Found {len(users)} scrypt-hashed users:')
        for u in users:
            print(f' - id={u.id}, email={u.email}')
