# THIS CONTRACT IS FOR TESTING PURPOSES AND IS NOT PART OF THE PROJECT

# Modified from: https://github.com/ethereum/vyper/blob/master/examples/tokens/ERC20_solidity_compatible/ERC20.v.py

Transfer: event({_from: indexed(address), _to: indexed(address), _value: uint256(wei)})
Approval: event({_owner: indexed(address), _spender: indexed(address), _value: uint256(wei)})

name: public(bytes32)
symbol: public(bytes32)
decimals: public(uint256)
balances: uint256(wei)[address]
allowances: (uint256(wei)[address])[address]
total_supply: uint256(wei)

@public
def __init__(_name: bytes32, _symbol: bytes32, _decimals: uint256, _supply: uint256(wei)):
    _sender: address = msg.sender
    self.name = _name
    self.symbol = _symbol
    self.decimals = _decimals
    self.balances[_sender] = _supply
    self.total_supply = _supply
    log.Transfer(ZERO_ADDRESS, _sender, _supply)

@public
@payable
def deposit():
    _value: uint256(wei) = msg.value
    _sender: address = msg.sender
    self.balances[_sender] = self.balances[_sender] + _value
    self.total_supply = self.total_supply + _value
    log.Transfer(ZERO_ADDRESS, _sender, _value)

@public
def withdraw(_value : uint256(wei)) -> bool:
    _sender: address = msg.sender
    self.balances[_sender] = self.balances[_sender] - _value
    self.total_supply = self.total_supply - _value
    send(_sender, _value)
    log.Transfer(_sender, ZERO_ADDRESS, _value)
    return True

@public
@constant
def totalSupply() -> uint256(wei):
    return self.total_supply

@public
@constant
def balanceOf(_owner : address) -> uint256(wei):
    return self.balances[_owner]

@public
def transfer(_to : address, _value : uint256(wei)) -> bool:
    _sender: address = msg.sender
    self.balances[_sender] = self.balances[_sender] - _value
    self.balances[_to] = self.balances[_to] + _value
    log.Transfer(_sender, _to, _value)
    return True

@public
def transferFrom(_from : address, _to : address, _value : uint256(wei)) -> bool:
    _sender: address = msg.sender
    allowance: uint256(wei) = self.allowances[_from][_sender]
    self.balances[_from] = self.balances[_from] - _value
    self.balances[_to] = self.balances[_to] + _value
    self.allowances[_from][_sender] = allowance - _value
    log.Transfer(_from, _to, _value)
    return True

@public
def approve(_spender : address, _value : uint256(wei)) -> bool:
    _sender: address = msg.sender
    self.allowances[_sender][_spender] = _value
    log.Approval(_sender, _spender, _value)
    return True

@public
@constant
def allowance(_owner : address, _spender : address) -> uint256(wei):
    return self.allowances[_owner][_spender]
