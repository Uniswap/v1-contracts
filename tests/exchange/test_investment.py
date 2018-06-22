def test_initialize(t, chain, utils, uni_token, uniswap_factory, uni_token_exchange, assert_tx_failed):
    assert uniswap_factory.get_exchange(uni_token.address) == uni_token_exchange.address
    uni_token.approve(uni_token_exchange.address, 100*10**18)
    uni_token_exchange.initialize(10*10**18, value=5*10**18, startgas=110950)
    # uni_token_exchange.initialize(10*10**18, value=5*10**18, startgas=108800)
    # uni_token_exchange.initialize(10*10**18, value=5*10**18, startgas=106650)
    assert chain.head_state.get_balance(uni_token_exchange.address) == 5*10**18
    assert uni_token.balanceOf(uni_token_exchange.address) == 10*10**18
    assert utils.remove_0x_head(uni_token_exchange.token_address()) == uni_token.address.hex()
    assert utils.remove_0x_head(uni_token_exchange.factory_address()) == uniswap_factory.address.hex()
    assert uni_token_exchange.totalSupply() == 5*10**18
    assert uni_token_exchange.balanceOf(t.a0) == 5*10**18
#
def test_invest_divest(t, chain, utils, uni_token, uniswap_factory, uni_token_exchange, assert_tx_failed):
    uni_token.transfer(t.a1, 10*10**18)
    uni_token.approve(uni_token_exchange.address, 100*10**18)
    uni_token.approve(uni_token_exchange.address, 10*10**18, sender=t.k1)
    uni_token_exchange.initialize(2*10**18, value=1*10**18)
    timeout = chain.head_state.timestamp + 300
    # First liquidity provider (t.a0) initializes exchange
    assert uni_token_exchange.totalSupply() == 1*10**18
    assert uni_token_exchange.balanceOf(t.a0) == 1*10**18
    assert uni_token_exchange.balanceOf(t.a1) == 0
    assert uni_token_exchange.balanceOf(t.a2) == 0
    assert uni_token.balanceOf(t.a1) == 10*10**18
    assert uni_token.balanceOf(t.a2) == 0
    assert chain.head_state.get_balance(uni_token_exchange.address) == 1*10**18
    assert uni_token.balanceOf(uni_token_exchange.address) == 2*10**18
    # Second liquidity provider (t.a1) invests in exchange
    uni_token_exchange.invest(1, timeout, value=5*10**18, sender=t.k1)
    assert uni_token_exchange.totalSupply() == 6*10**18
    assert uni_token_exchange.balanceOf(t.a0) == 1*10**18
    assert uni_token_exchange.balanceOf(t.a1) == 5*10**18
    assert uni_token_exchange.balanceOf(t.a2) == 0
    assert uni_token.balanceOf(t.a1) == 0
    assert chain.head_state.get_balance(uni_token_exchange.address) == 6*10**18
    assert uni_token.balanceOf(uni_token_exchange.address) == 12*10**18
    # Can't divest more share than owned
    assert_tx_failed(lambda: uni_token_exchange.divest((5*10**18 + 1), 1, 1, timeout, sender=t.k2))
    # Mine block
    chain.mine()
    # Second liquidity provider (t.a1) transfers shares to third liquidity provider (t.a2)
    uni_token_exchange.transfer(t.a2, 2*10**18, sender=t.k1)
    assert uni_token_exchange.balanceOf(t.a0) == 1*10**18
    assert uni_token_exchange.balanceOf(t.a1) == 3*10**18
    assert uni_token_exchange.balanceOf(t.a2) == 2*10**18
    assert uni_token.balanceOf(t.a1) == 0
    assert chain.head_state.get_balance(uni_token_exchange.address) == 6*10**18
    assert uni_token.balanceOf(uni_token_exchange.address) == 12*10**18
    # Can't initialize while their are any shares left
    assert_tx_failed(lambda: uni_token_exchange.initialize(2*10**18, value=1*10**18))
    # Mine block
    chain.mine()
    # Second and third liquidity providers cash out their shares
    uni_token_exchange.divest(1*10**18, 1, 1, timeout)
    uni_token_exchange.divest(3*10**18, 1, 1, timeout, sender=t.k1)
    uni_token_exchange.divest(2*10**18, 1, 1, timeout, sender=t.k2)
    assert uni_token_exchange.totalSupply() == 0
    assert uni_token_exchange.balanceOf(t.a0) == 0
    assert uni_token_exchange.balanceOf(t.a1) == 0
    assert uni_token_exchange.balanceOf(t.a2) == 0
    assert uni_token.balanceOf(t.a1) == 6*10**18
    assert uni_token.balanceOf(t.a2) == 4*10**18
    assert chain.head_state.get_balance(uni_token_exchange.address) == 0
    assert uni_token.balanceOf(uni_token_exchange.address) == 0
    # Can initialize again after all shares are divested
    uni_token_exchange.initialize(2*10**18, value=1*10**18)
