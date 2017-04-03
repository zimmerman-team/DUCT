
from django_filters import Filter, FilterSet
from api.generics.filters import CommaSeparatedCharFilter
from indicator.models import IndicatorDatapoint

class IndicatorDataFilter(FilterSet):

    class Meta:
        model = IndicatorDatapoint
        fields = (
            'id',
            'file_source_id',
            'date_format_id',
            'indicator_category_id',
            'indicator_id',
            'country_id',
            'date_value',
            'source_id',
            'country_id__region',
            'country_id__name',
        )
