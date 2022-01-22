import argparse
from lzma import MODE_FAST
from platform import architecture
from upbankapi import Client, NotAuthorizedException
from argparse import ArgumentParser
import json
from prettytable import PrettyTable

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
GOING_OUT_AMOUNT = data['going_out']
RENT = data['rent']
SPLURGE = data['splurge']
SMILE = data['smile']
EXTINGUISH = data['extinguish']
MOJO = data['mojo']
MOJO_AMOUNT = data['mojo_amount'] # todo: get this from API 
GRIN = data['grin']
GROW = data['grow']

# optionally check the token is valid
try:
    user_id = client.ping()
    print("Authorized: " + user_id)
except NotAuthorizedException:
    print("The token is invalid")

accounts_list = list(client.accounts())
prev_accounts = {}
new_accounts = {}
for account in accounts_list:
    prev_accounts[account.name] = account.balance
    new_accounts[account.name] = account.balance

"""payday"""
### scenario 1 (payday - all empty)
# new_accounts["Spending"] = 0
# new_accounts["💸 BLOW/daily"] = 0
# new_accounts["✨ BLOW/splurge"] = 0
# new_accounts["💰 BLOW/smile"] = 0
# new_accounts["🧯 BLOW/extinguish"] = 0
# new_accounts["🚨 MOJO/main"] = 0
# new_accounts["📈 GROW/main"] = 0

"""balance"""
### scenario 2 (Projected Savings, MOJO EMPTY)
# prev_accounts["Spending"] = 23
# prev_accounts["💸 BLOW/daily"] = 161
# prev_accounts["✨ BLOW/splurge"] = 130
# new_accounts["✨ BLOW/splurge"] = 130
# prev_accounts["💰 BLOW/smile"] = 130
# new_accounts["💰 BLOW/smile"] = 130
# prev_accounts["🧯 BLOW/extinguish"] = 211
# prev_accounts["🚨 MOJO/main"] = 0
# prev_accounts["📈 GROW/main"] = 0

### scenario 3 (Projected Savings, MOJO nearly full)
prev_accounts["Spending"] = 23
prev_accounts["💸 BLOW/daily"] = 161
prev_accounts["✨ BLOW/splurge"] = 130
new_accounts["✨ BLOW/splurge"] = 130
prev_accounts["💰 BLOW/smile"] = 130
new_accounts["💰 BLOW/smile"] = 130
prev_accounts["🧯 BLOW/extinguish"] = 211
prev_accounts["🚨 MOJO/main"] = 1950
prev_accounts["📈 GROW/main"] = 0

# payday 
if args.mode == "payday":
    prev_accounts["Spending"] += WEEKLY_PAY

    # calculate
    ## 60% into DAILY_EXPENSES
    new_accounts[DAILY_EXPENSES] += WEEKLY_PAY * 0.60
    ## "GOING OUT" amount to spending
    new_accounts["Spending"] += GOING_OUT_AMOUNT
    new_accounts[DAILY_EXPENSES] -= GOING_OUT_AMOUNT

    ## 20% into EXTINGUISH
    new_accounts[EXTINGUISH] += WEEKLY_PAY * 0.20

    ## 10% into splurge
    new_accounts[SPLURGE] += WEEKLY_PAY * 0.1

    ## 10% into smile (investments)
    new_accounts[SMILE] += WEEKLY_PAY * 0.1

    # print result & changes
    x = PrettyTable()
    x.field_names = ["Account", "Before", "After", "Change"]

    for account in new_accounts:
        change = new_accounts[account] - prev_accounts[account]
        x.add_row([account, str(prev_accounts[account]), str(new_accounts[account]), str(change)])

    print(x)

# EOW balance
if args.mode == "balance":
    """any unused cash in extinguish / daily expenses -> mojo -> grow"""
    # collect unused cash
    balanced_cash = 0
    balanced_cash += prev_accounts[EXTINGUISH]
    new_accounts[EXTINGUISH] = 0
    balanced_cash += prev_accounts[DAILY_EXPENSES]
    new_accounts[DAILY_EXPENSES] = 0
    balanced_cash += prev_accounts["Spending"]
    new_accounts["Spending"] = 0
    # fill mojo first!
    if prev_accounts[MOJO] < MOJO_AMOUNT:
        diff = MOJO_AMOUNT - prev_accounts[MOJO]
        if diff <= balanced_cash:
            new_accounts[MOJO] += diff
            balanced_cash -= diff
        else:
            new_accounts[MOJO] += balanced_cash
            balanced_cash = 0
            print("Not enough cash to fill MOJO!")
    # fill grow with whatever remains!
    new_accounts[GROW] += balanced_cash

    # print result & changes
    x = PrettyTable()
    x.field_names = ["Account", "Before", "After", "Change"]
    for account in new_accounts:
        change = new_accounts[account] - prev_accounts[account]
        x.add_row([account, str(prev_accounts[account]), str(new_accounts[account]), str(change)])

    print(x)



# for key in new_accounts.keys():
    # print(key, new_accounts[key])