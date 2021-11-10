import pytest
from brownie import Lottery, config, network
from scripts.helpers import *
from scripts.deploy import deploy_lottery


def test_entrance_fee():
    """tests entrance fee"""
    # Network based skip
    if network.show_active() != "hardhat":
        pytest.skip()
    # Arrange
    usd_per_eth = (INITIAL_AMOUNT  / (10 ** DECIMALS))
    expected_entrance_fee = (50 / usd_per_eth) * 10 ** 18
    lottery = deploy_lottery()
    # Act
    entrance_fee = lottery.getEntranceFee()
    # Assert
    assert entrance_fee == expected_entrance_fee
