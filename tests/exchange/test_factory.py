def test_factory(t, chain, utils, exchange_abi, uniswap_exchange, uni_token, exchange_factory, assert_tx_failed):
    # t.s.mine()
    assert utils.remove_0x_head(exchange_factory.exchangeTemplate()) == uniswap_exchange.address.hex()
    exchange_address = exchange_factory.launchExchange(uni_token.address)
    uni_exchange = t.ABIContract(chain, exchange_abi, exchange_address)
    assert exchange_factory.getExchange(uni_token.address) == exchange_address
    assert utils.remove_0x_head(exchange_factory.getToken(uni_exchange.address)) == uni_token.address.hex()
    # Exchange already exists
    assert_tx_failed(lambda: exchange_factory.launchExchange(uni_token.address))
    # Can't call setup on exchange
    assert_tx_failed(lambda: uni_exchange.setup(exchange_factory.address))
    # Exchange initial state
    assert chain.head_state.get_balance(uni_exchange.address) == 0
    assert uni_token.balanceOf(uni_exchange.address) == 0
    assert uni_exchange.totalSupply() == 0
    assert utils.remove_0x_head(uni_exchange.factoryAddress()) == exchange_factory.address.hex()
    assert utils.remove_0x_head(uni_exchange.tokenAddress()) == uni_token.address.hex()
