import requests
import os 
import readline
import getpass
import subprocess
import re
import sys
import readline

from bs4 import BeautifulSoup
from requests.auth import HTTPBasicAuth

class CateSubmission:
    def __init__(self, username_input, password_input, file_path=None):
        self.base_url = 'https://cate.doc.ic.ac.uk/'
        self.file_path = file_path

        status_code = None
        while status_code is not 200:
            username = username_input()
            password = password_input()
            self.auth = HTTPBasicAuth(username, password)
            status_code = requests.get(self.base_url, auth=self.auth).status_code

        self.students = None

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

    # returns the url of the homework page
    def get_submission_url(self, handin_urls):
        print('Which [assignment] would you like to hand in?')
        for i, key in enumerate(handin_urls.keys()):
            print('[{}]\t{}'.format(i, key))

        invalid_key_selected = True
        selected_key = None
        while invalid_key_selected:
            selected_key = int(raw_input('Select the number of the assignment to submit: '))
            invalid_key_selected = selected_key > len(handin_urls) or selected_key < 0

        return handin_urls[handin_urls.keys()[int(selected_key)]]

    def fetch_submission_page(submission_url):
        r = requests.get(self.base_url + submission_url, auth=self.auth)
        return r.text

    def submit_assignment(self, submission_page):
        if 'Group' in submission_page:
            if 'No declaration' in submission_page:
                print('Do you want to create a group on CATE and submit the work')
                user_response = raw_input('Do you want to create one? [Y/n]: ')
                if 'Y' in user_response:
                    submission_page = _submit_declaration()
                    _add_members_to_group()
                    _submit_files(submission_url, _get_files())
                else:
                    print('Come back to sign the declaration once a group has been formed')
                    exit()
            else:
                _submit_declaration()
                print('The declaration has been signed')
                exit()
        else:
            submission_page = _submit_declaration()
            _submit_files(submission_url, _get_files())

    # adds memebers to the group
    def _add_members_to_group(self, submission_page):
        self._init_students(page)
        readline.set_completer(self.completer)
        readline.set_completer_delims('')
        readline.parse_and_bind("tab: complete")

        student_name = ''
        while ('DONE' not in student_name):
            if student_name in self.students.keys():
                student = self.students[student_name]
                print'{} has been added to group'.format(student)
            else:
                print 'Use TAB to auto-complete or DONE when finished'
            student_name = raw_input('Enter Surname, Firstname.    E.G Joshi, Preeya (hj1612) - c2-0\n')

    def completer(self, text, state):
        options = [x for x in self.students.keys() if x.startswith(text)]
        try:
            return options[state]
        except IndexError:
            return None
    
    def _init_students(self, submission_page):
        list_of_students = submission_page.find_all('option')
        self.students = dict((student.get_text(), student['value']) for student in list_of_students)

    def _get_files(self):
        files = None
        if (os.path.isdir('.git')):
            _create_cate_token()
            _attach_file('cate_token.txt', files)
        for arg in sys.argv[1:]
            _attach_file(str(arg), files)
        return files

    def _attach_file(self, file_path, files):
        try:
            # HERE ERROR - 195 NOT ALWAYS CORRECT  
            files['file-195-none'] = open(file_path, 'rb')}
            print '{} created'.format(file_path)
        except IOError:
            print 'Fatal: IOError - file does not exist'
            exit()

        return files

    def _create_cate_token(self):
        call = subprocess.call("git rev-parse HEAD > cate_token.txt", shell=True)
        print 'cate_token.txt created'

    def _submit_files(self, submission_url, files, auth):
        submit_key = _get_value_by_name('key').split(':')
        submit_key = ':'.join(submit_key[:4] + ['submit',] + submit_key[5:])
        payload={'key':submit_key}
        r = requests.post(submission_url, files=files, data=payload, auth=auth)

        if 'NOT SUBMITTED' in r.text:
            print('File failed to upload, check extension or base name')
        elif r.status_code == 200:
            print('Boom! You\'re done')
        else:
            print('Something went wrong, try again or submit on CATE')
            exit()

    def _submit_declaration(self):
        payload = { 
        'inLeader':_get_value_by_name('inLeader'), 
        'inMember':_get_value_by_name('inMember'), 
        'version':_get_value_by_name('version'),
        'key':_get_value_by_name('key')
        }
        declartion_url = soup.find('form')['action']

        return BeautifulSoup(requests.post(self.base_url + declartion_url, data=payload, auth=self.auth))

    def _get_value_by_name(self, soup, name, extra_attrs={}):
        attrs = {'name':name}
        attrs.update(extra_attrs)
        return soup.find('input', attrs=attrs)['value']

def raw(message):
    return raw_input(message)

def main():
    # handle command line args
    cate = CateSubmission(lambda: raw('Username: '), lambda: getpass.getpass('Password: '))

    cate_page = cate.fetch_cate_homepage()
    timetable_key, timetable_class, timetable_period = cate.get_enrolled_class(cate_page)

    timetable = cate.fetch_timetable(timetable_key, timetable_class, timetable_period)
    assignments = cate.get_assignments(timetable)

    submission_url = cate.get_submission_url(assignments)
    submission_page = cate.fetch_submission_page(submission_url)

    cate.submit_assignment(submission_page)


if __name__=="__main__":
    main()
