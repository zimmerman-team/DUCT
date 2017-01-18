import strict_rfc3339
import datetime
from functools import wraps  # use this to preserve function signatures and docstrings
import pandas as pd

def ignore_errors(f):
    @wraps(f)
    def ignore(json_data, ignore_errors=False):
        if ignore_errors:
            try:
                return f(json_data)
            except (KeyError, TypeError, IndexError, AttributeError):
                return {}
        else:
            return f(json_data)
    return ignore


def to_list(item):
    if isinstance(item, list):
        return item
    return [item]


def get_no_exception(item, key, fallback):
    try:
        return item.get(key, fallback)
    except AttributeError:
        return fallback


def update_docs(document_parent, counter):
    count = 0
    documents = document_parent.get('documents', [])
    for document in documents:
        count += 1
        doc_type = document.get("documentType")
        if doc_type:
            counter.update([doc_type])
    return count


def datetime_or_date(instance):
    result = strict_rfc3339.validate_rfc3339(instance)
    if result:
        return result
    return datetime.datetime.strptime(instance, "%Y-%m-%d")

#serach for columns that map together, look for specific vlaues such as time
def serach_for_columns():
    return 0

def check_column_data(column1, column2):
    type1 = column1.dtypes
    type2 = column2.dtypes

    return (type1 == type2), str(type1), str(type2)
    

    #check dtypes of column 1 and column 2
    #if different return false
    #identify column against predefined data structure eg iso
    #if heading is clear and data structure for column is known check corresponding column
        #check for incorrect values #iso codes, coutry names
    #if column is a sum change is or highlight it
    
