EthToToken: event({buyer: indexed(address), eth_sold: indexed(uint256), tokens_purchased: indexed(uint256)})
TokenToEth: event({buyer: indexed(address), tokens_sold: indexed(uint256), eth_purchased: indexed(uint256)})
Investment: event({investor: indexed(address), eth_invested: indexed(uint256), tokens_invested: indexed(uint256)})
Divestment: event({investor: indexed(address), eth_divested: indexed(uint256), tokens_divested: indexed(uint256)})
Transfer: event({_from: indexed(address), _to: indexed(address), _value: uint256})
Approval: event({_owner: indexed(address), _spender: indexed(address), _value: uint256})

eth_pool: public(uint256)                   # total ETH liquidity
token_pool: public(uint256)                 # total token liquidity
total_shares: public(uint256)               # total share supply
shares: uint256[address]                    # share balance of an address
allowances: (uint256[address])[address]     # share balance that can be spent by one address on behalf of another
factory_address: public(address)            # the factory that created this exchange
token_address: address(ERC20)               # the ERC20 token that can be traded on this exchange

# Called by factory during launch
# Replaces constructor which is not supported on contracts deployed with create_with_code_of()
@public
def setup(token_addr: address) -> bool:
    assert self.factory_address == 0x0000000000000000000000000000000000000000
    self.factory_address = msg.sender
    self.token_address = token_addr
    assert self.factory_address != 0x0000000000000000000000000000000000000000
    return True

# Sets initial token pool, ETH pool, and share amount
# Constrained to limit extremely high or extremely low share cost
@public
@payable
def initialize(tokens_invested: uint256):
    assert self.total_shares == convert(0, 'uint256')
    assert self.factory_address != 0x0000000000000000000000000000000000000000
    assert self.token_address != 0x0000000000000000000000000000000000000000
    eth_invested: uint256 = convert(msg.value, 'uint256')
    assert uint256_ge(eth_invested, convert(100000, 'uint256'))
    assert uint256_le(eth_invested, convert(5*10**18, 'uint256'))
    assert uint256_ge(tokens_invested, convert(100000, 'uint256'))
    data: bytes[4096] = concat(method_id("token_to_exchange_lookup(address)"), convert(self.token_address, 'bytes32'))
    assert extract32(raw_call(self.factory_address, data, gas=750, outsize=32), 0, type=address) == self
    self.eth_pool = eth_invested
    self.token_pool = tokens_invested
    initial_shares: uint256 = uint256_div(eth_invested, convert(100000, 'uint256'))
    self.total_shares = initial_shares
    self.shares[msg.sender] = initial_shares
    self.token_address.transferFrom(msg.sender, self, tokens_invested)
    log.Investment(msg.sender, eth_invested, tokens_invested)
    assert uint256_gt(self.total_shares, convert(0, 'uint256'))

# Exchange ETH for tokens
@private
def eth_to_tokens(buyer: address, recipent: address, eth_sold: uint256, min_token_purchase: uint256):
    assert uint256_gt(self.total_shares, convert(0, 'uint256'))
    assert uint256_gt(eth_sold, convert(0, 'uint256'))
    eth_in_pool: uint256 = self.eth_pool
    tokens_in_pool: uint256 = self.token_pool
    invariant: uint256 = uint256_mul(eth_in_pool, tokens_in_pool)
    fee: uint256 = uint256_div(eth_sold, convert(500, 'uint256'))
    new_eth_pool: uint256 = uint256_add(eth_in_pool, eth_sold)
    temp_eth_pool: uint256 = uint256_sub(new_eth_pool, fee)
    new_token_pool: uint256 = uint256_div(invariant, temp_eth_pool)
    tokens_purchased: uint256 = uint256_sub(tokens_in_pool, new_token_pool)
    assert uint256_ge(tokens_purchased, min_token_purchase)
    self.eth_pool = new_eth_pool
    self.token_pool = new_token_pool
    self.token_address.transfer(recipent, tokens_purchased)
    log.EthToToken(buyer, eth_sold, tokens_purchased)

# Buyer converts ETH to tokens
@public
@payable
def eth_to_tokens_swap(min_token_purchase: uint256, timeout: uint256):
    assert uint256_gt(timeout, convert(block.timestamp, 'uint256'))
    self.eth_to_tokens(msg.sender, msg.sender, convert(msg.value, 'uint256'), min_token_purchase)

# Buyer sells ETH for tokens and sends tokens to recipient
@public
@payable
def eth_to_tokens_payment(recipent: address, min_token_purchase: uint256, timeout: uint256):
    assert uint256_gt(timeout, convert(block.timestamp, 'uint256'))
    assert recipent != 0x0000000000000000000000000000000000000000
    assert recipent != self
    self.eth_to_tokens(msg.sender, recipent, convert(msg.value, 'uint256'), min_token_purchase)

# Exchange tokens for ETH
@private
def tokens_to_eth(buyer: address, recipent: address, tokens_sold: uint256, min_eth_purchase: uint256):
    assert uint256_gt(self.total_shares, convert(0, 'uint256'))
    assert uint256_gt(tokens_sold, convert(0, 'uint256'))
    eth_in_pool: uint256 = self.eth_pool
    tokens_in_pool: uint256 = self.token_pool
    invariant: uint256 = uint256_mul(eth_in_pool, tokens_in_pool)
    fee: uint256 = uint256_div(tokens_sold, convert(500, 'uint256'))
    new_token_pool: uint256 = uint256_add(tokens_in_pool, tokens_sold)
    temp_token_pool: uint256 = uint256_sub(new_token_pool, fee)
    new_eth_pool: uint256 = uint256_div(invariant, temp_token_pool)
    eth_purchased: uint256 = uint256_sub(eth_in_pool, new_eth_pool)
    assert uint256_ge(eth_purchased, min_eth_purchase)
    self.eth_pool = new_eth_pool
    self.token_pool = new_token_pool
    self.token_address.transferFrom(buyer, self, tokens_sold)
    send(recipent, as_wei_value(convert(eth_purchased, 'int128'), 'wei'))
    log.TokenToEth(buyer, tokens_sold, eth_purchased)

# Buyer sells tokens for ETH
@public
def tokens_to_eth_swap(tokens_sold: uint256, min_eth_purchase: uint256, timeout: uint256):
    assert uint256_gt(timeout, convert(block.timestamp, 'uint256'))
    self.tokens_to_eth(msg.sender, msg.sender, tokens_sold, min_eth_purchase)

# Buyer sells tokens for ETH and sends tokens to recipient
@public
def tokens_to_eth_payment(recipent: address, tokens_sold: uint256, min_eth_purchase: uint256, timeout: uint256):
    assert uint256_gt(timeout, convert(block.timestamp, 'uint256'))
    assert recipent != 0x0000000000000000000000000000000000000000
    assert recipent != self
    self.tokens_to_eth(msg.sender, recipent, tokens_sold, min_eth_purchase)

# Receives ETH from another Uniswap exchange and sends tokens to buyer
# Can only be called by other exchanges during token to token trades
@public
@payable
def receive_tokens_to_tokens(recipent: address, min_token_purchase: uint256) -> bool:
    data: bytes[4096] = concat(method_id("exchange_to_token_lookup(address)"), convert(msg.sender, 'bytes32'))
    assert extract32(raw_call(self.factory_address, data, gas=750, outsize=32), 0, type=address) != 0x0000000000000000000000000000000000000000
    self.eth_to_tokens(msg.sender, recipent, convert(msg.value, 'uint256'), min_token_purchase)
    return True

# Exchange tokens for any other tokens
@private
def tokens_to_tokens(token_addr: address, buyer: address, recipent: address, tokens_sold: uint256, min_token_purchase: uint256):
    assert uint256_gt(self.total_shares, convert(0, 'uint256'))
    assert uint256_gt(tokens_sold, convert(0, 'uint256'))
    assert uint256_gt(min_token_purchase, convert(0, 'uint256'))
    assert token_addr != self.token_address
    factory_data: bytes[4096] = concat(method_id("token_to_exchange_lookup(address)"), convert(token_addr, 'bytes32'))
    exchange: address = extract32(raw_call(self.factory_address, factory_data, gas=750, outsize=32), 0, type=address)
    assert exchange != 0x0000000000000000000000000000000000000000
    eth_in_pool: uint256 = self.eth_pool
    tokens_in_pool: uint256 = self.token_pool
    invariant: uint256 = uint256_mul(eth_in_pool, tokens_in_pool)
    fee: uint256 = uint256_div(tokens_sold, convert(500, 'uint256'))
    new_token_pool: uint256 = uint256_add(tokens_in_pool, tokens_sold)
    temp_token_pool: uint256 = uint256_sub(new_token_pool, fee)
    new_eth_pool: uint256 = uint256_div(invariant, temp_token_pool)
    eth_purchased: uint256 = uint256_sub(eth_in_pool, new_eth_pool)
    self.eth_pool = new_eth_pool
    self.token_pool = new_token_pool
    self.token_address.transferFrom(buyer, self, tokens_sold)
    exchange_data: bytes[4096] = concat(method_id("receive_tokens_to_tokens(address,uint256)"), convert(recipent, 'bytes32'), convert(min_token_purchase, 'bytes32'))
    assert extract32(raw_call(exchange, exchange_data, value=as_wei_value(convert(eth_purchased, 'int128'), 'wei'), gas=55000, outsize=32), 0, type=bool) == True
    log.TokenToEth(buyer, tokens_sold, eth_purchased)

# Buyer sells tokens for any other tokens
@public
def tokens_to_tokens_swap(token_addr: address, tokens_sold: uint256, min_token_purchase: uint256, timeout: uint256):
    assert uint256_gt(timeout, convert(block.timestamp, 'uint256'))
    self.tokens_to_tokens(token_addr, msg.sender, msg.sender, tokens_sold, min_token_purchase)

# Buyer sells tokens for any other tokens and sends tokens to recipient
@public
def tokens_to_tokens_payment(token_addr: address, recipent: address, tokens_sold: uint256, min_token_purchase: uint256, timeout: uint256):
    assert uint256_gt(timeout, convert(block.timestamp, 'uint256'))
    assert recipent != 0x0000000000000000000000000000000000000000
    assert recipent != self
    self.tokens_to_tokens(token_addr, msg.sender, recipent, tokens_sold, min_token_purchase)

# Lock up ETH and tokens at current price ratio to mint shares
# Shares are minted proportional to liquidity invested
# Trading fees are added to liquidity pools increasing value of shares over time
@public
@payable
def invest(min_shares: uint256, timeout: uint256):
    assert uint256_gt(timeout, convert(block.timestamp, 'uint256'))
    share_total: uint256 = self.total_shares
    assert uint256_gt(share_total, convert(0, 'uint256'))
    assert uint256_gt(min_shares, convert(0, 'uint256'))
    eth_invested: uint256 = convert(msg.value, 'uint256')
    assert uint256_gt(eth_invested, convert(0, 'uint256'))
    eth_in_pool: uint256 = self.eth_pool
    tokens_in_pool: uint256 = self.token_pool
    shares_minted: uint256 = uint256_div(uint256_mul(eth_invested, share_total), eth_in_pool)
    assert uint256_gt(shares_minted, min_shares)
    tokens_invested: uint256 = uint256_div(uint256_mul(shares_minted, tokens_in_pool), share_total)
    self.shares[msg.sender] = uint256_add(self.shares[msg.sender], shares_minted)
    self.total_shares = uint256_add(share_total, shares_minted)
    self.eth_pool = uint256_add(eth_in_pool, eth_invested)
    self.token_pool = uint256_add(tokens_in_pool, tokens_invested)
    self.token_address.transferFrom(msg.sender, self, tokens_invested)
    log.Investment(msg.sender, eth_invested, tokens_invested)

# Burn shares to receive ETH and tokens at current price ratio
# Trading fees accumulated since investment are included in divested ETH and tokens
@public
@payable
def divest(shares_burned: uint256, min_eth_purchase: uint256, min_token_purchase: uint256, timeout: uint256):
    assert uint256_gt(timeout, convert(block.timestamp, 'uint256'))
    share_total: uint256 = self.total_shares
    assert uint256_gt(share_total, convert(0, 'uint256'))
    assert uint256_gt(shares_burned, convert(0, 'uint256'))
    assert uint256_gt(min_eth_purchase, convert(0, 'uint256'))
    assert uint256_gt(min_token_purchase, convert(0, 'uint256'))
    eth_in_pool: uint256 = self.eth_pool
    tokens_in_pool: uint256 = self.token_pool
    eth_divested: uint256 = uint256_div(uint256_mul(shares_burned, eth_in_pool), share_total)
    tokens_divested: uint256 = uint256_div(uint256_mul(shares_burned, tokens_in_pool), share_total)
    assert uint256_gt(eth_divested, min_eth_purchase)
    assert uint256_gt(tokens_divested, min_token_purchase)
    self.shares[msg.sender] = uint256_sub(self.shares[msg.sender], shares_burned)
    self.total_shares = uint256_sub(share_total, shares_burned)
    if self.total_shares != convert(0, 'uint256'):
        self.eth_pool = uint256_sub(eth_in_pool, eth_divested)
        self.token_pool = uint256_sub(tokens_in_pool, tokens_divested)
        assert self.eth_pool != convert(0, 'uint256')
        assert self.token_pool != convert(0, 'uint256')
    else:
        self.eth_pool = convert(0, 'uint256')
        self.token_pool = convert(0, 'uint256')
    self.token_address.transfer(msg.sender, tokens_divested)
    send(msg.sender, as_wei_value(convert(eth_divested, 'int128'), 'wei'))
    log.Divestment(msg.sender, eth_divested, tokens_divested)

# Return address of ERC20 token sold on this exchange
@public
@constant
def get_exchange_token() -> address:
    return self.token_address

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
    # Make sure sufficient funds are present implicitly through overflow protection
    self.shares[_sender] = uint256_sub(self.shares[_sender], _value)
    self.shares[_to] = uint256_add(self.shares[_to], _value)
    # Fire transfer event
    log.Transfer(_sender, _to, _value)
    return True

@public
def transferFrom(_from : address, _to : address, _value : uint256) -> bool:
    _sender: address = msg.sender
    allowance: uint256 = self.allowances[_from][_sender]
    # Make sure sufficient funds/allowance are present implicitly through overflow protection
    self.shares[_from] = uint256_sub(self.shares[_from], _value)
    self.shares[_to] = uint256_add(self.shares[_to], _value)
    self.allowances[_from][_sender] = uint256_sub(allowance, _value)
    # Fire transfer event
    log.Transfer(_from, _to, _value)
    return True

@public
def approve(_spender : address, _value : uint256) -> bool:
    _sender: address = msg.sender
    self.allowances[_sender][_spender] = _value
    # Fire approval event
    log.Approval(_sender, _spender, _value)
    return True

@public
@constant
def allowance(_owner : address, _spender : address) -> uint256:
    return self.allowances[_owner][_spender]
