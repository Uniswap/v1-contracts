from tests.constants import (
    ETH_RESERVE,
    HAY_RESERVE,
    ETH_SOLD,
    MIN_HAY_BOUGHT,
    HAY_BOUGHT,
    MAX_ETH_SOLD,
    INITIAL_ETH,
    DEADLINE,
)

def test_swap_default(w3, HAY_token, HAY_exchange, swap_input):
    a0, a1, a2 = w3.eth.accounts[:3]
    HAY_PURCHASED = swap_input(ETH_SOLD, ETH_RESERVE, HAY_RESERVE)
    # BUYER converts ETH to UNI
    w3.eth.sendTransaction({'to': HAY_exchange.address, 'value': ETH_SOLD, 'from': a1})
    # Updated balances of UNI exchange
    assert w3.eth.getBalance(HAY_exchange.address) == ETH_RESERVE + ETH_SOLD
    assert HAY_token.balanceOf(HAY_exchange.address) == HAY_RESERVE - HAY_PURCHASED
    # Updated balances of BUYER
    assert HAY_token.balanceOf(a1) == HAY_PURCHASED
    assert w3.eth.getBalance(a1) == INITIAL_ETH - ETH_SOLD

def test_swap_input(w3, HAY_token, HAY_exchange, swap_input):
    a0, a1, a2 = w3.eth.accounts[:3]
    HAY_PURCHASED = swap_input(ETH_SOLD, ETH_RESERVE, HAY_RESERVE)
    # BUYER converts ETH to UNI
    HAY_exchange.ethToTokenSwapInput(MIN_HAY_BOUGHT, DEADLINE, transact={'value': ETH_SOLD, 'from': a1})
    # Updated balances of UNI exchange
    assert w3.eth.getBalance(HAY_exchange.address) == ETH_RESERVE + ETH_SOLD
    assert HAY_token.balanceOf(HAY_exchange.address) == HAY_RESERVE - HAY_PURCHASED
    # Updated balances of BUYER
    assert HAY_token.balanceOf(a1) == HAY_PURCHASED
    assert w3.eth.getBalance(a1) == INITIAL_ETH - ETH_SOLD

def test_transfer_input(w3, HAY_token, HAY_exchange, swap_input):
    a0, a1, a2 = w3.eth.accounts[:3]
    HAY_PURCHASED = swap_input(ETH_SOLD, ETH_RESERVE, HAY_RESERVE)
    # BUYER converts ETH to UNI
    HAY_exchange.ethToTokenTransferInput(MIN_HAY_BOUGHT, DEADLINE, a2, transact={'value': ETH_SOLD, 'from': a1})
    # Updated balances of UNI exchange
    assert w3.eth.getBalance(HAY_exchange.address) == ETH_RESERVE + ETH_SOLD
    assert HAY_token.balanceOf(HAY_exchange.address) == HAY_RESERVE - HAY_PURCHASED
    # Updated balances of BUYER
    assert HAY_token.balanceOf(a1) == 0
    assert w3.eth.getBalance(a1) == INITIAL_ETH - ETH_SOLD
    # Updated balances of RECIPIENT
    assert HAY_token.balanceOf(a2) == HAY_PURCHASED
    assert w3.eth.getBalance(a2) == INITIAL_ETH

def test_swap_output(w3, HAY_token, HAY_exchange, swap_output):
    a0, a1, a2 = w3.eth.accounts[:3]
    ETH_COST = swap_output(HAY_BOUGHT, ETH_RESERVE, HAY_RESERVE)
    # BUYER converts ETH to UNI
    HAY_exchange.ethToTokenSwapOutput(HAY_BOUGHT, DEADLINE, transact={'value': MAX_ETH_SOLD, 'from': a1})
    # Updated balances of UNI exchange
    assert w3.eth.getBalance(HAY_exchange.address) == ETH_RESERVE + ETH_COST
    assert HAY_token.balanceOf(HAY_exchange.address) == HAY_RESERVE - HAY_BOUGHT
    # Updated balances of BUYER
    assert HAY_token.balanceOf(a1) == HAY_BOUGHT
    assert w3.eth.getBalance(a1) == INITIAL_ETH - ETH_COST

def test_transfer_output(w3, HAY_token, HAY_exchange, swap_output):
    a0, a1, a2 = w3.eth.accounts[:3]
    ETH_COST = swap_output(HAY_BOUGHT, ETH_RESERVE, HAY_RESERVE)
    # BUYER converts ETH to UNI
    HAY_exchange.ethToTokenTransferOutput(HAY_BOUGHT, DEADLINE, a2, transact={'value': MAX_ETH_SOLD, 'from': a1})
    # Updated balances of UNI exchange
    assert w3.eth.getBalance(HAY_exchange.address) == ETH_RESERVE + ETH_COST
    assert HAY_token.balanceOf(HAY_exchange.address) == HAY_RESERVE - HAY_BOUGHT
    # Updated balances of BUYER
    assert HAY_token.balanceOf(a1) == 0
    assert w3.eth.getBalance(a1) == INITIAL_ETH - ETH_COST
    # Updated balances of RECIPIENT
    assert HAY_token.balanceOf(a2) == HAY_BOUGHT
    assert w3.eth.getBalance(a2) == INITIAL_ETH
