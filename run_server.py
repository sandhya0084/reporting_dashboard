from importlib import import_module
import sys
import os
# Ensure repo root is on path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))
# Import the app (top-level index.py exports `app`)
mod = import_module('index')
app = getattr(mod, 'app', None) or getattr(mod, 'flask_app')

if __name__ == '__main__':
    # Run without reloader for stability
    app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)
