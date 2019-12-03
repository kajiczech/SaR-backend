# API Documentation
https://sarwithdronetag.docs.apiary.io/#

# Installation
**All commands are executed in the project root directory**

## Python version

Python version must be `3.6` or higher

## Python Requirements

    pip install requirements.txt

## Settings

### Selecting settings
Set environmental variable to the desired settings module or run `manage.py` with `--settings=<settings_module>`
 flag
 
e.g.

    export DJANGO_SETTINGS_MODULE = backend.settings.commonsettings

or

    python manage.py <action> --settings=backend.settings.commonsettings

You can create your own local settings use them as described above.
    
### Database
In settings module set up `DATABASES` array for your DB

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'dronetag',
            'USER': 'dronetag',
            'PASSWORD': 'dronetag',
            'HOST': 'postgres', #localhost on regular server
            'PORT': '5432',
        }
    }
    
### Allowed hosts
In settings module, set hostname of your server to `ALLOWED_HOSTS` array

e.g.

        ALLOWED_HOSTS = ['backend', 'localhost', 'turaco.eu']

## Migration
To create database or make database changes, run

    python manage.py migrate

## Create static files
To create static files (for administration and rest framework overhead), run

    python manage.py collectstatic --no-input
    
#How to run

### Development
In a development environment, run

    python manage.py runserver 0.0.0.0:<port>

**With this, the server will restart every time you make change to any source file**


### Production
In a production environment, run

    gunicorn backend.wsgi -b 0.0.0.0:<port> 

To restart, you need to kill the gunicorn process and run this again

# Deployment

To run this project from scratch, run these commands

(Setup `DATABASES` and `ALLOWED_HOSTS` in settings module first and make sure you have correct version of python installed)
    
    export DJANGO_SETTINGS_MODULE = <settings_module> #e.g. backend.settings.commonsettings
    python manage.py migrate
    python manage.py collectstatic --no-input
    python manage.py runserver 0.0.0.0:<port>

# Initial setup
To be able to access django administration and create an Oauth2 client to be able to authenticate, you need to create a superuser first.
To create superuser run
  
    python manage.py createsuperuser
    
and fill the fields. Then in django administration create a new oauth application:

- client id - web
- client type - public
- Authorization grant type - Resource owner password-based
- client secret - leave empty

# Debug

## Docker on Mac with PyCharm
   to debug on mac with docker follow remote debug server configuration tutorial (not ssh).
   copy pycharm-debug.egg to project root directory
    
    cp /Applications/PyCharm.app/Contents/debug-eggs/pycharm-debug.egg <backend_directory>
    
   Create Python remote debug configuration localhost name set to whatever you want, but port must be matching port in settrace function (below)... 
   Just Set it to 12345
   
   Then add this code to the file you want to debug:
   
    import sys
    sys.path.append("/src/pycharm-debug.egg")
    import pydevd
    pydevd.settrace('docker.for.mac.localhost', port=12345, stdoutToServer=True, stderrToServer=True)

And you can start debugging!

src. https://www.jetbrains.com/help/pycharm/remote-debugging-with-product.html
