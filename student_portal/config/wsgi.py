import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()
from django.core.management import call_command
call_command('migrate', verbosity=0)  # no --run-syncdb needed for postgres

application = get_wsgi_application()