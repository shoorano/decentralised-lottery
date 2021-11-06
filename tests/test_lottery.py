from brownie import Lottery, config, network
from scripts.helpers import STARTING_PRICE, DECIMALS, get_eth_price_feed_address, get_account


def test_entrance_fee():
    """tests entrance fee"""
    usd_per_eth = (STARTING_PRICE  / (10 ** DECIMALS))
    expected_entrance_fee = (50 / usd_per_eth) * 10 ** 18
    account = get_account()
    price_feed_address = get_eth_price_feed_address()
    lottery = Lottery.deploy(price_feed_address, {"from": account}, publish_source=config["networks"][network.show_active()].get("verify"))
    assert lottery.getEntranceFee() == expected_entrance_fee
