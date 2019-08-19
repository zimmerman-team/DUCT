from django.core.management.base import BaseCommand

from geodata.geoapp_data import CodeListImporter


class Command(BaseCommand):
    def handle(self, *args, **options):

        cl = CodeListImporter()
        cl.synchronise_with_codelists()
