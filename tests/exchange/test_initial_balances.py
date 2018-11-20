from tests.constants import (
    ETH_RESERVE,
    HAY_RESERVE,
    DEN_RESERVE,
    INITIAL_ETH,
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
