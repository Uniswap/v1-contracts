from tests.constants import (
    ETH_RESERVE,
    HAY_RESERVE,
    HAY_SOLD,
    MIN_ETH_BOUGHT,
    ETH_BOUGHT,
    MAX_HAY_SOLD,
    INITIAL_ETH,
    DEADLINE,
)

def test_swap_input(w3, HAY_token, HAY_exchange, swap_input):
    a0, a1, a2 = w3.eth.accounts[:3]
    ETH_PURCHASED = swap_input(HAY_SOLD, HAY_RESERVE, ETH_RESERVE)
    # Transfer HAY to BUYER
    HAY_token.transfer(a1, HAY_SOLD, transact={})
    HAY_token.approve(HAY_exchange.address, HAY_SOLD, transact={'from': a1})
    assert HAY_token.balanceOf(a1) == HAY_SOLD
    # BUYER converts ETH to UNI
    HAY_exchange.tokenToEthSwapInput(HAY_SOLD, MIN_ETH_BOUGHT, DEADLINE, transact={'from': a1})
    # Updated balances of UNI exchange
    assert w3.eth.getBalance(HAY_exchange.address) == ETH_RESERVE - ETH_PURCHASED
    assert HAY_token.balanceOf(HAY_exchange.address) == HAY_RESERVE + HAY_SOLD
    # Updated balances of BUYER
    assert HAY_token.balanceOf(a1) == 0
    assert w3.eth.getBalance(a1) == INITIAL_ETH + ETH_PURCHASED

def test_transfer_input(w3, HAY_token, HAY_exchange, swap_input):
    a0, a1, a2 = w3.eth.accounts[:3]
    ETH_PURCHASED = swap_input(HAY_SOLD, HAY_RESERVE, ETH_RESERVE)
    # Transfer HAY to BUYER
    HAY_token.transfer(a1, HAY_SOLD, transact={})
    HAY_token.approve(HAY_exchange.address, HAY_SOLD, transact={'from': a1})
    assert HAY_token.balanceOf(a1) == HAY_SOLD
    # BUYER converts ETH to UNI
    HAY_exchange.tokenToEthTransferInput(HAY_SOLD, 1, DEADLINE, a2, transact={'from': a1})
    # Updated balances of UNI exchange
    assert w3.eth.getBalance(HAY_exchange.address) == ETH_RESERVE - ETH_PURCHASED
    assert HAY_token.balanceOf(HAY_exchange.address) == HAY_RESERVE + HAY_SOLD
    # Updated balances of BUYER
    assert HAY_token.balanceOf(a1) == 0
    assert w3.eth.getBalance(a1) == INITIAL_ETH
    # Updated balances of RECIPIENT
    assert HAY_token.balanceOf(a2) == 0
    assert w3.eth.getBalance(a2) == INITIAL_ETH + ETH_PURCHASED

def test_swap_output(w3, HAY_token, HAY_exchange, swap_output):
    a0, a1, a2 = w3.eth.accounts[:3]
    HAY_COST = swap_output(ETH_BOUGHT, HAY_RESERVE, ETH_RESERVE)
    # Transfer HAY to BUYER
    HAY_token.transfer(a1, MAX_HAY_SOLD, transact={})
    HAY_token.approve(HAY_exchange.address, MAX_HAY_SOLD, transact={'from': a1})
    assert HAY_token.balanceOf(a1) == MAX_HAY_SOLD
    # BUYER converts ETH to UNI
    HAY_exchange.tokenToEthSwapOutput(ETH_BOUGHT, MAX_HAY_SOLD, DEADLINE, transact={'from': a1})
    # Updated balances of UNI exchange
    assert w3.eth.getBalance(HAY_exchange.address) == ETH_RESERVE - ETH_BOUGHT
    assert HAY_token.balanceOf(HAY_exchange.address) == HAY_RESERVE + HAY_COST
    # Updated balances of BUYER
    assert HAY_token.balanceOf(a1) == MAX_HAY_SOLD - HAY_COST
    assert w3.eth.getBalance(a1) == INITIAL_ETH + ETH_BOUGHT

def test_transfer_output(w3, HAY_token, HAY_exchange, swap_output):
    a0, a1, a2 = w3.eth.accounts[:3]
    HAY_COST = swap_output(ETH_BOUGHT, HAY_RESERVE, ETH_RESERVE)
    # Transfer HAY to BUYER
    HAY_token.transfer(a1, MAX_HAY_SOLD, transact={})
    HAY_token.approve(HAY_exchange.address, MAX_HAY_SOLD, transact={'from': a1})
    assert HAY_token.balanceOf(a1) == MAX_HAY_SOLD
    # BUYER converts ETH to UNI
    HAY_exchange.tokenToEthTransferOutput(ETH_BOUGHT, MAX_HAY_SOLD, DEADLINE, a2, transact={'from': a1})
    # Updated balances of UNI exchange
    assert w3.eth.getBalance(HAY_exchange.address) == ETH_RESERVE - ETH_BOUGHT
    assert HAY_token.balanceOf(HAY_exchange.address) == HAY_RESERVE + HAY_COST
    # Updated balances of BUYER
    assert HAY_token.balanceOf(a1) == MAX_HAY_SOLD - HAY_COST
    assert w3.eth.getBalance(a1) == INITIAL_ETH
    # Updated balances of RECIPIENT
    assert HAY_token.balanceOf(a2) == 0
    assert w3.eth.getBalance(a2) == INITIAL_ETH + ETH_BOUGHT
