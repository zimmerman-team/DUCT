import json
import math
import os
import sys

import numpy as np
import pandas as pd
from django.test import Client, RequestFactory
from rest_framework.test import APIClient

URL = "http://127.0.0.1:8000/api/"
WB = "World_Bank"
CRS = "CRS"
DEFAULT_INDICATOR_COLUMN = "indicator"
file_dict = {
    WB: {
        "tag": WB,
        "source": WB,
        "description": "Indicator data from WB (upload done through automation).",
        "mapping": {
            'indicator': [DEFAULT_INDICATOR_COLUMN],
            'unit_of_measure': [],
            'relationship': {
                '2003': 'date_value',
                '1997': 'date_value',
                '1988': 'date_value',
                '1989': 'date_value',
                '1986': 'date_value',
                '1987': 'date_value',
                '1984': 'date_value',
                '1985': 'date_value',
                '1968': 'date_value',
                '1969': 'date_value',
                '1980': 'date_value',
                '1981': 'date_value',
                '1964': 'date_value',
                '1965': 'date_value',
                '1966': 'date_value',
                '1967': 'date_value',
                '1960': 'date_value',
                '1961': 'date_value',
                '1962': 'date_value',
                '1963': 'date_value',
                '1996': 'date_value',
                '2014': 'date_value',
                '2017': 'date_value',
                '2016': 'date_value',
                '2011': 'date_value',
                '2010': 'date_value',
                '2013': 'date_value',
                '2012': 'date_value',
                '2005': 'date_value',
                '2015': 'date_value',
                '1982': 'date_value',
                '1983': 'date_value',
                '1991': 'date_value',
                '1990': 'date_value',
                '1993': 'date_value',
                '1992': 'date_value',
                '1995': 'date_value',
                '1994': 'date_value',
                '1979': 'date_value',
                '1978': 'date_value',
                '1977': 'date_value',
                '1976': 'date_value',
                '1975': 'date_value',
                '1974': 'date_value',
                '1973': 'date_value',
                '1972': 'date_value',
                '1971': 'date_value',
                '1970': 'date_value',
                '2002': 'date_value',
                '1999': 'date_value',
                '2000': 'date_value',
                '2001': 'date_value',
                '2006': 'date_value',
                '2007': 'date_value',
                '2004': 'date_value',
                '1998': 'date_value',
                '2008': 'date_value',
                '2009': 'date_value'
            },
            'left_over': {'2003': 'measure_value', '1997': 'measure_value', '1988': 'measure_value',
                          '1989': 'measure_value', '1986': 'measure_value', '1987': 'measure_value',
                          '1984': 'measure_value', '1985': 'measure_value', '1968': 'measure_value',
                          '1969': 'measure_value', '1980': 'measure_value', '1981': 'measure_value',
                          '1964': 'measure_value', '1965': 'measure_value', '1966': 'measure_value',
                          '1967': 'measure_value', '1960': 'measure_value', '1961': 'measure_value',
                          '1962': 'measure_value', '1963': 'measure_value', '1996': 'measure_value',
                          '2014': 'measure_value', '2017': 'measure_value', '2016': 'measure_value',
                          '2011': 'measure_value', '2010': 'measure_value', '2013': 'measure_value',
                          '2012': 'measure_value', '2005': 'measure_value', '2015': 'measure_value',
                          '1982': 'measure_value', '1983': 'measure_value', '1991': 'measure_value',
                          '1990': 'measure_value', '1993': 'measure_value', '1992': 'measure_value',
                          '1995': 'measure_value', '1994': 'measure_value', '1979': 'measure_value',
                          '1978': 'measure_value', '1977': 'measure_value', '1976': 'measure_value',
                          '1975': 'measure_value', '1974': 'measure_value', '1973': 'measure_value',
                          '1972': 'measure_value', '1971': 'measure_value', '1970': 'measure_value',
                          '2002': 'measure_value', '1999': 'measure_value', '2000': 'measure_value',
                          '2001': 'measure_value', '2006': 'measure_value', '2007': 'measure_value',
                          '2004': 'measure_value', '1998': 'measure_value', '2008': 'measure_value',
                          '2009': 'measure_value'},
            'country': ['Country Code'],
            'empty_indicator': 'test',
            'measure_value': ['1960', '1961', '1962', '1963', '1964', '1965', '1966',
                              '1967', '1968', '1969', '1970', '1971', '1972', '1973',
                              '1974', '1975', '1976', '1977', '1978', '1979', '1980',
                              '1981', '1982', '1983', '1984', '1985', '1986', '1987',
                              '1988', '1989', '1990', '1992', '1991', '1993', '1994',
                              '1995', '1996', '1997', '1998', '1999', '2000', '2001',
                              '2002', '2003', '2004', '2005', '2006', '2007', '2008',
                              '2009', '2010', '2011', '2012', '2013', '2014', '2015',
                              '2016', '2017'],
            'date_value': ['1960', '1961', '1962',
                           '1963', '1964', '1965', '1966', '1967', '1968', '1969',
                           '1970', '1971', '1972', '1973', '1974', '1975', '1976',
                           '1977', '1978', '1979', '1980', '1981', '1982', '1983',
                           '1984', '1985', '1986', '1987', '1988', '1989', '1990',
                           '1991', '1992', '1993', '1994', '1995', '1996', '1997',
                           '1998', '1999', '2000', '2001', '2002', '2003', '2004',
                           '2005', '2006', '2007', '2008', '2009', '2010', '2011',
                           '2012', '2013', '2014', '2015', '2016', '2017'],
            'source': [],
            'other': [],
            'indicator_filter': ['Indicator Name'],
            'empty_unit_of_measure': {'2003': 'Number', '1997': 'Number', '1988': 'Number', '1989': 'Number',
                                      '1986': 'Number', '1987': 'Number', '1984': 'Number', '1985': 'Number',
                                      '1968': 'Number', '1969': 'Number', '1980': 'Number', '1981': 'Number',
                                      '1964': 'Number', '1965': 'Number', '1966': 'Number', '1967': 'Number',
                                      '1960': 'Number', '1961': 'Number', '1962': 'Number', '1963': 'Number',
                                      '1996': 'Number', '2014': 'Number', '2017': 'Number', '2016': 'Number',
                                      '2011': 'Number', '2010': 'Number', '2013': 'Number', '2012': 'Number',
                                      '2005': 'Number', '2015': 'Number', '1982': 'Number', '1983': 'Number',
                                      '1991': 'Number', '1990': 'Number', '1993': 'Number', '1992': 'Number',
                                      '1995': 'Number', '1994': 'Number', '1979': 'Number', '1978': 'Number',
                                      '1977': 'Number', '1976': 'Number', '1975': 'Number', '1974': 'Number',
                                      '1973': 'Number', '1972': 'Number', '1971': 'Number', '1970': 'Number',
                                      '2002': 'Number', '1999': 'Number', '2000': 'Number', '2001': 'Number',
                                      '2006': 'Number', '2007': 'Number', '2004': 'Number', '1998': 'Number',
                                      '2008': 'Number', '2009': 'Number'}
        },
        "input_path": "../scripts/formatters/" + WB + "/input/",
        "output_path": "../scripts/formatters/" + WB + "/output/",
        "conversion": "../scripts/formatters/" + WB + "/",
        "columns": [
            DEFAULT_INDICATOR_COLUMN,
            "Indicator Name",
            "Country Code",
            "1960",
            "1961",
            "1962",
            "1963",
            "1964",
            "1965",
            "1966",
            "1967",
            "1968",
            "1969",
            "1970",
            "1971",
            "1972",
            "1973",
            "1974",
            "1975",
            "1976",
            "1977",
            "1978",
            "1979",
            "1980",
            "1981",
            "1982",
            "1983",
            "1984",
            "1985",
            "1986", "1987", "1988", "1989", "1990", "1991", "1992", "1993", "1994", "1995", "1996",
            "1997", "1998", "1999", "2000", "2001", "2002", "2003", "2004", "2005", "2006", "2007",
            "2008", "2009", "2010", "2011", "2012", "2013", "2014", "2015", "2016", "2017"
        ]
    },
    CRS: {
        "tag": CRS,
        "source": CRS,
        "description": "Aggregated CRS from OECD (upload done through automation).",
        "mapping": {
            'indicator': ['Flow Name'],
            'unit_of_measure': [],
            'relationship': {
                'Commitments Defl': 'indicator_category',
                'Disbursements': 'indicator_category',
                'Disbursements Defl': 'indicator_category',
                'Commitments': 'indicator_category'},
            'left_over': {
                'Commitments Defl': 'measure_value',
                'Disbursements': 'measure_value',
                'Disbursements Defl': 'measure_value',
                'Commitments': 'measure_value'},
            'country': ['Recipient'],
            'measure_value': ['Currency', 'Commitments', 'Disbursements', 'Commitments Defl', 'Disbursements Defl'],
            'date_value': ['Year'],
            'source': [],
            'other': [],
            'indicator_filter': ['Sector', 'Aid Type', 'Income Group', 'Purpose', 'Donor', 'Finance Type',
                                 'Commitments', 'Disbursements', 'Commitments Defl', 'Disbursements Defl'],
            'empty_unit_of_measure': {'Currency': 'Number', 'Disbursements': 'Number', 'Disbursements Defl': 'Number',
                                      'Commitments': 'Number', 'Commitments Defl': 'Number'}
        },
        "input_path": "../scripts/formatters/" + CRS + "/input/",
        "output_path": "../scripts/formatters/" + CRS + "/output/",
        "conversion": "../scripts/formatters/" + CRS + "/",
        "columns": [
            "Year",
            "DonorName",
            "RecipientName",
            "IncomegroupName",
            "FlowName",
            "Finance_t",
            "Aid_t",
            "usd_commitment",
            "usd_disbursement",
            "usd_commitment_defl",
            "usd_disbursement_defl",
            "CurrencyCode",
            "PurposeName",
            "SectorName"
        ],
        "nice_name": {
            "Year": "Year",
            "DonorName": "Donor",
            "RecipientName": "Recipient",
            "IncomegroupName": "Income Group",
            "FlowName": "Flow Name",
            "Finance_t": "Finance Type",
            "Aid_t": "Aid Type",
            "usd_commitment": "Commitments",
            "usd_disbursement": "Disbursements",
            "usd_commitment_defl": "Commitments Defl",
            "usd_disbursement_defl": "Disbursements Defl",
            "CurrencyCode": "Currency",
            "PurposeName": "Purpose",
            "SectorName": "Sector"
        },
        "measure_value": ["Commitments", "Disbursements", "Commitments Defl", "Disbursements Defl"]
    }
}

file_list = [WB, CRS]
character_sep = {WB: ",", CRS: "|"}


def add_external_data():
    global character_sep
    checked = False
    file_choice = CRS  # WB#CRS #temp
    # file_choice = ""
    """print("Enter one of the following: ", file_list)
                print("e for escape")
                while(not checked):
                    #try:
                    file_choice = input("Enter data desired from above:")
                    if(file_choice in file_list):
                        checked = True
                    elif(file_choice == "e"):
                        sys.exit()
                    #except EOFError:
                    #    error = ""
    """

    convert_data(file_choice)
    if (file_choice == CRS):
        flatten_data(file_choice)
    checkIfFilesTooBig(file_choice)
    start_mapping(file_choice)


def start_mapping(file_choice):
    global file_list, file_dict
    path = file_dict[file_choice]["output_path"]
    file_list = os.listdir(path)
    counter = 0
    request_dummy = RequestFactory().get('/')
    c = APIClient()

    for file_name in file_list:
        headers = {'Content-type': 'multipart/form-data'}
        with open(path + file_name, 'rb') as fp:
            res_file_upload = c.post(
                URL + 'file/?format=json',
                {
                    'file': fp,
                    'title': file_name,
                    'description': (file_name + " " + file_dict[file_choice]["description"]),
                    'file_name': file_name
                })
        print("Upload file: ", res_file_upload)

        headers = {'content-type': 'application/json'}
        patch_data = {
            'title': file_name,
            'description': file_name + " " + file_dict[file_choice]["description"],
            'file_name': file_name,
            "data_source": file_choice,
            "authorised": 1,
            "status": 1
        }

        id = res_file_upload.json()['id']
        print('id ', id)
        res = requests.patch(
            URL + 'file/{}/?format=json'.format(id),
            headers=headers,
            data=(json.dumps(patch_data))
        )  # """"""
        print("Update file: ", res)

        res = c.post(
            URL + 'validate/?format=json',
            {
                "id": id
            }, format='json')
        print("Validation: ", res)

        res = c.post(
            URL + 'manual-mapper/?format=json',
            {
                "id": id,
                "dict": file_dict[file_choice]['mapping']
            }, format='json')
        print("Mapping: ", res)

        res = c.post(
            URL + 'file/update_status/?format=json',
            {
                "id": id,
                "status": 5
            })
        print("Status: ", res.json())


def checkIfFilesTooBig(file_choice):
    global file_list, file_dict
    SPLIT_SIZE = 5500000
    path = file_dict[file_choice]["output_path"]
    file_list = os.listdir(path)
    counter = 0

    for file_name in file_list:
        size = os.path.getsize(path + file_name)
        if (size > SPLIT_SIZE):  # over 5.5mb split
            data = pd.read_csv(path + file_name, sep=character_sep[file_choice])
            print("Size of file: ", size)
            split_range = int(math.ceil(size / SPLIT_SIZE))
            data_split = np.array_split(data, split_range)
            for i in range(split_range):
                data_split[i].to_csv(
                    file_dict[file_choice]["output_path"] + file_name[:-4] + "(" + str(i) + ")" + ".csv", sep=',',
                    index=False)
            os.remove(path + file_name)

            print("Split file: ", split_range)


def convert_data(file_choice):
    global character_sep, file_dict
    file_list = os.listdir(file_dict[file_choice]["input_path"])
    counter = 0
    # get files in folder
    print("Begining Conversion")

    for file_name in file_list:
        print('File being converted: ', file_dict[file_choice]["input_path"] + file_name)
        data = pd.read_csv(file_dict[file_choice]["input_path"] + file_name, sep=character_sep[file_choice])
        rm_cols = filter(lambda k: 'Unnamed:' in k, data.columns)
        data.drop(columns=rm_cols, inplace=True)

        if file_choice == WB:
            data[DEFAULT_INDICATOR_COLUMN] = data[data.columns[0]]
            data[DEFAULT_INDICATOR_COLUMN] = file_name[:-4]
            data = data.iloc[4:]  # remove first 4 rows
        data = data[file_dict[file_choice]["columns"]]
        if "nice_name" in file_dict[file_choice]:
            data.rename(columns=file_dict[file_choice]["nice_name"], inplace=True)
        ##check column width and size an split accoringly
        data.to_csv(file_dict[file_choice]["output_path"] + file_name[:-4] + ".csv", sep=',', index=False)
        sys.stdout.write("\r%d%%" % ((counter / len(file_list)) * 100))

    sys.stdout.flush()
    # print("All files converted")


def flatten_data(file_choice):
    global character_sep, file_dict
    file_list = os.listdir(file_dict[file_choice]["output_path"])
    measure_values = file_dict[file_choice]["measure_value"]
    counter = 0
    columns = list(file_dict[file_choice]["nice_name"].values())
    columns = list(set(columns) - set(measure_values))
    aid_t_conv = pd.read_csv(file_dict[file_choice]["conversion"] + "aid_types.csv")
    aid_t_conv = pd.Series(aid_t_conv.Name.values, index=aid_t_conv.Code).to_dict()
    currency_t_conv = pd.read_csv(file_dict[file_choice]["conversion"] + "currency_types.csv")
    currency_t_conv = pd.Series(currency_t_conv.Name.values, index=currency_t_conv.Code).to_dict()
    finance_t_conv = pd.read_csv(file_dict[file_choice]["conversion"] + "finance_types.csv")
    finance_t_conv = pd.Series(finance_t_conv.Name.values, index=finance_t_conv.Code).to_dict()

    print("Begining Conversion")

    for file_name in file_list:
        print(file_dict[file_choice]["output_path"] + file_name)
        data = pd.read_csv(file_dict[file_choice]["output_path"] + file_name)
        data.fillna(value=0, inplace=True)
        data["Aid Type"] = data["Aid Type"].map(aid_t_conv)
        data["Finance Type"] = data["Finance Type"].map(finance_t_conv)
        data["Currency"] = data["Currency"].map(currency_t_conv)
        series_list = []

        for measure_value in measure_values:
            tmp = data.groupby(columns)[measure_value].sum()
            series_list.append(tmp)
        data = pd.concat(series_list, axis=1).reset_index()
        data.to_csv(file_dict[file_choice]["output_path"] + file_name[:-4] + ".csv", sep=',', index=False)
        sys.stdout.write("\r %d%%" % ((counter / len(file_list)) * 100))

    sys.stdout.flush()


def mapping(mapping_dict, file):
    print("Begining Mapping ", file)

    print("Finished Mapping ", file)
