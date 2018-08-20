contract Factory():
    def getExchange(token_addr: address) -> address: constant

contract Exchange():
    def ethToTokenExact(tokens_bought: uint256, eth_input: uint256(wei)) -> uint256(wei): constant
    def ethToTokenTransfer(recipent: address, token_amount: uint256, deadline: timestamp) -> uint256: modifying

TokenPurchase: event({buyer: indexed(address), eth_sold: indexed(uint256(wei)), tokens_bought: indexed(uint256)})
EthPurchase: event({buyer: indexed(address), tokens_sold: indexed(uint256), eth_bought: indexed(uint256(wei))})
AddLiquidity: event({provider: indexed(address), eth_amount: indexed(uint256(wei)), token_amount: indexed(uint256)})
RemoveLiquidity: event({provider: indexed(address), eth_amount: indexed(uint256(wei)), token_amount: indexed(uint256)})
Transfer: event({_from: indexed(address), _to: indexed(address), _value: uint256})
Approval: event({_owner: indexed(address), _spender: indexed(address), _value: uint256})

totalSupply: public(uint256)                            # total liquidity supply
liquidity_balances: uint256[address]                    # liquidity balance of an address
liquidity_allowances: (uint256[address])[address]       # liquidity allowance of one address on another
factoryAddress: public(address)                         # the factory that created this exchange
token: address(ERC20)                                   # the ERC20 token traded on this exchange
decimals: public(uint256)

# Called by factory during launch
# Replaces constructor which is not supported in contracts deployed using create_with_code_of()
@public
def setup(token_addr: address) -> bool:
    assert token_addr != ZERO_ADDRESS
    assert self.factoryAddress == ZERO_ADDRESS and self.token == ZERO_ADDRESS
    self.factoryAddress = msg.sender
    self.token = token_addr
    self.decimals = 18
    return True

# Add ETH and tokens to liquidity reserves at current price ratio
# Fees are added to liquidity increasing value over time
@public
@payable
def addLiquidity(amount: uint256, deadline: timestamp) -> uint256:
    assert deadline > block.timestamp
    assert amount > 0
    total_liquidity: uint256 = self.totalSupply
    if total_liquidity > 0:
        assert msg.value > 0
        eth_reserve: uint256(wei) = self.balance  - msg.value
        token_reserve: uint256 = self.token.balanceOf(self)
        liquidity_minted: uint256 = msg.value * total_liquidity / eth_reserve
        assert liquidity_minted > amount
        token_amount: uint256 = liquidity_minted * token_reserve / total_liquidity
        self.liquidity_balances[msg.sender] = self.liquidity_balances[msg.sender] + liquidity_minted
        self.totalSupply = total_liquidity + liquidity_minted
        assert self.token.transferFrom(msg.sender, self, token_amount)
        log.AddLiquidity(msg.sender, msg.value, token_amount)
        log.Transfer(ZERO_ADDRESS, msg.sender, liquidity_minted)
        return liquidity_minted
    else:
        assert self.factoryAddress != ZERO_ADDRESS and self.token != ZERO_ADDRESS
        assert msg.value >= 100000
        assert Factory(self.factoryAddress).getExchange(self.token) == self
        initial_liquidity: uint256 = as_unitless_number(self.balance)
        self.totalSupply = initial_liquidity
        self.liquidity_balances[msg.sender] = initial_liquidity
        assert self.token.transferFrom(msg.sender, self, amount)
        log.AddLiquidity(msg.sender, msg.value, amount)
        log.Transfer(ZERO_ADDRESS, msg.sender, initial_liquidity)
        return initial_liquidity

# Burn liquidity to receive ETH and tokens at current price ratio
@public
def removeLiquidity(amount: uint256, min_eth: uint256(wei), min_tokens: uint256, deadline: timestamp) -> bool:
    assert amount > 0 and deadline > block.timestamp
    assert min_eth > 0 and min_tokens > 0
    liquidity_total: uint256 = self.totalSupply
    token_reserve: uint256 = self.token.balanceOf(self)
    eth_amount: uint256(wei) = amount * self.balance / liquidity_total
    token_amount: uint256 = amount * token_reserve / liquidity_total
    assert eth_amount > min_eth and token_amount > min_tokens
    self.liquidity_balances[msg.sender] = self.liquidity_balances[msg.sender] - amount
    self.totalSupply = liquidity_total - amount
    assert self.token.transfer(msg.sender, token_amount)
    send(msg.sender, eth_amount)
    log.RemoveLiquidity(msg.sender, eth_amount, token_amount)
    log.Transfer(msg.sender, ZERO_ADDRESS, amount)
    return True

# Private function for determining eth to token exchange rate
@private
@constant
def ethToToken(eth_sold: uint256(wei)) -> uint256:
    # eth_reserve = eth_bal - eth_sold
    eth_bal: uint256(wei) = self.balance
    token_reserve: uint256 = self.token.balanceOf(self)
    fee: uint256(wei) = eth_sold / 400
    new_token_reserve: uint256 = (eth_bal - eth_sold) * token_reserve / (eth_bal - fee)
    return token_reserve - new_token_reserve

# Fallback function that converts received ETH to tokens
# User specifies exact input amount and minimum output amount
@public
@payable
def __default__():
    assert self.totalSupply > 0
    assert msg.value > 0
    token_amount: uint256 = self.ethToToken(msg.value)
    assert self.token.transfer(msg.sender, token_amount)
    log.TokenPurchase(msg.sender, msg.value, token_amount)

# Converts ETH to tokens, sender recieves tokens
# User specifies exact input amount and minimum output amount
@public
@payable
def ethToTokenSwap(min_tokens: uint256, deadline: timestamp) -> uint256:
    assert self.totalSupply > 0 and deadline > block.timestamp
    # assert self.totalSupply > 0 and deadline > block.timestamp
    assert msg.value > 0 and min_tokens > 0
    tokens_bought: uint256 = self.ethToToken(msg.value)
    assert tokens_bought >= min_tokens
    assert self.token.transfer(msg.sender, tokens_bought)
    log.TokenPurchase(msg.sender, msg.value, tokens_bought)
    return tokens_bought

# Converts ETH to tokens, recipent recieves tokens
# User specifies exact input amount and minimum output amount
@public
@payable
def ethToTokenTransfer(recipent: address, min_tokens: uint256, deadline: timestamp) -> uint256:
    assert self.totalSupply > 0 and deadline > block.timestamp
    assert msg.value > 0 and min_tokens > 0
    assert recipent != self and recipent != ZERO_ADDRESS
    eth_sold: uint256(wei) = msg.value
    tokens_bought: uint256 = self.ethToToken(eth_sold)
    assert tokens_bought >= min_tokens
    assert self.token.transfer(recipent, tokens_bought)
    log.TokenPurchase(msg.sender, eth_sold, tokens_bought)
    return tokens_bought

# Private function for determining eth to token exchange rate
@public
@constant
def ethToTokenExact(tokens_bought: uint256, eth_input: uint256(wei)) -> uint256(wei):
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
    assert self.totalSupply > 0 and deadline > block.timestamp
    assert msg.value > 0 and tokens_bought > 0
    eth_sold: uint256(wei) = self.ethToTokenExact(tokens_bought, msg.value)
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
def ethToTokenTransferExact(recipent: address, tokens_bought: uint256, deadline: timestamp) -> uint256(wei):
    assert self.totalSupply > 0 and deadline > block.timestamp
    assert msg.value > 0 and tokens_bought > 0
    assert recipent != self and recipent != ZERO_ADDRESS
    eth_sold: uint256(wei) = self.ethToTokenExact(tokens_bought, msg.value)
    # reverts if msg.value < eth_sold
    eth_refund: uint256(wei) = msg.value - eth_sold
    assert self.token.transfer(recipent, tokens_bought)
    send(msg.sender, eth_refund)
    log.TokenPurchase(msg.sender, eth_sold, tokens_bought)
    return eth_sold

# Private function for determining token to eth exchange rate
@private
@constant
def tokenToEth(tokens_sold: uint256) -> uint256(wei):
    eth_reserve: uint256(wei) = self.balance
    token_reserve: uint256 = self.token.balanceOf(self)
    fee: uint256 = tokens_sold / 400
    new_eth_reserve: uint256(wei) = eth_reserve * token_reserve / (token_reserve + tokens_sold - fee)
    return eth_reserve - new_eth_reserve

# Converts tokens to ETH, sender recieves tokens
# User specifies exact input amount and minimum output amount
@public
@payable
def tokenToEthSwap(tokens_sold: uint256, min_eth: uint256(wei), deadline: timestamp) -> uint256(wei):
    assert self.totalSupply > 0 and deadline > block.timestamp
    assert tokens_sold > 0 and min_eth > 0
    eth_bought: uint256(wei) = self.tokenToEth(tokens_sold)
    assert eth_bought >= min_eth
    assert self.token.transferFrom(msg.sender, self, tokens_sold)
    send(msg.sender, eth_bought)
    log.EthPurchase(msg.sender, tokens_sold, eth_bought)
    return eth_bought

# Converts tokens to ETH, recipent recieves tokens
# User specifies exact input amount and minimum output amount
@public
@payable
def tokenToEthTransfer(recipent: address, tokens_sold: uint256, min_eth: uint256(wei), deadline: timestamp) -> uint256(wei):
    assert self.totalSupply > 0 and deadline > block.timestamp
    assert tokens_sold > 0 and min_eth > 0
    assert recipent != self and recipent != ZERO_ADDRESS
    eth_bought: uint256(wei) = self.tokenToEth(tokens_sold)
    assert eth_bought >= min_eth
    assert self.token.transferFrom(msg.sender, self, tokens_sold)
    send(recipent, eth_bought)
    log.EthPurchase(msg.sender, tokens_sold, eth_bought)
    return eth_bought

# Private function for determining token to eth exchange rate
@public
@constant
def tokenToEthExact(eth_bought: uint256(wei)) -> uint256:
    eth_reserve: uint256(wei) = self.balance
    token_reserve: uint256 = self.token.balanceOf(self)
    new_eth_reserve: uint256(wei) = eth_reserve - eth_bought
    new_token_reserve: uint256 = eth_reserve * token_reserve / new_eth_reserve
    return (new_token_reserve - token_reserve) * 400 / 399

# Converts tokens to ETH, sender recieves tokens
# User specifies maximum input amount and exact output amount
@public
@payable
def tokenToEthSwapExact(max_tokens: uint256, eth_bought: uint256(wei), deadline: timestamp) -> uint256:
    assert self.totalSupply > 0 and deadline > block.timestamp
    assert max_tokens > 0 and eth_bought > 0
    tokens_sold: uint256 = self.tokenToEthExact(eth_bought)
    assert max_tokens >= tokens_sold
    assert self.token.transferFrom(msg.sender, self, tokens_sold)
    send(msg.sender, eth_bought)
    log.EthPurchase(msg.sender, tokens_sold, eth_bought)
    return tokens_sold

# Converts tokens to ETH, recipent recieves tokens
# User specifies maximum input amount and exact output amount
@public
@payable
def tokenToEthTransferExact(recipent: address, max_tokens: uint256, eth_amount: uint256(wei), deadline: timestamp) -> uint256:
    assert self.totalSupply > 0 and deadline > block.timestamp
    assert max_tokens > 0 and eth_amount > 0
    assert recipent != self and recipent != ZERO_ADDRESS
    tokens_sold: uint256 = self.tokenToEthExact(eth_amount)
    assert max_tokens >= tokens_sold
    assert self.token.transferFrom(msg.sender, self, tokens_sold)
    send(recipent, eth_amount)
    log.EthPurchase(msg.sender, tokens_sold, eth_amount)
    return tokens_sold

# Converts tokens to tokens, sender recieves tokens
# User specifies exact input amount and minimum output amount
@public
@payable
def tokenToTokenSwap(token_addr: address, tokens_sold: uint256, min_tokens_bought: uint256, deadline: timestamp) -> uint256:
    assert self.totalSupply > 0 and deadline > block.timestamp
    assert tokens_sold > 0 and min_tokens_bought > 0
    exchange_addr: address = Factory(self.factoryAddress).getExchange(token_addr)
    assert exchange_addr != ZERO_ADDRESS and exchange_addr != self
    eth_amount: uint256(wei) = self.tokenToEth(tokens_sold)
    assert self.token.transferFrom(msg.sender, self, tokens_sold)
    tokens_bought: uint256 = Exchange(exchange_addr).ethToTokenTransfer(msg.sender, min_tokens_bought, deadline, value=eth_amount)
    assert tokens_bought >= min_tokens_bought
    log.EthPurchase(msg.sender, tokens_sold, eth_amount)
    return tokens_bought

# Converts tokens to tokens, recipent recieves tokens
# User specifies exact input amount and minimum output amount
@public
@payable
def tokenToTokenTransfer(token_addr: address, recipent: address, tokens_sold: uint256, min_tokens_bought: uint256, deadline: timestamp) -> uint256:
    assert self.totalSupply > 0 and deadline > block.timestamp
    assert tokens_sold > 0 and min_tokens_bought > 0
    assert recipent != self and recipent != ZERO_ADDRESS
    exchange_addr: address = Factory(self.factoryAddress).getExchange(token_addr)
    assert exchange_addr != ZERO_ADDRESS and exchange_addr != self
    eth_amount: uint256(wei) = self.tokenToEth(tokens_sold)
    assert self.token.transferFrom(msg.sender, self, tokens_sold)
    tokens_bought: uint256 = Exchange(exchange_addr).ethToTokenTransfer(recipent, min_tokens_bought, deadline, value=eth_amount)
    assert tokens_bought >= min_tokens_bought
    log.EthPurchase(msg.sender, tokens_sold, eth_amount)
    return tokens_bought

# Converts tokens to tokens, sender recieves tokens
# User specifies maximum input amount and exact output amount
@public
@payable
def tokenToTokenSwapExact(token_addr: address, max_tokens_sold: uint256, tokens_bought: uint256, deadline: timestamp, exact_output: bool) -> uint256:
    assert self.totalSupply > 0 and deadline > block.timestamp
    assert max_tokens_sold > 0 and tokens_bought > 0
    exchange_addr: address = Factory(self.factoryAddress).getExchange(token_addr)
    assert exchange_addr != ZERO_ADDRESS and exchange_addr != self
    eth_required: uint256(wei) = Exchange(exchange_addr).ethToTokenExact(tokens_bought, 0)
    tokens_sold: uint256 = self.tokenToEthExact(eth_required)
    assert tokens_sold <= max_tokens_sold
    assert self.token.transferFrom(msg.sender, self, tokens_sold)
    assert Exchange(exchange_addr).ethToTokenTransfer(msg.sender, 1, deadline, value=eth_required)
    log.EthPurchase(msg.sender, tokens_sold, eth_required)
    return tokens_sold

# Converts tokens to tokens, recipent recieves tokens
# User specifies maximum input amount and exact output amount
@public
@payable
def tokenToTokenTransferExact(token_addr: address, recipent: address, max_tokens_sold: uint256, tokens_bought: uint256, deadline: timestamp) -> uint256:
    assert self.totalSupply > 0 and deadline > block.timestamp
    assert max_tokens_sold > 0 and tokens_bought > 0
    assert recipent != self and recipent != ZERO_ADDRESS
    exchange_addr: address = Factory(self.factoryAddress).getExchange(token_addr)
    assert exchange_addr != ZERO_ADDRESS and exchange_addr != self
    eth_required: uint256(wei) = Exchange(exchange_addr).ethToTokenExact(tokens_bought, 0)
    tokens_sold: uint256 = self.tokenToEthExact(eth_required)
    assert tokens_sold <= max_tokens_sold
    assert self.token.transferFrom(msg.sender, self, tokens_sold)
    assert Exchange(exchange_addr).ethToTokenTransfer(recipent, 1, deadline, value=eth_required)
    log.EthPurchase(msg.sender, tokens_sold, eth_required)
    return tokens_sold

# Converts tokens to tokens, recipent recieves tokens
# User specifies exact input amount and minimum output amount
# This function allows token to token trades across exchanges that were not created in the same factory as this exchange
@public
@payable
def tokenToExchangeTransfer(exchange_addr: address, recipent: address, tokens_sold: uint256, min_tokens_bought: uint256, deadline: timestamp) -> uint256:
    assert self.totalSupply > 0 and deadline > block.timestamp
    assert tokens_sold > 0 and min_tokens_bought > 0
    assert recipent != self and recipent != ZERO_ADDRESS
    assert exchange_addr != ZERO_ADDRESS and exchange_addr != self
    eth_amount: uint256(wei) = self.tokenToEth(tokens_sold)
    assert self.token.transferFrom(msg.sender, self, tokens_sold)
    tokens_bought: uint256 = Exchange(exchange_addr).ethToTokenTransfer(recipent, min_tokens_bought, deadline, value=eth_amount)
    assert tokens_bought >= min_tokens_bought
    log.EthPurchase(msg.sender, tokens_sold, eth_amount)
    return tokens_bought

# Converts tokens to tokens, recipent recieves tokens
# User specifies maximum input amount and exact output amount
# This function allows token to token trades across exchanges that were not created in the same factory as this exchange
@public
@payable
def tokenToExchangeTransferExact(exchange_addr: address, recipent: address, max_tokens_sold: uint256, tokens_bought: uint256, deadline: timestamp) -> uint256:
    assert self.totalSupply > 0 and deadline > block.timestamp
    assert max_tokens_sold > 0 and tokens_bought > 0
    assert recipent != self and recipent != ZERO_ADDRESS
    assert exchange_addr != ZERO_ADDRESS and exchange_addr != self
    eth_required: uint256(wei) = Exchange(exchange_addr).ethToTokenExact(tokens_bought, 0)
    tokens_sold: uint256 = self.tokenToEthExact(eth_required)
    assert tokens_sold <= max_tokens_sold
    assert self.token.transferFrom(msg.sender, self, tokens_sold)
    assert Exchange(exchange_addr).ethToTokenTransfer(recipent, 1, deadline, value=eth_required)
    log.EthPurchase(msg.sender, tokens_sold, eth_required)
    return tokens_sold

@public
@constant
def tokenAddress() -> address:
    return self.token

# ERC20 compatibility for exchange liquidity modified from
# https://github.com/ethereum/vyper/blob/master/examples/tokens/ERC20_solidity_compatible/ERC20.v.py

@public
@constant
def balanceOf(_owner : address) -> uint256:
    return self.liquidity_balances[_owner]

@public
def transfer(_to : address, _value : uint256) -> bool:
    _sender: address = msg.sender
    self.liquidity_balances[_sender] = self.liquidity_balances[_sender] - _value
    self.liquidity_balances[_to] = self.liquidity_balances[_to] + _value
    log.Transfer(_sender, _to, _value)
    return True

@public
def transferFrom(_from : address, _to : address, _value : uint256) -> bool:
    _sender: address = msg.sender
    allowance: uint256 = self.liquidity_allowances[_from][_sender]
    self.liquidity_balances[_from] = self.liquidity_balances[_from] - _value
    self.liquidity_balances[_to] = self.liquidity_balances[_to] + _value
    self.liquidity_allowances[_from][_sender] = allowance - _value
    log.Transfer(_from, _to, _value)
    return True

@public
def approve(_spender : address, _value : uint256) -> bool:
    _sender: address = msg.sender
    self.liquidity_allowances[_sender][_spender] = _value
    log.Approval(_sender, _spender, _value)
    return True

@public
@constant
def allowance(_owner : address, _spender : address) -> uint256:
    return self.liquidity_allowances[_owner][_spender]
