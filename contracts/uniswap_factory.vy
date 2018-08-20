contract Exchange():
    def setup(token_addr: address) -> bool: modifying

NewExchange: event({token: indexed(address), exchange: indexed(address)})

exchange_template: address
token_to_exchange: address[address]
exchange_to_token: address[address]

# sets the factory
@public
def setup(template: address):
    assert self.exchange_template == ZERO_ADDRESS
    assert template != ZERO_ADDRESS
    self.exchange_template = template

@public
def createExchange(token: address) -> address:
    assert token != ZERO_ADDRESS
    assert self.exchange_template != ZERO_ADDRESS
    assert self.token_to_exchange[token] == ZERO_ADDRESS
    exchange: address = create_with_code_of(self.exchange_template)
    assert Exchange(exchange).setup(token)
    self.token_to_exchange[token] = exchange
    self.exchange_to_token[exchange] = token
    log.NewExchange(token, exchange)
    return exchange

@public
@constant
def getExchange(token: address) -> address:
    return self.token_to_exchange[token]

@public
@constant
def getToken(exchange: address) -> address:
    return self.exchange_to_token[exchange]

@public
@constant
def exchangeTemplate() -> address:
    return self.exchange_template
