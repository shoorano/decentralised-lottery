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
    lottery.startLottery({"from": deployer})
    # Act
    lottery.enter({"from": entrant, "value": lottery.getEntranceFee()})
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
    lottery.startLottery({"from": deployer})
    lottery.enter({"from": entrant, "value": lottery.getEntranceFee()})
    fund_with_link(lottery)
    # Act
    lottery.endLottery({"from": deployer})
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
    lottery.startLottery({"from": deployer})
    # Act
    lottery.enter({"from": entrant, "value": lottery.getEntranceFee()})
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
    players = [deployer, entrant_1, entrant_2]
    winner = players[STATIC_RNG % (len(players) - 1)]
    winners_balance_before = winner.balance()
    lottery.startLottery({"from": deployer})
    lottery.enter({"from": entrant_1, "value": lottery.getEntranceFee()})
    lottery.enter({"from": entrant_2, "value": lottery.getEntranceFee()})
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
    assert lottery.lastWinner() == winner
    assert lottery.balance() == 0
    assert winner.balance() == winners_balance_before + lottery.getEntranceFee()