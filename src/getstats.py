#!/usr/bin/python3
#pip3 install -r requirements.txt
import sys
import flexpoolapi
import json
from influxdb import InfluxDBClient
from datetime import datetime, timedelta
from etherscan.accounts import Account
import requests
from time import sleep
from multiprocessing import Process
from colorama import Fore
import os
#from requests.models import RequestEncodingMixin


def time_string():
    current_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    return current_time


def profitability():
    selleth = eth_nzd()
    print("    ETH Sell price " + Fore.RED + "$" + str(round(selleth,2)) + 'NZD' + Fore.RESET)
    profit = miner.estimated_daily_revenue() / pow(10,18)
    nzprofit = selleth * profit
    print("    Current profitabilty " + Fore.RED + str(round(profit,4)) + "eth/Day. $" + str(round(nzprofit,2)) + "NZD/day" + Fore.RESET)
    json_body = [
    {
        "measurement": "Profitability",
        "tags": {
            "pool" : "flexpool"
        },
        "time": time_string(),
        "fields": {
            "ETH": profit,
            "NZD": nzprofit
        }
    }
    ]
    toinflux(json_body)


def current_hashrate():
    hashrate = miner.current_hashrate()[0]
    print("    Current Hashrate " + Fore.RED + str(round(hashrate/1000000,1)) + "MH/s" + Fore.RESET)
    json_body = [
    {
        "measurement": "worker-hashrate",
        "tags": {
            "pool" : "flexpool"
        },
        "time": time_string(),
        "fields": {
            "hashrate": hashrate
        }
    }
    ]
    toinflux(json_body)

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


    json_body = [
    {
        "measurement": "pool-hashrate",
        "tags": {
            "pool" : "flexpool",
            "region" : "Total"
        },
        "time": time_string(),
        "fields": {
            "hashrate": totalhash
        }
    },
    {
        "measurement": "pool-hashrate",
        "tags": {
            "pool" : "flexpool",
            "region" : "Asia"
        },
        "time": time_string(),
        "fields": {
            "hashrate": ashash
        }
    },
    {
        "measurement": "pool-hashrate",
        "tags": {
            "pool" : "flexpool",
            "region" : "Australasia"
        },
        "time": time_string(),
        "fields": {
            "hashrate": auhash
        }
    },
        {
        "measurement": "pool-hashrate",
        "tags": {
            "pool" : "flexpool",
            "region" : "South America"
        },
        "time": time_string(),
        "fields": {
            "hashrate": sahash
        }
    },
    {
        "measurement": "pool-hashrate",
        "tags": {
            "pool" : "flexpool",
            "region" : "Europe"
        },
        "time": time_string(),
        "fields": {
            "hashrate": euhash
        }
    },            
    {
        "measurement": "pool-hashrate",
        "tags": {
            "pool" : "flexpool",
            "region" : "US"
        },
        "time": time_string(),
        "fields": {
            "hashrate": ushash
        }
    }
    ]
    toinflux(json_body)

def getflex():
    ethbalance = miner.balance() / pow(10,18)
    return ethbalance

def getmeta():
    api = Account(address=wallet, api_key=key)
    balance = int(api.get_balance()) / pow(10,18)
    return balance

def update_balance():
    ethbalance = getflex()
    print("    " + Fore.RED +str(round(ethbalance,3)) + "ETH " + Fore.RESET + "in flexpool wallet")
    json_body = [
    {
        "measurement": "balance",
        "tags": {
            "wallet" : wallet,
            "currency" : "eth",
            "pool" : "flexpool"

        },
        "time": time_string(),
        "fields": {
            "amount": ethbalance
        }
    }
    ]
    toinflux(json_body)

def toinflux(input):
    client.write_points(input,time_precision='s')

def setdb():
    dbname = 'miner'
    makedb = True
    dbs = client.get_list_database()
    for x in dbs:
        if (x['name']) == dbname:
            makedb = False

    if makedb:
        print('making the db')
        client.create_database(dbname)
    else:
        client.switch_database(dbname)

def wallet_balance():   
    balance = getmeta()
    print("    " + Fore.RED + str(round(balance,3)) + "ETH " + Fore.RESET +  "in metamask wallet")
    json_body = [
    {
        "measurement": "wallet-balance",
        "tags": {
            "wallet" : wallet
        },
        "time": time_string(),
        "fields": {
            "balance": balance
        }
    }
    ]
    toinflux(json_body)

def value():
    selleth = eth_nzd()
    flex = getflex()
    meta = getmeta()
    value = ((flex + meta) * selleth)
    print("    Total holdings" + Fore.RED + "$" + str(round(value,2)) + "NZD" + Fore.RESET)

    json_body = [
    {
        "measurement": "value",
        "tags": {
            "wallet" : wallet
        },
        "time": time_string(),
        "fields": {
            "sellprice": selleth,
            "value": value
        }
    }
    ]
    toinflux(json_body)

def block_count():
    blocks = flexpoolapi.pool.block_count()
    block_total = blocks["confirmed"] + blocks["unconfirmed"]
    print("    Total Blocks Mined "+ Fore.RED + str(block_total) + Fore.RESET)

    json_body = [
    {
        "measurement": "block",
        "tags": {
            "pool" : "flexpool"
        },
        "time": time_string(),
        "fields": {
            "count": block_total
        }
    }
    ]
    toinflux(json_body)

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
    json_body = [
    {
        "measurement": "shares",
        "tags": {
            "pool" : "flexpool"
        },
        "time": time_string(),
        "fields": {
            "shares": shares24
        }
    }
    ]
    toinflux(json_body)
    print("    "+ Fore.RED + str(shares24) + Fore.RESET + " Shares in Last 24h")



def main():
    try:
        while(True):
            
            
            print(Fore.GREEN + "At " + str(datetime.now()) + Fore.RESET)
            
            p1 = Process(target=update_balance)
            p1.start()
            p2 = Process(target=wallet_balance)
            p2.start()
            p3 = Process(target=pool_hashrate)
            p3.start()
            p4 = Process(target=current_hashrate)
            p4.start()
            p5 = Process(target=value)
            p5.start()
            p6 = Process(target=block_count)
            p6.start()
            p7 = Process(target=profitability)
            p7.start()
            p8 = Process(target=shares)
            p8.start()
            p1.join()
            p2.join()
            p3.join()
            p4.join()
            p5.join()
            p6.join()
            p7.join()
            p8.join()

            print(Fore.GREEN + "    Done" + Fore.RESET)
            sleep(timetowait())

    except:
        print("Error ", sys.exc_info()[0])


# with open("./settings.json") as json_data_file:
#     settings = json.load(json_data_file)
#     wallet = settings['api-settings']['wallet']
#     key = settings['api-settings']['etherscan-key']
#     influxip = settings['influx-settings']['host']
#     influxport = settings['influx-settings']['port']
#     influxuser = settings['influx-settings']['username']
#     influspass = settings['influx-settings']['password']
influxip = os.environ['INFLUX_IP']
influxport = os.environ['INFLUX_PORT']
influxuser = os.environ['INFLUX_USER']
influxpass = os.environ['INFLUX_PASS']
key = os.environ['ETHERSCAN_KEY']
wallet = os.environ['WALLET']

miner = flexpoolapi.miner(wallet)
requests.packages.urllib3.disable_warnings()
client = InfluxDBClient(host=influxip, port=influxport, username=influxuser, password=influxpass,ssl=True,verify_ssl=False)

setdb()
main()
