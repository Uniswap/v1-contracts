Launch: event({token: indexed(address), exchange: indexed(address)})

exchange_template: public(address)
token_to_exchange: address[address]
exchange_to_token: address[address]

@public
def __init__(template: address):
    self.exchange_template = template

@public
def launch_exchange(token: address) -> address:
    assert self.token_to_exchange[token] == 0x0000000000000000000000000000000000000000
    exchange_addr: address = create_with_code_of(self.exchange_template)
    data: bytes[4096] = concat(method_id("setup(address)"), convert(token, 'bytes32'))
    assert extract32(raw_call(exchange_addr, data, gas=50000, outsize=32), 0, type=bool) == True
    self.token_to_exchange[token] = exchange_addr
    self.exchange_to_token[exchange_addr] = token
    log.Launch(token, exchange_addr)
    return exchange_addr

@public
@constant
def token_to_exchange_lookup(token_addr: address) -> address:
    return self.token_to_exchange[token_addr]

@public
@constant
def exchange_to_token_lookup(exchange_addr: address) -> address:
    return self.exchange_to_token[exchange_addr]
