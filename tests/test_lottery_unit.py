import pytest
from brownie import network, exceptions
from scripts.helpers import *
from scripts.deploy import deploy_lottery


@pytest.fixture
def lottery():
    """returns a brand new lottery contract object"""
    return deploy_lottery(new_instance=True)

def test_entrance_fee(lottery):
    """tests entrance fee"""
    # Network based skip
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    # Arrange
    usd_per_eth = (INITIAL_AMOUNT  / (10 ** DECIMALS))
    expected_entrance_fee = (50 / usd_per_eth) * 10 ** 18
    # Act
    entrance_fee = lottery.getEntranceFee()
    # Assert
    assert entrance_fee == expected_entrance_fee

def test_users_cannot_enter_when_state_is_closed(lottery):
    """tests that accounts cannot enter the lottery when: LOTTERY_STATE == CLOSED"""
    # Network based skip
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    # Arrange
    entrant = get_account(index=1)
    # Act
    with pytest.raises(exceptions.VirtualMachineError):
        lottery.enter({"from": entrant, "value": lottery.getEntranceFee()})

def test_can_enter_when_started(lottery):
    """tests that accounts can enter the lottery when: LOTTERY_STATE == OPEN"""
    # Network based skip
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    # Arrange
    deployer = get_account()
    entrant = get_account(index=1)
    txn_start = lottery.startLottery({"from": deployer})
    txn_start.wait(1)
    # Act
    txn_enter = lottery.enter({"from": entrant, "value": lottery.getEntranceFee()})
    txn_enter.wait(1)
    # Assert
    assert lottery.players(0) == entrant.address

def test_deployer_can_end_lottery(lottery):
    """tests deployer can end the lottery"""
    # Network based skip
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    # Arrange
    deployer = get_account()
    entrant = get_account(index=1)
    txn_start = lottery.startLottery({"from": deployer})
    txn_start.wait(1)
    txn_enter = lottery.enter({"from": entrant, "value": lottery.getEntranceFee()})
    txn_enter.wait(1)
    fund_with_link(lottery)
    # Act
    txn_end = lottery.endLottery({"from": deployer})
    txn_end.wait(1)
    # Assert
    assert lottery.lotteryState() == 2

def test_non_deployer_cannot_end_lottery(lottery):
    """tests non-deployer cannot end the lottery"""
    # Network based skip
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    # Arrange
    deployer = get_account()
    entrant = get_account(index=1)
    non_deployer = get_account(index=2)
    txn_start = lottery.startLottery({"from": deployer})
    txn_start.wait(1)
    # Act
    txn_enter = lottery.enter({"from": entrant, "value": lottery.getEntranceFee()})
    txn_enter.wait(1)
    fund_with_link(lottery)
    # Assert
    with pytest.raises(exceptions.VirtualMachineError):
        lottery.endLottery({"from": non_deployer})

def test_can_pick_winner_correctly(lottery):
    """tests the contract picks the correct winner"""
    # Network based skip
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    # Arrange
    deployer = get_account()
    entrant_1 = get_account(index=1)
    entrant_2 = get_account(index=2)
    players = [entrant_1.address, entrant_2.address]
    txn_start = lottery.startLottery({"from": deployer})
    txn_start.wait(1)
    txn_enter_1 = lottery.enter({"from": entrant_1, "value": lottery.getEntranceFee()})
    txn_enter_1.wait(1)
    txn_enter_2 = lottery.enter({"from": entrant_2, "value": lottery.getEntranceFee()})
    txn_enter_2.wait(1)
    fund_with_link(lottery)
    # Act
    txn_end = lottery.endLottery({"from": deployer})
    request_id = txn_end.events["RequestedRandomness"]["requestId"]
    get_contract("vrf_coordinator").callBackWithRandomness(
        request_id,
        STATIC_RNG,
        lottery.address,
        {"from": deployer}
    )
    txn_end.wait(1)
    # Assert
    assert lottery.lastWinner() == players[STATIC_RNG % (len(players) - 1)]