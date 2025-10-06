import requests
try:
    r = requests.get('http://127.0.0.1:5000/', timeout=3)
    print('STATUS', r.status_code)
    print(r.text[:200])
except Exception as e:
    print('ERROR', repr(e))
    raise
