import requests
import bs4
import getpass
from bs4 import BeautifulSoup
from requests.auth import HTTPBasicAuth

def main():
	baseURL = "https://cate.doc.ic.ac.uk/"

	#username and password for auth
	#TODO:fix this
	username = raw_input("Username: ")
	password = getpass.getpass("Password: ")

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
	location = 0
	print 'Which [assignment] would you like to hand in?'
	for key in handinURLs.keys():
		print '[' + str(location) + ']\t' + key
		location += 1

	selected_key = raw_input()
	while invalid_input(selected_key, len(handinURLs.keys())):
		print 'Invalid input'
		print 'Please select the number associated with the assignment'
		selected_key = raw_input()

	#go to that timetable page 
	timetableURL = handinURLs[handinURLs.keys()[int(selected_key)]]
	r = requests.get(baseURL + timetableURL, auth=auth)

	print r.url

def invalid_input(key, size):
	try:
		selected_key = int(key)
		if selected_key >= size or selected_key < 0:
			return True
	except ValueError:
			return True
	return False

if __name__=="__main__":
   main()