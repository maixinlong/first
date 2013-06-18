import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
os.environ['DJANGO_SETTINGS_MODULE'] = 'apps.settings'

cur_dir = os.path.dirname(os.path.abspath(__file__))

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
