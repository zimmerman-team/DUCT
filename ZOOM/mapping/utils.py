from metadata.models import FileSource
from indicator.models import Indicator
from geodata.models import COUNTRY_RELATION_TYPES


def update_country_on_indicator(file_source=FileSource):
    # Get indicator from file source
    indicator = Indicator.objects.get(file_source=file_source)

    # Get first data pint to check an geelocation on it
    data_point = indicator.datapoints_set.first()
    if data_point:
        # Check if type of the geolocation is postcode, province, country, etc.
        geolocation = data_point.geolocation

        # All COUNTRY_RELATION_TYPES
        if geolocation.type in COUNTRY_RELATION_TYPES:
            # Save the relation country of the geolocation
            country = geolocation.content_object.country

            if country:
                indicator.country = country
                indicator.save()
