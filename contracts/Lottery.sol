// SPDX-License-Identifier: MIT

pragma solidity ^0.6.6;

import "@chainlink/contracts/src/v0.6/interfaces/AggregatorV3Interface.sol";
import "@chainlink/contracts/src/v0.6/VRFConsumerBase.sol";
import "OpenZeppelin/openzeppelin-contracts@3.0.0/contracts/math/SafeMath.sol";
import "OpenZeppelin/openzeppelin-contracts@3.0.0/contracts/access/Ownable.sol";

contract Lottery is VRFConsumerBase, Ownable {
    using SafeMath for uint256;
    using SafeMath for int256;

    uint256 public randomness;
    uint256 public usdEntryFee;
    address payable[] public players;
    address payable public lastWinner;
    enum LOTTERY_STATE {
        OPEN,
        CLOSED,
        CALCULATING_WINNER
    }
    LOTTERY_STATE public lotteryState;

    AggregatorV3Interface internal ethUsdPriceFeed;

    bytes32 internal keyHash;
    uint256 internal fee;
    uint256 public randomResult;

    event RequestedRandomness(bytes32 requestId);

    constructor(
        address _ethUsdPriceFeedAddress,
        address _vrfCoordinatorAddress,
        address _linkTokenContractAddress,
        uint256 _fee,
        bytes32 _keyHash
    ) public VRFConsumerBase(
        _vrfCoordinatorAddress,
        _linkTokenContractAddress
    ) {
        keyHash = _keyHash;
        fee = _fee;
        usdEntryFee = 50 * 1_000_000_000_000_000_000;
        ethUsdPriceFeed = AggregatorV3Interface(_ethUsdPriceFeedAddress);
        lotteryState = LOTTERY_STATE.CLOSED;
    }

    function enter() public payable {
        // $50 minimum
        require(lotteryState == LOTTERY_STATE.OPEN, "Lottery is not currently open for entrants");
        require(msg.value >= getEntranceFee(), "Sent amount is not enough ETH");
        players.push(msg.sender);
    }

    function getEntranceFee() public view returns (uint256) {
        // Returns entrance fee in wei
        int256 price = getLatestPrice();
        uint256 adjustedPrice = uint256(price) * 10_000_000_000; // 18 decimals
        uint256 costToEnter = (usdEntryFee * 1_000_000_000_000_000_000) / adjustedPrice;
        return costToEnter;
    }

    function getLatestPrice() public view returns (int) {
        // returns eth price in $ multiplied by 10**8
        (,int256 price,,,) = ethUsdPriceFeed.latestRoundData();
        return price;
    }

    function startLottery() public onlyOwner {
        require(lotteryState == LOTTERY_STATE.CLOSED, "Cannot start the next lottery until the previous has ended");
        lotteryState = LOTTERY_STATE.OPEN;
    }

    function endLottery() public onlyOwner {
        require(lotteryState != LOTTERY_STATE.CLOSED, "Cannot end the lottery as it has already ended");
        lotteryState = LOTTERY_STATE.CALCULATING_WINNER;
        bytes32 requestId = requestRandomness(keyHash, fee);
        emit RequestedRandomness(requestId);
    }
    
    // sets randomResult, overrides ... google this
    function fulfillRandomness(bytes32 requestId, uint256 _randomness) internal override {
        require(lotteryState == LOTTERY_STATE.CALCULATING_WINNER, "Not required at this time");
        require(_randomness > 0, "random not found");
        pickWinner(_randomness);
    }

    function pickWinner(uint256 _randomness) internal {
        // Pick winner
        uint256 indexOfWinner = randomness % players.length;
        lastWinner = players[indexOfWinner];
        // Pay winner
        lastWinner.transfer(address(this).balance);
        // Reset the lottery
        players = new address payable[](0);
        lotteryState = LOTTERY_STATE.CLOSED;
        randomness = _randomness;
    }
}