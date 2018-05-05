class Factory():
    def token_to_exchange_lookup(token_addr: address) -> address: pass

# class Exchange():
#     def eth_to_tokens_payment(recipent: address, min_token_purchase: uint256, timeout: uint256) -> bool: pass

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
@payable
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
    assert eth_invested >= convert(100000000, 'uint256')
    assert tokens_invested >= convert(100000000, 'uint256')
    assert Factory(self.factory_address).token_to_exchange_lookup(self.token_address) == self
    self.eth_pool = eth_invested
    self.token_pool = tokens_invested
    initial_shares: uint256 = eth_invested / convert(100000, 'uint256')
    self.total_shares = initial_shares
    self.shares[msg.sender] = initial_shares
    self.token_address.transferFrom(msg.sender, self, tokens_invested)
    log.Investment(msg.sender, eth_invested, tokens_invested)
    assert self.total_shares > convert(0, 'uint256')

# Exchange ETH for tokens
@private
def eth_to_tokens(
        buyer: address,
        recipent: address,
        eth_sold: uint256,
        min_token_purchase: uint256
    ):
    assert self.total_shares > convert(0, 'uint256')
    assert eth_sold > convert(0, 'uint256')
    eth_in_pool: uint256 = self.eth_pool
    tokens_in_pool: uint256 = self.token_pool
    invariant: uint256 = eth_in_pool * tokens_in_pool
    fee: uint256 = eth_sold / convert(500, 'uint256')
    new_eth_pool: uint256 = eth_in_pool + eth_sold
    new_token_pool: uint256 = invariant / (new_eth_pool - fee)
    tokens_purchased: uint256 = tokens_in_pool - new_token_pool
    assert tokens_purchased >= min_token_purchase
    self.eth_pool = new_eth_pool
    self.token_pool = new_token_pool
    self.token_address.transfer(recipent, tokens_purchased)
    log.EthToToken(buyer, eth_sold, tokens_purchased)

# Buyer converts ETH to tokens
@public
@payable
def eth_to_tokens_swap(min_token_purchase: uint256, timeout: uint256) -> bool:
    assert timeout > convert(block.timestamp, 'uint256')
    self.eth_to_tokens(msg.sender, msg.sender, convert(msg.value, 'uint256'), min_token_purchase)
    return True

# Buyer sells ETH for tokens and sends tokens to recipient
@public
@payable
def eth_to_tokens_payment(recipent: address, min_token_purchase: uint256, timeout: uint256) -> bool:
    assert timeout > convert(block.timestamp, 'uint256')
    assert recipent != 0x0000000000000000000000000000000000000000
    assert recipent != self
    self.eth_to_tokens(msg.sender, recipent, convert(msg.value, 'uint256'), min_token_purchase)
    return True

# Exchange tokens for ETH
@private
def tokens_to_eth(
        buyer: address,
        recipent: address,
        tokens_sold: uint256,
        min_eth_purchase: uint256
    ):
    assert self.total_shares > convert(0, 'uint256')
    assert tokens_sold > convert(0, 'uint256')
    eth_in_pool: uint256 = self.eth_pool
    tokens_in_pool: uint256 = self.token_pool
    invariant: uint256 = eth_in_pool * tokens_in_pool
    fee: uint256 = tokens_sold / convert(500, 'uint256')
    new_token_pool: uint256 = tokens_in_pool + tokens_sold
    new_eth_pool: uint256 = invariant / (new_token_pool - fee)
    eth_purchased: uint256 = eth_in_pool - new_eth_pool
    assert eth_purchased >= min_eth_purchase
    self.eth_pool = new_eth_pool
    self.token_pool = new_token_pool
    self.token_address.transferFrom(buyer, self, tokens_sold)
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

# Exchange tokens for any other tokens
@private
def tokens_to_tokens(
        token_addr: address,
        buyer: address,
        recipent: address,
        tokens_sold: uint256,
        min_token_purchase: uint256,
        timeout: uint256
    ):
    assert self.total_shares > convert(0, 'uint256')
    assert tokens_sold > convert(0, 'uint256')
    assert min_token_purchase > convert(0, 'uint256')
    assert token_addr != self.token_address
    exchange_addr: address = Factory(self.factory_address).token_to_exchange_lookup(token_addr)
    assert exchange_addr != 0x0000000000000000000000000000000000000000
    eth_in_pool: uint256 = self.eth_pool
    tokens_in_pool: uint256 = self.token_pool
    invariant: uint256 = eth_in_pool * tokens_in_pool
    fee: uint256 = tokens_sold / convert(500, 'uint256')
    new_token_pool: uint256 = tokens_in_pool + tokens_sold
    new_eth_pool: uint256 = invariant / (new_token_pool - fee)
    eth_purchased: uint256 = eth_in_pool - new_eth_pool
    self.eth_pool = new_eth_pool
    self.token_pool = new_token_pool
    self.token_address.transferFrom(buyer, self, tokens_sold)
    exchange_data: bytes[4096] = concat(
        method_id("eth_to_tokens_payment(address,uint256,uint256)"),
        convert(recipent, 'bytes32'),
        convert(min_token_purchase, 'bytes32'),
        convert(timeout, 'bytes32'),
    )
    wei_purchased: wei_value = as_wei_value(convert(eth_purchased, 'int128'), 'wei')
    assert extract32(raw_call(exchange_addr, exchange_data, value=wei_purchased, gas=55000, outsize=32), 0, type=bool) == True
    # assert Exchange(exchange_addr).eth_to_tokens_payment(recipent, min_token_purchase, timeout, value=wei_purchased) == True
    log.TokenToEth(buyer, tokens_sold, eth_purchased)

# Buyer sells tokens for any other tokens
@public
def tokens_to_tokens_swap(
        token_addr: address,
        tokens_sold: uint256,
        min_token_purchase: uint256,
        timeout: uint256
    ) -> bool:
    assert timeout > convert(block.timestamp, 'uint256')
    self.tokens_to_tokens(token_addr, msg.sender, msg.sender, tokens_sold, min_token_purchase, timeout)
    return True

# Buyer sells tokens for any other tokens and sends tokens to recipient
@public
def tokens_to_tokens_payment(
        token_addr: address,
        recipent: address,
        tokens_sold: uint256,
        min_token_purchase: uint256,
        timeout: uint256
    ) -> bool:
    assert timeout > convert(block.timestamp, 'uint256')
    assert recipent != 0x0000000000000000000000000000000000000000
    assert recipent != self
    self.tokens_to_tokens(token_addr, msg.sender, recipent, tokens_sold, min_token_purchase, timeout)
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
    eth_in_pool: uint256 = self.eth_pool
    tokens_in_pool: uint256 = self.token_pool
    shares_minted: uint256 = (eth_invested * share_total) / eth_in_pool
    assert shares_minted > min_shares
    tokens_invested: uint256 = (shares_minted * tokens_in_pool) / share_total
    self.shares[msg.sender] = self.shares[msg.sender] + shares_minted
    self.total_shares = share_total + shares_minted
    self.eth_pool = eth_in_pool + eth_invested
    self.token_pool = tokens_in_pool + tokens_invested
    self.token_address.transferFrom(msg.sender, self, tokens_invested)
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
    eth_in_pool: uint256 = self.eth_pool
    tokens_in_pool: uint256 = self.token_pool
    eth_divested: uint256 = (shares_burned * eth_in_pool) / share_total
    tokens_divested: uint256 = (shares_burned * tokens_in_pool) / share_total
    assert eth_divested > min_eth
    assert tokens_divested > min_tokens
    self.shares[msg.sender] = self.shares[msg.sender] - shares_burned
    self.total_shares = share_total - shares_burned
    if self.total_shares != convert(0, 'uint256'):
        self.eth_pool = eth_in_pool - eth_divested
        self.token_pool = tokens_in_pool - tokens_divested
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
    self.shares[_sender] = self.shares[_sender] - _value
    self.shares[_to] = self.shares[_to] + _value
    log.Transfer(_sender, _to, _value)
    return True

@public
def transferFrom(_from : address, _to : address, _value : uint256) -> bool:
    _sender: address = msg.sender
    allowance: uint256 = self.allowances[_from][_sender]
    self.shares[_from] = self.shares[_from] - _value
    self.shares[_to] = self.shares[_to] + _value
    self.allowances[_from][_sender] = allowance - _value
    log.Transfer(_from, _to, _value)
    return True

@public
def approve(_spender : address, _value : uint256) -> bool:
    _sender: address = msg.sender
    self.allowances[_sender][_spender] = _value
    log.Approval(_sender, _spender, _value)
    return True

@public
@constant
def allowance(_owner : address, _spender : address) -> uint256:
    return self.allowances[_owner][_spender]
