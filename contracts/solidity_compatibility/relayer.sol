pragma solidity ^0.4.0;

contract TokenInterface {
    function approve(address, uint256) public returns (bool);
}

contract ExchangeInterface {
    function ethToTokenSwap(uint256, uint256) public payable returns (uint256);
    function tokenToEthSwap(uint256, uint256, uint256) public returns (uint256);
}


contract Relayer {

    address public exchangeAddress;
    address public tokenAddress;
    ExchangeInterface exchange;
    TokenInterface token;

    function() public payable {}

    function initialize(address _exchange, address _token) public {
        exchangeAddress = _exchange;
        tokenAddress = _token;
        token = TokenInterface(_token);
        exchange = ExchangeInterface(_exchange);
        token.approve(exchangeAddress, 100000000*10**18);
    }

    function ethToTokenTrade(uint256 deadline) public payable {
        exchange.ethToTokenSwap.value(msg.value)(1, deadline);
    }

    function tokenToEthTrade(uint256 amountSold, uint256 deadline) public {
        exchange.tokenToEthSwap(amountSold, 1, deadline);
    }
}
