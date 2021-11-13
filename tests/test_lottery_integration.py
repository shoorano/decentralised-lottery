import pytest
from time import sleep
from brownie import network
from scripts.helpers import *
from scripts.deploy import deploy_lottery


@pytest.fixture
def lottery():
    """returns a brand new lottery contract object"""
    return deploy_lottery(new_instance=True)

def test_can_pick_winner_correctly(lottery):
    """tests the contract picks the correct winner"""
    # Network based skip
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    # Arrange
    deployer = get_account()
    entrant_1 = get_account()
    entrant_2 = get_account()
    lottery.startLottery({"from": deployer})
    lottery.enter({"from": entrant_1, "value": lottery.getEntranceFee()})
    lottery.enter({"from": entrant_2, "value": lottery.getEntranceFee()})
    fund_with_link(lottery)
    # Act
    lottery.endLottery({"from": deployer})
    sleep(60)
    # Assert
    assert lottery.balance() == 0
    assert lottery.lastWinner() == deployer