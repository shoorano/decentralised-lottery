from time import sleep
from brownie import Lottery, config, network
from scripts.helpers import *


def deploy_lottery(new_instance=False):
    """grabs network based addresses and contract constructor args and returns lottery
    contract, deploys contract if contract object is empty"""
    account = get_account()
    if len(Lottery) > 0 and not new_instance:
        return Lottery[-1]
    return Lottery.deploy(
        get_contract("eth_usd_price_feed").address,
        get_contract("vrf_coordinator").address,
        get_contract("link_token").address,
        get_brownie_config_variable("vrf_coordinator_fee"),
        get_brownie_config_variable("vrf_coordinator_key_hash"),
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify", False)
    )

def start_lottery():
    """starts lottery"""
    account = get_account()
    lottery = Lottery[-1]
    starting_txn = lottery.startLottery({"from": account})
    starting_txn.wait(1)
    print("The lottery has started")

def add_participants():
    """"""
    account = get_account()
    lottery = Lottery[-1]
    entrance_fee = lottery.getEntranceFee({"from": account})
    for i in range(1, 5):
        account = get_account(index=i)
        enter_txn = lottery.enter({"from": account, "value": entrance_fee*1.2})
        enter_txn.wait(1)
    print("Participants have entered the lottery")

def end_lottery():
    """ends lottery"""
    account = get_account()
    lottery = Lottery[-1]
    fund_with_link(lottery.address, amount=get_brownie_config_variable("vrf_coordinator_fee")*20)
    ending_txn = lottery.endLottery({"from": account})
    ending_txn.wait(1)
    sleep(60)
    print("The lottery has ended")
    print(f"The winner was: {lottery.lastWinner}")

def main():
    """runs deployment method"""
    deploy_lottery()
    start_lottery()
    add_participants()
    end_lottery()