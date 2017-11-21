from django.contrib.postgres.search import SearchVector
from indicator.models import IndicatorDatapoint


def update_all_unset():
  vector=SearchVector('indicator', weight='A') + SearchVector('country__name', weight='B')
  count = 0

  for datapoint in IndicatorDatapoint.objects.filter(search_vector_text=None).prefetch_related("country").annotate(vector_text=vector):
      datapoint.search_vector_text = datapoint.vector_text
      datapoint.save(update_fields=['search_vector_text'])
      count += 1
      if count % 1000 == 0:
        print count


# def update_search_vectors_for_added_dataset():
