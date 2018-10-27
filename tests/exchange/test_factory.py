from web3.contract import ConciseContract

def test_factory(w3, exchange_template, omg_token, exchange_factory, pad_bytes32, exchange_bytecode, exchange_abi):
    a0, a1 = w3.eth.accounts[:2]
    # Factory initial state
    assert exchange_factory.exchangeTemplate() == exchange_template.address
    assert exchange_factory.getExchange(omg_token.address) == None
    # Create Exchange for UNI Token
    exchange_factory.createExchange(omg_token.address, transact={})
    omg_exchange_address = exchange_factory.getExchange(omg_token.address)
    assert omg_exchange_address != None
    omg_exchange = ConciseContract(w3.eth.contract(address=omg_exchange_address, abi=exchange_abi))
    assert exchange_factory.getToken(omg_exchange.address) == omg_token.address
    assert exchange_factory.tokenCount() == 1
    assert exchange_factory.getTokenWithId(1) == omg_token.address
    # # Can't call initializeFactory on factory twice
    # assert_tx_failed(lambda: exchange_factory.initializeFactory(omg_token.address))
    # # Exchange already exists
    # assert_tx_failed(lambda: exchange_factory.createExchange(omg_token.address))
    # # Can't call setup on exchange
    # assert_tx_failed(lambda: omg_exchange.setup(exchange_factory.address))
    # # Exchange initial state
    assert omg_exchange.name() == pad_bytes32('Uniswap V1')
    assert omg_exchange.symbol() == pad_bytes32('UNI-V1')
    assert omg_exchange.decimals() == 18
    assert omg_exchange.totalSupply() == 0
    assert omg_exchange.tokenAddress() == omg_token.address
    assert omg_exchange.factoryAddress() == exchange_factory.address
    assert w3.eth.getBalance(omg_exchange.address) == 0
    assert omg_token.balanceOf(omg_exchange.address) == 0
