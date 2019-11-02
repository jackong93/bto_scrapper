import requests

from bs4 import BeautifulSoup
from lxml import etree


URL = "https://services2.hdb.gov.sg/webapp/BP13AWFlatAvail/BP13EBSFlatSearch"
params = {
    "Town": "Punggol",
    "Flat_Type": "BTO",
    "selectedTown": "Punggol",
    "Flat": "5-Room",
    "ethnic": "Y",
    "ViewOption": "A",
    "projName": "A",
    "Block": "436A",
    "DesType": "A",
    "EthnicA": "Y",
    "EthnicM": "",
    "EthnicC": "",
    "EthnicO": "",
    "numSPR": "",
    "dteBallot": "201909",
    "Neighbourhood": "S4",
    "Contract": "C11",
    "BonusFlats1": "N",
    "searchDetails": "",
    "brochure": "true",
}

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/39.0.2171.95 Safari/537.36"
    )
}

response = requests.get(URL, headers=headers, params=params)

htmlparser = etree.HTMLParser()
tree = etree.HTML(response.text, htmlparser)
print(tree.xpath("//*[@id=\"blockDetails\"]/div[6]"))
