#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# Created By  : Voltaire Vergara
# Created Date: 7/6/2019
# =============================================================================
"""
The aim of this file is to reproduce the population data that is indicated in the document, Buffalo Turning the corner,
for the neighborhood, Ellicott Neighborhood.
Once reproduced, all the data will be turned into csv files for visualization
"""
import csv
import requests
from itertools import zip_longest
# =============================================================================
api_key = '29a7a4c8e02a8284f63e32523530ee0237fc03cc'  # API key
# The parameters are set to have my API key and the geography level down to the block level of Ellicott neighborhood
parameters = {"key": api_key, "for": "block group:1,2,4", "in": "state:36+county:029+tract:001402"}
num_blocks = 3
api_base_url = lambda acs_year: 'https://api.census.gov/data/' + acs_year + '/acs/acs5?'  # API call link
# ==============================================================================


def get_total_var_data(var_code, year):
    """
    takes in a variable and finds the original base of that variable.
    For example if the variable is the total of
    african american population, then it will return the variable code: total population of that area including all race
    :param var_code: original variable code
    :param year: year of that variable
    :return: Total variable code
    """
    if isinstance(var_code, list):
        new_var_code = var_code[0][:-3]
    else:
        new_var_code = var_code[:-3]
    new_var_code = new_var_code + "01E"
    return update_response_parameters(dict_param={"get": new_var_code}, base_url=api_base_url(str(year)))


def update_response_parameters(dict_param, base_url): # returns response
    """
    updates the parameters of api request to grab any variable that is needed
    :param dict_param: a dictionary that contains all the geographic and variable parameters
    :param base_url: the base url to call the api from
    :return: returns a json of all the data from the api request with the specific parameters
    """
    parameters.update(dict_param)

    # complications with acs api
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x86) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132'}
    response = requests.get(url=base_url, params=parameters, headers=header)

    response.raise_for_status()
    return response.json()

def main():

    # these are the variables needed for the gentrification early warning system
    variables = {"Total population": "B01003_001E",
                 # race
                 "Total number of person(only Black or African American)": "B02001_003E",
                 "Total number of person(only White)": "B02001_002E",
                 "Total number of person(only Hisapnic)": "B03002_012E",
                 # household type
                 "Total Number of Occupied Housing Units": "B25003_001E",
                 "Total Number of Renter per housing unit": "B25003_003E",
                 "Total Number of Owner per housing unit": "B25003_002E",
                 "Total Number of Housing Units": "B25001_001E",
                 "Total Number of Vacant Housing Units": "B25002_003E",

                 # poverty ...... to get total u subtract the last part yes?
                 "Total Population for whom poverty status is determined" : "C17002_001E",
                 "Total below povery line (population whose poverty level is determined)": ["C17002_002E", "C17002_003E"],
                 # gross rent as income
                 "Total Median Gross Rent As A Percentage Of Household Income In The Past 12 Months (Dollars)":
                                                                                                        "B25071_001E",
                 # educational attainment
                 "Total Population that is 25 years and older ": "B15003_001E",
                 "Total Population 25 years and older that have less than a college education":
                        ["B15003_0" + str(i).zfill(2) + "E" for i in range(2, 19)],

                 # rent/housing price

                 "Total Median contract rent (DOLLARS)": "B25058_001E",
                 "Total Median Housing values (DOLLARS)": "B25077_001E"}   # / Owner occupied housing units

    # This calculates the percentages on a block level , then puts them into a csv file
    for years in range(2013,2018):
        with open('Gentrification_data/UBgentrification_data-' + str(years) + '.csv', mode='w', newline= '') as data:
            data_writer = csv.writer(data, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
            # headers
            year_list = ["Year"]
            [year_list.append(years) for _ in range(0, num_blocks)]
            block_list = ["Block"]
            tract_list = ["Tract"]
            var_list = []

            year = years

            for var_title, var_code in variables.items():
                data_list = [] # this is for variables that needed accumulation of data

                # calculates whether there are multiple variables that needed to be added to get the whole percentage
                if isinstance(var_code, list):  # checks if the pair is a list
                    data_list = [0] * num_blocks  # initializes the array to zero so that it can accumulate totals
                    for codes in var_code:
                        json_data = update_response_parameters(dict_param={"get": codes}, base_url=api_base_url(str(year)))
                        for block_count in range(1, len(json_data)):  # it starts at 1 because that's after the header
                            data_list[block_count-1] += int(json_data[block_count][0])
                else:
                    json_data = update_response_parameters(dict_param={"get": var_code}, base_url=api_base_url(str(year)))

                var_data = [var_title]  # the is inside the for loop since it needs to keep adding variables onto the header
                perc_data = ["Percent " + var_title[6:]] if var_code[-3:] != "01E" else None
                for block in range(1, len(json_data)):

                    if json_data[block][0] is not None:
                        var_data.append(float(json_data[block][0]) if len(data_list) == 0 else float(data_list[block-1]))
                        percent_data = round((float(var_data[len(var_data)-1])
                                             / float(get_total_var_data(var_code, year)[block][0])) * 100, 2)
                    else: perc_data = None
                    if perc_data is not None:
                        perc_data.append(percent_data)
                    tract_list.append(json_data[block][3]) if len(tract_list) <= num_blocks else None
                    block_list.append(json_data[block][4]) if len(block_list) <= num_blocks else None # !! THESE ARE ONLY ADDED CUZ THERES NO YEARS

                var_list.append(var_data)
                if perc_data is not None:
                    var_list.append(perc_data)
            result = zip_longest(year_list,tract_list, block_list, *var_list, fillvalue='None')
            data_writer.writerows(result)
            data.close()

  #  print(list(result), sep = '\n')


if __name__ == '__main__':
    main()
