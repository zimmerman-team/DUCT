import csv

from geodata.models import Geolocation


class CheckGeolocation(object):
    file = None
    column_number = None

    def __init__(self, file, column_number):
        self.file = file
        self.column_number = column_number

    def check(self):
        valid = 0
        invalid = 0
        invalid_tags = []
        with open(self.file) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            next(csv_reader, None)
            for row in csv_reader:
                tag = row[self.column_number].lower()
                try:
                    Geolocation.objects.get(tag=tag)
                    valid = valid + 1
                    print('{tag} is valid. Valid is {valid}'.format(
                        tag=tag, valid=valid))
                except Geolocation.DoesNotExist:
                    invalid_tags.append(tag)
                    invalid = invalid + 1
                    print('{tag} is invalid. Invalid is {invalid}'.format(
                        tag=tag, invalid=invalid))

        print('Total valid {valid} and invalid {invalid}'.format(
            valid=valid, invalid=invalid))

        print('Invalid tags: {tags}'.format(tags=','.join(invalid_tags)))
