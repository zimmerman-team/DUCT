try:
    from .development_settings import *
except ImportError:
    SECRET_KEY = '__DEV_SECRET_KEY__'
    pass