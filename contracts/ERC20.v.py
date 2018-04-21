# Modified Version of:
# https://github.com/ethereum/vyper/blob/master/examples/tokens/ERC20_solidity_compatible/ERC20.v.py


# Events issued by the contract
Transfer: event({_from: indexed(address), _to: indexed(address), _value: uint256})
Approval: event({_owner: indexed(address), _spender: indexed(address), _value: uint256})

name: public(bytes32)
symbol: public(bytes32)
decimals: public(uint256)
balances: uint256[address]
allowances: (uint256[address])[address]
total_supply: uint256

@public
def __init__(_name: bytes32, _symbol: bytes32, _decimals: uint256, _supply: uint256):
    _sender: address = msg.sender
    self.name = _name
    self.symbol = _symbol
    self.decimals = _decimals
    self.balances[_sender] = _supply
    self.total_supply = _supply
    # Fire deposit event as transfer from 0x0
    log.Transfer(0x0000000000000000000000000000000000000000, _sender, _supply)

@public
@payable
def deposit():
    _value: uint256 = convert(msg.value, 'uint256')
    _sender: address = msg.sender
    self.balances[_sender] = uint256_add(self.balances[_sender], _value)
    self.total_supply = uint256_add(self.total_supply, _value)
    # Fire deposit event as transfer from 0x0
    log.Transfer(0x0000000000000000000000000000000000000000, _sender, _value)

@public
def withdraw(_value : uint256) -> bool:
    _sender: address = msg.sender
    # Make sure sufficient funds are present, op will not underflow supply
    # implicitly through overflow protection
    self.balances[_sender] = uint256_sub(self.balances[_sender], _value)
    self.total_supply = uint256_sub(self.total_supply, _value)
    send(_sender, as_wei_value(convert(_value, 'int128'), 'wei'))
    # Fire withdraw event as transfer to 0x0
    log.Transfer(_sender, 0x0000000000000000000000000000000000000000, _value)
    return True

@public
@constant
def totalSupply() -> uint256:
    return self.total_supply

@public
@constant
def balanceOf(_owner : address) -> uint256:
    return self.balances[_owner]

@public
def transfer(_to : address, _value : uint256) -> bool:
    _sender: address = msg.sender
    # Make sure sufficient funds are present implicitly through overflow protection
    self.balances[_sender] = uint256_sub(self.balances[_sender], _value)
    self.balances[_to] = uint256_add(self.balances[_to], _value)
    # Fire transfer event
    log.Transfer(_sender, _to, _value)
    return True

@public
def transferFrom(_from : address, _to : address, _value : uint256) -> bool:
    _sender: address = msg.sender
    allowance: uint256 = self.allowances[_from][_sender]
    # Make sure sufficient funds/allowance are present implicitly through overflow protection
    self.balances[_from] = uint256_sub(self.balances[_from], _value)
    self.balances[_to] = uint256_add(self.balances[_to], _value)
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
