import argparse
from lzma import MODE_FAST
from platform import architecture
from upbankapi import Client, NotAuthorizedException
from argparse import ArgumentParser
import json
from prettytable import PrettyTable


class Balancer:
    def __init__(self):
        # load api personal key from secrets.json
        self.prev_accounts = {}
        self.new_accounts = {}

        f = open('secrets.json')
        secrets = json.load(f)
        client = Client(token=secrets['up_api_key'])

        # setup configuration from config.json
        f = open('config.json')
        config = json.load(f)
        self.WEEKLY_PAY = config['weekly_pay']
        self.WEEKLY_RENT = config['weekly_rent']
        self.DAILY_EXPENSES = config['daily_expenses']
        self.GOING_OUT_AMOUNT = config['going_out']
        self.RENT = config['rent']
        self.SPLURGE = config['splurge']
        self.SMILE = config['smile']
        self.EXTINGUISH = config['extinguish']
        self.MOJO = config['mojo']
        self.MOJO_AMOUNT = config['mojo_amount']  # todo: get this from API
        self.GRIN = config['grin']
        self.GROW = config['grow']

        # optionally check the token is valid
        try:
            user_id = client.ping()
            print("Authorized: " + user_id)
        except NotAuthorizedException:
            print("The token is invalid")

        accounts_list = list(client.accounts())
        for account in accounts_list:
            self.prev_accounts[account.name] = account.balance
            self.new_accounts[account.name] = account.balance

    def run(self, mode):
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
        self.prev_accounts["Spending"] = 23
        self.prev_accounts["💸 BLOW/daily"] = 161
        self.prev_accounts["✨ BLOW/splurge"] = 130
        self.new_accounts["✨ BLOW/splurge"] = 130
        self.prev_accounts["💰 BLOW/smile"] = 130
        self.new_accounts["💰 BLOW/smile"] = 130
        self.prev_accounts["🧯 BLOW/extinguish"] = 211
        self.prev_accounts["🚨 MOJO/main"] = 1950
        self.prev_accounts["📈 GROW/main"] = 0

        # payday 
        if mode == "payday":
            self.prev_accounts["Spending"] += self.WEEKLY_PAY

            # calculate
            ## 60% into DAILY_EXPENSES
            self.new_accounts[self.DAILY_EXPENSES] += self.WEEKLY_PAY * 0.60
            ## "GOING OUT" amount to spending
            self.new_accounts["Spending"] += self.GOING_OUT_AMOUNT
            self.new_accounts[self.DAILY_EXPENSES] -= self.GOING_OUT_AMOUNT

            ## 20% into EXTINGUISH
            self.new_accounts[self.EXTINGUISH] += self.WEEKLY_PAY * 0.20

            ## 10% into splurge
            self.new_accounts[self.SPLURGE] += self.WEEKLY_PAY * 0.1

            ## 10% into smile (investments)
            self.new_accounts[self.SMILE] += self.WEEKLY_PAY * 0.1

            # print result & changes
            x = PrettyTable()
            x.field_names = ["Account", "Before", "After", "Change"]

            for account in self.new_accounts:
                change = self.new_accounts[account] - self.prev_accounts[account]
                x.add_row([account, str(self.prev_accounts[account]), str(self.new_accounts[account]), str(change)])

            print(x)

        # EOW balance
        if mode == "balance":
            """any unused cash in extinguish / daily expenses -> mojo -> grow"""
            # collect unused cash
            balanced_cash = 0
            balanced_cash += self.prev_accounts[self.EXTINGUISH]
            self.new_accounts[self.EXTINGUISH] = 0
            balanced_cash += self.prev_accounts[self.DAILY_EXPENSES]
            self.new_accounts[self.DAILY_EXPENSES] = 0
            balanced_cash += self.prev_accounts["Spending"]
            self.new_accounts["Spending"] = 0
            # fill mojo first!
            if self.prev_accounts[self.MOJO] < self.MOJO_AMOUNT:
                diff = self.MOJO_AMOUNT - self.prev_accounts[self.MOJO]
                if diff <= balanced_cash:
                    self.new_accounts[self.MOJO] += diff
                    balanced_cash -= diff
                else:
                    self.new_accounts[self.MOJO] += balanced_cash
                    balanced_cash = 0
                    print("Not enough cash to fill MOJO!")
            # fill grow with whatever remains!
            self.new_accounts[self.GROW] += balanced_cash

            # print result & changes
            x = PrettyTable()
            x.field_names = ["Account", "Before", "After", "Change"]
            for account in self.new_accounts:
                change = self.new_accounts[account] - self.prev_accounts[account]
                x.add_row([account, str(self.prev_accounts[account]), str(self.new_accounts[account]), str(change)])

            print(x)


if __name__ == "__main__":
    argparser = ArgumentParser(description='Upbank API client')
    argparser.add_argument("mode", help="Mode of operation", choices=["payday", "balance"])
    args = argparser.parse_args()

    b = Balancer()
    b.run(args.mode)