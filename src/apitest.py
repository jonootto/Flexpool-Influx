#import requests
#import json
import flexapi
address = "0xE34B8eAdc5DaB229aD8A87a860F30687719AC359"
balance = flexapi.profitGH()
if (balance):
    print("Total Paid: " + str(balance) + " eth")