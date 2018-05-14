contract Factory():
    def token_to_exchange_lookup(token_addr: address) -> address: pass

contract Exchange():
    def eth_to_tokens_payment(recipent: address, min_tokens: uint256, timeout: uint256) -> bool: pass

contract Token():
    def balanceOf(_owner : address) -> uint256: pass

EthToToken: event({buyer: indexed(address), eth_sold: indexed(uint256), tokens_purchased: indexed(uint256)})
TokenToEth: event({buyer: indexed(address), tokens_sold: indexed(uint256), eth_purchased: indexed(uint256)})
Investment: event({investor: indexed(address), eth_invested: indexed(uint256), tokens_invested: indexed(uint256)})
Divestment: event({investor: indexed(address), eth_divested: indexed(uint256), tokens_divested: indexed(uint256)})
Transfer: event({_from: indexed(address), _to: indexed(address), _value: uint256})
Approval: event({_owner: indexed(address), _spender: indexed(address), _value: uint256})

total_shares: public(uint256)                       # total share supply
shares: uint256[address]                            # share balance of an address
share_allowances: (uint256[address])[address]       # share allowances
factory_address: public(address)                    # the factory that created this exchange
token: address(ERC20)                               # the ERC20 token traded on this exchange

# Called by factory during launch
# Replaces constructor which is not supported on contracts deployed with create_with_code_of()
@public
@payable
def setup(token_addr: address) -> bool:
    assert self.factory_address == 0x0000000000000000000000000000000000000000
    self.factory_address = msg.sender
    self.token = token_addr
    assert self.factory_address != 0x0000000000000000000000000000000000000000
    return True

# Sets initial token pool, ETH pool, and share amount
# Constrained to limit extremely high or extremely low share cost
@public
@payable
def initialize(tokens_invested: uint256):
    assert self.total_shares == convert(0, 'uint256')
    assert self.factory_address != 0x0000000000000000000000000000000000000000
    assert self.token != 0x0000000000000000000000000000000000000000
    eth_invested: uint256 = convert(msg.value, 'uint256')
    assert eth_invested >= convert(100000000, 'uint256')
    assert tokens_invested >= convert(100000000, 'uint256')
    assert Factory(self.factory_address).token_to_exchange_lookup(self.token) == self
    initial_shares: uint256 = eth_invested / convert(100000, 'uint256')
    self.total_shares = initial_shares
    self.shares[msg.sender] = initial_shares
    self.token.transferFrom(msg.sender, self, tokens_invested)
    log.Investment(msg.sender, eth_invested, tokens_invested)
    assert self.total_shares > convert(0, 'uint256')

# Exchange all input ETH for tokens
@private
def eth_to_tokens(
        buyer: address,
        recipent: address,
        eth_sold: uint256,
        min_tokens: uint256
    ):
    assert self.total_shares > convert(0, 'uint256')
    assert eth_sold > convert(0, 'uint256')
    eth_pool: uint256 = convert(self.balance, 'uint256') - eth_sold
    token_pool: uint256 = Token(self.token).balanceOf(self)
    invariant: uint256 = eth_pool * token_pool
    fee: uint256 = eth_sold / convert(500, 'uint256')
    new_token_pool: uint256 = invariant / (eth_pool + eth_sold - fee)
    tokens_purchased: uint256 = token_pool - new_token_pool
    assert tokens_purchased >= min_tokens
    self.token.transfer(recipent, tokens_purchased)
    log.EthToToken(buyer, eth_sold, tokens_purchased)

# Buyer converts ETH to tokens
@public
@payable
def eth_to_tokens_swap(min_tokens: uint256, timeout: uint256) -> bool:
    assert timeout > convert(block.timestamp, 'uint256')
    self.eth_to_tokens(msg.sender, msg.sender, convert(msg.value, 'uint256'), min_tokens)
    return True

# Buyer sells ETH for tokens and sends tokens to recipient
@public
@payable
def eth_to_tokens_payment(recipent: address, min_tokens: uint256, timeout: uint256) -> bool:
    assert timeout > convert(block.timestamp, 'uint256')
    assert recipent != 0x0000000000000000000000000000000000000000
    assert recipent != self
    self.eth_to_tokens(msg.sender, recipent, convert(msg.value, 'uint256'), min_tokens)
    return True

# Exchange ETH for exact amount of tokens
# Any remaining ETH is refunded to buyer
@private
def eth_to_tokens_exact(
        buyer: address,
        recipent: address,
        max_eth: uint256,
        tokens_bought: uint256
    ):
    assert self.total_shares > convert(0, 'uint256')
    assert max_eth > convert(0, 'uint256')
    eth_pool: uint256 = convert(self.balance, 'uint256') - max_eth
    token_pool: uint256 = Token(self.token).balanceOf(self)
    invariant: uint256 = eth_pool * token_pool
    new_token_pool: uint256 = token_pool - tokens_bought
    new_eth_pool: uint256 = invariant / new_token_pool
    eth_required: uint256 = new_eth_pool - eth_pool
    eth_required_with_fee: uint256 = eth_required * convert(500, 'uint256') / convert(499, 'uint256')
    eth_refund: uint256 = max_eth - eth_required_with_fee
    self.token.transfer(recipent, tokens_bought)
    send(buyer, as_wei_value(convert(eth_refund, 'int128'), 'wei'))
    log.EthToToken(buyer, eth_required, tokens_bought)

# Buyer converts ETH to exact amount of tokens
@public
@payable
def eth_to_tokens_exact_swap(tokens_bought: uint256, timeout: uint256) -> bool:
    assert timeout > convert(block.timestamp, 'uint256')
    self.eth_to_tokens_exact(msg.sender, msg.sender, convert(msg.value, 'uint256'), tokens_bought)
    return True

# Buyer sells ETH for tokens and sends tokens to recipient
@public
@payable
def eth_to_tokens_exact_payment(recipent: address, tokens_bought: uint256, timeout: uint256) -> bool:
    assert timeout > convert(block.timestamp, 'uint256')
    assert recipent != 0x0000000000000000000000000000000000000000
    assert recipent != self
    self.eth_to_tokens_exact(msg.sender, recipent, convert(msg.value, 'uint256'), tokens_bought)
    return True

# Exchange all input tokens for ETH
@private
def tokens_to_eth(
        buyer: address,
        recipent: address,
        tokens_sold: uint256,
        min_eth_purchase: uint256
    ):
    assert self.total_shares > convert(0, 'uint256')
    assert tokens_sold > convert(0, 'uint256')
    eth_pool: uint256 = convert(self.balance, 'uint256')
    token_pool: uint256 = Token(self.token).balanceOf(self)
    invariant: uint256 = eth_pool * token_pool
    fee: uint256 = tokens_sold / convert(500, 'uint256')
    new_eth_pool: uint256 = invariant / (token_pool + tokens_sold - fee)
    eth_purchased: uint256 = eth_pool - new_eth_pool
    assert eth_purchased >= min_eth_purchase
    self.token.transferFrom(buyer, self, tokens_sold)
    send(recipent, as_wei_value(convert(eth_purchased, 'int128'), 'wei'))
    log.TokenToEth(buyer, tokens_sold, eth_purchased)

# Buyer sells tokens for ETH
@public
def tokens_to_eth_swap(tokens_sold: uint256, min_eth_purchase: uint256, timeout: uint256) -> bool:
    assert timeout > convert(block.timestamp, 'uint256')
    self.tokens_to_eth(msg.sender, msg.sender, tokens_sold, min_eth_purchase)
    return True

# Buyer sells tokens for ETH and sends tokens to recipient
@public
def tokens_to_eth_payment(
        recipent: address,
        tokens_sold: uint256,
        min_eth_purchase: uint256,
        timeout: uint256
    ) -> bool:
    assert timeout > convert(block.timestamp, 'uint256')
    assert recipent != 0x0000000000000000000000000000000000000000
    assert recipent != self
    self.tokens_to_eth(msg.sender, recipent, tokens_sold, min_eth_purchase)
    return True

# Exchange input tokens for exact amount of ETH
@private
def tokens_to_eth_exact(
        buyer: address,
        recipent: address,
        eth_bought: uint256,
        max_tokens_sold: uint256
    ):
    assert self.total_shares > convert(0, 'uint256')
    assert eth_bought > convert(0, 'uint256')
    eth_pool: uint256 = convert(self.balance, 'uint256')
    token_pool: uint256 = Token(self.token).balanceOf(self)
    invariant: uint256 = eth_pool * token_pool
    new_eth_pool: uint256 = eth_pool - eth_bought
    new_token_pool: uint256 = invariant/new_eth_pool
    tokens_required: uint256 = new_token_pool - token_pool
    tokens_required_with_fee: uint256 = tokens_required * convert(500, 'uint256') / convert(499, 'uint256')
    assert max_tokens_sold >= tokens_required_with_fee
    self.token.transferFrom(buyer, self, tokens_required_with_fee)
    send(recipent, as_wei_value(convert(eth_bought, 'int128'), 'wei'))
    log.TokenToEth(buyer, tokens_required_with_fee, eth_bought)

# Buyer sells tokens for ETH
@public
def tokens_to_eth_exact_swap(eth_bought: uint256, max_tokens_sold: uint256, timeout: uint256) -> bool:
    assert timeout > convert(block.timestamp, 'uint256')
    self.tokens_to_eth_exact(msg.sender, msg.sender, eth_bought, max_tokens_sold)
    return True

# Buyer sells tokens for ETH and sends tokens to recipient
@public
def tokens_to_eth_exact_payment(
        recipent: address,
        eth_bought: uint256,
        max_tokens_sold: uint256,
        timeout: uint256
    ) -> bool:
    assert timeout > convert(block.timestamp, 'uint256')
    assert recipent != 0x0000000000000000000000000000000000000000
    assert recipent != self
    self.tokens_to_eth_exact(msg.sender, recipent, eth_bought, max_tokens_sold)
    return True

# Exchange tokens for any other tokens
@private
def tokens_to_tokens(
        token_addr: address,
        buyer: address,
        recipent: address,
        tokens_sold: uint256,
        min_tokens: uint256,
        timeout: uint256
    ):
    assert self.total_shares > convert(0, 'uint256')
    assert tokens_sold > convert(0, 'uint256')
    assert min_tokens > convert(0, 'uint256')
    assert token_addr != self.token
    exchange: address = Factory(self.factory_address).token_to_exchange_lookup(token_addr)
    assert exchange != 0x0000000000000000000000000000000000000000
    eth_pool: uint256 = convert(self.balance, 'uint256')
    token_pool: uint256 = Token(self.token).balanceOf(self)
    invariant: uint256 = eth_pool * token_pool
    fee: uint256 = tokens_sold / convert(500, 'uint256')
    new_eth_pool: uint256 = invariant / (token_pool + tokens_sold - fee)
    eth_purchased: uint256 = eth_pool - new_eth_pool
    self.token.transferFrom(buyer, self, tokens_sold)
    data: bytes[4096] = concat(
        method_id("eth_to_tokens_payment(address,uint256,uint256)"),
        convert(recipent, 'bytes32'),
        convert(min_tokens, 'bytes32'),
        convert(timeout, 'bytes32'),
    )
    wei_purchased: wei_value = as_wei_value(convert(eth_purchased, 'int128'), 'wei')
    assert extract32(raw_call(exchange, data, value=wei_purchased, gas=41000, outsize=32), 0, type=bool) == True
    # assert Exchange(exchange).eth_to_tokens_payment(recipent, min_tokens, timeout, value=wei_purchased) == True
    log.TokenToEth(buyer, tokens_sold, eth_purchased)

# Buyer sells tokens for any other tokens
@public
def tokens_to_tokens_swap(
        token_addr: address,
        tokens_sold: uint256,
        min_tokens: uint256,
        timeout: uint256
    ) -> bool:
    assert timeout > convert(block.timestamp, 'uint256')
    self.tokens_to_tokens(token_addr, msg.sender, msg.sender, tokens_sold, min_tokens, timeout)
    return True

# Buyer sells tokens for any other tokens and sends tokens to recipient
@public
def tokens_to_tokens_payment(
        token_addr: address,
        recipent: address,
        tokens_sold: uint256,
        min_tokens: uint256,
        timeout: uint256
    ) -> bool:
    assert timeout > convert(block.timestamp, 'uint256')
    assert recipent != 0x0000000000000000000000000000000000000000
    assert recipent != self
    self.tokens_to_tokens(token_addr, msg.sender, recipent, tokens_sold, min_tokens, timeout)
    return True


#  CHANGE TO ETH_TO_TOKEN_EXACT_PAYMENT
# MAKE SURE ITS SAFE
 # Exchange tokens for any other tokens
@private
def tokens_to_tokens_exact(
        token_addr: address,
        buyer: address,
        recipent: address,
        tokens_bought: uint256,
        max_tokens_sold: uint256,
        timeout: uint256
    ):
    assert self.total_shares > convert(0, 'uint256')
    assert tokens_bought > convert(0, 'uint256')
    assert max_tokens_sold > convert(0, 'uint256')
    assert token_addr != self.token
    exchange: address = Factory(self.factory_address).token_to_exchange_lookup(token_addr)
    assert exchange != 0x0000000000000000000000000000000000000000
    eth_pool_output: uint256 = convert(exchange.balance, 'uint256')
    token_pool_output: uint256 = Token(token_addr).balanceOf(exchange)
    invariant_output: uint256 = eth_pool_output * token_pool_output
    new_token_pool_output: uint256 = token_pool_output - tokens_bought
    new_eth_pool_output: uint256 = invariant_output / new_token_pool_output
    eth_required_output: uint256 = new_eth_pool_output - eth_pool_output
    eth_required_with_fee_output: uint256 = eth_required_output * convert(500, 'uint256') / convert(499, 'uint256')
    eth_pool: uint256 = convert(self.balance, 'uint256')
    token_pool: uint256 = Token(self.token).balanceOf(self)
    invariant: uint256 = eth_pool * token_pool
    new_eth_pool: uint256 = eth_pool - eth_required_with_fee_output
    new_token_pool: uint256 = invariant / new_eth_pool
    tokens_required: uint256 = new_token_pool - token_pool
    tokens_required_with_fee: uint256 = tokens_required * convert(500, 'uint256') / convert(499, 'uint256')
    self.token.transferFrom(buyer, self, tokens_required_with_fee)
    data: bytes[4096] = concat(
        method_id("eth_to_tokens_payment(address,uint256,uint256)"),
        convert(recipent, 'bytes32'),
        convert(1, 'bytes32'),
        convert(timeout, 'bytes32'),
    )
    wei_bought: wei_value = as_wei_value(convert(eth_required_with_fee_output, 'int128'), 'wei')
    assert extract32(raw_call(exchange, data, value=wei_bought, gas=70000, outsize=32), 0, type=bool) == True
    # assert Exchange(exchange).eth_to_tokens_payment(recipent, min_tokens, timeout, value=wei_bought) == True
    log.TokenToEth(buyer, tokens_required_with_fee, eth_required_with_fee_output)

# Buyer sells tokens for any other tokens
@public
def tokens_to_tokens_exact_swap(
        token_addr: address,
        tokens_bought: uint256,
        max_tokens_sold: uint256,
        timeout: uint256
    ) -> bool:
    assert timeout > convert(block.timestamp, 'uint256')
    self.tokens_to_tokens_exact(token_addr, msg.sender, msg.sender, tokens_bought, max_tokens_sold, timeout)
    return True

# Buyer sells tokens for any other tokens and sends tokens to recipient
@public
def tokens_to_tokens_exact_payment(
        token_addr: address,
        recipent: address,
        tokens_bought: uint256,
        max_tokens_sold: uint256,
        timeout: uint256
    ) -> bool:
    assert timeout > convert(block.timestamp, 'uint256')
    assert recipent != 0x0000000000000000000000000000000000000000
    assert recipent != self
    self.tokens_to_tokens_exact(token_addr, msg.sender, recipent, tokens_bought, max_tokens_sold, timeout)
    return True

# Lock up ETH and tokens at current price ratio to mint shares
# Shares are minted proportional to liquidity invested
# Trading fees are added to liquidity pools increasing value of shares over time
@public
@payable
def invest(min_shares: uint256, timeout: uint256):
    assert timeout > convert(block.timestamp, 'uint256')
    share_total: uint256 = self.total_shares
    assert share_total > convert(0, 'uint256')
    assert min_shares > convert(0, 'uint256')
    eth_invested: uint256 = convert(msg.value, 'uint256')
    assert eth_invested > convert(0, 'uint256')
    eth_pool: uint256 = convert(self.balance, 'uint256')  - eth_invested
    token_pool: uint256 = Token(self.token).balanceOf(self)
    shares_minted: uint256 = (eth_invested * share_total) / eth_pool
    assert shares_minted > min_shares
    tokens_invested: uint256 = (shares_minted * token_pool) / share_total
    self.shares[msg.sender] = self.shares[msg.sender] + shares_minted
    self.total_shares = share_total + shares_minted
    self.token.transferFrom(msg.sender, self, tokens_invested)
    log.Investment(msg.sender, eth_invested, tokens_invested)

# Burn shares to receive ETH and tokens at current price ratio
# Trading fees accumulated since investment are included in divested ETH and tokens
@public
@payable
def divest(
        shares_burned: uint256,
        min_eth: uint256,
        min_tokens: uint256,
        timeout: uint256
    ):
    assert timeout > convert(block.timestamp, 'uint256')
    share_total: uint256 = self.total_shares
    assert share_total > convert(0, 'uint256')
    assert shares_burned > convert(0, 'uint256')
    assert min_eth > convert(0, 'uint256')
    assert min_tokens > convert(0, 'uint256')
    eth_pool: uint256 = convert(self.balance, 'uint256')
    token_pool: uint256 = Token(self.token).balanceOf(self)
    eth_divested: uint256 = (shares_burned * eth_pool) / share_total
    tokens_divested: uint256 = (shares_burned * token_pool) / share_total
    assert eth_divested > min_eth
    assert tokens_divested > min_tokens
    self.shares[msg.sender] = self.shares[msg.sender] - shares_burned
    self.total_shares = share_total - shares_burned
    if self.total_shares != convert(0, 'uint256'):
        assert convert(self.balance, 'uint256') != convert(0, 'uint256')
        assert Token(self.token).balanceOf(self) != convert(0, 'uint256')
    self.token.transfer(msg.sender, tokens_divested)
    send(msg.sender, as_wei_value(convert(eth_divested, 'int128'), 'wei'))
    log.Divestment(msg.sender, eth_divested, tokens_divested)

# Return address of ERC20 token sold on this exchange
@public
@constant
def get_exchange_token() -> address:
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
