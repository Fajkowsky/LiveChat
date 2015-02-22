DEBUG = True
PORT = 8000

MONGODB_SETTINGS = {
    'db': '',
    'host': ''
}

SECRET_KEY = 'verySecretKey!'

try:
    from local import *
except ImportError:
    pass
