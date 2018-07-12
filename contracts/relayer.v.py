contract Factory():
    def getExchange(token_addr: address) -> address: constant

contract Exchange():
    def tokenToEthSwap(token_amount: uint256, eth_amount: uint256, deadline: uint256) -> uint256(wei): modifying
    def ethToTokenTransfer(recipent: address, token_amount: uint256, deadline: uint256) -> uint256: modifying

contract Token():
    def transferFrom(_from : address, _to : address, _value : uint256) -> bool: modifying
    def approve(_spender : address, _value : uint256) -> bool: modifying

factory: public(address)
token_to_exchange: address[address]

@public
@payable
def __default__():
    pass

@public
def initialize(factory_addr: address) -> bool:
    assert self.factory == ZERO_ADDRESS
    self.factory = factory_addr
    return True

@public
def add_exchange(token_addr: address) -> address:
    assert self.token_to_exchange[token_addr] == ZERO_ADDRESS
    exchange_addr: address = Factory(self.factory).getExchange(token_addr)
    assert exchange_addr != ZERO_ADDRESS
    self.token_to_exchange[token_addr] = exchange_addr
    return exchange_addr

@public
def approve_exchange(token_addr: address, approve_amount: uint256) -> bool:
    exchange_addr: address = self.token_to_exchange[token_addr]
    assert exchange_addr != ZERO_ADDRESS
    assert Token(token_addr).approve(exchange_addr, approve_amount)
    return True

@public
def tokenToTokenSwap(
    input_token: address,
    output_token: address,
    input_amount: uint256,
    min_output_amount: uint256,
    deadline: uint256
) -> uint256:
    input_exchange: address = self.token_to_exchange[input_token]
    output_exchange: address = self.token_to_exchange[output_token]
    assert input_exchange != ZERO_ADDRESS and output_exchange != ZERO_ADDRESS
    assert Token(input_token).transferFrom(msg.sender, self, input_amount)
    eth_bought: uint256(wei) = Exchange(input_exchange).tokenToEthSwap(input_amount, 1, deadline)
    assert eth_bought > 0
    output_tokens_bought: uint256 =  Exchange(output_exchange).ethToTokenTransfer(msg.sender, min_output_amount, deadline, value=eth_bought)
    assert output_tokens_bought > min_output_amount
    return output_tokens_bought

@public
def tokenToExchangeSwap(
    input_token: address,
    output_exchange: address,
    input_amount: uint256,
    min_output_amount: uint256,
    deadline: uint256
) -> uint256:
    input_exchange: address = self.token_to_exchange[input_token]
    assert input_token != ZERO_ADDRESS and output_exchange != ZERO_ADDRESS
    assert Token(input_token).transferFrom(msg.sender, self, input_amount)
    eth_bought: uint256(wei) = Exchange(input_exchange).tokenToEthSwap(input_amount, 1, deadline)
    assert eth_bought > 0
    output_tokens_bought: uint256 =  Exchange(output_exchange).ethToTokenTransfer(msg.sender, min_output_amount, deadline, value=eth_bought)
    assert output_tokens_bought > min_output_amount
    return output_tokens_bought
