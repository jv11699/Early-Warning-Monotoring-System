#Author: Jason Yan
#This file is used to extract data from the US Census, which creates a CSV file named "LowerWestSide_Data.csv"

import csv
import json
import requests

#Filter Method
def cleanUpData(list):
    x = []
    jsonList = list.json()

    for data in jsonList:
        if data[3]=="006902" and ("Block Group 2" in data[0] or "Block Group 4" in data[0]):
            x.append(data)
        elif data[3]=="007101":
            x.append(data)
        elif data[3]=="007102" and ("Block Group 2" in data[0] or "Block Group 3" in data[0]):
            x.append(data)
    return x

def cleanUpData2(list):
    x = []
    jsonList = list.json()

    for data in jsonList:
        if data[3]=="006902" and ("2" in data[4] or "4" in data[4]):
            x.append(data)
        elif data[3]=="007101":
            x.append(data)
        elif data[3]=="007102" and ("2" in data[4] or "3" in data[4]):
            x.append(data)
    return x
#Returns a list of codes for education(Age 25 and over + Less than college education)
def returnCodeForEducation():
    list = []
    for i in range(2,10):
        list.append("B15003_00"+str(i)+"E")
    for i in range(10,19):
        list.append("B15003_0"+str(i)+"E")
    return list

#Returns the url based on year
def returnYear(year):
    return 'https://api.census.gov/data/' + str(year)+ '/acs/acs5?'

def parameterBuilder(json, i):
    blockStr = "block group:"+json[i][4]
    locationStr = "state:36+county:029+tract:"+json[i][3]
    parameters.update({"in":locationStr})
                      
def updateGet(code):
    parameters.update({"get":code})
    
def getBG(json, num):
    for data in json:
        if num in data[4]:
            return data
def getPercentage(code,value,i):
    code = code[:-3]
    code = code + "01E"
    updateGet(code)
    num = cleanUpData2(requests.get(returnYear(2016), params=parameters))
    total = getBG(num,blockGroupJson[i][4])[0]
    return str((float(value)/float(total))*100)[:5]
api_key = '84921378aea76df28e22b980926c1621f872d5c1' #API Key
#Lower West Side contains a portion of all block groups in these tracts with no patterns, so we will need to filter our data later
parameters = {"key": api_key, "get":"NAME","for":"block group:*", "in":"state:36+county:029+tract:006902,007101,007102"} 

#Gets Json of Data 
#requests.get(api_base_url, params=parameters).json()
blockGroupJson = cleanUpData(requests.get(returnYear(2016), params=parameters))
#Gets number of block groups in the request
numOfBlockGroups = len(blockGroupJson)

#Dictionary that contains the codes for data we need
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
                 "Total Population 25 years and older that have less than a college education": returnCodeForEducation(),

                 # rent/housing price

                 "Total Median contract rent (DOLLARS)": "B25058_001E",
                 "Total Median Housing values (DOLLARS)": "B25077_001E"}   # / Owner occupied housing units

with open('LowerWestSide_Data.csv', 'w', newline='') as f:
    data_writer = csv.writer(f)
    dataList = []
    print("1")
    header = []
    for i in range(0,numOfBlockGroups):
        dataList.clear()
        parameterBuilder(blockGroupJson,i)
        print(i)
        dataList.append(blockGroupJson[i][3])
        dataList.append(blockGroupJson[i][4])
        header.append("Tract")
        header.append("Block Group")
        for var_title,var_code in variables.items(): #Loops through dictionary
            print(var_title)
            if isinstance(var_code,list):
                num = 0
                for x in var_code:
                    updateGet(x)
                    js = cleanUpData2(requests.get(returnYear(2016), params=parameters))
                    num = num + int(getBG(js,blockGroupJson[i][4])[0])
                dataList.append(str(num))
                if i==0:
                    header.append(var_title)
                percentage = getPercentage(var_code[0],num,i)
                dataList.append(percentage)
                if i==0:
                    header.append("Percent of "+var_title)
            else:
                updateGet(var_code)
                js = cleanUpData2(requests.get(returnYear(2016), params=parameters))
                value = getBG(js,blockGroupJson[i][4])[0]
                dataList.append(value)
                if i==0:
                    header.append(var_title)
                if var_code[8:]!="01E":   
                    percentage = getPercentage(var_code,value,i)
                    dataList.append(percentage)
                    if i==0:
                        header.append("Percent of "+var_title)
                    #print(percentage)
                #print(header)
        if i==0:
            data_writer.writerow(header)
        print(dataList)
        data_writer.writerow(dataList)
f.close()                
