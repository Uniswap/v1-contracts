EthToToken: event({buyer: indexed(address), eth_in: indexed(wei_value), tokens_out: indexed(uint256)})
TokenToEth: event({buyer: indexed(address), tokens_in: indexed(currency_value), eth_out: indexed(wei_value)})
Investment: event({investor: indexed(address), eth_invested: indexed(wei_value), tokens_invested: indexed(currency_value)})
Divestment: event({investor: indexed(address), eth_divested: indexed(wei_value), tokens_divested: indexed(currency_value)})

eth_pool: public(wei_value)
token_pool: public(currency_value)
invariant: public(int128(wei * currency))
total_shares: public(int128)
token_address: address(ERC20)
factory_address: public(address)
shares: int128[address]

# Called by factory during launch
@public
def setup(token_addr: address) -> bool:
    assert self.factory_address == 0x0000000000000000000000000000000000000000
    self.factory_address = msg.sender
    self.token_address = token_addr
    return True

# Sets initial token pool and ether pool
@public
@payable
def initiate(token_amount: currency_value):
    assert self.factory_address != 0x0000000000000000000000000000000000000000
    data: bytes[4096] = concat(method_id("token_to_exchange_lookup(address)"), convert(self.token_address, 'bytes32'))
    assert extract32(raw_call(self.factory_address, data, gas=750, outsize=32), 0, type=address) == self
    assert self.invariant == 0
    assert self.total_shares == 0
    assert msg.value >= 10000
    assert token_amount >= 10000
    assert convert(msg.value, 'int128') <= 5*10**18
    self.eth_pool = msg.value
    self.token_pool = token_amount
    self.invariant = msg.value * token_amount
    self.total_shares = 1000
    self.shares[msg.sender] = 1000
    self.token_address.transferFrom(msg.sender, self, convert(token_amount, 'uint256'))
    assert self.invariant > 0

# Exchange ETH for Tokens
@private
def eth_to_tokens(buyer: address, recipent: address, eth_in: wei_value, min_tokens: currency_value):
    assert eth_in > 0
    assert self.invariant > 0
    fee: wei_value = floor(eth_in / 500)
    new_eth_pool: wei_value = self.eth_pool + eth_in
    new_token_pool: currency_value = floor(self.invariant / (new_eth_pool - fee))
    tokens_out: currency_value = self.token_pool - new_token_pool
    assert tokens_out >= min_tokens
    self.eth_pool = new_eth_pool
    self.token_pool = new_token_pool
    self.invariant = new_eth_pool * new_token_pool
    self.token_address.transfer(recipent, convert(tokens_out, 'uint256'))
    log.EthToToken(buyer, eth_in, convert(tokens_out, 'uint256'))

# Buyer sells ETH in exchange for tokens
@public
@payable
def eth_to_tokens_swap(min_tokens: currency_value):
    self.eth_to_tokens(msg.sender, msg.sender, msg.value, min_tokens)

# Buyer sells ETH, recipent receives tokens
@public
@payable
def eth_to_tokens_payment(recipent: address, min_tokens: currency_value):
    assert recipent != 0x0000000000000000000000000000000000000000
    assert recipent != self
    self.eth_to_tokens(msg.sender, recipent, msg.value, min_tokens)

# Exchange Tokens for ETH
@private
def tokens_to_eth(buyer: address, recipent: address, tokens_in: currency_value, min_eth: wei_value):
    assert tokens_in > 0
    assert self.invariant > 0
    fee: currency_value = floor(tokens_in / 500)
    new_token_pool: currency_value = self.token_pool + tokens_in
    new_eth_pool: wei_value = floor(self.invariant / (new_token_pool - fee))
    eth_out: wei_value = self.eth_pool - new_eth_pool
    assert eth_out >= min_eth
    self.eth_pool = new_eth_pool
    self.token_pool = new_token_pool
    self.invariant = new_eth_pool * new_token_pool
    self.token_address.transferFrom(buyer, self, convert(tokens_in, 'uint256'))
    send(recipent, eth_out)
    log.TokenToEth(buyer, tokens_in, eth_out)

# Buyer sells tokens in exchange for ETH
@public
def tokens_to_eth_swap(tokens_in: currency_value, min_eth: wei_value):
    self.tokens_to_eth(msg.sender, msg.sender, tokens_in, min_eth)

# Buyer sells tokens, recipent receives ETH
@public
def tokens_to_eth_payment(recipent: address, tokens_in: currency_value, min_eth: wei_value):
    assert recipent != 0x0000000000000000000000000000000000000000
    assert recipent != self
    self.tokens_to_eth(msg.sender, recipent, tokens_in, min_eth)

# Can only be called by other uniswap exchange contracts in token to token trades
@public
@payable
def tokens_to_tokens_incoming(recipent: address) -> bool:
    assert self.invariant > 0
    data: bytes[4096] = concat(method_id("exchange_to_token_lookup(address)"), convert(msg.sender, 'bytes32'))
    assert extract32(raw_call(self.factory_address, data, gas=750, outsize=32), 0, type=address) != 0x0000000000000000000000000000000000000000
    assert msg.value > 0
    self.eth_to_tokens(msg.sender, recipent, msg.value, 1)
    return True

# Sells tokens to the contract in exchange for other tokens
@private
def tokens_to_tokens(token_addr: address, buyer: address, recipent: address, tokens_in: currency_value, min_tokens: currency_value):
    assert tokens_in > 0
    assert self.invariant > 0
    assert token_addr != self.token_address
    lookup_data: bytes[4096] = concat(method_id("token_to_exchange_lookup(address)"), convert(token_addr, 'bytes32'))
    exchange: address = extract32(raw_call(self.factory_address, lookup_data, gas=750, outsize=32), 0, type=address)
    assert exchange != 0x0000000000000000000000000000000000000000
    fee: currency_value = floor(tokens_in / 500)
    new_token_pool: currency_value = self.token_pool + tokens_in
    new_eth_pool: wei_value = floor(self.invariant / (new_token_pool - fee))
    eth_out: wei_value = self.eth_pool - new_eth_pool
    self.eth_pool = new_eth_pool
    self.token_pool = new_token_pool
    self.invariant = new_eth_pool * new_token_pool
    self.token_address.transferFrom(buyer, self, convert(tokens_in, 'uint256'))
    exchange_data: bytes[4096] = concat(method_id("tokens_to_tokens_incoming(address)"), convert(recipent, 'bytes32'))
    log.TokenToEth(buyer, tokens_in, eth_out)
    assert extract32(raw_call(exchange, exchange_data, value=eth_out, gas=75000, outsize=32), 0, type=bool) == True

# Buyer sells tokens in exchange for ETH
@public
def tokens_to_tokens_swap(token_addr: address, tokens_in: currency_value, min_tokens: currency_value):
    self.tokens_to_tokens(token_addr, msg.sender, msg.sender, tokens_in, min_tokens)

# Buyer sells tokens, recipent receives ETH
@public
def tokens_to_tokens_payment(token_addr: address, recipent: address, tokens_in: currency_value, min_tokens: currency_value):
    assert recipent != 0x0000000000000000000000000000000000000000
    assert recipent != self
    self.tokens_to_tokens(token_addr, msg.sender, recipent, tokens_in, min_tokens)

@public
@payable
def invest():
    assert self.invariant > 0
    assert msg.value > 0
    shares_minted: int128 = floor((msg.value * self.total_shares) / self.eth_pool)
    tokens_invested: currency_value = floor((shares_minted * self.token_pool) / self.total_shares)
    self.shares[msg.sender] = self.shares[msg.sender] + shares_minted
    self.total_shares = self.total_shares + shares_minted
    self.eth_pool = self.eth_pool + msg.value
    self.token_pool = self.token_pool + tokens_invested
    self.invariant = self.eth_pool * self.token_pool
    self.token_address.transferFrom(msg.sender, self, convert(tokens_invested, 'uint256'))
    log.Investment(msg.sender, msg.value, tokens_invested)

@public
@payable
def divest(shares_burned: int128):
    assert self.invariant > 0
    assert shares_burned > 0
    assert self.shares[msg.sender] >= shares_burned
    eth_divested: wei_value = floor((shares_burned * self.eth_pool) / self.total_shares)
    tokens_divested: currency_value = floor((shares_burned * self.token_pool) / self.total_shares)
    self.shares[msg.sender] = self.shares[msg.sender] - shares_burned
    self.total_shares = self.total_shares - shares_burned
    self.eth_pool = self.eth_pool - eth_divested
    self.token_pool = self.token_pool - tokens_divested
    self.invariant = self.eth_pool * self.token_pool
    send(msg.sender, eth_divested)
    self.token_address.transfer(msg.sender, convert(tokens_divested, 'uint256'))
    log.Divestment(msg.sender, eth_divested, tokens_divested)

@public
@constant
def get_token_address() -> address:
    return self.token_address

@public
@constant
def get_shares(addr: address) -> int128:
    return self.shares[addr]
