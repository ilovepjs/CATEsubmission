import requests
import bs4
import getpass
import subprocess
from bs4 import BeautifulSoup
from requests.auth import HTTPBasicAuth

def main():
	baseURL = "https://cate.doc.ic.ac.uk/"

	#username and password for auth
	#TODO:incorrect user/pass combo fail case
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

	#go to selected handin page
	#TODO: refactor timetableURL to submissionURL
	timetableURL = handinURLs[handinURLs.keys()[int(selected_key)]]
	r = requests.get(baseURL + timetableURL, auth=auth)

	# submit declaration
	# TODO: fix naming & clean up code
	soup = BeautifulSoup(r.text)

	# handles group submissions
	if 'Group' in soup.find_all('b')[24].text:
		#if group exists
		#sign decleration
		print('You are already part of a team and your decleration has been signed')
		#else
		print('No team exists, would you like to form one? [Y/n]')
		user_response = raw_input('NOTE: Doing this requires you to submit the work\n')
		if ('Y' in user_response):
			do = 'do stuff'
		else:
			exit()

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

	# declartionURL = soup.find('form')['action']
	# print payload
	# print declartionURL
	# print auth
	# requests.post(baseURL + declartionURL, data=payload, auth=auth)

	# # TODO: Add support for non-git based assignments
	# # submit file
	# subprocess.call("git log | grep commit | head -n 1 | cut -c8- > cate_token.txt", shell=True)
	# files={'file': open('Ex3FunctionsCodeGenerator.hs', 'rb')}
	# payload={'key':'2013:1:129:c2:new:hj1612'}

	# requests.put(baseURL + timetableURL, files=files, auth=auth)
	# requests.post(baseURL + timetableURL, data=payload, auth=auth)
	
def groupDeclaration(soup):
	#TODO: refactor code from ^ function
	#submit declaration as before
	#if group leader
		#add group members
		#attach work
	#if group member
		#sign as with indivuals
	print 'TODO:implement'

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