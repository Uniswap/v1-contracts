def test_initiate(t, chain, utils, uni_token, uniswap_factory, uni_token_exchange, assert_tx_failed):
    assert uni_token_exchange.factory_address() == '0x0000000000000000000000000000000000000000'
    assert uni_token_exchange.get_token_address() == '0x0000000000000000000000000000000000000000'
    assert uniswap_factory.token_to_exchange_lookup(uni_token.address) == uni_token_exchange.address
    uni_token.approve(uni_token_exchange.address, 100*10**18)
    uni_token_exchange.initiate(uniswap_factory.address, uni_token.address, 10*10**18, value=5*10**18)
    assert utils.remove_0x_head(uni_token_exchange.get_token_address()) == uni_token.address.hex()
    assert utils.remove_0x_head(uni_token_exchange.factory_address()) == uniswap_factory.address.hex()
    assert uni_token_exchange.total_shares() == 1000
    assert uni_token_exchange.get_shares(t.a0) == 1000

def test_invest_divest(t, chain, utils, uni_token, uniswap_factory, uni_token_exchange, assert_tx_failed):
    uni_token.transfer(t.a1, 10*10**18)
    uni_token.approve(uni_token_exchange.address, 100*10**18)
    uni_token.approve(uni_token_exchange.address, 10*10**18, sender=t.k1)
    uni_token_exchange.initiate(uniswap_factory.address, uni_token.address, 2*10**18, value=1*10**18)
    assert uni_token_exchange.total_shares() == 1000
    assert uni_token_exchange.get_shares(t.a0) == 1000
    assert uni_token_exchange.get_shares(t.a1) == 0
    assert uni_token.balanceOf(t.a1) == 10*10**18
    uni_token_exchange.invest(value=5*10**18, sender=t.k1)
    assert uni_token_exchange.total_shares() == 6000
    assert uni_token_exchange.get_shares(t.a0) == 1000
    assert uni_token_exchange.get_shares(t.a1) == 5000
    assert uni_token.balanceOf(t.a1) == 0
    uni_token_exchange.divest(5000, sender=t.k1)
    assert uni_token_exchange.total_shares() == 1000
    assert uni_token_exchange.get_shares(t.a0) == 1000
    assert uni_token_exchange.get_shares(t.a1) == 0
    assert uni_token.balanceOf(t.a1) == 10*10**18
