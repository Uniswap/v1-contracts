contract Factory():
    def getExchange(token_addr: address) -> address: constant

contract Exchange():
    def getEthToTokenExactPrice(tokens_bought: uint256) -> uint256(wei): constant
    def ethToTokenTransfer(min_tokens: uint256, deadline: timestamp, recipent: address) -> uint256: modifying
    def ethToTokenTransferExact(tokens_bought: uint256, deadline: timestamp, recipent: address) -> uint256(wei): modifying

TokenPurchase: event({buyer: indexed(address), eth_sold: indexed(uint256(wei)), tokens_bought: indexed(uint256)})
EthPurchase: event({buyer: indexed(address), tokens_sold: indexed(uint256), eth_bought: indexed(uint256(wei))})
AddLiquidity: event({provider: indexed(address), eth_amount: indexed(uint256(wei)), token_amount: indexed(uint256)})
RemoveLiquidity: event({provider: indexed(address), eth_amount: indexed(uint256(wei)), token_amount: indexed(uint256)})
Transfer: event({_from: indexed(address), _to: indexed(address), _value: uint256})
Approval: event({_owner: indexed(address), _spender: indexed(address), _value: uint256})

name: public(bytes32)                                   # Uniswap
symbol: public(bytes32)                                 # UNI
decimals: public(uint256)                               # 18
totalSupply: public(uint256)                            # total liquidity supply
liquidity_balances: uint256[address]                    # liquidity balance of an address
liquidity_allowances: (uint256[address])[address]       # liquidity allowance of one address on another
token: address(ERC20)                                   # the ERC20 token traded on this exchange
factory: Factory                                        # interface to factory that created this exchange

# Called by factory during launch
# Replaces constructor which is not supported in contracts deployed using create_with_code_of()
@public
def setup(token_addr: address) -> bool:
    assert (self.factory == ZERO_ADDRESS and self.token == ZERO_ADDRESS) and token_addr != ZERO_ADDRESS
    self.factory = msg.sender
    self.token = token_addr
    self.name = 0x556e69737761702045786368616e676500000000000000000000000000000000
    self.symbol = 0x554e490000000000000000000000000000000000000000000000000000000000
    self.decimals = 18
    return True

# Add ETH and tokens to liquidity reserves at current price ratio
@public
@payable
def addLiquidity(min_amount: uint256, deadline: timestamp) -> uint256:
    assert deadline > block.timestamp and min_amount > 0
    total_liquidity: uint256 = self.totalSupply
    if total_liquidity > 0:
        eth_reserve: uint256(wei) = self.balance - msg.value
        token_reserve: uint256 = self.token.balanceOf(self)
        token_amount: uint256 = msg.value * token_reserve / eth_reserve
        liquidity_minted: uint256 = msg.value * total_liquidity / eth_reserve
        assert (liquidity_minted > min_amount) and msg.value > 0
        self.liquidity_balances[msg.sender] += liquidity_minted
        self.totalSupply = total_liquidity + liquidity_minted
        assert self.token.transferFrom(msg.sender, self, token_amount)
        log.AddLiquidity(msg.sender, msg.value, token_amount)
        log.Transfer(ZERO_ADDRESS, msg.sender, liquidity_minted)
        return liquidity_minted
    else:
        assert (self.factory != ZERO_ADDRESS and self.token != ZERO_ADDRESS) and msg.value >= 1000000000
        assert self.factory.getExchange(self.token) == self
        token_amount: uint256 = min_amount
        initial_liquidity: uint256 = as_unitless_number(self.balance)
        self.totalSupply = initial_liquidity
        self.liquidity_balances[msg.sender] = initial_liquidity
        assert self.token.transferFrom(msg.sender, self, token_amount)
        log.AddLiquidity(msg.sender, msg.value, token_amount)
        log.Transfer(ZERO_ADDRESS, msg.sender, initial_liquidity)
        return initial_liquidity

# Burn liquidity to receive ETH and tokens at current price ratio
@public
def removeLiquidity(amount: uint256, min_eth: uint256(wei), min_tokens: uint256, deadline: timestamp) -> (uint256(wei), uint256):
    assert (amount > 0 and deadline > block.timestamp) and (min_eth > 0 and min_tokens > 0)
    total_liquidity: uint256 = self.totalSupply
    token_reserve: uint256 = self.token.balanceOf(self)
    eth_amount: uint256(wei) = amount * self.balance / total_liquidity
    token_amount: uint256 = amount * token_reserve / total_liquidity
    assert eth_amount > min_eth and token_amount > min_tokens
    self.liquidity_balances[msg.sender] -= amount
    self.totalSupply = total_liquidity - amount
    assert self.token.transfer(msg.sender, token_amount)
    send(msg.sender, eth_amount)
    log.RemoveLiquidity(msg.sender, eth_amount, token_amount)
    log.Transfer(msg.sender, ZERO_ADDRESS, amount)
    return eth_amount, token_amount

@private
@constant
def ethToTokenPrice(eth_sold: uint256(wei)) -> uint256:
    # eth_reserve = eth_bal - eth_sold
    eth_bal: uint256(wei) = self.balance
    token_reserve: uint256 = self.token.balanceOf(self)
    fee: uint256(wei) = eth_sold / 400 + 1
    new_token_reserve: uint256 = (eth_bal - eth_sold) * token_reserve / (eth_bal - fee)
    return token_reserve - new_token_reserve - 1

@public
@constant
def getEthToTokenPrice(eth_sold: uint256(wei)) -> uint256:
    return self.ethToTokenPrice(eth_sold)

@private
def ethToToken(eth_sold: uint256(wei), min_tokens: uint256, deadline: timestamp, buyer: address, recipent: address) -> uint256:
    assert (self.totalSupply > 0 and deadline >= block.timestamp) and (eth_sold > 0 and min_tokens > 0)
    tokens_bought: uint256 = self.ethToTokenPrice(eth_sold)
    assert tokens_bought > min_tokens
    assert self.token.transfer(recipent, tokens_bought)
    log.TokenPurchase(buyer, eth_sold, tokens_bought)
    return tokens_bought

# Fallback function that converts received ETH to tokens
# User specifies exact input amount and minimum output amount
@public
@payable
def __default__():
    self.ethToToken(msg.value, 1, block.timestamp, msg.sender, msg.sender)

# # Converts ETH to tokens, sender recieves tokens
# # User specifies exact input amount and minimum output amount
@public
@payable
def ethToTokenSwap(min_tokens: uint256, deadline: timestamp) -> uint256:
    return self.ethToToken(msg.value, min_tokens, deadline, msg.sender, msg.sender)

# Converts ETH to tokens, recipent recieves tokens
# User specifies exact input amount and minimum output amount
@public
@payable
def ethToTokenTransfer(min_tokens: uint256, deadline: timestamp, recipent: address) -> uint256:
    assert recipent != self and recipent != ZERO_ADDRESS
    return self.ethToToken(msg.value, min_tokens, deadline, msg.sender, recipent)

# Function for determining eth to token exchange rate
@private
@constant
def ethToTokenExactPrice(tokens_bought: uint256, eth_input: uint256(wei)) -> uint256(wei):
    assert tokens_bought > 0
    eth_reserve: uint256(wei) = self.balance - eth_input
    token_reserve: uint256 = self.token.balanceOf(self)
    new_token_reserve: uint256 = token_reserve - tokens_bought
    new_eth_reserve: uint256(wei) = eth_reserve * token_reserve / new_token_reserve
    eth_sold: uint256(wei) = new_eth_reserve - eth_reserve + as_wei_value(1, 'wei')
    return eth_sold * 400 / 399 + as_wei_value(1, 'wei')

@public
@constant
def getEthToTokenExactPrice(tokens_bought: uint256) -> uint256(wei):
    return self.ethToTokenExactPrice(tokens_bought, 0)

@private
def ethToTokenExact(tokens_bought: uint256, max_eth: uint256(wei), deadline: timestamp, buyer: address, recipent: address) -> uint256(wei):
    assert (self.totalSupply > 0 and deadline >= block.timestamp) and max_eth > 0
    eth_sold: uint256(wei) = self.ethToTokenExactPrice(tokens_bought, max_eth)
    assert self.token.transfer(recipent, tokens_bought)
    eth_refund: uint256(wei) = max_eth - eth_sold
    if eth_refund > 0:
        send(buyer, eth_refund)
    log.TokenPurchase(buyer, eth_sold, tokens_bought)
    return eth_refund

# Converts ETH to tokens, sender recieves tokens
# User specifies maximum input amount and exact output amount
@public
@payable
def ethToTokenSwapExact(tokens_bought: uint256, deadline: timestamp) -> uint256(wei):
    return self.ethToTokenExact(tokens_bought, msg.value, deadline, msg.sender, msg.sender)

# Converts ETH to tokens, recipent recieves tokens
# User specifies maximum input amount and exact output amount
@public
@payable
def ethToTokenTransferExact(tokens_bought: uint256, deadline: timestamp, recipent: address) -> uint256(wei):
    assert recipent != self and recipent != ZERO_ADDRESS
    return self.ethToTokenExact(tokens_bought, msg.value, deadline, msg.sender, recipent)

# Function for determining token to eth exchange rate
@private
@constant
def tokenToEthPrice(tokens_sold: uint256) -> uint256(wei):
    assert tokens_sold > 0
    eth_reserve: uint256(wei) = self.balance
    token_reserve: uint256 = self.token.balanceOf(self)
    fee: uint256 = tokens_sold / 400 + 1
    new_eth_reserve: uint256(wei) = eth_reserve * token_reserve / (token_reserve + tokens_sold - fee)
    return eth_reserve - new_eth_reserve - as_wei_value(1, 'wei')

@public
@constant
def getTokenToEthPrice(tokens_sold: uint256) -> uint256(wei):
    return self.tokenToEthPrice(tokens_sold)

@private
def tokenToEth(tokens_sold: uint256, min_eth: uint256(wei), deadline: timestamp, buyer: address, recipent: address) -> uint256(wei):
    assert self.totalSupply > 0 and deadline >= block.timestamp
    eth_bought: uint256(wei) = self.tokenToEthPrice(tokens_sold)
    assert eth_bought > min_eth and min_eth > 0
    assert self.token.transferFrom(buyer, self, tokens_sold)
    send(recipent, eth_bought)
    log.EthPurchase(buyer, tokens_sold, eth_bought)
    return eth_bought

# Converts tokens to ETH, sender recieves tokens
# User specifies exact input amount and minimum output amount
@public
def tokenToEthSwap(tokens_sold: uint256, min_eth: uint256(wei), deadline: timestamp) -> uint256(wei):
    return self.tokenToEth(tokens_sold, min_eth, deadline, msg.sender, msg.sender)

# Converts tokens to ETH, recipent recieves tokens
# User specifies exact input amount and minimum output amount
@public
def tokenToEthTransfer(tokens_sold: uint256, min_eth: uint256(wei), deadline: timestamp, recipent: address) -> uint256(wei):
    assert recipent != self and recipent != ZERO_ADDRESS
    return self.tokenToEth(tokens_sold, min_eth, deadline, msg.sender, recipent)

# Function for determining token to eth exchange rate
@private
@constant
def tokenToEthExactPrice(eth_bought: uint256(wei)) -> uint256:
    assert eth_bought > 0
    eth_reserve: uint256(wei) = self.balance
    token_reserve: uint256 = self.token.balanceOf(self)
    new_eth_reserve: uint256(wei) = eth_reserve - eth_bought
    new_token_reserve: uint256 = eth_reserve * token_reserve / new_eth_reserve
    tokens_sold: uint256 = new_token_reserve - token_reserve + 1
    return tokens_sold * 400 / 399 + 1

@public
@constant
def getTokenToEthExactPrice(eth_bought: uint256(wei)) -> uint256:
    return self.tokenToEthExactPrice(eth_bought)

@private
def tokenToEthExact(eth_bought: uint256(wei), max_tokens: uint256, deadline: timestamp, buyer: address, recipent: address) -> uint256:
    assert self.totalSupply > 0 and deadline >= block.timestamp
    tokens_sold: uint256 = self.tokenToEthExactPrice(eth_bought)
    assert max_tokens > tokens_sold and max_tokens > 0
    assert self.token.transferFrom(buyer, self, tokens_sold)
    send(recipent, eth_bought)
    log.EthPurchase(buyer, tokens_sold, eth_bought)
    return tokens_sold

# Converts tokens to ETH, sender recieves tokens
# User specifies maximum input amount and exact output amount
@public
def tokenToEthSwapExact(eth_bought: uint256(wei), max_tokens: uint256, deadline: timestamp) -> uint256:
    return self.tokenToEthExact(eth_bought, max_tokens, deadline, msg.sender, msg.sender)

# Converts tokens to ETH, recipent recieves tokens
# User specifies maximum input amount and exact output amount
@public
def tokenToEthTransferExact(eth_bought: uint256(wei), max_tokens: uint256, deadline: timestamp, recipent: address) -> uint256:
    assert recipent != self and recipent != ZERO_ADDRESS
    return self.tokenToEthExact(eth_bought, max_tokens, deadline, msg.sender, recipent)

@private
def tokenToToken(tokens_sold: uint256, min_tokens_bought: uint256, deadline: timestamp, buyer: address, recipent: address, exchange_addr: address) -> uint256:
    assert self.totalSupply > 0 and deadline >= block.timestamp
    assert exchange_addr != self
    eth_bought: uint256(wei) = self.tokenToEthPrice(tokens_sold)
    assert self.token.transferFrom(buyer, self, tokens_sold)
    # call fails if exchange_addr == ZERO_ADDRESS
    tokens_bought: uint256 = Exchange(exchange_addr).ethToTokenTransfer(min_tokens_bought, deadline, recipent, value=eth_bought)
    assert tokens_bought > min_tokens_bought and min_tokens_bought > 0
    log.EthPurchase(buyer, tokens_sold, eth_bought)
    return tokens_bought

# Converts tokens to tokens, sender recieves tokens
# User specifies exact input amount and minimum output amount
# TODO: add min_eth
@public
def tokenToTokenSwap(tokens_sold: uint256, min_tokens_bought: uint256, deadline: timestamp, token_addr: address) -> uint256:
    # returns ZERO_ADDRESS if no exchange exists for token_addr
    exchange_addr: address = self.factory.getExchange(token_addr)
    return self.tokenToToken(tokens_sold, min_tokens_bought, deadline, msg.sender, msg.sender, exchange_addr)

# Converts tokens to tokens, recipent recieves tokens
# User specifies exact input amount and minimum output amount
@public
def tokenToTokenTransfer(tokens_sold: uint256, min_tokens_bought: uint256, deadline: timestamp, recipent: address, token_addr: address) -> uint256:
    exchange_addr: address = self.factory.getExchange(token_addr)
    return self.tokenToToken(tokens_sold, min_tokens_bought, deadline, msg.sender, recipent, exchange_addr)

@private
def tokenToTokenExact(tokens_bought: uint256, max_tokens_sold: uint256, deadline: timestamp, buyer: address, recipent: address, exchange_addr: address) -> uint256:
    assert self.totalSupply > 0 and deadline >= block.timestamp
    assert exchange_addr != self
    eth_bought: uint256(wei) = Exchange(exchange_addr).getEthToTokenExactPrice(tokens_bought)
    tokens_sold: uint256 = self.tokenToEthExactPrice(eth_bought)
    assert max_tokens_sold > tokens_sold and tokens_sold > 0
    assert self.token.transferFrom(buyer, self, tokens_sold)
    eth_refund: uint256(wei) = Exchange(exchange_addr).ethToTokenTransferExact(tokens_bought, deadline, recipent, value=eth_bought)
    log.EthPurchase(buyer, tokens_sold, eth_bought)
    return tokens_sold

# Converts tokens to tokens, sender recieves tokens
# User specifies maximum input amount and exact output amount
@public
def tokenToTokenSwapExact(tokens_bought: uint256, max_tokens_sold: uint256, deadline: timestamp, token_addr: address) -> uint256:
    exchange_addr: address = self.factory.getExchange(token_addr)
    return self.tokenToTokenExact(tokens_bought, max_tokens_sold, deadline, msg.sender, msg.sender, exchange_addr)

# Converts tokens to tokens, recipent recieves tokens
# User specifies maximum input amount and exact output amount
@public
def tokenToTokenTransferExact(tokens_bought: uint256, max_tokens_sold: uint256, deadline: timestamp, recipent: address, token_addr: address) -> uint256:
    exchange_addr: address = self.factory.getExchange(token_addr)
    return self.tokenToTokenExact(tokens_bought, max_tokens_sold, deadline, msg.sender, recipent, exchange_addr)

# Converts tokens to tokens, sender recieves tokens
# User specifies exact input amount and minimum output amount
# This function allows token to token trades across exchanges that were not created in the same factory as this exchange
@public
def tokenToExchangeSwap(tokens_sold: uint256, min_tokens_bought: uint256, deadline: timestamp, exchange_addr: address) -> uint256:
    return self.tokenToToken(tokens_sold, min_tokens_bought, deadline, msg.sender, msg.sender, exchange_addr)

# Converts tokens to tokens, recipent recieves tokens
# User specifies exact input amount and minimum output amount
# This function allows token to token trades across exchanges that were not created in the same factory as this exchange
@public
def tokenToExchangeTransfer(tokens_sold: uint256, min_tokens_bought: uint256, deadline: timestamp, recipent: address, exchange_addr: address) -> uint256:
    assert recipent != self
    return self.tokenToToken(tokens_sold, min_tokens_bought, deadline, msg.sender, recipent, exchange_addr)

# Converts tokens to tokens, sender recieves tokens
# User specifies maximum input amount and exact output amount
# This function allows token to token trades across exchanges that were not created in the same factory as this exchange
@public
def tokenToExchangeSwapExact(tokens_bought: uint256, max_tokens_sold: uint256, deadline: timestamp, exchange_addr: address) -> uint256:
    return self.tokenToTokenExact(tokens_bought, max_tokens_sold, deadline, msg.sender, msg.sender, exchange_addr)

# Converts tokens to tokens, recipent recieves tokens
# User specifies maximum input amount and exact output amount
# This function allows token to token trades across exchanges that were not created in the same factory as this exchange
@public
def tokenToExchangeTransferExact(tokens_bought: uint256, max_tokens_sold: uint256, deadline: timestamp, recipent: address, exchange_addr: address) -> uint256:
    assert recipent != self
    return self.tokenToTokenExact(tokens_bought, max_tokens_sold, deadline, msg.sender, recipent, exchange_addr)

@public
@constant
def tokenAddress() -> address:
    return self.token

@public
@constant
def factoryAddress() -> address(Factory):
    return self.factory

# ERC20 compatibility for exchange liquidity modified from
# https://github.com/ethereum/vyper/blob/master/examples/tokens/ERC20_solidity_compatible/ERC20.v.py

@public
@constant
def balanceOf(_owner : address) -> uint256:
    return self.liquidity_balances[_owner]

@public
def transfer(_to : address, _value : uint256) -> bool:
    self.liquidity_balances[msg.sender] -= _value
    self.liquidity_balances[_to] += _value
    log.Transfer(msg.sender, _to, _value)
    return True

@public
def transferFrom(_from : address, _to : address, _value : uint256) -> bool:
    self.liquidity_balances[_from] -= _value
    self.liquidity_balances[_to] += _value
    self.liquidity_allowances[_from][msg.sender] -= _value
    log.Transfer(_from, _to, _value)
    return True

@public
def approve(_spender : address, _value : uint256) -> bool:
    self.liquidity_allowances[msg.sender][_spender] = _value
    log.Approval(msg.sender, _spender, _value)
    return True

@public
@constant
def allowance(_owner : address, _spender : address) -> uint256:
    return self.liquidity_allowances[_owner][_spender]
