def test_initialize(t, chain, utils, uni_token, exchange_factory, uni_exchange, assert_tx_failed):
    assert exchange_factory.getExchange(uni_token.address) == uni_exchange.address
    assert utils.remove_0x_head(uni_exchange.tokenAddress()) == uni_token.address.hex()
    assert utils.remove_0x_head(uni_exchange.factoryAddress()) == exchange_factory.address.hex()
    uni_token.approve(uni_exchange.address, 100*10**18)
    # Can't initialize without tokens
    assert_tx_failed(lambda: uni_exchange.initialize(10*10**18, value=5*10**18, sender=t.k1))
    chain.mine()
    # msg.value can't be 0
    assert_tx_failed(lambda: uni_exchange.initialize(10*10**18))
    chain.mine()
    # Token value can't be 0
    assert_tx_failed(lambda: uni_exchange.initialize(0, value=5*10**18))
    chain.mine()
    # Throw exception if not enough gas is provided
    assert_tx_failed(lambda: uni_exchange.initialize(10*10**18, value=5*10**18, startgas=25000))
    # Liquidity provider (t.a0) initializes exchange
    uni_exchange.initialize(10*10**18, value=5*10**18, startgas=110950)
    assert chain.head_state.get_balance(uni_exchange.address) == 5*10**18
    assert uni_token.balanceOf(uni_exchange.address) == 10*10**18
    assert uni_exchange.totalSupply() == 5*10**18
    assert uni_exchange.balanceOf(t.a0) == 5*10**18
    # Can't initialize twice
    assert_tx_failed(lambda: uni_exchange.initialize(10*10**18, value=5*10**18))

def test_add_remove_liquidity(t, chain, utils, uni_token, exchange_factory, uni_exchange, assert_tx_failed):
    timeout = chain.head_state.timestamp + 300
    uni_token.transfer(t.a1, 10*10**18)
    uni_token.approve(uni_exchange.address, 100*10**18)
    uni_token.approve(uni_exchange.address, 10*10**18, sender=t.k1)
    # First liquidity provider (t.a0) initializes exchange
    uni_exchange.initialize(2*10**18, value=1*10**18)
    assert uni_exchange.totalSupply() == 1*10**18
    assert uni_exchange.balanceOf(t.a0) == 1*10**18
    assert uni_exchange.balanceOf(t.a1) == 0
    assert uni_exchange.balanceOf(t.a2) == 0
    assert uni_token.balanceOf(t.a1) == 10*10**18
    assert uni_token.balanceOf(t.a2) == 0
    assert chain.head_state.get_balance(uni_exchange.address) == 1*10**18
    assert uni_token.balanceOf(uni_exchange.address) == 2*10**18
    # Second liquidity provider (t.a1) invests in exchange
    uni_exchange.addLiquidity(1, timeout, value=5*10**18, sender=t.k1)
    assert uni_exchange.totalSupply() == 6*10**18
    assert uni_exchange.balanceOf(t.a0) == 1*10**18
    assert uni_exchange.balanceOf(t.a1) == 5*10**18
    assert uni_exchange.balanceOf(t.a2) == 0
    assert uni_token.balanceOf(t.a1) == 0
    assert chain.head_state.get_balance(uni_exchange.address) == 6*10**18
    assert uni_token.balanceOf(uni_exchange.address) == 12*10**18
    # Can't divest more share than owned
    assert_tx_failed(lambda: uni_exchange.removeLiquidity((5*10**18 + 1), 1, 1, timeout, sender=t.k2))
    # Mine block
    chain.mine()
    # Second liquidity provider (t.a1) transfers shares to third liquidity provider (t.a2)
    uni_exchange.transfer(t.a2, 2*10**18, sender=t.k1)
    assert uni_exchange.balanceOf(t.a0) == 1*10**18
    assert uni_exchange.balanceOf(t.a1) == 3*10**18
    assert uni_exchange.balanceOf(t.a2) == 2*10**18
    assert uni_token.balanceOf(t.a1) == 0
    assert chain.head_state.get_balance(uni_exchange.address) == 6*10**18
    assert uni_token.balanceOf(uni_exchange.address) == 12*10**18
    # Can't initialize while their are any shares left
    assert_tx_failed(lambda: uni_exchange.initialize(2*10**18, value=1*10**18))
    # Mine block
    chain.mine()
    # Second and third liquidity providers cash out their shares
    uni_exchange.removeLiquidity(1*10**18, 1, 1, timeout)
    uni_exchange.removeLiquidity(3*10**18, 1, 1, timeout, sender=t.k1)
    uni_exchange.removeLiquidity(2*10**18, 1, 1, timeout, sender=t.k2)
    assert uni_exchange.totalSupply() == 0
    assert uni_exchange.balanceOf(t.a0) == 0
    assert uni_exchange.balanceOf(t.a1) == 0
    assert uni_exchange.balanceOf(t.a2) == 0
    assert uni_token.balanceOf(t.a1) == 6*10**18
    assert uni_token.balanceOf(t.a2) == 4*10**18
    assert chain.head_state.get_balance(uni_exchange.address) == 0
    assert uni_token.balanceOf(uni_exchange.address) == 0
    # Can initialize again after all shares are divested
    uni_exchange.initialize(2*10**18, value=1*10**18)
