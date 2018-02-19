import re
from flask import Flask, request
from collections import Counter
import urllib.request
from bs4 import BeautifulSoup
import pickle
import os
import json
from pymongo import MongoClient


import time
import atexit
import pymongo

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from binance.client import Client


CONNECTION="mongodb://chaturbots:F1inindia@ds125198.mlab.com:25198/cryptobot"
client = MongoClient(CONNECTION)
db = client.cryptobot

def get_profits():
	y = 0
	c1 = 0 
	x = 0 
	c2 = 0
	trans = db.trans.find()
	for t in trans: 
		if t["action"] == "buy":
			c1 = c1 + 1
			x = x + float(t["price"])
		elif t["action"] == "sell":
			c2 = c2 + 1
			y = y + float(t["price"])
	print(c1)
	print(c2)
	print(float(y)-float(x))

get_profits()
