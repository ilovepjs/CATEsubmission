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

	def test_get_enrolled_class(self):
		#gets enrolled class details
		# r = requests.get(self.baseURL, auth=self.auth)
		timetable_key, timetable_class, timetable_period = self.cate.get_enrolled_class()
		
		expected_timetable_key = '2013:none:none:hj1612'
		self.assertEquals(expected_timetable_key, timetable_key)

		expected_timetable_class = 'c2'
		self.assertEquals(expected_timetable_class, timetable_class)
		
		expected_timetable_period = '1'
		self.assertEquals(expected_timetable_period, timetable_period)

if __name__ == '__main__':
	unittest.main()