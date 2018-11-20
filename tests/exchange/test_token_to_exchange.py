from tests.constants import (
    ETH_RESERVE,
    HAY_RESERVE,
    DEN_RESERVE,
    HAY_SOLD,
    MIN_ETH_BOUGHT,
    MIN_DEN_BOUGHT,
    DEN_BOUGHT,
    MAX_HAY_SOLD,
    MAX_ETH_SOLD,
    INITIAL_ETH,
    DEADLINE,
)

def test_swap_input(w3, HAY_token, DEN_token, HAY_exchange, DEN_exchange, swap_input):
    a0, a1, a2 = w3.eth.accounts[:3]
    ETH_PURCHASED = swap_input(HAY_SOLD, HAY_RESERVE, ETH_RESERVE)
    DEN_PURCHASED = swap_input(ETH_PURCHASED, ETH_RESERVE, DEN_RESERVE)
    # Transfer HAY to BUYER
    HAY_token.transfer(a1, HAY_SOLD, transact={})
    HAY_token.approve(HAY_exchange.address, HAY_SOLD, transact={'from': a1})
    assert HAY_token.balanceOf(a1) == HAY_SOLD
    # BUYER converts ETH to UNI
    HAY_exchange.tokenToExchangeSwapInput(HAY_SOLD, MIN_DEN_BOUGHT, MIN_ETH_BOUGHT, DEADLINE, DEN_exchange.address, transact={'from': a1})
    # Updated balances of UNI exchange
    assert w3.eth.getBalance(HAY_exchange.address) == ETH_RESERVE - ETH_PURCHASED
    assert HAY_token.balanceOf(HAY_exchange.address) == HAY_RESERVE + HAY_SOLD
    # Updated balances of SWAP exchange
    assert w3.eth.getBalance(DEN_exchange.address) == ETH_RESERVE + ETH_PURCHASED
    assert DEN_token.balanceOf(DEN_exchange.address) == DEN_RESERVE - DEN_PURCHASED
    # Updated balances of BUYER
    assert HAY_token.balanceOf(a1) == 0
    assert DEN_token.balanceOf(a1) == DEN_PURCHASED
    assert w3.eth.getBalance(a1) == INITIAL_ETH

def test_transfer_input(w3, HAY_token, DEN_token, HAY_exchange, DEN_exchange, swap_input):
    a0, a1, a2 = w3.eth.accounts[:3]
    ETH_PURCHASED = swap_input(HAY_SOLD, HAY_RESERVE, ETH_RESERVE)
    DEN_PURCHASED = swap_input(ETH_PURCHASED, ETH_RESERVE, DEN_RESERVE)
    # Transfer HAY to BUYER
    HAY_token.transfer(a1, HAY_SOLD, transact={})
    HAY_token.approve(HAY_exchange.address, HAY_SOLD, transact={'from': a1})
    assert HAY_token.balanceOf(a1) == HAY_SOLD
    # BUYER converts ETH to UNI
    HAY_exchange.tokenToExchangeTransferInput(HAY_SOLD, MIN_DEN_BOUGHT, MIN_ETH_BOUGHT, DEADLINE, a2, DEN_exchange.address, transact={'from': a1})
    # Updated balances of UNI exchange
    assert w3.eth.getBalance(HAY_exchange.address) == ETH_RESERVE - ETH_PURCHASED
    assert HAY_token.balanceOf(HAY_exchange.address) == HAY_RESERVE + HAY_SOLD
    # Updated balances of SWAP exchange
    assert w3.eth.getBalance(DEN_exchange.address) == ETH_RESERVE + ETH_PURCHASED
    assert DEN_token.balanceOf(DEN_exchange.address) == DEN_RESERVE - DEN_PURCHASED
    # Updated balances of BUYER
    assert HAY_token.balanceOf(a1) == 0
    assert DEN_token.balanceOf(a1) == 0
    assert w3.eth.getBalance(a1) == INITIAL_ETH
    # Updated balances of RECIPIENT
    assert HAY_token.balanceOf(a2) == 0
    assert DEN_token.balanceOf(a2) == DEN_PURCHASED
    assert w3.eth.getBalance(a2) == INITIAL_ETH

def test_swap_output(w3, HAY_token, DEN_token, HAY_exchange, DEN_exchange, swap_output):
    a0, a1, a2 = w3.eth.accounts[:3]
    ETH_COST = swap_output(DEN_BOUGHT, ETH_RESERVE, DEN_RESERVE)
    HAY_COST = swap_output(ETH_COST, HAY_RESERVE, ETH_RESERVE)
    # Transfer HAY to BUYER
    HAY_token.transfer(a1, MAX_HAY_SOLD, transact={})
    HAY_token.approve(HAY_exchange.address, MAX_HAY_SOLD, transact={'from': a1})
    assert HAY_token.balanceOf(a1) == MAX_HAY_SOLD
    # BUYER converts ETH to UNI
    HAY_exchange.tokenToExchangeSwapOutput(DEN_BOUGHT, MAX_HAY_SOLD, MAX_ETH_SOLD, DEADLINE, DEN_exchange.address, transact={'from': a1})
    # Updated balances of UNI exchange
    assert w3.eth.getBalance(HAY_exchange.address) == ETH_RESERVE - ETH_COST
    assert HAY_token.balanceOf(HAY_exchange.address) == HAY_RESERVE + HAY_COST
    # Updated balances of SWAP exchange
    assert w3.eth.getBalance(DEN_exchange.address) == ETH_RESERVE + ETH_COST
    assert DEN_token.balanceOf(DEN_exchange.address) == DEN_RESERVE - DEN_BOUGHT
    # Updated balances of BUYER
    assert HAY_token.balanceOf(a1) == MAX_HAY_SOLD - HAY_COST
    assert DEN_token.balanceOf(a1) == DEN_BOUGHT
    assert w3.eth.getBalance(a1) == INITIAL_ETH

def test_transfer_output(w3, HAY_token, DEN_token, HAY_exchange, DEN_exchange, swap_output):
    a0, a1, a2 = w3.eth.accounts[:3]
    ETH_COST = swap_output(DEN_BOUGHT, ETH_RESERVE, DEN_RESERVE)
    HAY_COST = swap_output(ETH_COST, HAY_RESERVE, ETH_RESERVE)
    # Transfer HAY to BUYER
    HAY_token.transfer(a1, MAX_HAY_SOLD, transact={})
    HAY_token.approve(HAY_exchange.address, MAX_HAY_SOLD, transact={'from': a1})
    assert HAY_token.balanceOf(a1) == MAX_HAY_SOLD
    # BUYER converts ETH to UNI
    HAY_exchange.tokenToExchangeTransferOutput(DEN_BOUGHT, MAX_HAY_SOLD, MAX_ETH_SOLD, DEADLINE, a2, DEN_exchange.address, transact={'from': a1})
    # Updated balances of UNI exchange
    assert w3.eth.getBalance(HAY_exchange.address) == ETH_RESERVE - ETH_COST
    assert HAY_token.balanceOf(HAY_exchange.address) == HAY_RESERVE + HAY_COST
    # Updated balances of SWAP exchange
    assert w3.eth.getBalance(DEN_exchange.address) == ETH_RESERVE + ETH_COST
    assert DEN_token.balanceOf(DEN_exchange.address) == DEN_RESERVE - DEN_BOUGHT
    # Updated balances of BUYER
    assert HAY_token.balanceOf(a1) == MAX_HAY_SOLD - HAY_COST
    assert DEN_token.balanceOf(a1) == 0
    assert w3.eth.getBalance(a1) == INITIAL_ETH
    # Updated balances of RECIPIENT
    assert HAY_token.balanceOf(a2) ==  0
    assert DEN_token.balanceOf(a2) == DEN_BOUGHT
    assert w3.eth.getBalance(a2) == INITIAL_ETH
