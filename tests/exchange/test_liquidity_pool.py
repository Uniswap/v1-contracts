from tests.constants import (
    ETH_RESERVE,
    HAY_RESERVE,
    DEN_RESERVE,
    INITIAL_ETH,
    DEADLINE,
)

def test_initial_balances(w3, HAY_token, HAY_exchange, DEN_token, DEN_exchange):
    a0, a1, a2 = w3.eth.accounts[:3]
    # BUYER
    assert HAY_token.balanceOf(a1) == 0
    assert DEN_token.balanceOf(a1) == 0
    assert w3.eth.getBalance(a1) == INITIAL_ETH
    # RECIPIENT
    assert HAY_token.balanceOf(a2) == 0
    assert DEN_token.balanceOf(a2) == 0
    assert w3.eth.getBalance(a2) == INITIAL_ETH
    # HAY exchange
    assert w3.eth.getBalance(HAY_exchange.address) == ETH_RESERVE
    assert HAY_token.balanceOf(HAY_exchange.address) == HAY_RESERVE
    assert DEN_token.balanceOf(HAY_exchange.address) == 0
    # DEN exchange
    assert w3.eth.getBalance(DEN_exchange.address) == ETH_RESERVE
    assert HAY_token.balanceOf(DEN_exchange.address) == 0
    assert DEN_token.balanceOf(DEN_exchange.address) == DEN_RESERVE

def test_liquidity_pool(w3, HAY_token, factory, HAY_exchange, assert_fail):
    a0, a1, a2 = w3.eth.accounts[:3]
    HAY_token.transfer(a1, 15*10**18, transact={})
    HAY_token.approve(HAY_exchange.address, 15*10**18, transact={'from': a1})
    assert HAY_token.balanceOf(a1) == 15*10**18
    # First liquidity provider (t.a0) adds liquidity (in conftest.py)
    assert HAY_exchange.totalSupply() == ETH_RESERVE
    assert HAY_exchange.balanceOf(a0) == ETH_RESERVE
    assert w3.eth.getBalance(HAY_exchange.address) == ETH_RESERVE
    assert HAY_token.balanceOf(HAY_exchange.address) == HAY_RESERVE
    ETH_ADDED = 25*10**17
    HAY_ADDED = 5*10**18
    # min_liquidity == 0 (while totalSupply > 0)
    assert_fail(lambda: HAY_exchange.addLiquidity(0, 15*10**18, DEADLINE, transact={'value': ETH_ADDED, 'from': a1}))
    # max_tokens < tokens needed
    assert_fail(lambda: HAY_exchange.addLiquidity(1, HAY_ADDED - 1, DEADLINE, transact={'value': ETH_ADDED, 'from': a1}))
    # deadline < block.timestamp
    assert_fail(lambda: HAY_exchange.addLiquidity(1, 15*10**18, 1, transact={'value': ETH_ADDED, 'from': a1}))
    # Second liquidity provider (a1) adds liquidity
    HAY_exchange.addLiquidity(1, 15*10**18, DEADLINE, transact={'value': ETH_ADDED, 'from': a1})
    assert HAY_exchange.totalSupply() == ETH_RESERVE + ETH_ADDED
    assert HAY_exchange.balanceOf(a0) == ETH_RESERVE
    assert HAY_exchange.balanceOf(a1) == ETH_ADDED
    assert w3.eth.getBalance(HAY_exchange.address) == ETH_RESERVE + ETH_ADDED
    assert HAY_token.balanceOf(HAY_exchange.address) == HAY_RESERVE + HAY_ADDED + 1
    # Can't transfer more liquidity than owned
    assert_fail(lambda: HAY_exchange.transfer(a2, ETH_ADDED + 1, transact={'from': a1}))
    # Second liquidity provider (a1) transfers liquidity to third liquidity provider (a2)
    HAY_exchange.transfer(a2, 1*10**18, transact={'from': a1})
    assert HAY_exchange.balanceOf(a0) == ETH_RESERVE
    assert HAY_exchange.balanceOf(a1) == ETH_ADDED - 1*10**18
    assert HAY_exchange.balanceOf(a2) == 1*10**18
    assert w3.eth.getBalance(HAY_exchange.address) == ETH_RESERVE + ETH_ADDED
    assert HAY_token.balanceOf(HAY_exchange.address) == HAY_RESERVE + HAY_ADDED + 1
    # amount == 0
    assert_fail(lambda: HAY_exchange.removeLiquidity(0, 1, 1, DEADLINE, transact={'from': a2}))
    # amount > owned (liquidity)
    assert_fail(lambda: HAY_exchange.removeLiquidity(1*10**18 + 1, 1, 1, DEADLINE, transact={'from': a2}))
    # min eth > eth divested
    assert_fail(lambda: HAY_exchange.removeLiquidity(1*10**18, 1*10**18 + 1, 1, DEADLINE, transact={'from': a2}))
    # min tokens > tokens divested
    assert_fail(lambda: HAY_exchange.removeLiquidity(1*10**18, 1, 2*10**18 + 1, DEADLINE, transact={'from': a2}))
    # deadline < block.timestamp
    assert_fail(lambda: HAY_exchange.removeLiquidity(1*10**18, 1, 1, 1, transact={'from': a2}))
    # First, second and third liquidity providers remove their remaining liquidity
    HAY_exchange.removeLiquidity(ETH_RESERVE, 1, 1, DEADLINE, transact={})
    HAY_exchange.removeLiquidity(ETH_ADDED - 1*10**18, 1, 1, DEADLINE, transact={'from': a1})
    HAY_exchange.removeLiquidity(1*10**18, 1, 1, DEADLINE, transact={'from': a2})
    assert HAY_exchange.totalSupply() == 0
    assert HAY_exchange.balanceOf(a0) == 0
    assert HAY_exchange.balanceOf(a1) == 0
    assert HAY_exchange.balanceOf(a2) == 0
    assert HAY_token.balanceOf(a1) == 13*10**18 - 1
    assert HAY_token.balanceOf(a2) == 2*10**18 + 1
    assert w3.eth.getBalance(HAY_exchange.address) == 0
    assert HAY_token.balanceOf(HAY_exchange.address) == 0
    # Can add liquidity again after all liquidity is divested
    HAY_token.approve(HAY_exchange.address, 100*10**18, transact={})
    HAY_exchange.addLiquidity(0, HAY_RESERVE, DEADLINE, transact={'value': ETH_RESERVE})
