def test_add_liquidity(w3, omg_token, exchange_factory, omg_exchange, assert_tx_failed):
    a0, a1, a2 = w3.eth.accounts[:3]
    deadline = w3.eth.getBlock(w3.eth.blockNumber).timestamp + 300
    assert exchange_factory.getExchange(omg_token.address) == omg_exchange.address
    assert omg_exchange.tokenAddress() == omg_token.address
    assert omg_exchange.factoryAddress() == exchange_factory.address
    omg_token.approve(omg_exchange.address, 100*10**18, transact={})
    # # Can't add liquidity without tokens
    # assert_tx_failed(lambda: omg_exchange.addLiquidity(10*10**18, deadline, value=5*10**18, sender=t.k1))
    # # msg.value can't be 0
    # assert_tx_failed(lambda: omg_exchange.addLiquidity(10*10**18, deadline))
    # # Token value can't be 0
    # assert_tx_failed(lambda: omg_exchange.addLiquidity(0, deadline, value=5*10**18))
    # # Throw exception if not enough gas is provided
    # assert_tx_failed(lambda: omg_exchange.addLiquidity(10*10**18, deadline, value=5*10**18, startgas=25000))
    # Liquidity provider (t.a0) adds liquidity
    omg_exchange.addLiquidity(10*10**18, deadline, transact={'value': 5*10**18})
    assert w3.eth.getBalance(omg_exchange.address) == 5*10**18
    assert omg_token.balanceOf(omg_exchange.address) == 10*10**18
    assert omg_exchange.totalSupply() == 5*10**18
    assert omg_exchange.balanceOf(a0) == 5*10**18

def test_liquidity_pool(w3, omg_token, exchange_factory, omg_exchange, assert_tx_failed):
    a0, a1, a2 = w3.eth.accounts[:3]
    deadline = w3.eth.getBlock(w3.eth.blockNumber).timestamp + 300
    omg_token.transfer(a1, 10*10**18 + 1, transact={})
    omg_token.approve(omg_exchange.address, 100*10**18, transact={})
    omg_token.approve(omg_exchange.address, 10*10**18 + 1, transact={'from': a1})
    # First liquidity provider (t.a0) adds liquidity
    omg_exchange.addLiquidity(2*10**18, deadline, transact={'value': 1*10**18})
    assert omg_exchange.totalSupply() == 1*10**18
    assert omg_exchange.balanceOf(a0) == 1*10**18
    assert omg_exchange.balanceOf(a1) == 0
    assert omg_exchange.balanceOf(a2) == 0
    assert omg_token.balanceOf(a1) == 10*10**18 + 1
    assert omg_token.balanceOf(a2) == 0
    assert w3.eth.getBalance(omg_exchange.address) == 1*10**18
    assert omg_token.balanceOf(omg_exchange.address) == 2*10**18
    # Second liquidity provider (a1) adds liquidity
    omg_exchange.addLiquidity(1, deadline, transact={'value': 5*10**18, 'from': a1})
    assert omg_exchange.totalSupply() == 6*10**18
    assert omg_exchange.balanceOf(a0) == 1*10**18
    assert omg_exchange.balanceOf(a1) == 5*10**18
    assert omg_exchange.balanceOf(a2) == 0
    assert omg_token.balanceOf(a1) == 0
    assert w3.eth.getBalance(omg_exchange.address) == 6*10**18
    assert omg_token.balanceOf(omg_exchange.address) == 12*10**18 + 1
    # # Can't divest more liquidity than owned
    # assert_tx_failed(lambda: omg_exchange.removeLiquidity((5*10**18 + 1), 1, 1, deadline, transact={'from': a2})
    # Second liquidity provider (a1) transfers liquidity to third liquidity provider (a2)
    omg_exchange.transfer(a2, 2*10**18, transact={'from': a1})
    assert omg_exchange.balanceOf(a0) == 1*10**18
    assert omg_exchange.balanceOf(a1) == 3*10**18
    assert omg_exchange.balanceOf(a2) == 2*10**18
    assert omg_token.balanceOf(a1) == 0
    assert w3.eth.getBalance(omg_exchange.address) == 6*10**18
    assert omg_token.balanceOf(omg_exchange.address) == 12*10**18 + 1
    # First, second and third liquidity providers remove their remaining liquidity
    omg_exchange.removeLiquidity(1*10**18, 1, 1, deadline, transact={})
    omg_exchange.removeLiquidity(3*10**18, 1, 1, deadline, transact={'from': a1})
    omg_exchange.removeLiquidity(2*10**18, 1, 1, deadline, transact={'from': a2})
    assert omg_exchange.totalSupply() == 0
    assert omg_exchange.balanceOf(a0) == 0
    assert omg_exchange.balanceOf(a1) == 0
    assert omg_exchange.balanceOf(a2) == 0
    assert omg_token.balanceOf(a1) == 6*10**18
    assert omg_token.balanceOf(a2) == 4*10**18 + 1
    assert w3.eth.getBalance(omg_exchange.address) == 0
    assert omg_token.balanceOf(omg_exchange.address) == 0
    # Can add liquidity again after all liquidity is divested
    omg_exchange.addLiquidity(2*10**18, deadline, transact={'value': 1*10**18})
