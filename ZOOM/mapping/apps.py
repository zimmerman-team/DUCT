from __future__ import unicode_literals

from django.apps import AppConfig


class MappingConfig(AppConfig):
    name = 'mapping'

    def ready(self):
        import mapping.signals  # NOQA: F401
