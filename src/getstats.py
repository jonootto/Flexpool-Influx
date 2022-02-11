#!/usr/bin/python3
import requests
import json
from prometheus_client import start_http_server, Gauge
import time
import os

toeth = 1e-18
address = os.environ['WALLET']
refresh = int(os.environ['REFRESH'])

gunpaid = Gauge('flex_balance_unpaid', 'Unpaid Balance')
gpaid = Gauge('flex_balance_paid', 'Paid Balance')
gprofit = Gauge('flex_profit_ghash', 'Profiability/G hash')
gblocks = Gauge('flex_total_blocks', 'Total Blocks')
ghash = Gauge('flex_miner_hashrate', 'Miner Hashrate')


start_http_server(8000)

while True:
	response = requests.get("https://api.flexpool.io/v2/miner/balance?coin=eth&address=" + address + "&countervalue=NZD")
	balance = response.json()
	bal = balance['result']['balance']*toeth
	gunpaid.set(bal)
	print("Balance " + str(bal) + "eth")

	response = requests.get("https://api.flexpool.io/v2/miner/paymentsStats?coin=eth&address=" + address)
	payment = response.json()
	paid = payment['result']['stats']['totalPaid']*toeth
	gpaid.set(paid)
	print("Total Paid: " + str(paid) + "eth")


	response = requests.get("https://api.flexpool.io/v2/pool/dailyRewardPerGigahashSec?coin=eth")
	profit = response.json()
	pr = profit['result']*toeth
	gprofit.set(pr)
	print("Profitability " + str(pr) + " eth/GH/s/Day")

	response = requests.get("https://api.flexpool.io/v2/pool/blockStatistics?coin=eth")
	blocks = response.json()
	block = blocks['result']['total']['blocks']
	gblocks.set(block)
	print("Total Blocks: " + str(block))


	response = requests.get("https://api.flexpool.io/v2/miner/stats?coin=eth&address=" + address)
	miner = response.json()
	hashrate = miner['result']['currentEffectiveHashrate']
	ghash.set(hashrate)
	print("Current hashrate: " + str(hashrate/1000000) + " Mh/s")



	time.sleep(refresh)