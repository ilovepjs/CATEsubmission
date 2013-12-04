import os 
import getpass
import subprocess
import sys
import requests.auth
import unittest 
from bs4 import BeautifulSoup
from requests.auth import HTTPBasicAuth
from cate import CateSubmission

class TestCateSubmission(unittest.TestCase):

	cate = CateSubmission(username, password, None)

	def test_login(self):
		#checks to see if user login was success 
		r = requests.get(self.cate.baseURL, auth=self.cate.auth)
		self.assertEquals(r.status_code, 200)
		class_information = self.cate.get_enrolled_class()
		print class_information

	# def test_get_enrolled_class(self):
	# 	#gets enrolled class details
	# 	r = requests.get(self.baseURL, auth=self.auth)
		
	# 	print class_information
	# 	expected = 0

if __name__ == '__main__':
	unittest.main()