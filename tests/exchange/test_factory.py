def test_factory(t, chain, utils, exchange_abi, exchange_template, omg_token, exchange_factory, assert_tx_failed, pad_bytes32):
    # Factory initial state
    assert utils.remove_0x_head(exchange_factory.templateAddress()) == exchange_template.address.hex()
    # Create Exchange for UNI Token
    exchange_address = exchange_factory.createExchange(omg_token.address)
    omg_exchange = t.ABIContract(chain, exchange_abi, exchange_address)
    assert exchange_factory.getExchange(omg_token.address) == exchange_address
    assert utils.remove_0x_head(exchange_factory.getToken(omg_exchange.address)) == omg_token.address.hex()
    # Can't call setup on factory twice
    assert_tx_failed(lambda: exchange_factory.setup(omg_token.address))
    # Exchange already exists
    assert_tx_failed(lambda: exchange_factory.createExchange(omg_token.address))
    # Can't call setup on exchange
    assert_tx_failed(lambda: omg_exchange.setup(exchange_factory.address))
    # Exchange initial state
    assert omg_exchange.name() == pad_bytes32('Uniswap Exchange')
    assert omg_exchange.symbol() == pad_bytes32('UNI')
    assert omg_exchange.decimals() == 18
    assert omg_exchange.totalSupply() == 0
    assert utils.remove_0x_head(omg_exchange.tokenAddress()) == omg_token.address.hex()
    assert utils.remove_0x_head(omg_exchange.factoryAddress()) == exchange_factory.address.hex()
    assert chain.head_state.get_balance(omg_exchange.address) == 0
    assert omg_token.balanceOf(omg_exchange.address) == 0
