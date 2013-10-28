import requests
import os 
import bs4
import getpass
import subprocess
import sys
from bs4 import BeautifulSoup
from requests.auth import HTTPBasicAuth

soup = None

def main():
	global soup

	baseURL = "https://cate.doc.ic.ac.uk/"

	#Username and password for auth
	r = None
	while r is None or r.status_code is not 200:
		username = raw_input("Username: ")
		password = getpass.getpass("Password: ")
		auth = HTTPBasicAuth(username, password)
		r = requests.get(baseURL, auth=auth)

	soup = BeautifulSoup(r.text)

	keyt = get_value('keyt')
	klass = soup.find(name="input", attrs={'checked':True, 'name': 'class'})['value']
	period = soup.find(name="input", attrs={'checked':True, 'name': 'period'})['value']

	payload = {'keyt':keyt, 'class':klass, 'period':period}
	r = requests.get(baseURL + 'timetable.cgi', auth=auth, params=payload)
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
	                handinURLs[title] = baseURL + handin['href']

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
	r = requests.get(submissionURL, auth=auth)
	soup = BeautifulSoup(r.text)
	files = None

	if ('Group' in r.text):
		if ('No declaration' in r.text):
			print 'There is no declaration for your group'
			print 'If you create one you will have to submit the work'
			user_response = raw_input('Do you want to create one? [Y/n]: ')
			if ('Y' in user_response):
				r = submit_declaration(baseURL, auth)
				soup = BeautifulSoup(r.text)
				key = soup.find_all('input', attrs={'type':'hidden', 'name':'key'})[2]['value']

				print 'Please add the people in your group'
				user_id_text = raw_input('Enter group member\'s id or DONE when finished: ')
				while ('DONE' not in user_id_text):
					user_id_value = None
					for user_id in soup.find_all('option'):
						if user_id_text in user_id['value']:
							user_id_value = user_id['value']
							validation = raw_input('Is ' + user_id_value + ' correct? [Y/n]: ')
							if ('Y' in validation):
								payload = { 'grpmember':user_id_value, 'key':key}
								r = requests.post(submissionURL, data=payload, auth=auth)
								print user_id_value + ' has been added to group'
							else:
								print ('Invalid user id, please try again, E.G hj1612')
							break
					user_id_text = raw_input('Enter group member id or DONE when finished: ')

				files = get_file()
				soup = submit_file(submissionURL, files, auth)
			else:
				exit_message('Come back to sign the declaration once a group has been formed')
		else:
			user_details = soup.find('input', attrs={'type':'checkbox'})
			payload = {
				'key':soup.find('input', attrs={'type':'hidden'})['value'],
				user_details['name']:user_details['value']
			}
			requests.post(submissionURL, data=payload, auth=auth)
			exit_message('Your declaration has been submitted')
	else:
		r = submit_declaration(baseURL, auth)

		files = get_file()
		soup = submit_file(submissionURL, files, auth)

	if soup.find(text='NOT SUBMITTED'):
		exit_message('File failed to upload, check extension or base name')
	elif r.status_code == 200:
		exit_message('Boom! You\'re done')
	else:
		exit_message('Something went wrong, try again or submit on CATE')

def exit_message(message):
	print message
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

def submit_file(submissionURL, files, auth):
	submit_key = get_value('key').split(':')
	submit_key = ':'.join(submit_key[:4] + ['submit',] + submit_key[5:])
	payload={'key':submit_key}
	r = requests.post(submissionURL, files=files, data=payload, auth=auth)
	return BeautifulSoup(r.text)

def submit_declaration(baseURL, auth):
	payload = { 
		'inLeader':get_value('inLeader'), 
		'inMember':get_value('inMember'), 
		'version':get_value('version'),
		'key':get_value('key')
	}
	declartionURL = soup.find('form')['action']
	return requests.post(baseURL + declartionURL, data=payload, auth=auth)

def get_value(name):
	return soup.find('input', attrs={'name':name})['value']

def get_file():
	#Checks to see if file given or to generate a cate_token
	file_path = None
	if (len(sys.argv) == 1):
		if (os.path.isdir('.git')):
			call = subprocess.call("git log | grep commit | head -n 1 | cut -c8- > cate_token.txt",
				shell=True)
			file_path = 'cate_token.txt'
		else:
			exit_message('Fatal: Not a git repository (or any of the parent directories): .git')
	else:
		file_path = str(sys.argv[1])

	files = None
	try:
		files={'file-195-none': open(file_path, 'rb')}
	except IOError:
		exit_message('Fatal: IOError - file does not exist')

	return files

if __name__=="__main__":
   main()