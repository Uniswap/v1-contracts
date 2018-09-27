# @title Uniswap Exchange Interface V1
# @author Hayden Adams (@haydenadams)
# @notice Source code found at https://github.com/uniswap
# @notice Use at your own risk

contract Factory():
    def getExchange(token_addr: address) -> address: constant

contract Exchange():
    def getEthToTokenExactPrice(tokens_bought: uint256) -> uint256(wei): constant
    def ethToTokenTransfer(min_tokens: uint256, deadline: timestamp, recipient: address) -> uint256: modifying
    def ethToTokenTransferExact(tokens_bought: uint256, deadline: timestamp, recipient: address) -> uint256(wei): modifying

TokenPurchase: event({buyer: indexed(address), eth_sold: indexed(uint256(wei)), tokens_bought: indexed(uint256)})
EthPurchase: event({buyer: indexed(address), tokens_sold: indexed(uint256), eth_bought: indexed(uint256(wei))})
AddLiquidity: event({provider: indexed(address), eth_amount: indexed(uint256(wei)), token_amount: indexed(uint256)})
RemoveLiquidity: event({provider: indexed(address), eth_amount: indexed(uint256(wei)), token_amount: indexed(uint256)})
Transfer: event({_from: indexed(address), _to: indexed(address), _value: uint256})
Approval: event({_owner: indexed(address), _spender: indexed(address), _value: uint256})

name: public(bytes32)                             # Uniswap Exchange
symbol: public(bytes32)                           # UNI
decimals: public(uint256)                         # 18
totalSupply: public(uint256)                      # total number of liquidity tokens in existence
balances: uint256[address]                        # liquidity balance of an address
allowances: (uint256[address])[address]           # liquidity allowance of one address on another
token: address(ERC20)                             # address of the ERC20 token traded on this exchange
factory: Factory                                  # interface for the factory that created this exchange

# @dev This function acts as a contract constructor which is not currently supported in contracts deployed
#      using create_with_code_of(). It is called once by the factory during contract ceation.
@public
def setup(token_addr: address):
    assert (self.factory == ZERO_ADDRESS and self.token == ZERO_ADDRESS) and token_addr != ZERO_ADDRESS
    self.factory = msg.sender
    self.token = token_addr
    self.name = 0x556e69737761702045786368616e676500000000000000000000000000000000
    self.symbol = 0x554e490000000000000000000000000000000000000000000000000000000000
    self.decimals = 18

# @notice Deposit ETH and Tokens (self.token) at current ratio to mint UNI tokens.
# @dev min_amount has a djfferent meaning when total UNI supply is 0.
# @param min_amount Minimum number of UNI tokens sender will receive (when UNI supply is not 0).
# @param min_amount Number of tokens deposited (when total UNI supply is 0).
# @param deadline Time after which this transaction can no longer be executed.
# @return The amount of UNI minted.
@public
@payable
def addLiquidity(min_amount: uint256, deadline: timestamp) -> uint256:
    assert deadline > block.timestamp and min_amount > 0
    total_liquidity: uint256 = self.totalSupply
    if total_liquidity > 0:
        eth_reserve: uint256(wei) = self.balance - msg.value
        token_reserve: uint256 = self.token.balanceOf(self)
        token_amount: uint256 = msg.value * token_reserve / eth_reserve + 1
        liquidity_minted: uint256 = msg.value * total_liquidity / eth_reserve
        assert liquidity_minted > min_amount
        self.balances[msg.sender] += liquidity_minted
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
        self.balances[msg.sender] = initial_liquidity
        assert self.token.transferFrom(msg.sender, self, token_amount)
        log.AddLiquidity(msg.sender, msg.value, token_amount)
        log.Transfer(ZERO_ADDRESS, msg.sender, initial_liquidity)
        return initial_liquidity

# @dev Burn UNI tokens to withdraw ETH and Tokens at current ratio.
# @param amount Amount of UNI burned.
# @param min_eth Minimum ETH withdrawn.
# @param min_tokens Minimum Tokens withdrawn.
# @param deadline Time after which this transaction can no longer be executed.
# @return The amount of ETH and Tokens withdrawn.
@public
def removeLiquidity(amount: uint256, min_eth: uint256(wei), min_tokens: uint256, deadline: timestamp) -> (uint256(wei), uint256):
    assert (amount > 0 and deadline > block.timestamp) and (min_eth > 0 and min_tokens > 0)
    total_liquidity: uint256 = self.totalSupply
    assert total_liquidity > 0
    token_reserve: uint256 = self.token.balanceOf(self)
    eth_amount: uint256(wei) = amount * self.balance / total_liquidity
    token_amount: uint256 = amount * token_reserve / total_liquidity
    assert eth_amount > min_eth and token_amount > min_tokens
    self.balances[msg.sender] -= amount
    self.totalSupply = total_liquidity - amount
    assert self.token.transfer(msg.sender, token_amount)
    send(msg.sender, eth_amount)
    log.RemoveLiquidity(msg.sender, eth_amount, token_amount)
    log.Transfer(msg.sender, ZERO_ADDRESS, amount)
    return eth_amount, token_amount

# @dev Pricing functon for converting between ETH and Tokens.
# @param input_amount Amount of ETH or Tokens being sold.
# @param input_reserve Amount of ETH or Tokens (input type) in exchange reserves.
# @param output_reserve Amount of ETH or Tokens (output type) in exchange reserves.
# @return Amount of ETH or Tokens purchased.
@private
@constant
def getInputPrice(input_amount: uint256, input_reserve: uint256, output_reserve: uint256) -> uint256:
    assert input_reserve > 0 and output_reserve > 0
    input_amount_with_fee: uint256 = input_amount * 997
    numerator: uint256 = input_amount_with_fee * output_reserve
    denominator: uint256 = (input_reserve * 1000) + input_amount_with_fee
    return numerator / denominator

# @dev Pricing functon for converting between ETH and Tokens.
# @param output_amount Amount of ETH or Tokens being purchased.
# @param input_reserve Amount of ETH or Tokens (input type) in exchange reserves.
# @param output_reserve Amount of ETH or Tokens (output type) in exchange reserves.
# @return Amount of ETH or Tokens sold.
@private
@constant
def getOutputPrice(output_amount: uint256, input_reserve: uint256, output_reserve: uint256) -> uint256:
    assert input_reserve > 0 and output_reserve > 0
    numerator: uint256 = input_reserve * output_amount * 1000
    denominator: uint256 = (output_reserve - output_amount) * 997
    return numerator / denominator + 1

@private
def ethToToken(eth_sold: uint256(wei), min_tokens: uint256, deadline: timestamp, buyer: address, recipient: address) -> uint256:
    assert deadline >= block.timestamp and (eth_sold > 0 and min_tokens > 0)
    token_reserve: uint256 = self.token.balanceOf(self)
    tokens_bought: uint256 = self.getInputPrice(as_unitless_number(eth_sold), as_unitless_number(self.balance - eth_sold), token_reserve)
    assert tokens_bought > min_tokens
    assert self.token.transfer(recipient, tokens_bought)
    log.TokenPurchase(buyer, eth_sold, tokens_bought)
    return tokens_bought

# @notice Convert ETH to Tokens.
# @dev For default function purchases user specifies input amount but cannot specify
#      minimum output or transaction deadline.
@public
@payable
def __default__():
    self.ethToToken(msg.value, 1, block.timestamp, msg.sender, msg.sender)

# @notice Convert ETH to Tokens.
# @dev User specifies exact input (msg.value) and minimum output.
# @param min_tokens Minimum Tokens purchased.
# @param deadline Time after which this transaction can no longer be executed.
@public
@payable
def ethToTokenSwap(min_tokens: uint256, deadline: timestamp) -> uint256:
    return self.ethToToken(msg.value, min_tokens, deadline, msg.sender, msg.sender)

# @notice Convert ETH to Tokens and transfers Tokens to recipient.
# @dev User specifies exact input (msg.value) and minimum output
@public
@payable
def ethToTokenTransfer(min_tokens: uint256, deadline: timestamp, recipient: address) -> uint256:
    assert recipient != self and recipient != ZERO_ADDRESS
    return self.ethToToken(msg.value, min_tokens, deadline, msg.sender, recipient)

@private
def ethToTokenExact(tokens_bought: uint256, max_eth: uint256(wei), deadline: timestamp, buyer: address, recipient: address) -> uint256(wei):
    assert deadline >= block.timestamp and (tokens_bought > 0 and max_eth > 0)
    token_reserve: uint256 = self.token.balanceOf(self)
    eth_sold: uint256 = self.getOutputPrice(tokens_bought, as_unitless_number(self.balance - max_eth), token_reserve)
    # Throws if eth_sold > max_eth
    eth_refund: uint256(wei) = max_eth - as_wei_value(eth_sold, 'wei')
    if eth_refund > 0:
        send(buyer, eth_refund)
    assert self.token.transfer(recipient, tokens_bought)
    log.TokenPurchase(buyer, as_wei_value(eth_sold, 'wei'), tokens_bought)
    return eth_refund

# Converts ETH to Tokens
# User specifies maximum input and exact output
@public
@payable
def ethToTokenSwapExact(tokens_bought: uint256, deadline: timestamp) -> uint256(wei):
    return self.ethToTokenExact(tokens_bought, msg.value, deadline, msg.sender, msg.sender)

# Converts ETH to Tokens and transfers Tokens to recipient
# User specifies maximum input and exact output
@public
@payable
def ethToTokenTransferExact(tokens_bought: uint256, deadline: timestamp, recipient: address) -> uint256(wei):
    assert recipient != self and recipient != ZERO_ADDRESS
    return self.ethToTokenExact(tokens_bought, msg.value, deadline, msg.sender, recipient)

@private
def tokenToEth(tokens_sold: uint256, min_eth: uint256(wei), deadline: timestamp, buyer: address, recipient: address) -> uint256(wei):
    assert deadline >= block.timestamp and (tokens_sold > 0 and min_eth > 0)
    token_reserve: uint256 = self.token.balanceOf(self)
    eth_bought: uint256 = self.getInputPrice(tokens_sold, token_reserve, as_unitless_number(self.balance))
    wei_bought: uint256(wei) = as_wei_value(eth_bought, 'wei')
    assert wei_bought > min_eth
    assert self.token.transferFrom(buyer, self, tokens_sold)
    send(recipient, wei_bought)
    log.EthPurchase(buyer, tokens_sold, wei_bought)
    return wei_bought

# Converts Tokens to ETH
# User specifies exact input and minimum output
@public
def tokenToEthSwap(tokens_sold: uint256, min_eth: uint256(wei), deadline: timestamp) -> uint256(wei):
    return self.tokenToEth(tokens_sold, min_eth, deadline, msg.sender, msg.sender)

# Converts Tokens to ETH and transfers ETH to recipient
# User specifies exact input and minimum output
@public
def tokenToEthTransfer(tokens_sold: uint256, min_eth: uint256(wei), deadline: timestamp, recipient: address) -> uint256(wei):
    assert recipient != self and recipient != ZERO_ADDRESS
    return self.tokenToEth(tokens_sold, min_eth, deadline, msg.sender, recipient)

@private
def tokenToEthExact(eth_bought: uint256(wei), max_tokens: uint256, deadline: timestamp, buyer: address, recipient: address) -> uint256:
    assert deadline >= block.timestamp and eth_bought > 0
    token_reserve: uint256 = self.token.balanceOf(self)
    tokens_sold: uint256 = self.getOutputPrice(as_unitless_number(eth_bought), token_reserve, as_unitless_number(self.balance))
    assert max_tokens > tokens_sold         # tokens sold is always > 0, so max_tokens > 0
    assert self.token.transferFrom(buyer, self, tokens_sold)
    send(recipient, eth_bought)
    log.EthPurchase(buyer, tokens_sold, eth_bought)
    return tokens_sold

# Converts Tokens to ETH
# User specifies maximum input and exact output
@public
def tokenToEthSwapExact(eth_bought: uint256(wei), max_tokens: uint256, deadline: timestamp) -> uint256:
    return self.tokenToEthExact(eth_bought, max_tokens, deadline, msg.sender, msg.sender)

# Converts Tokens to ETH and transfers ETH to recipient
# User specifies maximum input and exact output
@public
def tokenToEthTransferExact(eth_bought: uint256(wei), max_tokens: uint256, deadline: timestamp, recipient: address) -> uint256:
    assert recipient != self and recipient != ZERO_ADDRESS
    return self.tokenToEthExact(eth_bought, max_tokens, deadline, msg.sender, recipient)

@private
def tokenToToken(tokens_sold: uint256, min_tokens_bought: uint256, min_eth_bought: uint256(wei), deadline: timestamp, buyer: address, recipient: address, exchange_addr: address) -> uint256:
    assert deadline >= block.timestamp and (tokens_sold > 0 and min_tokens_bought > 0)
    assert exchange_addr != self and exchange_addr != ZERO_ADDRESS
    token_reserve: uint256 = self.token.balanceOf(self)
    eth_bought: uint256 = self.getInputPrice(tokens_sold, token_reserve, as_unitless_number(self.balance))
    wei_bought: uint256(wei) = as_wei_value(eth_bought, 'wei')
    assert wei_bought > min_eth_bought and min_eth_bought > 0
    assert self.token.transferFrom(buyer, self, tokens_sold)
    # call fails if exchange_addr == ZERO_ADDRESS
    tokens_bought: uint256 = Exchange(exchange_addr).ethToTokenTransfer(min_tokens_bought, deadline, recipient, value=wei_bought)
    log.EthPurchase(buyer, tokens_sold, wei_bought)
    return tokens_bought

# Converts Tokens (self.token) to Tokens (token_addr)
# User specifies exact input and minimum output
@public
def tokenToTokenSwap(tokens_sold: uint256, min_tokens_bought: uint256, min_eth_bought: uint256(wei), deadline: timestamp, token_addr: address) -> uint256:
    # returns ZERO_ADDRESS if no exchange exists for token_addr
    exchange_addr: address = self.factory.getExchange(token_addr)
    return self.tokenToToken(tokens_sold, min_tokens_bought, min_eth_bought, deadline, msg.sender, msg.sender, exchange_addr)

# Converts Tokens (self.token) to Tokens (token_addr) and transfers Tokens (token_addr) to recipient
# User specifies exact input and minimum output
@public
def tokenToTokenTransfer(tokens_sold: uint256, min_tokens_bought: uint256, min_eth_bought: uint256(wei), deadline: timestamp, recipient: address, token_addr: address) -> uint256:
    exchange_addr: address = self.factory.getExchange(token_addr)
    return self.tokenToToken(tokens_sold, min_tokens_bought, min_eth_bought, deadline, msg.sender, recipient, exchange_addr)

@private
def tokenToTokenExact(tokens_bought: uint256, max_tokens_sold: uint256, min_eth_bought: uint256(wei), deadline: timestamp, buyer: address, recipient: address, exchange_addr: address) -> uint256:
    assert deadline >= block.timestamp and (tokens_bought > 0 and min_eth_bought > 0)
    assert exchange_addr != self and exchange_addr != ZERO_ADDRESS
    eth_bought: uint256(wei) = Exchange(exchange_addr).getEthToTokenExactPrice(tokens_bought)
    token_reserve: uint256 = self.token.balanceOf(self)
    tokens_sold: uint256 = self.getOutputPrice(as_unitless_number(eth_bought), token_reserve, as_unitless_number(self.balance))
    assert max_tokens_sold > tokens_sold and eth_bought > min_eth_bought
    assert self.token.transferFrom(buyer, self, tokens_sold)
    eth_refund: uint256(wei) = Exchange(exchange_addr).ethToTokenTransferExact(tokens_bought, deadline, recipient, value=eth_bought)
    log.EthPurchase(buyer, tokens_sold, eth_bought)
    return tokens_sold

# Converts tokens to tokens, sender recieves tokens
# User specifies maximum input and exact output
@public
def tokenToTokenSwapExact(tokens_bought: uint256, max_tokens_sold: uint256, min_eth_bought: uint256(wei), deadline: timestamp, token_addr: address) -> uint256:
    exchange_addr: address = self.factory.getExchange(token_addr)
    return self.tokenToTokenExact(tokens_bought, max_tokens_sold, min_eth_bought, deadline, msg.sender, msg.sender, exchange_addr)

# Converts Tokens (self.token) to Tokens (token_addr) and transfers Tokens (token_addr) to recipient
# User specifies maximum input and exact output
@public
def tokenToTokenTransferExact(tokens_bought: uint256, max_tokens_sold: uint256, min_eth_bought: uint256(wei), deadline: timestamp, recipient: address, token_addr: address) -> uint256:
    exchange_addr: address = self.factory.getExchange(token_addr)
    return self.tokenToTokenExact(tokens_bought, max_tokens_sold, min_eth_bought, deadline, msg.sender, recipient, exchange_addr)

# Converts Tokens (self.token) to Tokens (exchange_addr.token)
# User specifies exact input and minimum output
# This function allows trades across exchanges that were not created in the same factory as this exchange
@public
def tokenToExchangeSwap(tokens_sold: uint256, min_tokens_bought: uint256, min_eth_bought: uint256(wei), deadline: timestamp, exchange_addr: address) -> uint256:
    return self.tokenToToken(tokens_sold, min_tokens_bought, min_eth_bought, deadline, msg.sender, msg.sender, exchange_addr)

# Converts Tokens (self.token) to Tokens (exchange_addr.token) and transfers Tokens (exchange_addr.token) to recipient
# User specifies exact input and minimum output
# This function allows trades across exchanges that were not created in the same factory as this exchange
@public
def tokenToExchangeTransfer(tokens_sold: uint256, min_tokens_bought: uint256, min_eth_bought: uint256(wei), deadline: timestamp, recipient: address, exchange_addr: address) -> uint256:
    assert recipient != self
    return self.tokenToToken(tokens_sold, min_tokens_bought, min_eth_bought, deadline, msg.sender, recipient, exchange_addr)

# Converts Tokens (self.token) to Tokens (exchange_addr.token)
# User specifies maximum input and exact output
# This function allows trades across exchanges that were not created in the same factory as this exchange
@public
def tokenToExchangeSwapExact(tokens_bought: uint256, max_tokens_sold: uint256, min_eth_bought: uint256(wei), deadline: timestamp, exchange_addr: address) -> uint256:
    return self.tokenToTokenExact(tokens_bought, max_tokens_sold, min_eth_bought, deadline, msg.sender, msg.sender, exchange_addr)

# Converts Tokens (self.token) to Tokens (exchange_addr.token) and transfers Tokens (exchange_addr.token) to recipient
# User specifies maximum input and exact output
# This function allows trades across exchanges that were not created in the same factory as this exchange
@public
def tokenToExchangeTransferExact(tokens_bought: uint256, max_tokens_sold: uint256, min_eth_bought: uint256(wei), deadline: timestamp, recipient: address, exchange_addr: address) -> uint256:
    assert recipient != self
    return self.tokenToTokenExact(tokens_bought, max_tokens_sold, min_eth_bought, deadline, msg.sender, recipient, exchange_addr)

# Publc price function for ethToToken()
@public
@constant
def getEthToTokenPrice(eth_sold: uint256(wei)) -> uint256:
    token_reserve: uint256 = self.token.balanceOf(self)
    return self.getInputPrice(as_unitless_number(eth_sold), as_unitless_number(self.balance), token_reserve)

# Publc price function for ethToTokenExact()
@public
@constant
def getEthToTokenExactPrice(tokens_bought: uint256) -> uint256(wei):
    token_reserve: uint256 = self.token.balanceOf(self)
    eth_sold: uint256 = self.getOutputPrice(tokens_bought, as_unitless_number(self.balance), token_reserve)
    return as_wei_value(eth_sold, 'wei')

# Publc price function for tokenToEth()
@public
@constant
def getTokenToEthPrice(tokens_sold: uint256) -> uint256(wei):
    token_reserve: uint256 = self.token.balanceOf(self)
    eth_bought: uint256 = self.getInputPrice(tokens_sold, token_reserve, as_unitless_number(self.balance))
    return as_wei_value(eth_bought, 'wei')

# Publc price function for tokenToEthExact()
@public
@constant
def getTokenToEthExactPrice(eth_bought: uint256(wei)) -> uint256:
    token_reserve: uint256 = self.token.balanceOf(self)
    return self.getOutputPrice(as_unitless_number(eth_bought), token_reserve, as_unitless_number(self.balance))


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
    return self.balances[_owner]

@public
def transfer(_to : address, _value : uint256) -> bool:
    self.balances[msg.sender] -= _value
    self.balances[_to] += _value
    log.Transfer(msg.sender, _to, _value)
    return True

@public
def transferFrom(_from : address, _to : address, _value : uint256) -> bool:
    self.balances[_from] -= _value
    self.balances[_to] += _value
    self.allowances[_from][msg.sender] -= _value
    log.Transfer(_from, _to, _value)
    return True

@public
def approve(_spender : address, _value : uint256) -> bool:
    self.allowances[msg.sender][_spender] = _value
    log.Approval(msg.sender, _spender, _value)
    return True

@public
@constant
def allowance(_owner : address, _spender : address) -> uint256:
    return self.allowances[_owner][_spender]
