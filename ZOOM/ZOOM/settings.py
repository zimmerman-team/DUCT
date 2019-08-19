try:
    from .development_settings import *  # NOQA: F401 F403
except ImportError:
    SECRET_KEY = '__DEV_SECRET_KEY__'
    pass
