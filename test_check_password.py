from index import app
from models import User

with app.app_context():
    u = User.query.get(1)
    if not u:
        print('No user')
    else:
        print('Stored password:', u.password[:60] + '...' if u.password else None)
        print('check_password TempPass!2025 ->', u.check_password('TempPass!2025'))
        print('check_password wrongpass ->', u.check_password('wrongpass'))
