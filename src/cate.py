import requests
import os 
import getpass
import subprocess
import re
import sys
from bs4 import BeautifulSoup
from requests.auth import HTTPBasicAuth

class CateSubmission:
    def __init__(self, username, password, file_path):
        self.base_url = 'https://cate.doc.ic.ac.uk/'
        self.auth = HTTPBasicAuth(username, password)
        self.file_path = file_path

    def fetch_cate_homepage(self):
        r = requests.get(self.base_url, auth=self.auth)
        return BeautifulSoup(r.text)

    # extracts timetable auth from cate page 
    # returns auth for timetable
    def get_enrolled_class(self, cate_page):
        timetable_key = self._get_value_by_name(cate_page, 'keyt')
        timetable_class = self._get_value_by_name(cate_page, 'class', {'checked':True})
        timetable_period = self._get_value_by_name(cate_page, 'period', {'checked':True})

        return (timetable_key, timetable_class, timetable_period)

    def fetch_timetable(self, timetable_key, timetable_class, timetable_period):
        payload = {
        'keyt':timetable_key, 
        'class':timetable_class, 
        'period':timetable_period
        }
        
        r = requests.get(self.base_url + 'timetable.cgi', auth=self.auth, params=payload)
        return BeautifulSoup(r.text)

    # gets timetable page with assignments on it
    # puts all assignments due in into a dict handin_urls
    def get_assignments(self, timetable):
        handin_urls = {}
        handin_links = timetable.find_all(href=re.compile('handins'))
        for handin_link in handin_links:
            handin_container = handin_link.parent
            handin_title = handin_container.text[2:]
            handin_urls[handin_title] = handin_link['href']

        return handin_urls

    # goes through the handin_urls and sees what homework needs to be handed in
    # returns the url of the homework page
    def get_submission_url(self, handin_urls):
        print 'Which [assignment] would you like to hand in?'
        for i, key in enumerate(handin_urls.keys()):
            print '[{}]\t{}'.format(i, key)

        invalid_key_selected = True
        selected_key = None
        while invalid_key_selected:
            selected_key = int(raw_input('Select the number of the assignment to submit: '))
            invalid_key_selected = selected_key > len(handin_urls) or selected_key < 0

        return handin_urls[handin_urls.keys()[int(selected_key)]]

    def fetch_submission_page(submission_url):
        r = requests.get(self.base_url + submission_url, auth=self.auth)
        return r.text
    
    # gets the assignment hand in page
    # submits the assigment (group or solo)
    def submit_assignment(self, submission_page):
        if ('Group' in submission_page):
            submit_group_assignment(submission_url)
        else:
            submit_page = _submit_declaration(base_url, auth)
            files = _get_file()
            _submit_file(submission_url, files, auth, submit_page)

    # checks submission page to see if decleration exists
    # if it does, signs it else creates one 
    def submit_group_assignment(self, submission_url):
        if ('No declaration' in r.text):
            print 'Do you want to create a group on CATE and submit the work'
            user_response = raw_input('Do you want to create one? [Y/n]: ')
            if ('Y' in user_response):
                r = _submit_declaration(base_url, auth)
                soup = BeautifulSoup(r.text)

                _add_members_to_group()
                files = _get_file()
                _submit_file(submission_url, files, auth)
            else:
                print 'Come back to sign the declaration once a group has been formed'
                exit()
        else:
            user_details = soup.find('input', attrs={'type':'checkbox'})
            payload = {
            'key':_get_value_by_name(soup, 'key', {'type':'hidden'}),
            user_details['name']:user_details['value']
            }
            requests.post(submission_url, data=payload, auth=auth)
            print 'Your declaration has been submitted'
            exit()

    # adds memebers to the group
    def _add_members_to_group(self):
        add_grpmember_key = soup.find_all('input', attrs={'type':'hidden', 'name':'key'})[2]['value']

        print 'Add the people in your group'
        user_id_text = raw_input('Enter group member\'s id or DONE when finished: ')
        while ('DONE' not in user_id_text):
            user_id_value = None
            for user_id in soup.find_all('option'):
                if user_id_text in user_id['value']:
                    user_id_value = user_id['value']
                    validation = raw_input('Is {} correct? [Y/n]: '.format(user_id_value))
                    if ('Y' in validation):
                        payload = { 'grpmember':user_id_value, 'key':add_grpmember_key}
                        r = requests.post(submission_url, data=payload, auth=auth)
                        print '{} has been added to group'.format(user_id_value)
                    else:
                        print ('Invalid user id, please try again, E.G hj1612')
                        break
            user_id_text = raw_input('Enter group member id or DONE when finished: ')

    def _get_file(self):
        if (file_path == None):
            _create_cate_token()
            file_path = 'cate_token.txt'
        else:
            file_path = str(sys.argv[1])

            files = None
        try:
            files={'file-195-none': open(file_path, 'rb')}
        except IOError:
            print 'Fatal: IOError - file does not exist'
            exit()

        return files

    def _create_cate_token(self):
        if (os.path.isdir('.git')):
            call = subprocess.call("git rev-parse HEAD > cate_token.txt",
                    shell=True)
        else:
            print 'Fatal: Not a git repository (or any of the parent directories): .git'
            exit()

    def _submit_file(self, submission_url, files, auth):
        submit_key = _get_value_by_name('key').split(':')
        submit_key = ':'.join(submit_key[:4] + ['submit',] + submit_key[5:])
        payload={'key':submit_key}
        r = requests.post(submission_url, files=files, data=payload, auth=auth)

        if 'NOT SUBMITTED' in r.text:
            print 'File failed to upload, check extension or base name'
        elif r.status_code == 200:
            print 'Boom! You\'re done'
        else:
            print 'Something went wrong, try again or submit on CATE'
            exit()

    def _submit_declaration(self, base_url, auth):
        payload = { 
        'inLeader':_get_value_by_name('inLeader'), 
        'inMember':_get_value_by_name('inMember'), 
        'version':_get_value_by_name('version'),
        'key':_get_value_by_name('key')
        }
        declartion_url = soup.find('form')['action']

        return requests.post(base_url + declartion_url, data=payload, auth=auth)

    def _get_value_by_name(self, soup, name, extra_attrs={}):
        attrs = {'name':name}
        attrs.update(extra_attrs)
        return soup.find('input', attrs=attrs)['value']

def main():
    r = None
    # while r is None or r.status_code is not 200:
    username = raw_input('Username: ')
    password = getpass.getpass('Password: ')

    cate = CateSubmission(username, password, None)

    cate_page = cate.fetch_cate_homepage()
    timetable_key, timetable_class, timetable_period = cate.get_enrolled_class(cate_page)

    timetable = cate.fetch_timetable(timetable_key, timetable_class, timetable_period)
    assignments = cate.get_assignments(timetable)

    submission_url = cate.get_submission_url(assignments)
    submission_page = cate.fetch_submission_page(submission_url)


    # def get_assignments(self, timetable_key, timetable_class, timetable_period):
    # def get_submission_url(self, handin_urls):
    # def submit_assignment(self, submission_url):
    # def submit_group_assignment(self, submission_url):

if __name__=="__main__":
    main()
