// SPDX-License-Identifier: MIT

pragma solidity ^0.6.6;

import "@chainlink/contracts/src/v0.6/interfaces/AggregatorV3Interface.sol";
import "@chainlink/contracts/src/v0.6/VRFConsumerBase.sol";
import "OpenZeppelin/openzeppelin-contracts@3.0.0/contracts/math/SafeMath.sol";
import "OpenZeppelin/openzeppelin-contracts@3.0.0/contracts/access/Ownable.sol";

contract Lottery is VRFConsumerBase, Ownable {
    using SafeMath for uint256;
    using SafeMath for int256;

    
    uint256 public randomResult;
    address payable[] public players;
    uint256 public usdEntryFee;
    AggregatorV3Interface internal ethUsdPriceFeed;
    enum LOTTERY_STATE {
        OPEN,
        CLOSED,
        CALCULATING_WINNER
    }
    LOTTERY_STATE public lotteryState;
    bytes32 internal keyHash;
    uint256 internal fee;
    event RequestedRandomness(bytes32 requestId);

    constructor(
        address _ethUsdPriceFeedAddress,
        address _vrfAddress,
        address _linkAddress,
        bytes32 _keyHash,
        uint256 _fee
    ) public VRFConsumerBase(
        0xdD3782915140c8f3b190B5D67eAc6dc5760C46E9, // VRF Coordinator
        0xa36085F69e2889c224210F603D836748e7dC0088  // LINK Token
    ) {
        keyHash = _keyHash; // 0x6c3699283bda56ad74f6b855546325b68d482e983852a7a82979cc4807b641f4; // unique identifier for the chainlink node we use
        fee = _fee; // 0.1 * 10 ** 18;
        usdEntryFee = 50 * 1_000_000_000_000_000_000;
        ethUsdPriceFeed = AggregatorV3Interface(_ethUsdPriceFeedAddress);
        lotteryState = LOTTERY_STATE.CLOSED;
    }

    function enter() public payable {
        // $50 minimum
        require(lotteryState == LOTTERY_STATE.OPEN, "Lottery is not currently open for entrants");
        require(msg.value > getEntranceFee(), "Sent amount is not enough ETH");
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
    }

    function getRandomNumber() public returns (bytes32 requestId) {
        require(LINK.balanceOf(address(this)) >= fee, "Not enough LINK - fill contract with faucet");
        return requestRandomness(keyHash, fee);
    }
    
    function fulfillRandomness(bytes32 requestId, uint256 randomness) internal override {
        randomResult = randomness;
    }
}