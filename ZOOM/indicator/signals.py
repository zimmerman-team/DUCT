from dateutil import parser
from django.db.models import signals
from django.dispatch import receiver

from indicator.models import Datapoints, Indicator


@receiver(signals.pre_save, sender=Indicator)
def indicator_pre_save(sender, instance, **kwargs):
    s_date = str(instance.last_data_year)

    try:
        v_date = parser.parse(s_date)
        # Change the value of last_data_year
        instance.last_data_year = str(v_date.year)

    except ValueError:
        # We only have value error if the value of year is decimal
        # like '2000.0' or '1990.0'

        if len(s_date) == 6:
            # If year like '2000.0' or '1990.1' them remove the decimal value
            v_date = parser.parse(str(int(float(s_date))))
            # Change the value of last_data_year
            instance.last_data_year = str(v_date.year)


@receiver(signals.pre_save, sender=Datapoints)
def datapoints_pre_save(sender, instance, **kwargs):
    s_date = str(instance.date)

    try:
        d_value = parser.parse(s_date)
        # Change the value of last_data_year
        instance.date = str(d_value.year)

    except ValueError:
        # We only have value error if the value of year is decimal
        # like '2000.0' or '1990.0'

        if len(s_date) == 6:
            # If year like '2000.0' or '1990.1' them remove the decimal value
            d_value = parser.parse(str(int(float(s_date))))
            # Change the value of last_data_year
            instance.date = str(d_value.year)
