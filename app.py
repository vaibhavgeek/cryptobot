import re
from flask import Flask, request
from collections import Counter
import urllib.request
from bs4 import BeautifulSoup
import pickle
import os
import json
from pymongo import MongoClient

app = Flask(__name__)

import time
import atexit
import pymongo

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from binance.client import Client

CONNECTION="mongodb://chaturbots:F1inindia@ds125198.mlab.com:25198/cryptobot"
client = MongoClient(CONNECTION)
db = client.cryptobot

api_key = "RQTH6gzgaHTGpTherAiK8Ids28y6J1LXb7DhnDaQSEupgEDAHEcKDlAzFgRlzdBW"
api_secret = "jQkycwqwX0IBSMdPjMwpyeIp9OOFlxJfeUDIH8OvvLr33q9sGi5bgsMX2OWpb47k"
#profit = 0
client = Client(api_key, api_secret)
price = client.get_symbol_ticker(symbol="LTCUSDT")
now = time.time()
db.trans.insert({ "action": "buy" , "price": price['price'] , "time": now})
db.prices.insert({"coin": price['symbol'], "price": price['price'] , "slope": 0 , "time": now , "slope_sign": 1  , "whattodo": "buy"})
#db.profits.insert({"profits": profit})


def get_slope(y2, y1, x2, x1):
	m = (float(y2) - float(y1))/(float(x2) - float(x1))
	return m

def get_binance_values():
	client = Client(api_key, api_secret)
	price = client.get_symbol_ticker(symbol="LTCUSDT")
	now = time.time()

	p_action = db.trans.find().sort('$natural', pymongo.DESCENDING).limit(-1).next()
	pac = p_action["action"]
	#db.prices.insert({"coin": price['symbol'], "price": price['price'] , "whattodo": "buy"})
	previous = db.prices.find().sort('$natural', pymongo.DESCENDING).limit(-1).next()
	p2 = price['price']
	p1 = previous['price']
	t2 = time.time()
	t1 = previous["time"]
	p_slope = previous["slope"]
	p_sign = previous["slope_sign"]
	slope = get_slope(p2,p1,t2,t1)
	slope_sign = 1 if slope >= 0 else 0

	#pro = db.profits.find().sort('$natural', pymongo.DESCENDING).limit(-1).next()

	if p_sign == slope_sign:
		db.prices.insert({"coin": price['symbol'], "price": price['price'] , "time": now , "slope": slope , "slope_sign": slope_sign , "whattodo": "not"})
	elif p_sign == 0 and slope_sign == 1 and pac == "sell" and price['price'] < p_action['price']:
		db.prices.insert({"coin": price['symbol'], "price": price['price'] , "time": now , "slope": slope , "slope_sign": slope_sign , "whattodo": "buy"})
		db.trans.insert({"action": "buy", "price": price['price'] , "time": now })
	elif p_sign == 1 and slope_sign == 0 and pac == "buy" and price['price'] > p_action['price']:
		db.prices.insert({"coin": price['symbol'], "price": price['price'] , "time": now , "slope": slope , "slope_sign": slope_sign , "whattodo": "sell"})
		db.trans.insert({"action": "sell", "price": price['price'] , "time": now })
	
	#db.profits.update({"_id": pro["_id"]}, {
    #                           "$set": {"profits":prof }})


# place a test market buy order, to place an actual order use the create_order function
	

# get all symbol prices
	# prices = client.get_all_tickers()
	# for price in prices:
	# 	if price["symbol"] == "LTCUSDT":
	# 		print(price)

	


scheduler = BackgroundScheduler()
scheduler.start()
scheduler.add_job(
    func=get_binance_values,
    trigger=IntervalTrigger(seconds=1),
    id='printing_job',
    name='every one second! get price and dictate a transaction!!',
    replace_existing=True)
# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())



@app.route('/', methods=['GET'])
def hello():
    return "Hello World"


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 33507))
    app.run(host="0.0.0.0", port=port, debug=True)

