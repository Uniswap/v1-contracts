contract Exchange():
    def setup(_token: address) -> bool: pass

Launch: event({token: indexed(address), exchange: indexed(address)})

exchange_template: public(address)
token_to_exchange: address[address]
exchange_to_token: address[address]

@public
def __init__(_template: address):
    self.exchange_template = _template

@public
def launch_exchange(_token: address) -> address:
    assert self.token_to_exchange[_token] == 0x0000000000000000000000000000000000000000
    _exchange: address = create_with_code_of(self.exchange_template)
    assert Exchange(_exchange).setup(_token) == True
    self.token_to_exchange[_token] = _exchange
    self.exchange_to_token[_exchange] = _token
    log.Launch(_token, _exchange)
    return _exchange

@public
@constant
def token_to_exchange_lookup(_token: address) -> address:
    return self.token_to_exchange[_token]

@public
@constant
def exchange_to_token_lookup(_exchange: address) -> address:
    return self.exchange_to_token[_exchange]
