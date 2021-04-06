import json
import os
import unittest
from time import time

from django.test import TestCase

# Create your tests here.
from app.views import har_parse


class TestSingleTestcase(unittest.TestCase):
	def test01(self):
		print(os.path.dirname(os.path.dirname(__file__)))
		harpath = os.path.join(os.path.dirname(os.path.dirname(__file__)), "userfile/mubu.har")
		print(harpath)
		har_parse(harpath)
		
	def test_time(self):
		print(str(int(time())))