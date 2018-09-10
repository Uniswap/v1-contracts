contract Exchange():
    def setup(token_addr: address): modifying

NewExchange: event({token: indexed(address), exchange: indexed(address)})

exchangeTemplate: public(address)
token_to_exchange: address[address]
exchange_to_token: address[address]

@public
def initializeFactory(template: address):
    assert self.exchangeTemplate == ZERO_ADDRESS
    assert template != ZERO_ADDRESS
    self.exchangeTemplate = template

@public
def createExchange(token: address) -> address:
    assert token != ZERO_ADDRESS
    assert self.exchangeTemplate != ZERO_ADDRESS
    assert self.token_to_exchange[token] == ZERO_ADDRESS
    exchange: address = create_with_code_of(self.exchangeTemplate)
    Exchange(exchange).setup(token)
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
