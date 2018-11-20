from web3.contract import ConciseContract

def test_factory(w3, exchange_template, HAY_token, factory, pad_bytes32, exchange_abi):
    a0, a1 = w3.eth.accounts[:2]
    # Factory initial state
    assert factory.exchangeTemplate() == exchange_template.address
    assert factory.getExchange(HAY_token.address) == None
    # Create Exchange for UNI Token
    factory.createExchange(HAY_token.address, transact={})
    HAY_exchange_address = factory.getExchange(HAY_token.address)
    assert HAY_exchange_address != None
    HAY_exchange = ConciseContract(w3.eth.contract(address=HAY_exchange_address, abi=exchange_abi))
    assert factory.getToken(HAY_exchange.address) == HAY_token.address
    assert factory.tokenCount() == 1
    assert factory.getTokenWithId(1) == HAY_token.address
    # # Can't call initializeFactory on factory twice
    # assert_tx_failed(lambda: factory.initializeFactory(HAY_token.address))
    # # Exchange already exists
    # assert_tx_failed(lambda: factory.createExchange(HAY_token.address))
    # # Can't call setup on exchange
    # assert_tx_failed(lambda: HAY_exchange.setup(factory.address))
    # # Exchange initial state
    assert HAY_exchange.name() == pad_bytes32('Uniswap V1')
    assert HAY_exchange.symbol() == pad_bytes32('UNI-V1')
    assert HAY_exchange.decimals() == 18
    assert HAY_exchange.totalSupply() == 0
    assert HAY_exchange.tokenAddress() == HAY_token.address
    assert HAY_exchange.factoryAddress() == factory.address
    assert w3.eth.getBalance(HAY_exchange.address) == 0
    assert HAY_token.balanceOf(HAY_exchange.address) == 0
