// SPDX-License-Identifier: MIT

pragma solidity ^0.6.6;

contract Lottery {
    address payable[] public players;
    uint256 public USDEntryFee;
    // v3aggregator blah = priceFeed
    constructor(address priceFeed) public {
        // pass priceFeed to v3 aggregator
    }

    function enter() public payable {
        // $50 minimum
        require(msg.value > getEntranceFee(), "Sent amount is not enough");
        players.push(msg.sender);
    }

    function getEntranceFee() public view returns (uint256) {
        return 123;
    }

    function startLottery() public {}

    function endLottery() public {}
}