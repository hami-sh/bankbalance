import argparse
from lzma import MODE_FAST
from platform import architecture
from upbankapi import Client, NotAuthorizedException
from argparse import ArgumentParser
import json
from prettytable import PrettyTable


class Balancer:
    def __init__(self, config_path='config.json', secrets_path='secrets.json'):
        self.up_client = None

        self.prev_accounts = {}
        self.new_accounts = {}

        self.__WEEKLY_PAY = None
        self.__WEEKLY_RENT = None
        self.__DAILY_EXPENSES = None
        self.__GOING_OUT_AMOUNT = None
        self.__RENT = None
        self.__SPLURGE = None
        self.__SMILE = None
        self.__EXTINGUISH = None
        self.__MOJO = None
        self.__MOJO_AMOUNT = None  # todo: get this from API
        self.__GRIN = None
        self.__GROW = None

        self.up_client = self.create_up_client_from_api_key_file(secrets_path)

        if config_path is not None:
            self.load_config_from_file(config_path)

        # check validity of token
        try:
            user_id = self.up_client.ping()
            print("Authorized: " + user_id)
        except NotAuthorizedException:
            print("The token is invalid")

        # load accounts & balances from up api
        accounts_list = list(self.up_client.accounts())
        for account in accounts_list:
            self.prev_accounts[account.name] = account.balance
            self.new_accounts[account.name] = account.balance

    def load_config_from_file(self, path: str):
        # setup configuration from config.json
        f = open(path)
        config = json.load(f)
        self.load_config(config)

    def load_config(self, config: dict):
        # setup configuration from config variable
        self.__WEEKLY_PAY = config['weekly_pay']
        self.__WEEKLY_RENT = config['weekly_rent']
        self.__DAILY_EXPENSES = config['daily_expenses']
        self.__GOING_OUT_AMOUNT = config['going_out']
        self.__SPLURGE = config['splurge']
        self.__SMILE = config['smile']
        self.__EXTINGUISH = config['extinguish']
        self.__MOJO = config['mojo']
        self.__MOJO_AMOUNT = config['mojo_amount']  # todo: get this from API
        self.__GROW = config['grow']

    def create_up_client_from_api_key_file(self, path: str):
        # load api personal key from secrets.json
        f = open(path)
        secrets = json.load(f)
        client = Client(token=secrets['up_api_key'])
        return client

    def run(self, mode):
        # payday
        if mode == "payday":
            self.prev_accounts["Spending"] += self.__WEEKLY_PAY

            # calculate
            ## 60% into DAILY_EXPENSES
            self.new_accounts[self.__DAILY_EXPENSES] += self.__WEEKLY_PAY * 0.60
            ## "GOING OUT" amount to spending
            self.new_accounts["Spending"] += self.__GOING_OUT_AMOUNT
            self.new_accounts[self.__DAILY_EXPENSES] -= self.__GOING_OUT_AMOUNT

            ## 20% into EXTINGUISH
            self.new_accounts[self.__EXTINGUISH] += self.__WEEKLY_PAY * 0.20

            ## 10% into splurge
            self.new_accounts[self.__SPLURGE] += self.__WEEKLY_PAY * 0.1

            ## 10% into smile (investments)
            self.new_accounts[self.__SMILE] += self.__WEEKLY_PAY * 0.1

            self.print_table()

        # EOW balance
        if mode == "balance":
            """any unused cash in extinguish / daily expenses -> mojo -> grow"""
            self.new_accounts = self.prev_accounts.copy()

            # collect unused cash
            balanced_cash = 0
            balanced_cash += self.prev_accounts[self.__EXTINGUISH]
            self.new_accounts[self.__EXTINGUISH] = 0
            balanced_cash += self.prev_accounts[self.__DAILY_EXPENSES]
            self.new_accounts[self.__DAILY_EXPENSES] = 0
            balanced_cash += self.prev_accounts["Spending"]
            self.new_accounts["Spending"] = 0
            # fill mojo first!
            if self.prev_accounts[self.__MOJO] < self.__MOJO_AMOUNT:
                diff = self.__MOJO_AMOUNT - self.prev_accounts[self.__MOJO]
                if diff <= balanced_cash:
                    self.new_accounts[self.__MOJO] += diff
                    balanced_cash -= diff
                else:
                    self.new_accounts[self.__MOJO] += balanced_cash
                    balanced_cash = 0
                    print("Not enough cash to fill MOJO!")
            # fill grow with whatever remains!
            self.new_accounts[self.__GROW] += balanced_cash

            self.print_table()

    def print_table(self):
        # print result & changes
        x = PrettyTable()
        x.field_names = ["Account", "Before", "After", "Change"]
        x.align["Account"] = 'l'
        x.align["Change"] = 'r'
        res = {}
        for account in self.new_accounts:
            change = self.new_accounts[account] - self.prev_accounts[account]
            res[account] = [account, str(self.prev_accounts[account]), str(self.new_accounts[account]), str(change)]
        x.add_row(res['Spending'])
        x.add_row(res[self.__DAILY_EXPENSES])
        x.add_row(res[self.__EXTINGUISH])
        x.add_row(res[self.__SPLURGE])
        x.add_row(res[self.__SMILE])
        x.add_row(res[self.__MOJO])
        x.add_row(res[self.__GROW])
        print(x)


if __name__ == "__main__":
    argparser = ArgumentParser(description='Upbank API client')
    argparser.add_argument("mode", help="Mode of operation", choices=["payday", "balance"])
    args = argparser.parse_args()

    b = Balancer()
    b.run(args.mode)
