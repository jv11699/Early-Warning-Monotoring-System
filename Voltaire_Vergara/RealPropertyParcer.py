#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# Created By  : Voltaire Vergara
# Created Date: 11/8/2019
# =============================================================================
"""
The aim of this file is to reproduce a beautiful soup object that contains
the tax history data of an individual through the erie county tax parcel website. Here we use an individiuals
unique SBL to query information
"""

import requests
from bs4 import BeautifulSoup
import urllib.parse as urlparse
from urllib.parse import parse_qs

def grab_source_SBL(sbl,mode= "ecgov"):
    """
    Queries the Real Property Parcer of erie county(Specifically only SBL values), which can be found on this link:
                            http://www2.erie.gov/ecrpts/index.php?q=real-property-parcel-search
    This function will return a beautiful soup object of the source code of a SBL's tax History.
    :param sbl: SBL value that we are searching for
    :return: a Beautiful soup object of the tax extry history of that SBL
    """
    body = {'txtsbl': sbl,  # WE CAN CHANGE THIS TO SBL BUT THIS IS OWNER NAME
            'showHistory': 'y'}
    url2 = 'https://paytax.erie.gov/webprop/'  # url we needed adding to since this is the root link
    url = 'https://paytax.erie.gov/webprop/property_info_results.asp'  # search website
    link = requests.post(url, data=body)
    source_soup = BeautifulSoup(link.content, 'lxml')
    mode = "property_info_history" if mode != "ecgov" else "ecgov"
    for owner in source_soup.find_all('a', href=True):
        parsed = urlparse.urlparse(owner['href'])   # this part is to ensure that it goes through the right SBL link
        if not parsed.query:
            break
        parsed_sbl = parse_qs(parsed.query)['sbl']
        if str(owner['href']).startswith("property_info_details") and len(parsed_sbl) > 0\
                and sbl in str(parsed_sbl[0]):
            con2 = requests.post(url2+owner['href'])
            details_soup = BeautifulSoup(con2.content, 'lxml')
            for a in details_soup.find_all('a', href=True):
                if str(a['href']).startswith(mode):
                    return BeautifulSoup(requests.post(url2 + a['href']).content, 'lxml')
    # if none of them were found then the data does not exist
    return None

print(grab_source_SBL('123.11-1-1.11').prettify())