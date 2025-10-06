from index import app

EMAIL = 'sandhyachirumamilla6@gmail.com'
PASSWORD = 'TempPass!2025'

# Disable CSRF for the test run so Flask-WTF form validation succeeds
app.config.setdefault('WTF_CSRF_ENABLED', False)

with app.test_client() as c:
    # GET login page first to set session cookies
    _ = c.get('/login')
    # POST credentials
    r = c.post('/login', data={'email': EMAIL, 'password': PASSWORD}, follow_redirects=False)
    print('POST /login status_code =', r.status_code)
    # If redirect, print location
    if 300 <= r.status_code < 400:
        print('Redirect location:', r.headers.get('Location'))
    else:
        # print body snippet
        print('Response length:', len(r.get_data(as_text=True)))
        print(r.get_data(as_text=True)[:400])
