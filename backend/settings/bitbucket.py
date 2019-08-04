from backend.settings.commonsettings import *
import os

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# This will allow us to create test models
INSTALLED_APPS += ['backend.core.tests']
