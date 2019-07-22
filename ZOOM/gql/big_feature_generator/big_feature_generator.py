import ast
import time
import sys
import math
from multiprocessing import Process, Manager, cpu_count
import pydash
import datetime
datetime.datetime.now()


# so the main purpose of this class is to use multiprocessing to increase the geojson processing
# of huge amounts of data, if the data amount passed in here is not huge,
# the process_amount should be set to one as then it will just work as a simple one off function
# if the data IS big then the process amount should be passed in depending on your requirement
# best is to use one process for 10000 - 20000 data items, and of course this process amount
# is very much dependant on the machines specs, use too much -> its gonna be slower
# use too little -> it could be faster
class BigFeatureGenerator:

    def __init__(self, all_results, result_count,  process_amount=1):
        max_cpu = cpu_count() - 1 if cpu_count() > 1 else 1
        self.features = []
        self.existing_geolocations = []
        self.max_value = -sys.maxsize - 1
        self.min_value = sys.maxsize
        # so we don't want the specified process amount to exceed or be equal
        # to the max cpu count on this machine(at least one cpu should remain for any
        # other tasks)
        self.process_amount = process_amount if process_amount <= cpu_count() else max_cpu
        self.all_results = all_results
        self.result_count = result_count

    def geo_data_process(self, results, process_number, return_dict):
        number_of_processed = 0
        local_min_value = sys.maxsize
        local_max_value = -sys.maxsize - 1
        features = []
        for result in results:
            if 'geolocation__polygons' in result and result['geolocation__polygons'] is not None:

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

                features.append({
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

        return_dict[process_number] = {
            "features": features,
            "min_value": local_min_value,
            "max_value": local_max_value
        }

    def generate_features(self):
        processes = []
        batch_start = 0
        batch_size = math.ceil(self.result_count/self.process_amount)

        manager = Manager()
        return_dict = manager.dict()

        start_time = time.time()

        print('proccesors used: ', self.process_amount)

        # we start the processes
        for i in range(0, self.process_amount):
            batch_end = batch_start+batch_size
            batch_end = batch_end if batch_end < self.result_count else self.result_count
            curr_results = list(self.all_results[batch_start:batch_end])
            processes.append(Process(target=self.geo_data_process, args=(curr_results, i, return_dict)))
            processes[-1].start()
            batch_start += batch_size

        # we join the processes
        for process in processes:
            """
            Waits for processes to complete before moving on with the main
            script.
            """
            process.join()

        generated_items = return_dict.values()

        # and here we get the overall min and max values
        # generated by each process from their used batch's
        for item in generated_items:
            if self.max_value < item['max_value']:
                self.max_value = item['max_value']
            if self.min_value > item['min_value']:
                self.min_value = item['min_value']
            self.features += item['features']

        end_time = time.time()

        if self.result_count > 40000:
            print('[', datetime.datetime.now(), ']')
            print('Processors used: ', self.process_amount)
            print('Time it took to process geojson with ',
                  self.result_count, ' records in it: ', end_time - start_time)

        # and we return features
        return self.features
