from importlib import import_module
import sys
sys.path.insert(0, r'c:/Users/Gouse Basha/OneDrive/Desktop/sandhya/reporting paltform/reporting_dashboard-1')
mod = import_module('api.index')
app = mod.flask_app
with app.app_context():
    # ensure user exists
    from models import db, User
    db.create_all()
    u = User.query.filter_by(email='localtest@example.com').first()
    if not u:
        u = User(username='localtest', email='localtest@example.com')
        u.set_password('testpass')
        u.verified = True
        db.session.add(u)
        db.session.commit()

with app.test_client() as client:
    r = client.post('/login', data={'email':'localtest@example.com','password':'testpass'}, follow_redirects=True)
    print('status', r.status_code)
    print('path', getattr(r, 'request', None) and r.request.path)
    print('contains invalid?', b'Invalid email or password' in r.data)
    open('last_testclient_api.html','wb').write(r.data)
