import requests
import os 
import bs4
import getpass
import subprocess
import sys
from bs4 import BeautifulSoup
from requests.auth import HTTPBasicAuth

def main():
	baseURL = "https://cate.doc.ic.ac.uk/"

	#Username and password for auth
	r = None
	while r is None or r.status_code is not 200:
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

	#Dict between handin page link and lab names
	handinURLs = {}
	for line in soup.find_all('td'):
	    sublines = line.find_all(name="a", attrs={'title':'View exercise specification'})
	    for subline in sublines:
	        title = subline.string
	        handins = line.find_all(name="a", attrs={'href':True})
	        for handin in handins:
	            if 'handin' in handin['href']:
	                handinURLs[title] = handin['href']

	#Ask user what homework to hand in
	selected_key = None
	while selected_key is None or invalid_input(selected_key, len(handinURLs.keys())):
		location = 0
		print 'Which [assignment] would you like to hand in?'
		for key in handinURLs.keys():
			print '[' + str(location) + ']\t' + key
			location += 1
		selected_key = raw_input('Please select the number associated with the assignment\n')

	#Handin assignment page
	submissionURL = handinURLs[handinURLs.keys()[int(selected_key)]]
	r = requests.get(baseURL + submissionURL, auth=auth)

	#Submit declaration
	soup = BeautifulSoup(r.text)

	inLeader = inMember = version = key = None
	for line in soup.find_all('td'):
		for subline in line.find_all('input', attrs={'type':'hidden'}):
			if 'inLeader' in subline['name']:
				inLeader = subline['value']
			elif 'inMember' in subline['name']:
				inMember = subline['value']
			elif 'version' in subline['name']:
				version = subline['value']
			elif 'key' in subline['name']:
				key = subline['value']

	payload = { 'inLeader':inLeader, 'inMember':inMember, 'version':version, 'key':key}
	declartionURL = soup.find('form')['action']
	requests.post(baseURL + declartionURL, data=payload, auth=auth)

	#Checks to see if file given or to generate a cate_token
	file_path = None
	if (len(sys.argv) == 1):
		if (os.path.isdir('/.git')):
			call = subprocess.call("git log | grep commit | head -n 1 | cut -c8- > cate_token.txt",
				shell=True)
			file_path = 'cate_token.txt'
		else:
			show_error('Fatal: Not a git repository (or any of the parent directories): .git')

	else:
		file_path = str(sys.argv[1])

	files = None
	try:
		files={'file-195-none': open(file_path, 'rb')}
	except IOError:
		show_error('Fatal: IOError - file does not exist')

	submit_key = key.split(':')
	submit_key = ':'.join(submit_key[:4] + ['submit',] + submit_key[5:])
	payload={'key':submit_key}
	r = requests.post(baseURL + submissionURL, files=files, data=payload, auth=auth)
	soup = BeautifulSoup(r.text)

	if soup.find(text='NOT SUBMITTED'):
		show_error('File failed to upload, check extension or base name')
	elif r.status_code == 200:
		print 'Boom! You\'re done'
	else:
		show_error('Something went wrong, please try again or submit the old-fashioned way')

def show_error(error):
	print error	
	print 'Goodbye'
	exit()

def invalid_input(key, size):
	try:
		selected_key = int(key)
		if selected_key >= size or selected_key < 0:
			return True
	except ValueError:
			print 'Invalid input'
			return True
	return False

if __name__=="__main__":
   main()