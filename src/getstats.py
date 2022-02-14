#!/usr/bin/python3
from audioop import add
import requests
import json
from prometheus_client import start_http_server, Gauge
import time
import os
import flexapi

toETH = 1e-18
address = os.environ['WALLET']
refresh = int(os.environ['REFRESH'])

gUnpaid = Gauge('flex_balance_unpaid', 'Unpaid Balance')
gPaid = Gauge('flex_balance_paid', 'Paid Balance')
gProfit = Gauge('flex_profit_ghash', 'Profiability/G hash')
gBlocks = Gauge('flex_total_blocks', 'Total Blocks')
gHash = Gauge('flex_miner_hashrate', 'Miner Hashrate')
gMinerProfit = Gauge('flex_miner_profit', 'Current Profitability')

start_http_server(8000)

def main():
	while True:
		balance = flexapi.minerBalance(address)
		if balance:
			gUnpaid.set(balance)
			print("Balance " + str(round(balance,6)) + " ETH")

		paid = flexapi.totalPaid(address)
		if paid:
			gPaid.set(paid)
			print("Total Paid: " + str(round(paid,6)) + " ETH")

		profit = flexapi.profitGH()
		if profit:
			gProfit.set(profit)
			print("Profit per GH: " + str(round(profit,6)) + " ETH/day")

		blocks = flexapi.poolBlocks()
		if blocks:
			gBlocks.set(blocks)
			print("Total Blocks Mined : " + str(round(blocks,6)))

		hash = flexapi.hashrate(address)
		if hash:
			gHash.set(hash)
			print("Current hashrate: " + str(hash/(1e6)) + " Mh/s")
		
		if (hash and profit):
			minerprofit = (profit * hash / 1e9)
			gProfit.set(minerprofit)
			print("Current Proftability: " + str(round(minerprofit,6)) + " ETH/Day")

		time.sleep(refresh)

if __name__ == "__main__":
    main()