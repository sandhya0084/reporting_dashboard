"""Set a temporary password for user id=1 (for local testing only)."""
from index import app
from models import User, db

TEMP_PASSWORD = 'TempPass!2025'

with app.app_context():
    u = User.query.get(1)
    if not u:
        print('No user with id=1')
    else:
        u.set_password(TEMP_PASSWORD)
        db.session.commit()
        print(f"Set temporary password for id={u.id}, email={u.email}")
        print('Temporary password is:', TEMP_PASSWORD)
