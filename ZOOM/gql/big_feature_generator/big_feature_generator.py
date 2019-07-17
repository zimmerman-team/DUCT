import ast
import time
import sys
import math
from threading import Thread
import pydash


# so the main purpose of this class is to use threads to increase the geojson processing
# of huge amounts of data, if the data amount passed in here is not huge,
# the thread_amount should be set to one as then it will just work as a simple one off function
# if the data IS big then the thread amount should be passed in depending on your requirement
# best is to use one thread for 10000 - 20000 data items, and of course this thread amount
# is very much dependant on the machines specs, use too much -> its gonna be slower
# use too little -> it could be faster
class BigFeatureGenerator:

    def __init__(self, all_results, result_count,  thread_amount=1):
        self.features = []
        self.existing_geolocations = []
        self.max_value = -sys.maxsize - 1
        self.min_value = sys.maxsize
        self.min_max_array = []
        self.thread_amount = thread_amount
        self.all_results = all_results
        self.result_count = result_count

    def geo_data_process_thread(self, results, thread_number):
        print('START ', thread_number)
        number_of_processed = 0
        local_min_value = sys.maxsize
        local_max_value = -sys.maxsize - 1
        for result in results:
            if result['geolocation__polygons'] is not None:

                print('MY NUMBER: ', thread_number, 'ITEMS PROCESSED: ', number_of_processed)
                value_format = result['value_format__type'][0] if \
                    isinstance(result['value_format__type'], list) else result['value_format__type']

                tool_tip_labels = []
                # so if values are a list that means that the data
                # is being dissagregated by sub-indicators(filters)
                # so we need to form the tooltipLabels accordingly
                if isinstance(result['value'], list):
                    # Note: the filters will also be a list if the values are
                    # a list in this scenario
                    for index, filter_name in enumerate(result['filters__name']):
                        existing_filter_index = pydash.arrays.find_index(
                            tool_tip_labels, lambda tool_tip: tool_tip['subIndName'] == filter_name)

                        if existing_filter_index != -1:
                            # so if the filter name already exists in a tooltip
                            # we add the parallel value to that tooltip item
                            tool_tip_labels[existing_filter_index]['value'] += result['value'][index]
                        else:
                            label = result['indicator__name'] + ' - ' + filter_name
                            # otherwise we push in a new tooltip item
                            tool_tip_labels.append({
                                "subIndName": filter_name,
                                "format": result['value_format__type'][index],
                                "label": label,
                                "value": result['value'][index]
                            })
                else:
                    filter_string = result['filters__name'] if isinstance(result['filters__name'], str) else \
                        ', '.join(result['filters__name'])
                    label = result['indicator__name'] + ' - ' + filter_string

                    # so if values are NOT a list that means that data
                    # IS Aggregated by sub-indicators(filters)
                    # meaning there will only be one tooltip item
                    # with datapoint values summed up
                    tool_tip_labels.append({
                        "subIndName": filter_string,
                        "format": value_format,
                        "label": label,
                        "value": result['value']
                    })

                sum_value = sum(result['value']) if isinstance(result['value'], list) else result['value']

                if local_max_value < sum_value:
                    local_max_value = sum_value
                if local_min_value > sum_value:
                    local_min_value = sum_value

                self.features.append({
                    "geometry": ast.literal_eval(result['geolocation__polygons'].json),
                    "properties": {
                        "indName": result['indicator__name'],
                        "name": result['geolocation__tag'],
                        "iso2": result['geolocation__iso2'],
                        "geolocationType": result['geolocation__type'],
                        "value": sum_value,
                        "format": value_format,
                        "percentile": 0,
                        "tooltipLabels": tool_tip_labels,
                    }
                }
                )

            number_of_processed += 1

        self.min_max_array.append({
            "min_value": local_min_value,
            "max_value": local_max_value
        })

    def generate_features(self):
        threads = []
        batch_start = 0
        batch_size = math.ceil(self.result_count/self.thread_amount)

        start_time = time.time()

        # we start the threads
        for i in range(0, self.thread_amount):
            batch_end = batch_start+batch_size
            batch_end = batch_end if batch_end < self.result_count else self.result_count
            curr_results = self.all_results[batch_start:batch_end]
            threads.append(Thread(target=self.geo_data_process_thread, args=(curr_results, i)))
            threads[-1].start()
            batch_start += batch_size

        # we join the threads
        for thread in threads:
            """
            Waits for threads to complete before moving on with the main
            script.
            """
            thread.join()

        # and here we get the overall min and max values
        # generated by each thread from their used batch's
        for item in self.min_max_array:
            if self.max_value < item['max_value']:
                self.max_value = item['max_value']
            if self.min_value > item['min_value']:
                self.min_value = item['min_value']

        end_time = time.time()

        print('Time it took to process geojson with ',
              self.thread_amount, ' threads: ', end_time-start_time)

        # and we return features
        return self.features
