contract Exchange():
    def setup(_token: address) -> bool: modifying

NewExchange: event({token: indexed(address), exchange: indexed(address)})

exchange_template: public(address)
token_to_exchange: address[address]
exchange_to_token: address[address]

@public
def __init__(_template: address):
    self.exchange_template = _template

@public
def launch_exchange(_token: address) -> address:
    assert self.token_to_exchange[_token] == ZERO_ADDRESS
    _exchange: address = create_with_code_of(self.exchange_template)
    assert Exchange(_exchange).setup(_token)
    self.token_to_exchange[_token] = _exchange
    self.exchange_to_token[_exchange] = _token
    log.NewExchange(_token, _exchange)
    return _exchange

@public
@constant
def get_exchange(_token: address) -> address:
    return self.token_to_exchange[_token]

@public
@constant
def get_token(_exchange: address) -> address:
    return self.exchange_to_token[_exchange]
