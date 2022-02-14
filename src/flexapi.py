import re
import requests

TO_ETH = 1e-18

def flex_api(api,parameters,wallet="",coin="eth"):
    coin = "eth"
    parameters = parameters.replace("coin=x","coin=" + coin)
    if api == "miner":
        parameters = parameters.replace("address=x","address=" + wallet)
    url = "https://api.flexpool.io/v2/"+ api + "/" + parameters
    response = False
    try:
        response = requests.get(url)
        if (response.status_code == 200):
            return response.json()
        else:
            print("API Error " + response.status_code)
    except:
        if response:
            print("API Error: " + (response.status_code))
            response = False
        else:
            print("No Response from API")
    return response


def minerBalance(wallet):
    response = flex_api("miner","balance?coin=x&address=x",wallet)
    if (response):
        response = response['result']['balance']*TO_ETH
    return response

def totalPaid(wallet):
    response = flex_api("miner","paymentsStats?coin=x&address=x",wallet)
    if (response):
        response = response['result']['stats']['totalPaid']*TO_ETH
    return response

def profitGH():
    response = flex_api("pool","dailyRewardPerGigahashSec?coin=x")
    if (response):
        response = response['result']*TO_ETH
    return response

def poolBlocks():
    response = flex_api("pool","blockStatistics?coin=x")
    if(response):
        response = response['result']['total']['blocks']
    return response

def hashrate(wallet):
    response = flex_api("miner","stats?coin=x&address=x",wallet)
    if(response):
        response = response['result']['currentEffectiveHashrate']
    return response

