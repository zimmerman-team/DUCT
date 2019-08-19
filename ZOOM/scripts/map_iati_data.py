# So yeah this script at least at its current state
# turns aidsfonds iati data into a DUCT dataset and maps it out
# it works with the /transactions/aggregations/ end point and
# creates 'Sector', 'Transactions' & 'Activity Status' indicator
# dataset
import csv
import datetime
import os

import pydash
import requests
from django.conf import settings

from indicator.models import Indicator
from mapping.mapper import begin_mapping
from metadata.models import File, FileSource

oipa_base_url = 'https://yoda.oipa.nl/api/'

iati_indicator_endpoint = 'transactions/aggregations/'

aids_fonds_identifier = 'NL-KVK-41207989'

activity_status_query = oipa_base_url + iati_indicator_endpoint + "?group_by=transaction_date_year,recipient_country," \
                                                                  "activity_status&aggregations=activity_count&format" \
                                                                  "=json&reporting_organisation_identifier=" + \
                        aids_fonds_identifier

sector_query = oipa_base_url + iati_indicator_endpoint + "?aggregations=activity_count&format=json&group_by" \
                                                         "=transaction_date_year,recipient_country," \
                                                         "sector&reporting_organisation_identifier=" + \
               aids_fonds_identifier

transactions_query = oipa_base_url + iati_indicator_endpoint + "?aggregations=value&format=json&group_by" \
                                                               "=transaction_date_year,recipient_country," \
                                                               "transaction_type&reporting_organisation_identifier=" \
                     + aids_fonds_identifier

# with this query we will check if the organisations
# data has been updated in OIPA, meaning if the
# last_updated_datetime has changed, ONLY THEN
# will we remapp the iati dataset
last_updated_query = oipa_base_url + "activities/?fields=last_updated_datetime&page=1&page_size=1&format=json" \
                                     "&reporting_organisation_identifier=" + aids_fonds_identifier

iati_indicator_metadata = [{
    "query": activity_status_query,
    "ind_val": 'Activity Status',
    "filter_place": 'activity_status.name',
    "geo_place": 'recipient_country.code',
    "date_place": 'transaction_date_year',
    "format_val": 'Activities',
    "value_place": 'activity_count'
}, {
    "query": sector_query,
    "ind_val": 'Sector',
    "filter_place": 'sector.name',
    "geo_place": 'recipient_country.code',
    "date_place": 'transaction_date_year',
    "format_val": 'Activities',
    "value_place": 'activity_count'
}, {
    "query": transactions_query,
    "ind_val": 'Transactions',
    "filter_place": 'transaction_type.name',
    "geo_place": 'recipient_country.code',
    "date_place": 'transaction_date_year',
    "format_val": 'EUR',
    "value_place": 'value'
}]


def map_iati_data():
    try:
        # so first we check if OIPA data has been updated
        last_updated_data = requests.get(last_updated_query).json()
        last_updated_time = last_updated_data['results'][0][
            'last_updated_datetime']

        file_source_name = 'AIDSFONDS IATI DATASET'

        dataset_title = file_source_name + last_updated_time

        file_source = FileSource.objects.filter(name=file_source_name)
        map_it = False

        if file_source.count() > 0:
            file_source = file_source.get()
            # we found the file source and then we find the file
            file = File.objects.filter(source=file_source).get()

            # so here we check if the files title is different from the
            # one currently formed, if it is different, that means
            # that the last_updated_time has changed meaning that
            # OIPA data for this IATI/OIPA dataset of ours has changed
            # and we can easily update it, otherwise nothing should be
            # done
            if file.title != dataset_title:
                print(
                    'OIPA DATA HAS BEEN UPDATED, IATI DATASET REMAPPING INITIATED: ',
                    datetime.datetime.now())
                map_it = True
                # then we find the indicators
                indicators = Indicator.objects.filter(file__id=file.id)
                # and now we delete them all
                # NOTE: no need to delete the csv file itself
                # cause it will just be overwritten
                indicators.delete()
                file_source.delete()
                file.delete()
            else:
                print(
                    'OIPA DATA HAS NOT BEEN UPDATED, NOT REMAPPING THE IATI DATASET: ',
                    datetime.datetime.now())
        else:
            print('NEW IATI DATASET BEING MAPPED', datetime.datetime.now())
            map_it = True

        if map_it:
            print('STARTED MAPPING IATI DATA')
            print('TIME:', datetime.datetime.now())

            # creating the file source for the dataset
            file_source = FileSource.objects.create(name=file_source_name)

            full_path_to_dataset = os.path.join(
                os.path.join(settings.MEDIA_ROOT, settings.DATASETS_URL),
                'AIDSFONDS_IATI_DATASET.csv')

            # create and saving the csv file
            with open(full_path_to_dataset, 'w') as writeFile:
                writer = csv.writer(writeFile)
                # we write the headers
                writer.writerow([
                    'Indicator', 'Sub-indicator', 'ISO2', 'Year',
                    'Value Format', 'Value'
                ])
                # and here we retrieve and write the actual values of this dataset
                for iati_ind_item in iati_indicator_metadata:
                    # and here we start forming the dataset
                    # starting from activity status
                    iati_data = requests.get(iati_ind_item['query']).json()

                    for item in iati_data['results']:
                        # so yeah here we form the dataset with values
                        writer.writerow([
                            iati_ind_item['ind_val'],
                            pydash.objects.get(item,
                                               iati_ind_item['filter_place']),
                            pydash.objects.get(item,
                                               iati_ind_item['geo_place']),
                            pydash.objects.get(item,
                                               iati_ind_item['date_place']),
                            iati_ind_item['format_val'],
                            pydash.objects.get(item,
                                               iati_ind_item['value_place'])
                        ])

            writeFile.close()

            # and now out of this file we create the file object
            file_man = File.objects.create(
                title=dataset_title,
                description=dataset_title,
                contains_subnational_data=False,
                organisation='Zimmerman&Zimmerman',
                maintainer='Zimmerman&Zimmerman',
                date_of_dataset=datetime.datetime.now(),
                methodology='Iati',
                define_methodology='Iati',
                update_frequency='Pretty frequent',
                comments='No comments',
                accessibility='a',
                data_quality='best',
                number_of_rows=1,
                file_types='csv',
                source=file_source,
                original_file_location=full_path_to_dataset,
                file_status='1',
                error_file_location='',
                file=full_path_to_dataset)
            # datatypes_overview_file_location

            # so this is gonna be the mapping dict for that
            # iati data
            data = {
                "metadata_id": file_man.id,
                "filter_headings": {
                    "Sub-indicator": "Sub-indicator"
                },
                "extra_information": {
                    "empty_entries": {
                        "empty_indicator": '',
                        "empty_geolocation": {
                            "value": '',
                            "type": ''
                        },
                        "empty_filter": '',
                        "empty_value_format": {},
                        "empty_date": ''
                    },
                    "multi_mapped": {
                        "column_heading": {},
                        "column_values": {}
                    },
                    "point_based_info": {
                        "coord": {
                            "lat": '',
                            "lon": ''
                        },
                        "subnational": '',
                        "country": '',
                        "type": ''
                    }
                },
                "mapping_dict": {
                    "indicator": ['Indicator'],
                    "filters": ['Sub-indicator'],
                    "geolocation": ['ISO2'],
                    "date": ['Year'],
                    "value_format": ['Value Format'],
                    "value": ['Value'],
                    "comment": []
                }
            }

            begin_mapping(data)

            print('MAPPING IATI DATA FINISHED')
            print('TIME:', datetime.datetime.now())

    except Exception as e:
        print('ERROR:', e)
