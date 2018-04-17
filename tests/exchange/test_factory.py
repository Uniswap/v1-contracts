def test_factory(t, chain, utils, exchange_abi, uniswap_exchange, uni_token, uniswap_factory, assert_tx_failed):
    assert utils.remove_0x_head(uniswap_factory.exchange_template()) == uniswap_exchange.address.hex()
    exchange_address = uniswap_factory.launch_exchange(uni_token.address)
    uni_token_exchange = t.ABIContract(chain, exchange_abi, exchange_address)
    # assert utils.remove_0x_head(uni_token_exchange.uniswap_factory()) == uniswap_factory.address.hex()
    assert uniswap_factory.token_to_exchange_lookup(uni_token.address) == exchange_address
    assert utils.remove_0x_head(uniswap_factory.exchange_to_token_lookup(uni_token_exchange.address)) == uni_token.address.hex()
    # Exchange already exists
    assert_tx_failed(lambda: uniswap_factory.launch_exchange(uni_token.address))
    # Test UNI Exchange initial state
    assert uni_token_exchange.eth_pool() == 0
    assert uni_token_exchange.token_pool() == 0
    assert uni_token_exchange.invariant() == 0
    assert uni_token_exchange.total_shares() == 0
