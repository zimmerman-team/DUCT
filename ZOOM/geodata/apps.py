from __future__ import unicode_literals

from django.apps import AppConfig


class GeodataConfig(AppConfig):
    name = 'geodata'

    def ready(self):
        import geodata.signals
