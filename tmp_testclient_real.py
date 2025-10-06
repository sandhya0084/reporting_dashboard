from importlib import import_module
import sys
sys.path.insert(0, r'c:/Users/Gouse Basha/OneDrive/Desktop/sandhya/reporting paltform/reporting_dashboard-1')
mod = import_module('api.index')
app = mod.flask_app
with app.test_client() as client:
    r = client.post('/login', data={'email':'localtest@example.com','password':'testpass'}, follow_redirects=True)
    print('status', r.status_code)
    try:
        print('final path:', r.request.path)
    except Exception as e:
        print('no r.request', e)
    print('contains invalid?', b'Invalid email or password' in r.data)
    open('last_testclient_login.html','wb').write(r.data)
