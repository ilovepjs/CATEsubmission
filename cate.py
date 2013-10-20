import requests
import bs4
import getpass
from bs4 import BeautifulSoup
from requests.auth import HTTPBasicAuth

baseURL = "https://cate.doc.ic.ac.uk/"

#username and password for auth
#TODO:fix this
username = raw_input("Username: ")
password = getpass.getpass("Password: ")
auth = HTTPBasicAuth(username, password)

r = requests.get(baseURL, auth=auth)

soup = BeautifulSoup(r.text)

keyt = soup.find(name="input", attrs={'name': 'keyt'})['value']
klass = soup.find(name="input", attrs={'checked':True, 'name': 'class'})['value']
period = soup.find(name="input", attrs={'checked':True, 'name': 'period'})['value']

payload = {'keyt':keyt, 'class':klass, 'period':period}
r = requests.get("https://cate.doc.ic.ac.uk/timetable.cgi", auth=auth, params=payload)

soup = BeautifulSoup(r.text)

#create a dict between handin page link and lab names
handinURLs = {}
#TODO:clean up code
for line in soup.find_all('td'):
    ls = line.find_all(name="a", attrs={'title':'View exercise specification'})
    for l in ls:
        title = l.string
        lees = line.find_all(name="a", attrs={'href':True})
        for lee in lees:
            if 'handin' in lee['href']:
                handinURLs[title] = lee['href']

#ask user what homework to hand in
#go to that timetable page 
