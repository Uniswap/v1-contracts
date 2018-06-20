contract Factory():
    def get_token_to_exchange(_token: address) -> address: constant

contract Exchange():
    def pay_eth_to_tokens_all(recipent: address, min_tokens_bought: uint256, timeout: uint256) -> bool: modifying

contract Token():
    def balanceOf(_owner : address) -> uint256: constant

EthToToken: event({buyer: indexed(address), eth_sold: indexed(uint256(wei)), tokens_purchased: indexed(uint256)})
TokenToEth: event({buyer: indexed(address), tokens_sold: indexed(uint256), eth_purchased: indexed(uint256(wei))})
Investment: event({investor: indexed(address), eth_invested: indexed(uint256(wei)), tokens_invested: indexed(uint256)})
Divestment: event({investor: indexed(address), eth_divested: indexed(uint256(wei)), tokens_divested: indexed(uint256)})
Transfer: event({_from: indexed(address), _to: indexed(address), _value: uint256})
Approval: event({_owner: indexed(address), _spender: indexed(address), _value: uint256})

total_shares: uint256                              # total share supply
shares: uint256[address]                            # share balance of an address
share_allowances: (uint256[address])[address]       # share allowance of one adddress on another
factory: address                                   # the factory that created this exchange
token: address(ERC20)                               # the ERC20 token traded on this exchange

# Called by factory during launch
# Replaces constructor which is not supported on contracts deployed with create_with_code_of()
@public
@payable
def setup(_token: address) -> bool:
    assert self.factory == 0x0000000000000000000000000000000000000000
    self.factory = msg.sender
    self.token = _token
    assert self.factory != 0x0000000000000000000000000000000000000000
    assert self.token != 0x0000000000000000000000000000000000000000
    return True

# Sets initial token pool, ETH pool, and share amount
# Constrained to limit extremely high or low share cost
@public
@payable
def initialize(tokens_invested: uint256) -> bool:
    assert self.total_shares == 0
    assert self.factory != 0x0000000000000000000000000000000000000000
    assert self.token != 0x0000000000000000000000000000000000000000
    assert msg.value >= 100000000 and tokens_invested >= 100000000
    assert Factory(self.factory).get_token_to_exchange(self.token) == self
    initial_shares: uint256 = as_unitless_number(self.balance)
    self.total_shares = initial_shares
    self.shares[msg.sender] = initial_shares
    self.token.transferFrom(msg.sender, self, tokens_invested)
    log.Investment(msg.sender, msg.value, tokens_invested)
    assert Token(self.token).balanceOf(self) > 0
    assert self.total_shares > 0 and self.balance > 0
    return True

@private
@constant
def eth_to_tokens_all(eth_sold: uint256(wei)) -> uint256:
    assert self.total_shares > 0 and eth_sold > 0
    eth_pool: uint256(wei) = self.balance - eth_sold
    token_pool: uint256 = Token(self.token).balanceOf(self)
    fee: uint256(wei) = eth_sold / 500
    new_token_pool: uint256 = (eth_pool * token_pool) / (eth_pool + eth_sold - fee)
    return token_pool - new_token_pool

# Fallback function that converts received ETH to tokens
@public
@payable
def __default__():
    tokens_purchased: uint256 = self.eth_to_tokens_all(msg.value)
    self.token.transfer(msg.sender, tokens_purchased)
    log.EthToToken(msg.sender, msg.value, tokens_purchased)

# Converts all ETH (msg.value) to tokens, msg.sender recieves tokens
@public
@payable
def swap_eth_to_tokens_all(min_tokens_bought: uint256, timeout: timestamp) -> bool:
    assert timeout > block.timestamp
    tokens_purchased: uint256 = self.eth_to_tokens_all(msg.value)
    assert tokens_purchased >= min_tokens_bought
    self.token.transfer(msg.sender, tokens_purchased)
    log.EthToToken(msg.sender, msg.value, tokens_purchased)
    return True

# Converts all ETH (msg.value) to tokens, recipent recieves tokens
@public
@payable
def pay_eth_to_tokens_all(recipent: address, min_tokens_bought: uint256, timeout: timestamp) -> bool:
    assert timeout > block.timestamp
    assert recipent != self and recipent != 0x0000000000000000000000000000000000000000
    eth_sold: uint256(wei) = msg.value
    tokens_purchased: uint256 = self.eth_to_tokens_all(eth_sold)
    assert tokens_purchased >= min_tokens_bought
    self.token.transfer(recipent, tokens_purchased)
    log.EthToToken(msg.sender, eth_sold, tokens_purchased)
    return True

@private
@constant
def eth_to_tokens_exact(tokens_bought: uint256, max_eth: uint256(wei)) -> uint256(wei):
    assert self.total_shares > 0 and tokens_bought > 0
    eth_pool: uint256(wei) = self.balance - max_eth
    token_pool: uint256 = Token(self.token).balanceOf(self)
    new_token_pool: uint256 = token_pool - tokens_bought
    new_eth_pool: uint256(wei) = (eth_pool * token_pool) / new_token_pool
    eth_required: uint256(wei) = new_eth_pool - eth_pool
    return eth_required * as_wei_value(500, 'wei') / as_wei_value(499, 'wei')

# Converts ETH to an exact amount of tokens, msg.sender recieves tokens
# msg.value represents the maximum eth that can be sold, any remaining ETH is refunded to buyer
@public
@payable
def swap_eth_to_tokens_exact(tokens_bought: uint256, timeout: timestamp) -> bool:
    assert timeout > block.timestamp
    assert msg.value > 0
    eth_required_with_fee: uint256(wei) = self.eth_to_tokens_exact(tokens_bought, msg.value)
    eth_refund: uint256(wei) = msg.value - eth_required_with_fee
    self.token.transfer(msg.sender, tokens_bought)
    send(msg.sender, eth_refund)
    log.EthToToken(msg.sender, eth_required_with_fee, tokens_bought)
    return True

# Converts ETH to an exact amount of tokens, recipent recieves tokens
# msg.value represents the maximum eth that can be sold, any remaining ETH is refunded to msg.sender
@public
@payable
def pay_eth_to_tokens_exact(recipent: address, tokens_bought: uint256, timeout: timestamp) -> bool:
    assert timeout > block.timestamp
    assert recipent != self and recipent != 0x0000000000000000000000000000000000000000
    assert msg.value > 0
    eth_required_with_fee: uint256(wei) = self.eth_to_tokens_exact(tokens_bought, msg.value)
    eth_refund: uint256(wei) = msg.value - eth_required_with_fee
    self.token.transfer(recipent, tokens_bought)
    send(msg.sender, eth_refund)
    log.EthToToken(msg.sender, eth_required_with_fee, tokens_bought)
    return True

@private
@constant
def tokens_to_eth_all(tokens_sold: uint256) -> uint256(wei):
    assert self.total_shares > 0 and tokens_sold > 0
    eth_pool: uint256(wei) = self.balance
    token_pool: uint256 = Token(self.token).balanceOf(self)
    fee: uint256 = tokens_sold / 500
    new_eth_pool: uint256(wei) = (eth_pool * token_pool) / (token_pool + tokens_sold - fee)
    return eth_pool - new_eth_pool

# Converts tokens_sold to ETH, msg.sender recieves ETH
@public
def swap_tokens_to_eth_all(tokens_sold: uint256, min_eth_bought: uint256(wei), timeout: timestamp) -> bool:
    assert timeout > block.timestamp
    eth_purchased: uint256(wei) = self.tokens_to_eth_all(tokens_sold)
    assert eth_purchased >= min_eth_bought
    send(msg.sender, eth_purchased)
    self.token.transferFrom(msg.sender, self, tokens_sold)
    log.TokenToEth(msg.sender, tokens_sold, eth_purchased)
    return True

# Converts tokens_sold to ETH, recipent recieves ETH
@public
def pay_tokens_to_eth_all(recipent: address, tokens_sold: uint256, min_eth_bought: uint256(wei), timeout: timestamp) -> bool:
    assert timeout > block.timestamp
    assert recipent != self and recipent != 0x0000000000000000000000000000000000000000
    eth_purchased: uint256(wei) = self.tokens_to_eth_all(tokens_sold)
    assert eth_purchased >= min_eth_bought
    send(recipent, eth_purchased)
    self.token.transferFrom(msg.sender, self, tokens_sold)
    log.TokenToEth(msg.sender, tokens_sold, eth_purchased)
    return True

@private
@constant
def tokens_to_eth_exact(eth_bought: uint256(wei)) -> uint256:
    assert self.total_shares > 0 and eth_bought > 0
    eth_pool: uint256(wei) = self.balance
    token_pool: uint256 = Token(self.token).balanceOf(self)
    new_eth_pool: uint256(wei) = eth_pool - eth_bought
    new_token_pool: uint256 = (eth_pool * token_pool) / new_eth_pool
    tokens_required: uint256 = new_token_pool - token_pool
    return tokens_required * 500 / 499

# Converts tokens to an exact amount of ETH, msg.sender recieves ETH
@public
def swap_tokens_to_eth_exact(eth_bought: uint256(wei), max_tokens_sold: uint256, timeout: timestamp) -> bool:
    assert max_tokens_sold > 0
    assert timeout > block.timestamp
    tokens_required_with_fee: uint256 = self.tokens_to_eth_exact(eth_bought)
    assert max_tokens_sold >= tokens_required_with_fee
    self.token.transferFrom(msg.sender, self, tokens_required_with_fee)
    send(msg.sender, eth_bought)
    log.TokenToEth(msg.sender, tokens_required_with_fee, eth_bought)
    return True

# Converts tokens to an exact amount of ETH, recipent recieves ETH
@public
def pay_tokens_to_eth_exact(recipent: address, eth_bought: uint256(wei), max_tokens_sold: uint256, timeout: timestamp) -> bool:
    assert timeout > block.timestamp
    assert recipent != self and recipent != 0x0000000000000000000000000000000000000000
    assert max_tokens_sold > 0
    tokens_required_with_fee: uint256 = self.tokens_to_eth_exact(eth_bought)
    assert max_tokens_sold >= tokens_required_with_fee
    self.token.transferFrom(msg.sender, self, tokens_required_with_fee)
    send(recipent, eth_bought)
    log.TokenToEth(msg.sender, tokens_required_with_fee, eth_bought)
    return True

# Converts tokens (self.token) to other tokens (token_addr), msg.sender recieves tokens (token_addr)
@public
def swap_tokens_to_tokens_all(token_addr: address, tokens_sold: uint256, min_tokens_bought: uint256, timeout: timestamp) -> bool:
    assert timeout > block.timestamp
    assert min_tokens_bought > 0
    assert token_addr != self.token
    exchange: address = Factory(self.factory).get_token_to_exchange(token_addr)
    assert exchange != 0x0000000000000000000000000000000000000000
    eth_purchased: uint256(wei) = self.tokens_to_eth_all(tokens_sold)
    self.token.transferFrom(msg.sender, self, tokens_sold)
    assert Exchange(exchange).pay_eth_to_tokens_all(msg.sender, min_tokens_bought, as_unitless_number(timeout), value=eth_purchased)
    log.TokenToEth(msg.sender, tokens_sold, eth_purchased)
    return True

# Converts tokens (self.token) to other tokens (token_addr), recipent recieves tokens (token_addr)
@public
def pay_tokens_to_tokens_all(token_addr: address, recipent: address, tokens_sold: uint256, min_tokens_bought: uint256, timeout: timestamp) -> bool:
    assert timeout > block.timestamp
    assert recipent != self and recipent != 0x0000000000000000000000000000000000000000
    assert min_tokens_bought > 0
    assert token_addr != self.token
    exchange: address = Factory(self.factory).get_token_to_exchange(token_addr)
    assert exchange != 0x0000000000000000000000000000000000000000
    eth_purchased: uint256(wei) = self.tokens_to_eth_all(tokens_sold)
    self.token.transferFrom(msg.sender, self, tokens_sold)
    assert Exchange(exchange).pay_eth_to_tokens_all(recipent, min_tokens_bought, as_unitless_number(timeout), value=eth_purchased)
    log.TokenToEth(msg.sender, tokens_sold, eth_purchased)
    return True

# Converts tokens (self.token) to an exact amount other tokens (token_addr), msg.sender recieves tokens (token_addr)
@public
def swap_tokens_to_tokens_exact(token_addr: address, tokens_bought: uint256, max_tokens_sold: uint256, timeout: timestamp) -> bool:
    assert timeout > block.timestamp
    assert max_tokens_sold > 0
    assert token_addr != self.token
    exchange: address = Factory(self.factory).get_token_to_exchange(token_addr)
    assert exchange != 0x0000000000000000000000000000000000000000
    eth_pool_output: uint256(wei) = exchange.balance
    token_pool_output: uint256 = Token(token_addr).balanceOf(exchange)
    new_token_pool_output: uint256 = token_pool_output - tokens_bought
    new_eth_pool_output: uint256(wei) = (eth_pool_output * token_pool_output) / new_token_pool_output
    eth_required_output: uint256(wei) = new_eth_pool_output - eth_pool_output
    eth_required_with_fee_output: uint256(wei) = eth_required_output * 500 / 499
    tokens_required_with_fee: uint256 = self.tokens_to_eth_exact(eth_required_with_fee_output)
    self.token.transferFrom(msg.sender, self, tokens_required_with_fee)
    assert Exchange(exchange).pay_eth_to_tokens_all(msg.sender, 1, as_unitless_number(timeout), value=eth_required_with_fee_output)
    log.TokenToEth(msg.sender, tokens_required_with_fee, eth_required_with_fee_output)
    return True

# Converts tokens (self.token) to an exact amount other tokens (token_addr), recipent recieves tokens (token_addr)
@public
def pay_tokens_to_tokens_exact(token_addr: address, recipent: address, tokens_bought: uint256, max_tokens_sold: uint256, timeout: timestamp) -> bool:
    assert timeout > block.timestamp
    assert recipent != self and recipent != 0x0000000000000000000000000000000000000000
    assert max_tokens_sold > 0
    assert token_addr != self.token
    exchange: address = Factory(self.factory).get_token_to_exchange(token_addr)
    assert exchange != 0x0000000000000000000000000000000000000000
    eth_pool_out: uint256(wei) = exchange.balance
    token_pool_out: uint256 = Token(token_addr).balanceOf(exchange)
    new_token_pool_out: uint256 = token_pool_out - tokens_bought
    new_eth_pool_out: uint256(wei) = (eth_pool_out * token_pool_out) / new_token_pool_out
    eth_required_out: uint256(wei) = new_eth_pool_out - eth_pool_out
    eth_required_with_fee_out: uint256(wei) = eth_required_out * 500 / 499
    tokens_required_with_fee: uint256 = self.tokens_to_eth_exact(eth_required_with_fee_out)
    self.token.transferFrom(msg.sender, self, tokens_required_with_fee)
    assert Exchange(exchange).pay_eth_to_tokens_all(recipent, 1, as_unitless_number(timeout), value=eth_required_with_fee_out)
    log.TokenToEth(msg.sender, tokens_required_with_fee, eth_required_with_fee_out)
    return True

# Lock up ETH and tokens at current price ratio to mint shares
# Shares are minted proportional to liquidity invested
# Trading fees are added to liquidity pools increasing value of shares over time
@public
@payable
def invest(min_shares: uint256, timeout: timestamp) -> bool:
    assert timeout > block.timestamp
    assert msg.value > 0
    share_total: uint256 = self.total_shares
    assert share_total > 0 and min_shares > 0
    eth_invested: uint256(wei) = msg.value
    eth_pool: uint256(wei) = self.balance  - eth_invested
    token_pool: uint256 = Token(self.token).balanceOf(self)
    shares_minted: uint256 = (eth_invested * share_total) / eth_pool
    assert shares_minted > min_shares
    tokens_invested: uint256 = (shares_minted * token_pool) / share_total
    self.shares[msg.sender] = self.shares[msg.sender] + shares_minted
    self.total_shares = share_total + shares_minted
    self.token.transferFrom(msg.sender, self, tokens_invested)
    log.Investment(msg.sender, eth_invested, tokens_invested)
    return True

# Burn shares to receive ETH and tokens at current price ratio
# Trading fees accumulated since investment are included in divested ETH and tokens
@public
def divest(shares_burned: uint256, min_eth: uint256(wei), min_tokens: uint256, timeout: timestamp) -> bool:
    assert timeout > block.timestamp
    share_total: uint256 = self.total_shares
    assert share_total > 0 and shares_burned > 0
    assert min_eth > 0 and min_tokens > 0
    token_pool: uint256 = Token(self.token).balanceOf(self)
    eth_divested: uint256(wei) = (shares_burned * self.balance) / share_total
    tokens_divested: uint256 = (shares_burned * token_pool) / share_total
    assert eth_divested > min_eth and tokens_divested > min_tokens
    self.shares[msg.sender] = self.shares[msg.sender] - shares_burned
    self.total_shares = share_total - shares_burned
    self.token.transfer(msg.sender, tokens_divested)
    send(msg.sender, eth_divested)
    log.Divestment(msg.sender, eth_divested, tokens_divested)
    return True

@public
@constant
def getFactoryAddress() -> address:
    return self.factory

@public
@constant
def getTokenAddress() -> address:
    return self.token

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
