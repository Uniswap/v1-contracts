Launch: event({token: indexed(address), exchange: indexed(address)})

exchange_template: public(address)
token_to_exchange: address[address]
exchange_to_token: address[address]
test: public(int128)

@public
def __init__(template: address):
    self.exchange_template = template

@public
def launch_exchange(token: address) -> address:
    assert self.token_to_exchange[token] == 0x0000000000000000000000000000000000000000
    exchange: address = create_with_code_of(self.exchange_template)
    self.token_to_exchange[token] = exchange
    self.exchange_to_token[exchange] = token
    log.Launch(token, exchange)
    return exchange

@public
def token_to_exchange_lookup(token: address) -> address:
    return self.token_to_exchange[token]

@public
@constant
def exchange_to_token_lookup(exchange: address) -> address:
    return self.exchange_to_token[exchange]
