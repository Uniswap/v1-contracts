EthToToken: event({buyer: indexed(address), eth_in: indexed(uint256), tokens_out: indexed(uint256)})
TokenToEth: event({buyer: indexed(address), tokens_in: indexed(uint256), eth_out: indexed(uint256)})
Investment: event({investor: indexed(address), eth_invested: indexed(uint256), tokens_invested: indexed(uint256)})
Divestment: event({investor: indexed(address), eth_divested: indexed(uint256), tokens_divested: indexed(uint256)})

eth_pool: public(uint256)
token_pool: public(uint256)
invariant: public(uint256)
total_shares: public(uint256)
token_address: address(ERC20)
factory_address: public(address)
shares: uint256[address]

# Called by factory during launch
@public
def setup(token_addr: address) -> bool:
    assert self.factory_address == 0x0000000000000000000000000000000000000000
    self.factory_address = msg.sender
    self.token_address = token_addr
    assert self.factory_address != 0x0000000000000000000000000000000000000000
    return True

# Sets initial token pool, ether pool, and shares
@public
@payable
def initialize(token_amount: uint256):
    assert self.invariant == convert(0, 'uint256')
    assert self.total_shares == convert(0, 'uint256')
    assert self.factory_address != 0x0000000000000000000000000000000000000000
    eth_in: uint256 = convert(msg.value, 'uint256')
    assert uint256_ge(eth_in, convert(100000, 'uint256'))
    assert uint256_le(eth_in, convert(5*10**18, 'uint256'))
    assert uint256_ge(token_amount, convert(100000, 'uint256'))
    data: bytes[4096] = concat(method_id("token_to_exchange_lookup(address)"), convert(self.token_address, 'bytes32'))
    assert extract32(raw_call(self.factory_address, data, gas=750, outsize=32), 0, type=address) == self
    self.eth_pool = eth_in
    self.token_pool = token_amount
    self.invariant = uint256_mul(eth_in, token_amount)
    initial_shares: uint256 = uint256_div(eth_in, convert(100000, 'uint256'))
    self.total_shares = initial_shares
    self.shares[msg.sender] = initial_shares
    self.token_address.transferFrom(msg.sender, self, token_amount)
    assert uint256_gt(self.invariant, convert(0, 'uint256'))

# Exchange ETH for tokens
@private
def eth_to_tokens(buyer: address, recipent: address, eth_in: uint256, min_tokens: uint256):
    assert uint256_gt(self.invariant, convert(0, 'uint256'))
    assert uint256_gt(eth_in, convert(0, 'uint256'))
    fee: uint256 = uint256_div(eth_in, convert(500, 'uint256'))
    new_eth_pool: uint256 = uint256_add(self.eth_pool, eth_in)
    temp_eth_pool: uint256 = uint256_sub(new_eth_pool, fee)
    new_token_pool: uint256 = uint256_div(self.invariant, temp_eth_pool)
    tokens_out: uint256 = uint256_sub(self.token_pool, new_token_pool)
    assert uint256_ge(tokens_out, min_tokens)
    self.eth_pool = new_eth_pool
    self.token_pool = new_token_pool
    self.invariant = uint256_mul(new_eth_pool, new_token_pool)
    self.token_address.transfer(recipent, tokens_out)
    log.EthToToken(buyer, eth_in, tokens_out)

# Buyer sells ETH , buyer receives tokens
@public
@payable
def eth_to_tokens_swap(min_tokens: uint256):
    self.eth_to_tokens(msg.sender, msg.sender, convert(msg.value, 'uint256'), min_tokens)

# Buyer sells ETH, recipent receives tokens
@public
@payable
def eth_to_tokens_payment(recipent: address, min_tokens: uint256):
    assert recipent != 0x0000000000000000000000000000000000000000
    assert recipent != self
    self.eth_to_tokens(msg.sender, recipent, convert(msg.value, 'uint256'), min_tokens)

# Exchange tokens for ETH
@private
def tokens_to_eth(buyer: address, recipent: address, tokens_in: uint256, min_eth: uint256):
    assert uint256_gt(self.invariant, convert(0, 'uint256'))
    assert uint256_gt(tokens_in, convert(0, 'uint256'))
    fee: uint256 = uint256_div(tokens_in, convert(500, 'uint256'))
    new_token_pool: uint256 = uint256_add(self.token_pool, tokens_in)
    temp_token_pool: uint256 = uint256_sub(new_token_pool, fee)
    new_eth_pool: uint256 = uint256_div(self.invariant, temp_token_pool)
    eth_out: uint256 = uint256_sub(self.eth_pool, new_eth_pool)
    assert uint256_ge(eth_out, min_eth)
    self.eth_pool = new_eth_pool
    self.token_pool = new_token_pool
    self.invariant = uint256_mul(new_eth_pool, new_token_pool)
    self.token_address.transferFrom(buyer, self, tokens_in)
    send(recipent, as_wei_value(convert(eth_out, 'int128'), 'wei'))
    log.TokenToEth(buyer, tokens_in, eth_out)

# Buyer sells tokens, buyer receives ETH
@public
def tokens_to_eth_swap(tokens_in: uint256, min_eth: uint256):
    self.tokens_to_eth(msg.sender, msg.sender, tokens_in, min_eth)

# Buyer sells tokens, recipent receives ETH
@public
def tokens_to_eth_payment(recipent: address, tokens_in: uint256, min_eth: uint256):
    assert recipent != 0x0000000000000000000000000000000000000000
    assert recipent != self
    self.tokens_to_eth(msg.sender, recipent, tokens_in, min_eth)

# Called by other uniswap exchange contracts in token to token trades
@public
@payable
def tokens_to_tokens_incoming(recipent: address, min_tokens: uint256) -> bool:
    data: bytes[4096] = concat(method_id("exchange_to_token_lookup(address)"), convert(msg.sender, 'bytes32'))
    assert extract32(raw_call(self.factory_address, data, gas=750, outsize=32), 0, type=address) != 0x0000000000000000000000000000000000000000
    self.eth_to_tokens(msg.sender, recipent, convert(msg.value, 'uint256'), min_tokens) # NEED TO PASS MIN VALUE
    return True

# Exchange tokens for any token in factory/registry
@private
def tokens_to_tokens(token_addr: address, buyer: address, recipent: address, tokens_in: uint256, min_tokens: uint256):
    assert uint256_gt(self.invariant, convert(0, 'uint256'))
    assert uint256_gt(tokens_in, convert(0, 'uint256'))
    assert uint256_gt(min_tokens, convert(0, 'uint256'))
    assert token_addr != self.token_address
    factory_data: bytes[4096] = concat(method_id("token_to_exchange_lookup(address)"), convert(token_addr, 'bytes32'))
    exchange: address = extract32(raw_call(self.factory_address, factory_data, gas=750, outsize=32), 0, type=address)
    assert exchange != 0x0000000000000000000000000000000000000000
    fee: uint256 = uint256_div(tokens_in, convert(500, 'uint256'))
    new_token_pool: uint256 = uint256_add(self.token_pool, tokens_in)
    temp_token_pool: uint256 = uint256_sub(new_token_pool, fee)
    new_eth_pool: uint256 = uint256_div(self.invariant, temp_token_pool)
    eth_out: uint256 = uint256_sub(self.eth_pool, new_eth_pool)
    self.eth_pool = new_eth_pool
    self.token_pool = new_token_pool
    self.invariant = uint256_mul(new_eth_pool, new_token_pool)
    self.token_address.transferFrom(buyer, self, tokens_in)
    exchange_data: bytes[4096] = concat(method_id("tokens_to_tokens_incoming(address,uint256)"), convert(recipent, 'bytes32'), convert(min_tokens, 'bytes32'))
    assert extract32(raw_call(exchange, exchange_data, value=as_wei_value(convert(eth_out, 'int128'), 'wei'), gas=100000, outsize=32), 0, type=bool) == True
    log.TokenToEth(buyer, tokens_in, eth_out)

# Buyer sells tokens, buyer receives different tokens
@public
def tokens_to_tokens_swap(token_addr: address, tokens_in: uint256, min_tokens: uint256):
    self.tokens_to_tokens(token_addr, msg.sender, msg.sender, tokens_in, min_tokens)

# Buyer sells tokens, recipent receives different tokens
@public
def tokens_to_tokens_payment(token_addr: address, recipent: address, tokens_in: uint256, min_tokens: uint256):
    assert recipent != 0x0000000000000000000000000000000000000000
    assert recipent != self
    self.tokens_to_tokens(token_addr, msg.sender, recipent, tokens_in, min_tokens)

# Lock up ETH and tokens for shares
@public
@payable
def invest(min_shares: uint256):
    assert uint256_gt(self.invariant, convert(0, 'uint256'))
    assert uint256_gt(min_shares, convert(0, 'uint256'))
    assert msg.value > 0
    eth_invested: uint256 = convert(msg.value, 'uint256')
    shares_minted: uint256 = uint256_div(uint256_mul(eth_invested, self.total_shares), self.eth_pool)
    assert uint256_gt(shares_minted, min_shares)
    tokens_invested: uint256 = uint256_div(uint256_mul(shares_minted, self.token_pool), self.total_shares)
    self.shares[msg.sender] = uint256_add(self.shares[msg.sender], shares_minted)
    self.total_shares = uint256_add(self.total_shares, shares_minted)
    self.eth_pool = uint256_add(self.eth_pool, eth_invested)
    self.token_pool = uint256_add(self.token_pool, tokens_invested)
    self.invariant = uint256_mul(self.eth_pool, self.token_pool)
    self.token_address.transferFrom(msg.sender, self, tokens_invested)
    log.Investment(msg.sender, eth_invested, tokens_invested)

# Burn shares to receive ETH, tokens, and fees
@public
@payable
def divest(shares_burned: uint256, min_eth: uint256, min_tokens: uint256):
    assert uint256_gt(self.invariant, convert(0, 'uint256'))
    assert uint256_gt(shares_burned, convert(0, 'uint256'))
    assert uint256_gt(min_eth, convert(0, 'uint256'))
    assert uint256_gt(min_tokens, convert(0, 'uint256'))
    eth_divested: uint256 = uint256_div(uint256_mul(shares_burned, self.eth_pool), self.total_shares)
    tokens_divested: uint256 = uint256_div(uint256_mul(shares_burned, self.token_pool), self.total_shares)
    assert uint256_gt(eth_divested, min_eth)
    assert uint256_gt(tokens_divested, min_tokens)
    self.shares[msg.sender] = uint256_sub(self.shares[msg.sender], shares_burned)
    self.total_shares = uint256_sub(self.total_shares, shares_burned)
    if self.total_shares != convert(0, 'uint256'):
        self.eth_pool = uint256_sub(self.eth_pool, eth_divested)
        self.token_pool = uint256_sub(self.token_pool, tokens_divested)
        self.invariant = uint256_mul(self.eth_pool, self.token_pool)
    else:
        self.eth_pool = convert(0, 'uint256')
        self.token_pool = convert(0, 'uint256')
        self.invariant = convert(0, 'uint256')
    self.token_address.transfer(msg.sender, tokens_divested)
    send(msg.sender, as_wei_value(convert(eth_divested, 'int128'), 'wei'))
    log.Divestment(msg.sender, eth_divested, tokens_divested)

@public
@constant
def get_token_address() -> address:
    return self.token_address

@public
@constant
def get_shares(addr: address) -> uint256:
    return self.shares[addr]
