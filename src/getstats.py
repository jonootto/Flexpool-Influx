#!/usr/bin/python3
import requests
import json
from prometheus_client import start_http_server, Gauge
import time

toeth = 1e-18
address = "0xE34B8eAdc5DaB229aD8A87a860F30687719AC359"

gunpaid = Gauge('flex_balance_unpaid', 'Unpaid Balance')
gpaid = Gauge('flex_balance_paid', 'Paid Balance')
gprofit = Gauge('flex_profit_ghash', 'Profiability/G hash')
gblocks = Gauge('flex_total_blocks', 'Total Blocks')


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
	print("Profitability " + str(pr) + "Eth/GH/s/Day")

	response = requests.get("https://api.flexpool.io/v2/pool/blockStatistics?coin=eth")
	blocks = response.json()
	block = blocks['result']['total']['blocks']
	gblocks.set(block)
	print("Total Blocks: " + str(block))
	time.sleep(10)
