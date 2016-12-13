
#... A LOT OF DJANGO STUFF HERE ...



AUTH_USER_MODEL = 'backend.ChinoUser'

AUTHENTICATION_BACKENDS = [
    'backend.models.ChinoRemoteUserBackend',
]


# PUT YOUR CHINO DATA HERE.
CHINO_ID = '...'
CHINO_KEY = '...'
CHINO_URL = 'https://api.dev.chino.io/'

# production URL:
#CHINO_URL = 'https://api.chino.io/'

CHINO_APPLICATION_ID = '...'
CHINO_APPLICATION_SECRET = '...'
