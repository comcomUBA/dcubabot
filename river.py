#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# STL imports
from datetime import datetime
# Cuasi STL imports
import requests


def getMatches():
	r = requests.get('http://il-divino-codino.herokuapp.com/riverLocalMatches')
	matches = r.json()
	for match in matches:
		dateString = match['matchDate']
		date = datetime.strptime(dateString, "%d/%m/%Y")
		if date.weekday() != 6: yield date
	return
