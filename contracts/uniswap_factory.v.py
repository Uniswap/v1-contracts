class Exchange():
    def setup(token_addr: address) -> bool: pass

Launch: event({token: indexed(address), exchange: indexed(address)})

exchange_template: public(address)
token_to_exchange: address[address]
exchange_to_token: address[address]

@public
def __init__(template_contract: address):
    self.exchange_template = template_contract

@public
def launch_exchange(token_addr: address) -> address:
    assert self.token_to_exchange[token_addr] == 0x0000000000000000000000000000000000000000
    exchange_addr: address = create_with_code_of(self.exchange_template)
    assert Exchange(exchange_addr).setup(token_addr) == True
    self.token_to_exchange[token_addr] = exchange_addr
    self.exchange_to_token[exchange_addr] = token_addr
    log.Launch(token_addr, exchange_addr)
    return exchange_addr

@public
@constant
def token_to_exchange_lookup(token_addr: address) -> address:
    return self.token_to_exchange[token_addr]

@public
@constant
def exchange_to_token_lookup(exchange_addr: address) -> address:
    return self.exchange_to_token[exchange_addr]
