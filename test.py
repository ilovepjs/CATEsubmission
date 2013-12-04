import requests
import os 
import getpass
import subprocess
import sys
import requests.auth 
from bs4 import BeautifulSoup

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
		self.assertEquals(r.status_code, 400)

		# #gets enrolled class details
		# class_information = cate.get_enrolled_class()
		# sel

if __name__ == '__main__':
	unittest.main()