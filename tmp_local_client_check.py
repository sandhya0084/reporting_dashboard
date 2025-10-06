from importlib import import_module
import sys
sys.path.insert(0, r'c:/Users/Gouse Basha/OneDrive/Desktop/sandhya/reporting paltform/reporting_dashboard-1')
mod = import_module('api.index')
app = mod.flask_app
with app.test_client() as client:
    r = client.get('/')
    print('status', r.status_code)
    print('body snippet:', r.data[:200])
