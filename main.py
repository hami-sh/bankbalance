import argparse
from lzma import MODE_FAST
from platform import architecture
from upbankapi import Client, NotAuthorizedException
from argparse import ArgumentParser
import json
 
argparser = ArgumentParser(description='Upbank API client')
argparser.add_argument("mode", help="Mode of operation", choices=["payday", "balance"])
args = argparser.parse_args()

# globals
WEEKLY_PAY = 0
WEEKLY_RENT = 0
DAILY_EXPENSES = ""
RENT = ""
SPLURGE = ""
SMILE = ""
EXTINGUISH = ""
MOJO = ""
MOJO_AMOUNT = 0
GRIN = ""
GROW = ""


# load api personal key from secrets.json
f = open('secrets.json')
data = json.load(f)
client = Client(token=data['up_api_key'])

# setup configuration from config.json
f = open('config.json')
data = json.load(f)
WEEKLY_PAY = data['weekly_pay']
WEEKLY_RENT = data['weekly_rent']
DAILY_EXPENSES = data['daily_expenses']
RENT = data['rent']
SPLURGE = data['splurge']
SMILE = data['smile']
EXTINGUISH = data['extinguish']
MOJO = data['mojo']
MOJO_AMOUNT = data['mojo_amount']
GRIN = data['grin']
GROW = data['grow']

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
    de = WEEKLY_PAY * 0.45
    accounts[RENT] += WEEKLY_RENT
    accounts[DAILY_EXPENSES] += de - WEEKLY_RENT

    ## 10% into splurge
    accounts[SPLURGE] += WEEKLY_PAY * 0.1

    ## 10% into smile (investments)
    accounts[SMILE] += WEEKLY_PAY * 0.1
    
    ## 10% into grin (cash savings)
    accounts[GRIN] += WEEKLY_PAY * 0.1

    ## 25% into extinguish (bills)  
    accounts[EXTINGUISH] += WEEKLY_PAY * 0.25

# EOW balance
if args.mode == "balance":
    # if emergency fund is less than "saver amount", fill this first
    if accounts[MOJO] < MOJO_AMOUNT:
        amount_to_cover = MOJO_AMOUNT - accounts[MOJO]
        amount_can_be_covered = (accounts[DAILY_EXPENSES] - amount_to_cover) >= 0
        accounts[MOJO] += 
        if accounts[MOJO] < MOJO_AMOUNT:
            print("\tALERT: Need to cover emergency fund with savings")
        accounts[GROW] = 0
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