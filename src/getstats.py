#!/usr/bin/python3
#pip3 install -r requirements.txt
import sys
import flexpoolapi
import json
from datetime import datetime, timedelta
from etherscan.accounts import Account
import requests
from time import sleep
from multiprocessing import Process
from colorama import Fore
import os
from prometheus_client import Gauge, start_http_server


def time_string():
    current_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    return current_time


def profitability():
    selleth = eth_nzd()
    print("    ETH Sell price " + Fore.RED + "$" + str(round(selleth,2)) + 'NZD' + Fore.RESET)
    profit = miner.estimated_daily_revenue() / pow(10,18)
    nzprofit = selleth * profit
    print("    Current profitabilty " + Fore.RED + str(round(profit,4)) + "eth/Day. $" + str(round(nzprofit,2)) + "NZD/day" + Fore.RESET)
    g['profit'].labels(currency="NZD").set(nzprofit)
    g['profit'].labels(currency="ETH").set(profit)


def current_hashrate():
    hashrate = miner.current_hashrate()[0]
    print("    Current Hashrate " + Fore.RED + str(round(hashrate/1000000,1)) + "MH/s" + Fore.RESET)
    g['hashrate'].set(hashrate)
    

def eth_nzd():
    response = requests.get("https://api.easycrypto.nz/public/api/ticker/ETHNZD")
    if response.json()["bid"] is None:
        selleth = response.json()["ask"]
        print("no sell price, estimating.")
        selleth = selleth * 0.97
    else:
        selleth = response.json()["bid"]

    return selleth

def pool_hashrate():
    hashrate = flexpoolapi.pool.hashrate()
    print("    Total Pool Hashrate "+ Fore.RED + str(round(hashrate["total"]/1000000000,1)) + "GH/s" + Fore.RESET)
    totalhash = int(hashrate["total"])
    ashash = int(hashrate["as"])
    auhash = int(hashrate["au"])
    euhash = int(hashrate["eu"])
    ushash = int(hashrate["us"])
    sahash = int(hashrate["sa"])
    g['pool'].labels(region="Total").set(totalhash)
    g['pool'].labels(region="Asia").set(ashash)    
    g['pool'].labels(region="Australia").set(auhash)    
    g['pool'].labels(region="Europe").set(euhash)
    g['pool'].labels(region="US").set(ushash)
    g['pool'].labels(region="South America").set(sahash)        


def getflex():
    ethbalance = miner.balance() / pow(10,18)
    return ethbalance

def getmeta():
    try:
        balance = int(api.get_balance()) / pow(10,18)
    except:
        print("API issue")
        print("Error ", sys.exc_info()[0])
        balance = 0
    return balance

def update_balance():
    ethbalance = getflex()
    print("    " + Fore.RED +str(round(ethbalance,3)) + "ETH " + Fore.RESET + "in flexpool wallet")
    g['balance'].labels(wallet="Flexpool").set(ethbalance)


def wallet_balance():   
    balance = getmeta()
    print("    " + Fore.RED + str(round(balance,3)) + "ETH " + Fore.RESET +  "in metamask wallet")
    g['balance'].labels(wallet="Metamask").set(balance)

def value():
    selleth = eth_nzd()
    flex = getflex() * selleth
    meta = getmeta() * selleth
    value = (flex + meta)
    g['value'].labels(wallet="Metamask").set(meta)
    g['value'].labels(wallet="Flexpool").set(flex)
    g['ethsell'].set(selleth)

    print("    Total holdings" + Fore.RED + "$" + str(round(value,2)) + "NZD" + Fore.RESET)

def block_count():
    blocks = flexpoolapi.pool.block_count()
    block_total = blocks["confirmed"] + blocks["unconfirmed"]
    print("    Total Blocks Mined "+ Fore.RED + str(block_total) + Fore.RESET)
    g['blocks'].set(block_total)

def timetowait():
    delta = timedelta(minutes=1)
    now = datetime.now()
    next_minute = (now + delta).replace(microsecond=0,second=30)
    wait_seconds = (next_minute - now)
    wait_seconds = int((wait_seconds).total_seconds())
    print(Fore.CYAN + "    " + str(wait_seconds)+"s until next" + Fore.RESET)
    return(wait_seconds)

def shares():
    shares24 = flexpoolapi.miner(wallet).stats().valid_shares
    g['shares'].set(shares24)
    print("    "+ Fore.RED + str(shares24) + Fore.RESET + " Shares in Last 24h")


def main():
    try:
        start_http_server(7890)

        while(True):
            
          print(Fore.GREEN + "At " + str(datetime.now()) + Fore.RESET)
          update_balance()
          wallet_balance()
          pool_hashrate()
          current_hashrate()
          value()
          block_count()
          profitability()
          shares()

          
        #   p1 = Process(target=update_balance)
        #   p1.start()
        #   p2 = Process(target=wallet_balance)
        #   p2.start()
        #   p3 = Process(target=pool_hashrate)
        #   p3.start()
        #   p4 = Process(target=current_hashrate)
        #   p4.start()
        #   p5 = Process(target=value)
        #   p5.start()
        #   p6 = Process(target=block_count)
        #   p6.start()
        #   p7 = Process(target=profitability)
        #   p7.start()
        #   p8 = Process(target=shares)
        #   p8.start()
        #   p1.join()
        #   p2.join()
        #   p3.join()
        #   p4.join()
        #   p5.join()
        #   p6.join()
        #   p7.join()
        #   p8.join()

          print(Fore.GREEN + "    Done" + Fore.RESET)
          sleep(timetowait())

    except:
        print("Error ", sys.exc_info()[0])



key = os.environ['ETHERSCAN_KEY']

wallet = os.environ['WALLET']

api = Account(address=wallet, api_key=key)

miner = flexpoolapi.miner(wallet)
g = {}
g['balance'] = Gauge('flex_balance_eth','Wallet Balance in Eth',['wallet'])
g['pool'] = Gauge('flex_hashrate','Flexpool Hashrate',['region'])
g['hashrate'] = Gauge('miner_hashrate','Miner Hashrate')
g['value'] = Gauge('flex_value','wallet value',['wallet'])
g['blocks'] = Gauge('flex_blocks','Block count')
g['profit'] = Gauge('flex_profit','Current 24h profit',['currency'])
g['shares'] = Gauge('flex_shares','24h shares')
g['ethsell'] = Gauge('flex_price','Eth Sell Price Easycrypto')

main()
