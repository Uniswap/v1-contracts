contract Factory():
    def getExchange(token_addr: address) -> address: constant

contract Exchange():
    def getTokenCost(tokens_bought: uint256) -> uint256(wei): constant
    def ethToTokenTransfer(recipent: address, token_amount: uint256, deadline: uint256) -> bool: modifying

contract Token():
    def balanceOf(_owner : address) -> uint256: constant

EthToToken: event({buyer: indexed(address), eth_sold: indexed(uint256(wei)), tokens_bought: indexed(uint256)})
TokenToEth: event({buyer: indexed(address), tokens_sold: indexed(uint256), eth_bought: indexed(uint256(wei))})
Investment: event({investor: indexed(address), eth_invested: indexed(uint256(wei)), tokens_invested: indexed(uint256)})
Divestment: event({investor: indexed(address), eth_divested: indexed(uint256(wei)), tokens_divested: indexed(uint256)})
Transfer: event({_from: indexed(address), _to: indexed(address), _value: uint256})
Approval: event({_owner: indexed(address), _spender: indexed(address), _value: uint256})

total_shares: uint256                                # total share supply
shares: uint256[address]                             # share balance of an address
share_allowances: (uint256[address])[address]        # share allowance of one adddress on another
factoryAddress: public(address)                      # the factory that created this exchange
token: address(ERC20)                                # the ERC20 token traded on this exchange

# Called by factory during launch
# Replaces constructor which is not supported in contracts deployed with create_with_code_of()
@public
@payable
def setup(token_addr: address) -> bool:
    assert self.factoryAddress == ZERO_ADDRESS and self.token == ZERO_ADDRESS
    self.factoryAddress = msg.sender
    self.token = token_addr
    assert self.factoryAddress != ZERO_ADDRESS and self.token != ZERO_ADDRESS
    return True

# Sets initial token pool, ETH pool, and share amount
@public
@payable
def initialize(tokens_invested: uint256) -> bool:
    assert self.total_shares == 0
    assert self.factoryAddress != ZERO_ADDRESS and self.token != ZERO_ADDRESS
    assert msg.value >= 1000000 and tokens_invested >= 1000000
    assert Factory(self.factoryAddress).getExchange(self.token) == self
    self.total_shares = as_unitless_number(self.balance)
    self.shares[msg.sender] = as_unitless_number(self.balance)
    # initial_tokens: uint256 = self.token.balanceOf(self)
    self.token.transferFrom(msg.sender, self, tokens_invested)
    # Safer than assert transferFrom() because not all ERC20 transferFrom() implementations return bools
    # assert self.token.balanceOf(self) == initial_tokens + tokens_invested
    assert self.total_shares > 0 and self.balance > 0
    log.Investment(msg.sender, msg.value, tokens_invested)
    return True

# Lock up ETH and tokens at current price ratio
# Shares are minted proportional to liquidity invested
# Trading fees are added to liquidity pools increasing value of shares over time
# log transfer event for token minting
@public
@payable
def addLiquidity(min_shares: uint256, deadline: uint256) -> bool:
    assert msg.value > 0 and deadline > as_unitless_number(block.timestamp)
    share_total: uint256 = self.total_shares
    assert share_total > 0 and min_shares > 0
    eth_invested: uint256(wei) = msg.value
    eth_pool: uint256(wei) = self.balance  - eth_invested
    token_pool: uint256 = self.token.balanceOf(self)
    shares_minted: uint256 = (eth_invested * share_total) / eth_pool
    assert shares_minted > min_shares
    tokens_invested: uint256 = (shares_minted * token_pool) / share_total
    self.shares[msg.sender] = self.shares[msg.sender] + shares_minted
    self.total_shares = share_total + shares_minted
    self.token.transferFrom(msg.sender, self, tokens_invested)
    log.Investment(msg.sender, eth_invested, tokens_invested)
    return True

# Burn shares to receive ETH and tokens at current price ratio
@public
def removeLiquidity(shares_burned: uint256, min_eth: uint256(wei), min_tokens: uint256, deadline: uint256) -> bool:
    assert shares_burned > 0 and deadline > as_unitless_number(block.timestamp)
    assert min_eth > 0 and min_tokens > 0
    share_total: uint256 = self.total_shares
    token_pool: uint256 = self.token.balanceOf(self)
    eth_divested: uint256(wei) = (shares_burned * self.balance) / share_total
    tokens_divested: uint256 = (shares_burned * token_pool) / share_total
    assert eth_divested > min_eth and tokens_divested > min_tokens
    self.shares[msg.sender] = self.shares[msg.sender] - shares_burned
    self.total_shares = share_total - shares_burned
    self.token.transfer(msg.sender, tokens_divested)
    send(msg.sender, eth_divested)
    log.Divestment(msg.sender, eth_divested, tokens_divested)
    return True

@private
@constant
def ethToToken(eth_sold: uint256(wei)) -> uint256:
    eth_pool: uint256(wei) = self.balance - eth_sold
    token_pool: uint256 = self.token.balanceOf(self)
    fee: uint256(wei) = eth_sold / 500
    new_token_pool: uint256 = (eth_pool * token_pool) / (eth_pool + eth_sold - fee)
    return token_pool - new_token_pool

@private
@constant
def ethToTokenExact(token_amount: uint256, max_eth: uint256(wei)) -> uint256(wei):
    eth_pool: uint256(wei) = self.balance - max_eth
    token_pool: uint256 = self.token.balanceOf(self)
    new_token_pool: uint256 = token_pool - token_amount
    new_eth_pool: uint256(wei) = (eth_pool * token_pool) / new_token_pool
    return (new_eth_pool - eth_pool) * 500 / 499

# Fallback function that converts received ETH to tokens
@public
@payable
def __default__():
    token_amount: uint256 = self.ethToToken(msg.value)
    self.token.transfer(msg.sender, token_amount)
    log.EthToToken(msg.sender, msg.value, token_amount)

# Converts ETH to tokens, sender recieves tokens
@public
@payable
def ethToTokenSwap(min_output: uint256, deadline: uint256) -> uint256:
    assert self.total_shares > 0 and deadline > as_unitless_number(block.timestamp)
    assert msg.value > 0 and min_output > 0
    tokens_bought: uint256 = self.ethToToken(msg.value)
    assert tokens_bought >= min_output
    self.token.transfer(msg.sender, tokens_bought)
    log.EthToToken(msg.sender, msg.value, tokens_bought)
    return tokens_bought

# Converts ETH to tokens, sender recieves tokens
@public
@payable
def ethToTokenSwapExact(tokens_bought: uint256, deadline: uint256) -> uint256:
    assert self.total_shares > 0 and deadline > as_unitless_number(block.timestamp)
    assert msg.value > 0 and tokens_bought > 0
    eth_sold: uint256(wei) = self.ethToTokenExact(tokens_bought, msg.value)
    # reverts if msg.value < eth_sold
    eth_refund: uint256(wei) = msg.value - eth_sold
    self.token.transfer(msg.sender, tokens_bought)
    send(msg.sender, eth_refund)
    log.EthToToken(msg.sender, eth_sold, tokens_bought)
    return as_unitless_number(eth_refund)

# Converts ETH to tokens, recipent recieves tokens
@public
@payable
def ethToTokenTransfer(recipent: address, min_tokens: uint256, deadline: uint256) -> uint256:
    assert self.total_shares > 0 and deadline > as_unitless_number(block.timestamp)
    assert msg.value > 0 and min_tokens > 0
    assert recipent != self and recipent != ZERO_ADDRESS
    eth_sold: uint256(wei) = msg.value
    tokens_bought: uint256 = self.ethToToken(eth_sold)
    assert tokens_bought >= min_tokens
    self.token.transfer(recipent, tokens_bought)
    log.EthToToken(msg.sender, eth_sold, tokens_bought)
    return tokens_bought

# Converts ETH to tokens, recipent recieves tokens
@public
@payable
def ethToTokenTransferExact(recipent: address, tokens_bought: uint256, deadline: uint256) -> uint256:
    assert self.total_shares > 0 and deadline > as_unitless_number(block.timestamp)
    assert msg.value > 0 and tokens_bought > 0
    assert recipent != self and recipent != ZERO_ADDRESS
    eth_sold: uint256(wei) = self.ethToTokenExact(tokens_bought, msg.value)
    # reverts if msg.value < eth_sold
    eth_refund: uint256(wei) = msg.value - eth_sold
    self.token.transfer(recipent, tokens_bought)
    send(msg.sender, eth_refund)
    log.EthToToken(msg.sender, eth_sold, tokens_bought)
    return as_unitless_number(eth_sold)

@private
@constant
def tokenToEth(tokens_sold: uint256) -> uint256(wei):
    eth_pool: uint256(wei) = self.balance
    token_pool: uint256 = self.token.balanceOf(self)
    fee: uint256 = tokens_sold / 500
    new_eth_pool: uint256(wei) = (eth_pool * token_pool) / (token_pool + tokens_sold - fee)
    return eth_pool - new_eth_pool

@private
@constant
def tokenToEthExact(eth_bought: uint256(wei)) -> uint256:
    eth_pool: uint256(wei) = self.balance
    token_pool: uint256 = self.token.balanceOf(self)
    new_eth_pool: uint256(wei) = eth_pool - eth_bought
    new_token_pool: uint256 = (eth_pool * token_pool) / new_eth_pool
    return (new_token_pool - token_pool) * 500 / 499

# Converts tokens to ETH, sender recieves tokens
@public
@payable
def tokenToEthSwap(tokens_sold: uint256, min_eth: uint256(wei), deadline: uint256) -> uint256:
    assert self.total_shares > 0 and deadline > as_unitless_number(block.timestamp)
    assert tokens_sold > 0 and min_eth > 0
    eth_bought: uint256(wei) = self.tokenToEth(tokens_sold)
    assert eth_bought >= min_eth
    self.token.transferFrom(msg.sender, self, tokens_sold)
    send(msg.sender, eth_bought)
    log.TokenToEth(msg.sender, tokens_sold, eth_bought)
    return as_unitless_number(eth_bought)

# Converts tokens to ETH, sender recieves tokens
@public
@payable
def tokenToEthSwapExact(max_tokens: uint256, eth_bought: uint256(wei), deadline: uint256) -> uint256:
    assert self.total_shares > 0 and deadline > as_unitless_number(block.timestamp)
    assert max_tokens > 0 and eth_bought > 0
    tokens_sold: uint256 = self.tokenToEthExact(eth_bought)
    assert max_tokens >= tokens_sold
    self.token.transferFrom(msg.sender, self, tokens_sold)
    send(msg.sender, eth_bought)
    log.TokenToEth(msg.sender, tokens_sold, eth_bought)
    return tokens_sold

# Converts tokens to ETH, recipent recieves tokens
@public
@payable
def tokenToEthTransfer(recipent: address, tokens_sold: uint256, min_eth: uint256(wei), deadline: uint256) -> uint256:
    assert self.total_shares > 0 and deadline > as_unitless_number(block.timestamp)
    assert tokens_sold > 0 and min_eth > 0
    assert recipent != self and recipent != ZERO_ADDRESS
    eth_bought: uint256(wei) = self.tokenToEth(tokens_sold)
    assert eth_bought >= min_eth
    self.token.transferFrom(msg.sender, self, tokens_sold)
    send(recipent, eth_bought)
    log.TokenToEth(msg.sender, tokens_sold, eth_bought)
    return as_unitless_number(eth_bought)

# Converts tokens to ETH, recipent recieves tokens
@public
@payable
def tokenToEthTransferExact(recipent: address, max_tokens: uint256, eth_amount: uint256(wei), deadline: uint256) -> uint256:
    assert self.total_shares > 0 and deadline > as_unitless_number(block.timestamp)
    assert max_tokens > 0 and eth_amount > 0
    assert recipent != self and recipent != ZERO_ADDRESS
    tokens_sold: uint256 = self.tokenToEthExact(eth_amount)
    assert max_tokens >= tokens_sold
    self.token.transferFrom(msg.sender, self, tokens_sold)
    send(recipent, eth_amount)
    log.TokenToEth(msg.sender, tokens_sold, eth_amount)
    return tokens_sold

# Converts tokens to tokens, sender recieves tokens
@public
@payable
def tokenToTokenSwap(token_addr: address, tokens_sold: uint256, min_tokens_bought: uint256, deadline: uint256) -> bool:
    assert self.total_shares > 0 and deadline > as_unitless_number(block.timestamp)
    assert tokens_sold > 0 and min_tokens_bought > 0
    exchange: address = Factory(self.factoryAddress).getExchange(token_addr)
    assert exchange != ZERO_ADDRESS
    eth_amount: uint256(wei) = self.tokenToEth(tokens_sold)
    self.token.transferFrom(msg.sender, self, tokens_sold)
    assert Exchange(exchange).ethToTokenTransfer(msg.sender, min_tokens_bought, deadline, value=eth_amount)
    log.TokenToEth(msg.sender, tokens_sold, eth_amount)
    return True

# Converts tokens to tokens, sender recieves tokens
@public
@payable
def tokenToTokenSwapExact(token_addr: address, max_tokens_sold: uint256, tokens_bought: uint256, deadline: uint256, exact_output: bool) -> bool:
    assert self.total_shares > 0 and deadline > as_unitless_number(block.timestamp)
    assert max_tokens_sold > 0 and tokens_bought > 0
    exchange: address = Factory(self.factoryAddress).getExchange(token_addr)
    assert exchange != ZERO_ADDRESS
    eth_pool_output: uint256(wei) = exchange.balance
    token_pool_output: uint256 = Token(token_addr).balanceOf(exchange)
    new_token_pool_output: uint256 = token_pool_output - tokens_bought
    new_eth_pool_output: uint256(wei) = (eth_pool_output * token_pool_output) / new_token_pool_output
    eth_required: uint256(wei) = (new_eth_pool_output - eth_pool_output) * 500 / 499
    tokens_sold: uint256 = self.tokenToEthExact(eth_required)
    assert tokens_sold <= max_tokens_sold
    self.token.transferFrom(msg.sender, self, tokens_sold)
    assert Exchange(exchange).ethToTokenTransfer(msg.sender, 1, deadline, value=eth_required)
    log.TokenToEth(msg.sender, tokens_sold, eth_required)
    return True

# Converts tokens to tokens, recipent recieves tokens
@public
@payable
def tokenToTokenTransfer(token_addr: address, recipent: address, tokens_sold: uint256, min_tokens_bought: uint256, deadline: uint256) -> bool:
    assert self.total_shares > 0 and deadline > as_unitless_number(block.timestamp)
    assert tokens_sold > 0 and min_tokens_bought > 0
    assert recipent != self and recipent != ZERO_ADDRESS
    exchange: address = Factory(self.factoryAddress).getExchange(token_addr)
    assert exchange != ZERO_ADDRESS
    eth_amount: uint256(wei) = self.tokenToEth(tokens_sold)
    self.token.transferFrom(msg.sender, self, tokens_sold)
    assert Exchange(exchange).ethToTokenTransfer(recipent, min_tokens_bought, deadline, value=eth_amount)
    log.TokenToEth(msg.sender, tokens_sold, eth_amount)
    return True

# Converts tokens to tokens, recipent recieves tokens
@public
@payable
def tokenToTokenTransferExact(token_addr: address, recipent: address, max_tokens_sold: uint256, tokens_bought: uint256, deadline: uint256) -> bool:
    assert self.total_shares > 0 and deadline > as_unitless_number(block.timestamp)
    assert max_tokens_sold > 0 and tokens_bought > 0
    assert recipent != self and recipent != ZERO_ADDRESS
    exchange: address = Factory(self.factoryAddress).getExchange(token_addr)
    assert exchange != ZERO_ADDRESS
    eth_pool_output: uint256(wei) = exchange.balance
    token_pool_output: uint256 = Token(token_addr).balanceOf(exchange)
    new_token_pool_output: uint256 = token_pool_output - tokens_bought
    new_eth_pool_output: uint256(wei) = (eth_pool_output * token_pool_output) / new_token_pool_output
    eth_required: uint256(wei) = (new_eth_pool_output - eth_pool_output) * 500 / 499
    tokens_sold: uint256 = self.tokenToEthExact(eth_required)
    assert tokens_sold <= max_tokens_sold
    self.token.transferFrom(msg.sender, self, tokens_sold)
    assert Exchange(exchange).ethToTokenTransfer(recipent, 1, deadline, value=eth_required)
    log.TokenToEth(msg.sender, tokens_sold, eth_required)
    return True

@public
@constant
def tokenAddress() -> address:
    return self.token

@public
@constant
def getTokenCost(tokens_bought: uint256) -> uint256(wei):
    token_pool: uint256 = self.token.balanceOf(self)
    eth_pool: uint256(wei) = self.balance
    new_token_pool: uint256 = token_pool - tokens_bought
    new_eth_pool: uint256(wei) = (eth_pool * token_pool) / new_token_pool
    return (new_eth_pool - eth_pool) * 500 / 499

# ERC20 compatibility for exchange shares modified from
# https://github.com/ethereum/vyper/blob/master/examples/tokens/ERC20_solidity_compatible/ERC20.v.py
@public
@constant
def totalSupply() -> uint256:
    return self.total_shares

@public
@constant
def balanceOf(_owner : address) -> uint256:
    return self.shares[_owner]

@public
def transfer(_to : address, _value : uint256) -> bool:
    _sender: address = msg.sender
    self.shares[_sender] = self.shares[_sender] - _value
    self.shares[_to] = self.shares[_to] + _value
    log.Transfer(_sender, _to, _value)
    return True

@public
def transferFrom(_from : address, _to : address, _value : uint256) -> bool:
    _sender: address = msg.sender
    allowance: uint256 = self.share_allowances[_from][_sender]
    self.shares[_from] = self.shares[_from] - _value
    self.shares[_to] = self.shares[_to] + _value
    self.share_allowances[_from][_sender] = allowance - _value
    log.Transfer(_from, _to, _value)
    return True

@public
def approve(_spender : address, _value : uint256) -> bool:
    _sender: address = msg.sender
    self.share_allowances[_sender][_spender] = _value
    log.Approval(_sender, _spender, _value)
    return True

@public
@constant
def allowance(_owner : address, _spender : address) -> uint256:
    return self.share_allowances[_owner][_spender]
