import argparse
from platform import architecture
from upbankapi import Client, NotAuthorizedException
from argparse import ArgumentParser
import json
 
argparser = ArgumentParser(description='Upbank API client')
argparser.add_argument("mode", help="Mode of operation", choices=["payday", "balance"])
args = argparser.parse_args()

# globals
WEEKLY_PAY = 1346.153846

# load api personal key from config.json
f = open('config.json')
data = json.load(f)
client = Client(token=data['up_api_key'])

# optionally check the token is valid
try:
    user_id = client.ping()
    print("Authorized: " + user_id)
except NotAuthorizedException:
    print("The token is invalid")

accounts_list = list(client.accounts())
accounts = {}
for account in accounts_list:
    accounts[account.name] = account.balance

### scenario 1 (all empty)
# accounts["💸 BLOW/daily"] = 0
# accounts["🚪 BLOW/rent"] = 0
# accounts["✨ BLOW/splurge"] = 0
# accounts["💰 BLOW/smile"] = 0
# accounts["🧯 BLOW/extinguish"] = 0
# accounts["🚨 MOJO/main"] = 0
# accounts["😁 MOJO/grin"] = 0
# accounts["📈 GROW/main"] = 0

### scenario 2 (all empty)
accounts["💸 BLOW/daily"] = 0
accounts["🚪 BLOW/rent"] = 0
accounts["✨ BLOW/splurge"] = 0
accounts["💰 BLOW/smile"] = 0
accounts["🧯 BLOW/extinguish"] = 0
accounts["🚨 MOJO/main"] = 0
accounts["😁 MOJO/grin"] = 0
accounts["📈 GROW/main"] = 0

# payday 
if args.mode == "payday":
    # setup
    accounts["Spending"] = WEEKLY_PAY

    # calculate
    ## 45 % split between (40%) BLOW/daily & (60%) BLOW/rent
    accounts["🚪 BLOW/rent"] += WEEKLY_PAY * 0.45 * 0.7
    accounts["💸 BLOW/daily"] += WEEKLY_PAY * 0.45 * (1 - 0.7)

    ## 10% into splurge
    accounts["✨ BLOW/splurge"] += WEEKLY_PAY * 0.1

    ## 10% into smile (investments)
    accounts["💰 BLOW/smile"] += WEEKLY_PAY * 0.1
    
    ## 10% into grin (cash savings)
    accounts["😁 MOJO/grin"] += WEEKLY_PAY * 0.1

    ## 25% into extinguish (bills)  
    accounts["🧯 BLOW/extinguish"] += WEEKLY_PAY * 0.25

# EOW balance
if args.mode == "balance":
    # any left over BLOW/daily, 80% into 💰 BLOW/smile, 20% into 😁 MOJO/grin
    accounts["💰 BLOW/smile"] += accounts["💸 BLOW/daily"] * 0.8
    accounts["😁 MOJO/grin"] += accounts["💸 BLOW/daily"] * 0.2
    accounts["💸 BLOW/daily"] = 0

    # any left over in BLOW/extinguish, 80% into 💰 BLOW/smile, 20% into 😁 MOJO/grin
    accounts["💰 BLOW/smile"] += accounts["🧯 BLOW/extinguish"] * 0.8
    accounts["😁 MOJO/grin"] += accounts["🧯 BLOW/extinguish"] * 0.2
    accounts["🧯 BLOW/extinguish"] = 0


for key in accounts.keys():
    print(key, accounts[key])