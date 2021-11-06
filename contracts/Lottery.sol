// SPDX-License-Identifier: MIT

pragma solidity ^0.6.6;

import "@chainlink/contracts/src/v0.6/interfaces/AggregatorV3Interface.sol";
import "OpenZeppelin/openzeppelin-contracts@3.0.0/contracts/math/SafeMath.sol";

contract Lottery {
    using SafeMath for uint256;
    using SafeMath for int256;
    address payable[] public players;
    uint256 public usdEntryFee;
    AggregatorV3Interface internal ethUsdPriceFeed;

    constructor(address _ethUsdPriceFeedAddress) public {
        usdEntryFee = 50 * 1_000_000_000_000_000_000;
        ethUsdPriceFeed = AggregatorV3Interface(_ethUsdPriceFeedAddress);
    }

    function enter() public payable {
        // $50 minimum
        require(msg.value > getEntranceFee(), "Sent amount is not enough");
        players.push(msg.sender);
    }

    function getEntranceFee() public view returns (uint256) {
        // Returns entrance fee in wei
        int256 price = getLatestPrice();
        uint256 adjustedPrice = uint256(price) * 10_000_000_000; // 18 decimals
        uint256 costToEnter = (usdEntryFee * 1_000_000_000_000_000_000) / adjustedPrice;
        return costToEnter;
    }

    /**
     * Returns the latest price
     */
    function getLatestPrice() public view returns (int) {
        // returns eth price in $ multiplied by 10**8
        (,int256 price,,,) = ethUsdPriceFeed.latestRoundData();
        return price;
    }

    function startLottery() public {}

    function endLottery() public {}
}