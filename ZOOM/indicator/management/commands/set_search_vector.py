from django.core.management.base import BaseCommand
from indicator.search_vector_update import update_all_unset

class Command(BaseCommand):
    """
      Fills the search indexes with indicator name and country name.
  
      TODO - 2017-11-21
      this has to loop over all the lines so its slow, this is due to the country__name that's in another model
      one way to optimize this is adding the country name to the IndicatorDatapoint model and than doing this:
      IndicatorDatapoint.objects.update(search_vector_text=vector)
    """
    def handle(self, *args, **options):
      update_all_unset()
