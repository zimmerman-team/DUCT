from django.core.management.base import BaseCommand
from django.contrib.postgres.search import SearchVector
from indicator.models import IndicatorDatapoint


class Command(BaseCommand):
    """
      Fills the search indexes with indicator name and country name.
  
      TODO - 2017-11-21
      this has to loop over all the lines so its slow, this is due to the country__name that's in another model
      one way to optimize this is adding the country name to the IndicatorDatapoint model and than doing this:
      IndicatorDatapoint.objects.update(search_vector_text=vector)
    """
    def handle(self, *args, **options):
      vector=SearchVector('indicator', weight='A') + SearchVector('country__name', weight='B')
      count = 0
      for datapoint in IndicatorDatapoint.objects.filter(search_vector_text=None).prefetch_related("country").annotate(vector_text=vector):
          datapoint.search_vector_text = datapoint.vector_text
          datapoint.save(update_fields=['search_vector_text'])
          count += 1
          if count % 1000 == 0:
            break
