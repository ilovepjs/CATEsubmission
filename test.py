import requests
import os 
import getpass
import subprocess
import sys
from bs4 import BeautifulSoup
from requests.auth import HTTPBasicAuthimport unittest

class TestCateSubmission(unittest.TestCase):

	def setUp(self):
		self.baseURL = 'https://cate.doc.ic.ac.uk/'
		username = raw_input('Username: ')
    	password = getpass.getpass('Password: ')
        self.auth = HTTPBasicAuth(username, password)
        cate = CateSubmission(username, password, None)

    def test_get_enrolled_class(self):
    	#checks to see if user login was success 
    	r = requests.get(baseURL, auth=auth)
    	self.assertNotEquals(r.status_code, None)

    	#gets enrolled class details
    	class_information = cate.get_enrolled_class()
    	sel



    



if __name__ == '__main__':
    unittest.main()