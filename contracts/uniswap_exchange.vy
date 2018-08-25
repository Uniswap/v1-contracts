contract Factory():
    def getExchange(token_addr: address) -> address: constant

contract Exchange():
    def ethToTokenExactPrice(tokens_bought: uint256, eth_input: uint256(wei)) -> uint256(wei): constant
    def ethToTokenTransfer(min_tokens: uint256, deadline: timestamp, recipent: address) -> uint256: modifying

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
    assert self.factory == ZERO_ADDRESS and self.token == ZERO_ADDRESS
    assert token_addr != ZERO_ADDRESS
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
    assert deadline > block.timestamp
    assert min_amount > 0
    total_liquidity: uint256 = self.totalSupply
    if total_liquidity > 0:
        assert msg.value > 0
        eth_reserve: uint256(wei) = self.balance - msg.value
        token_reserve: uint256 = self.token.balanceOf(self)
        liquidity_minted: uint256 = msg.value * total_liquidity / eth_reserve
        assert liquidity_minted > min_amount
        token_amount: uint256 = liquidity_minted * token_reserve / total_liquidity
        self.liquidity_balances[msg.sender] += liquidity_minted
        self.totalSupply = total_liquidity + liquidity_minted
        assert self.token.transferFrom(msg.sender, self, token_amount)
        log.AddLiquidity(msg.sender, msg.value, token_amount)
        log.Transfer(ZERO_ADDRESS, msg.sender, liquidity_minted)
        return liquidity_minted
    else:
        assert self.factory != ZERO_ADDRESS and self.token != ZERO_ADDRESS
        assert msg.value >= 1000000000
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
    assert amount > 0 and deadline > block.timestamp
    assert min_eth > 0 and min_tokens > 0
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

# Function for determining eth to token exchange rate
@public
@constant
def ethToTokenPrice(eth_sold: uint256(wei), min_tokens: uint256) -> uint256:
    assert eth_sold > 0 and min_tokens > 0
    # eth_reserve = eth_bal - eth_sold
    eth_bal: uint256(wei) = self.balance
    token_reserve: uint256 = self.token.balanceOf(self)
    fee: uint256(wei) = eth_sold / 400
    new_token_reserve: uint256 = (eth_bal - eth_sold) * token_reserve / (eth_bal - fee)
    tokens_bought: uint256 =  token_reserve - new_token_reserve
    assert tokens_bought >= min_tokens
    return tokens_bought

# Fallback function that converts received ETH to tokens
# User specifies exact input amount and minimum output amount
@public
@payable
def __default__():
    assert self.totalSupply > 0
    tokens_bought: uint256 = self.ethToTokenPrice(msg.value, 1)
    assert self.token.transfer(msg.sender, tokens_bought)
    log.TokenPurchase(msg.sender, msg.value, tokens_bought)

# Converts ETH to tokens, sender recieves tokens
# User specifies exact input amount and minimum output amount
@public
@payable
def ethToTokenSwap(min_tokens: uint256, deadline: timestamp) -> uint256:
    assert self.totalSupply > 0 and deadline >= block.timestamp
    tokens_bought: uint256 = self.ethToTokenPrice(msg.value, min_tokens)
    assert self.token.transfer(msg.sender, tokens_bought)
    log.TokenPurchase(msg.sender, msg.value, tokens_bought)
    return tokens_bought

# Converts ETH to tokens, recipent recieves tokens
# User specifies exact input amount and minimum output amount
@public
@payable
def ethToTokenTransfer(min_tokens: uint256, deadline: timestamp, recipent: address) -> uint256:
    assert self.totalSupply > 0 and deadline >= block.timestamp
    assert recipent != self and recipent != ZERO_ADDRESS
    tokens_bought: uint256 = self.ethToTokenPrice(msg.value, min_tokens)
    assert self.token.transfer(recipent, tokens_bought)
    log.TokenPurchase(msg.sender, msg.value, tokens_bought)
    return tokens_bought

# Function for determining eth to token exchange rate
@public
@constant
def ethToTokenExactPrice(tokens_bought: uint256, eth_input: uint256(wei)) -> uint256(wei):
    assert tokens_bought > 0
    eth_reserve: uint256(wei) = self.balance - eth_input
    token_reserve: uint256 = self.token.balanceOf(self)
    new_token_reserve: uint256 = token_reserve - tokens_bought
    new_eth_reserve: uint256(wei) = eth_reserve * token_reserve / new_token_reserve
    return (new_eth_reserve - eth_reserve) * 400 / 399

# Converts ETH to tokens, sender recieves tokens
# User specifies maximum input amount and exact output amount
@public
@payable
def ethToTokenSwapExact(tokens_bought: uint256, deadline: timestamp) -> uint256(wei):
    assert self.totalSupply > 0 and deadline >= block.timestamp
    assert msg.value > 0
    eth_sold: uint256(wei) = self.ethToTokenExactPrice(tokens_bought, msg.value)
    # reverts if msg.value < eth_sold
    eth_refund: uint256(wei) = msg.value - eth_sold
    assert self.token.transfer(msg.sender, tokens_bought)
    send(msg.sender, eth_refund)
    log.TokenPurchase(msg.sender, eth_sold, tokens_bought)
    return eth_refund

# Converts ETH to tokens, recipent recieves tokens
# User specifies maximum input amount and exact output amount
@public
@payable
def ethToTokenTransferExact(tokens_bought: uint256, deadline: timestamp, recipent: address) -> uint256(wei):
    assert self.totalSupply > 0 and deadline >= block.timestamp
    assert msg.value > 0
    assert recipent != self and recipent != ZERO_ADDRESS
    eth_sold: uint256(wei) = self.ethToTokenExactPrice(tokens_bought, msg.value)
    # reverts if msg.value < eth_sold
    eth_refund: uint256(wei) = msg.value - eth_sold
    assert self.token.transfer(recipent, tokens_bought)
    send(msg.sender, eth_refund)
    log.TokenPurchase(msg.sender, eth_sold, tokens_bought)
    return eth_sold

# Function for determining token to eth exchange rate
@public
@constant
def tokenToEthPrice(tokens_sold: uint256, min_eth: uint256(wei)) -> uint256(wei):
    assert tokens_sold > 0 and min_eth > 0
    eth_reserve: uint256(wei) = self.balance
    token_reserve: uint256 = self.token.balanceOf(self)
    fee: uint256 = tokens_sold / 400
    new_eth_reserve: uint256(wei) = eth_reserve * token_reserve / (token_reserve + tokens_sold - fee)
    eth_bought: uint256(wei) =  eth_reserve - new_eth_reserve
    assert eth_bought >= min_eth
    return eth_bought

# Converts tokens to ETH, sender recieves tokens
# User specifies exact input amount and minimum output amount
@public
@payable
def tokenToEthSwap(tokens_sold: uint256, min_eth: uint256(wei), deadline: timestamp) -> uint256(wei):
    assert self.totalSupply > 0 and deadline >= block.timestamp
    eth_bought: uint256(wei) = self.tokenToEthPrice(tokens_sold, min_eth)
    assert self.token.transferFrom(msg.sender, self, tokens_sold)
    send(msg.sender, eth_bought)
    log.EthPurchase(msg.sender, tokens_sold, eth_bought)
    return eth_bought

# Converts tokens to ETH, recipent recieves tokens
# User specifies exact input amount and minimum output amount
@public
@payable
def tokenToEthTransfer(tokens_sold: uint256, min_eth: uint256(wei), deadline: timestamp, recipent: address) -> uint256(wei):
    assert self.totalSupply > 0 and deadline >= block.timestamp
    assert recipent != self and recipent != ZERO_ADDRESS
    eth_bought: uint256(wei) = self.tokenToEthPrice(tokens_sold, min_eth)
    assert self.token.transferFrom(msg.sender, self, tokens_sold)
    send(recipent, eth_bought)
    log.EthPurchase(msg.sender, tokens_sold, eth_bought)
    return eth_bought

# Function for determining token to eth exchange rate
@public
@constant
def tokenToEthExactPrice(eth_bought: uint256(wei), max_tokens: uint256) -> uint256:
    assert max_tokens > 0 and eth_bought > 0
    eth_reserve: uint256(wei) = self.balance
    token_reserve: uint256 = self.token.balanceOf(self)
    new_eth_reserve: uint256(wei) = eth_reserve - eth_bought
    new_token_reserve: uint256 = eth_reserve * token_reserve / new_eth_reserve
    tokens_sold: uint256 = (new_token_reserve - token_reserve) * 400 / 399
    assert max_tokens >= tokens_sold
    return tokens_sold

# Converts tokens to ETH, sender recieves tokens
# User specifies maximum input amount and exact output amount
@public
@payable
def tokenToEthSwapExact(eth_bought: uint256(wei), max_tokens: uint256, deadline: timestamp) -> uint256:
    assert self.totalSupply > 0 and deadline >= block.timestamp
    tokens_sold: uint256 = self.tokenToEthExactPrice(eth_bought, max_tokens)
    assert self.token.transferFrom(msg.sender, self, tokens_sold)
    send(msg.sender, eth_bought)
    log.EthPurchase(msg.sender, tokens_sold, eth_bought)
    return tokens_sold

# Converts tokens to ETH, recipent recieves tokens
# User specifies maximum input amount and exact output amount
@public
@payable
def tokenToEthTransferExact(eth_bought: uint256(wei), max_tokens: uint256, deadline: timestamp, recipent: address) -> uint256:
    assert self.totalSupply > 0 and deadline >= block.timestamp
    assert recipent != self and recipent != ZERO_ADDRESS
    tokens_sold: uint256 = self.tokenToEthExactPrice(eth_bought, max_tokens)
    assert self.token.transferFrom(msg.sender, self, tokens_sold)
    send(recipent, eth_bought)
    log.EthPurchase(msg.sender, tokens_sold, eth_bought)
    return tokens_sold

# Converts tokens to tokens, sender recieves tokens
# User specifies exact input amount and minimum output amount
# TODO: add min_eth
@public
@payable
def tokenToTokenSwap(tokens_sold: uint256, min_tokens_bought: uint256, deadline: timestamp, token_addr: address) -> uint256:
    assert self.totalSupply > 0 and deadline >= block.timestamp
    # returns ZERO_ADDRESS if no exchange exists for token_addr
    exchange_addr: address = self.factory.getExchange(token_addr)
    assert exchange_addr != self
    eth_bought: uint256(wei) = self.tokenToEthPrice(tokens_sold, 1)
    assert self.token.transferFrom(msg.sender, self, tokens_sold)
    # call fails if exchange_addr == ZERO_ADDRESS
    tokens_bought: uint256 = Exchange(exchange_addr).ethToTokenTransfer(min_tokens_bought, deadline, msg.sender, value=eth_bought)
    log.EthPurchase(msg.sender, tokens_sold, eth_bought)
    return tokens_bought


# Converts tokens to tokens, recipent recieves tokens
# User specifies exact input amount and minimum output amount
@public
@payable
def tokenToTokenTransfer(tokens_sold: uint256, min_tokens_bought: uint256, deadline: timestamp, recipent: address, token_addr: address) -> uint256:
    assert self.totalSupply > 0 and deadline >= block.timestamp
    exchange_addr: address = self.factory.getExchange(token_addr)
    assert recipent != self and exchange_addr != self
    eth_bought: uint256(wei) = self.tokenToEthPrice(tokens_sold, 1)
    assert self.token.transferFrom(msg.sender, self, tokens_sold)
    tokens_bought: uint256 = Exchange(exchange_addr).ethToTokenTransfer(min_tokens_bought, deadline, recipent, value=eth_bought)
    log.EthPurchase(msg.sender, tokens_sold, eth_bought)
    return tokens_bought

# Converts tokens to tokens, sender recieves tokens
# User specifies maximum input amount and exact output amount
@public
@payable
def tokenToTokenSwapExact(tokens_bought: uint256, max_tokens_sold: uint256, deadline: timestamp, token_addr: address) -> uint256:
    assert self.totalSupply > 0 and deadline >= block.timestamp
    exchange_addr: address = self.factory.getExchange(token_addr)
    assert exchange_addr != self
    eth_bought: uint256(wei) = Exchange(exchange_addr).ethToTokenExactPrice(tokens_bought, 0)
    tokens_sold: uint256 = self.tokenToEthExactPrice(eth_bought, max_tokens_sold)
    assert self.token.transferFrom(msg.sender, self, tokens_sold)
    assert Exchange(exchange_addr).ethToTokenTransfer(tokens_bought, deadline, msg.sender, value=eth_bought)
    log.EthPurchase(msg.sender, tokens_sold, eth_bought)
    return tokens_sold

# Converts tokens to tokens, recipent recieves tokens
# User specifies maximum input amount and exact output amount
@public
@payable
def tokenToTokenTransferExact(tokens_bought: uint256, max_tokens_sold: uint256, deadline: timestamp, recipent: address, token_addr: address) -> uint256:
    assert self.totalSupply > 0 and deadline >= block.timestamp
    exchange_addr: address = self.factory.getExchange(token_addr)
    assert recipent != self and exchange_addr != self
    eth_bought: uint256(wei) = Exchange(exchange_addr).ethToTokenExactPrice(tokens_bought, 0)
    tokens_sold: uint256 = self.tokenToEthExactPrice(eth_bought, max_tokens_sold)
    assert self.token.transferFrom(msg.sender, self, tokens_sold)
    assert Exchange(exchange_addr).ethToTokenTransfer(tokens_bought, deadline, recipent, value=eth_bought)
    log.EthPurchase(msg.sender, tokens_sold, eth_bought)
    return tokens_sold

# Converts tokens to tokens, recipent recieves tokens
# User specifies exact input amount and minimum output amount
# This function allows token to token trades across exchanges that were not created in the same factory as this exchange
@public
@payable
def tokenToExchangeTransfer(tokens_sold: uint256, min_tokens_bought: uint256, deadline: timestamp, recipent: address, exchange_addr: address) -> uint256:
    assert self.totalSupply > 0 and deadline >= block.timestamp
    assert recipent != self and exchange_addr != self
    eth_bought: uint256(wei) = self.tokenToEthPrice(tokens_sold, 1)
    assert self.token.transferFrom(msg.sender, self, tokens_sold)
    tokens_bought: uint256 = Exchange(exchange_addr).ethToTokenTransfer(min_tokens_bought, deadline, recipent, value=eth_bought)
    log.EthPurchase(msg.sender, tokens_sold, eth_bought)
    return tokens_bought

# Converts tokens to tokens, recipent recieves tokens
# User specifies maximum input amount and exact output amount
# This function allows token to token trades across exchanges that were not created in the same factory as this exchange
@public
@payable
def tokenToExchangeTransferExact(tokens_bought: uint256, max_tokens_sold: uint256, deadline: timestamp, recipent: address, exchange_addr: address) -> uint256:
    assert self.totalSupply > 0 and deadline >= block.timestamp
    assert recipent != self and exchange_addr != self
    eth_bought: uint256(wei) = Exchange(exchange_addr).ethToTokenExactPrice(tokens_bought, 0)
    tokens_sold: uint256 = self.tokenToEthExactPrice(eth_bought, max_tokens_sold)
    assert self.token.transferFrom(msg.sender, self, tokens_sold)
    assert Exchange(exchange_addr).ethToTokenTransfer(1, deadline, recipent, value=eth_bought)
    log.EthPurchase(msg.sender, tokens_sold, eth_bought)
    return tokens_sold

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
