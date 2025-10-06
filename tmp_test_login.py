import sys
sys.path.insert(0, r'c:/Users/Gouse Basha/OneDrive/Desktop/sandhya/reporting paltform/reporting_dashboard-1')
from importlib import import_module
mod = import_module('api.index')
app = mod.flask_app
from models import db, User

with app.app_context():
    # Ensure tables exist and create a test user
    db.create_all()
    # Remove existing test user if any
    u = User.query.filter_by(email='testuser@example.com').first()
    if u:
        db.session.delete(u)
        db.session.commit()
    user = User(username='testuser', email='testuser@example.com')
    user.set_password('password123')
    user.verified = True
    db.session.add(user)
    db.session.commit()

with app.test_client() as client:
    r = client.post('/login', data={'email':'testuser@example.com','password':'password123'}, follow_redirects=True)
    print('POST /login status:', r.status_code)
    body = r.get_data(as_text=True)
    print('Has invalid message?', 'Invalid email or password' in body)
    open('last_login_response.html','w', encoding='utf-8').write(body)
print('Wrote last_login_response.html')
