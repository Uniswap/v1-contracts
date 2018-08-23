def test_add_liquidity(t, chain, utils, omg_token, exchange_factory, omg_exchange, assert_tx_failed):
    deadline = chain.head_state.timestamp + 300
    assert exchange_factory.getExchange(omg_token.address) == omg_exchange.address
    assert utils.remove_0x_head(omg_exchange.tokenAddress()) == omg_token.address.hex()
    assert utils.remove_0x_head(omg_exchange.factoryAddress()) == exchange_factory.address.hex()
    omg_token.approve(omg_exchange.address, 100*10**18)
    # Can't add liquidity without tokens
    assert_tx_failed(lambda: omg_exchange.addLiquidity(10*10**18, deadline, value=5*10**18, sender=t.k1))
    chain.mine()
    # msg.value can't be 0
    assert_tx_failed(lambda: omg_exchange.addLiquidity(10*10**18, deadline))
    chain.mine()
    # Token value can't be 0
    assert_tx_failed(lambda: omg_exchange.addLiquidity(0, deadline, value=5*10**18))
    chain.mine()
    # Throw exception if not enough gas is provided
    assert_tx_failed(lambda: omg_exchange.addLiquidity(10*10**18, deadline, value=5*10**18, startgas=25000))
    # Liquidity provider (t.a0) adds liquidity
    omg_exchange.addLiquidity(10*10**18, deadline, value=5*10**18)
    assert chain.head_state.get_balance(omg_exchange.address) == 5*10**18
    assert omg_token.balanceOf(omg_exchange.address) == 10*10**18
    assert omg_exchange.totalSupply() == 5*10**18
    assert omg_exchange.balanceOf(t.a0) == 5*10**18

def test_liquidity_pool(t, chain, utils, omg_token, exchange_factory, omg_exchange, assert_tx_failed):
    deadline = chain.head_state.timestamp + 300
    omg_token.transfer(t.a1, 10*10**18)
    omg_token.approve(omg_exchange.address, 100*10**18)
    omg_token.approve(omg_exchange.address, 10*10**18, sender=t.k1)
    # First liquidity provider (t.a0) adds liquidity
    omg_exchange.addLiquidity(2*10**18, deadline, value=1*10**18)
    assert omg_exchange.totalSupply() == 1*10**18
    assert omg_exchange.balanceOf(t.a0) == 1*10**18
    assert omg_exchange.balanceOf(t.a1) == 0
    assert omg_exchange.balanceOf(t.a2) == 0
    assert omg_token.balanceOf(t.a1) == 10*10**18
    assert omg_token.balanceOf(t.a2) == 0
    assert chain.head_state.get_balance(omg_exchange.address) == 1*10**18
    assert omg_token.balanceOf(omg_exchange.address) == 2*10**18
    # Second liquidity provider (t.a1) adds liquidity
    omg_exchange.addLiquidity(1, deadline, value=5*10**18, sender=t.k1)
    assert omg_exchange.totalSupply() == 6*10**18
    assert omg_exchange.balanceOf(t.a0) == 1*10**18
    assert omg_exchange.balanceOf(t.a1) == 5*10**18
    assert omg_exchange.balanceOf(t.a2) == 0
    assert omg_token.balanceOf(t.a1) == 0
    assert chain.head_state.get_balance(omg_exchange.address) == 6*10**18
    assert omg_token.balanceOf(omg_exchange.address) == 12*10**18
    # Can't divest more liquidity than owned
    assert_tx_failed(lambda: omg_exchange.removeLiquidity((5*10**18 + 1), 1, 1, deadline, sender=t.k2))
    # Mine block
    chain.mine()
    # Second liquidity provider (t.a1) transfers liquidity to third liquidity provider (t.a2)
    omg_exchange.transfer(t.a2, 2*10**18, sender=t.k1)
    assert omg_exchange.balanceOf(t.a0) == 1*10**18
    assert omg_exchange.balanceOf(t.a1) == 3*10**18
    assert omg_exchange.balanceOf(t.a2) == 2*10**18
    assert omg_token.balanceOf(t.a1) == 0
    assert chain.head_state.get_balance(omg_exchange.address) == 6*10**18
    assert omg_token.balanceOf(omg_exchange.address) == 12*10**18
    # Mine block
    chain.mine()
    # First, second and third liquidity providers remove their remaining liquidity
    omg_exchange.removeLiquidity(1*10**18, 1, 1, deadline)
    omg_exchange.removeLiquidity(3*10**18, 1, 1, deadline, sender=t.k1)
    omg_exchange.removeLiquidity(2*10**18, 1, 1, deadline, sender=t.k2)
    assert omg_exchange.totalSupply() == 0
    assert omg_exchange.balanceOf(t.a0) == 0
    assert omg_exchange.balanceOf(t.a1) == 0
    assert omg_exchange.balanceOf(t.a2) == 0
    assert omg_token.balanceOf(t.a1) == 6*10**18
    assert omg_token.balanceOf(t.a2) == 4*10**18
    assert chain.head_state.get_balance(omg_exchange.address) == 0
    assert omg_token.balanceOf(omg_exchange.address) == 0
    # Can add liquidity again after all liquidity is divested
    omg_exchange.addLiquidity(2*10**18, deadline, value=1*10**18)
