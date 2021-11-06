from brownie import Lottery, config, network
from scripts.helpers import DECIMALS, STARTING_PRICE, get_account, get_eth_price_feed_address

def deploy_lottery():
    """basic deployer method"""
    account = get_account()
    price_feed_address = get_eth_price_feed_address()
    return Lottery.deploy(price_feed_address, {"from": account}, publish_source=config["networks"][network.show_active()].get("verify"))

def main():
    """runs deployment method"""
    lottery = deploy_lottery()