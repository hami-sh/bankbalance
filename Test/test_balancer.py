import pytest
from balancer import Balancer


@pytest.fixture(scope='module')
def b():
    b = Balancer(secrets_path="../secrets.json", config_path=None)

    config = {}
    config['weekly_pay'] = 1307.46
    config['weekly_rent'] = 400
    config['daily_expenses'] = "💸 BLOW/daily"
    config['going_out'] = 75
    config['splurge'] = "✨ BLOW/splurge"
    config['smile'] = "💰 BLOW/smile"
    config['extinguish'] = "🧯 BLOW/extinguish"
    config['mojo'] = "🚨 MOJO/main"
    config['mojo_amount'] = 2000  # todo: get this from API
    config['grow'] = "📈 GROW/main"

    b.load_config(config)

    yield b


### PAYDAY
def test_no_money_payday(b: Balancer):
    b.new_accounts["Spending"] = 0
    b.new_accounts["💸 BLOW/daily"] = 0
    b.new_accounts["✨ BLOW/splurge"] = 0
    b.new_accounts["💰 BLOW/smile"] = 0
    b.new_accounts["🧯 BLOW/extinguish"] = 0
    b.new_accounts["🚨 MOJO/main"] = 0

    b.run("payday")


### BALANCE
def test_no_money_mojo_nearly_full(b: Balancer):
    b.prev_accounts["Spending"] = 23
    b.prev_accounts["💸 BLOW/daily"] = 161
    b.prev_accounts["🧯 BLOW/extinguish"] = 211
    b.prev_accounts["✨ BLOW/splurge"] = 130
    b.prev_accounts["💰 BLOW/smile"] = 130
    b.prev_accounts["🚨 MOJO/main"] = 1950
    b.prev_accounts["📈 GROW/main"] = 0

    b.run("balance")


