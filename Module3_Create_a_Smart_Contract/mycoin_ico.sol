pragma solidity ^0.4.21;

contract mycoin_ico {
    //introducing the maximum number of mycoin available for sale
    uint public maxMycoin = 1000000;

    //introducing USD to mycoin conversion rate
    uint public USDToMycoin = 1000;

    // introducing the total number of mycoin that have been bought by the investors
    uint public totalMycoinBought = 0;

    // mapping from the investor address to its equity in mycoin and usd
    mapping (address => uint) equityMycoin;
    mapping (address => uint) equityUSD;

    // check if an invester can by mycoin
    modifier checkMycoinBuyable(uint usdInvested) {
        require(usdInvested * USDToMycoin + totalMycoinBought <= maxMycoin);
        _;
    }

    // get the equity in mycoin of an investor
    function equityInMycoin(address investor) external view returns (uint) {
        return equityMycoin[investor];
    }

    // get the equity in usd of an investor
    function equityInUSD(address investor) external view returns (uint) {
        return equityUSD[investor];
    }

    // buy mycoin
    function buyMycoin(address investor, uint investedUSD) external
    checkMycoinBuyable(investedUSD) {
        uint mycoinBought = investedUSD * USDToMycoin;
        equityMycoin[investor] += mycoinBought;
        equityUSD[investor] = equityMycoin[investor]/USDToMycoin;
        totalMycoinBought += mycoinBought;
    }

    // sell mycoin
    function sellMycoin(address investor, uint soldMycoin) external {
        equityMycoin[investor] -= soldMycoin;
        equityUSD[investor] = equityMycoin[investor]/USDToMycoin;
        totalMycoinBought -= soldMycoin;
    }
}