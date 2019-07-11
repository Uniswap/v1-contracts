contract Exchange():
    def setup(token_addr: address): modifying

NewExchange: event({token: indexed(address), exchange: indexed(address)})

exchangeTemplate: public(address)
tokenCount: public(uint256)
getExchange: public(map(address, address))
getToken: public(map(address, address))
getTokenWithId: public(map(uint256, address))

@public
def initializeFactory(template: address):
    assert self.exchangeTemplate == ZERO_ADDRESS
    assert template != ZERO_ADDRESS
    self.exchangeTemplate = template

@public
def createExchange(token: address) -> address:
    assert token != ZERO_ADDRESS
    assert self.exchangeTemplate != ZERO_ADDRESS
    assert self.getExchange[token] == ZERO_ADDRESS
    exchange: address = create_forwarder_to(self.exchangeTemplate)
    Exchange(exchange).setup(token)
    self.getExchange[token] = exchange
    self.getToken[exchange] = token
    token_id: uint256 = self.tokenCount + 1
    self.tokenCount = token_id
    self.getTokenWithId[token_id] = token
    log.NewExchange(token, exchange)
    return exchange
