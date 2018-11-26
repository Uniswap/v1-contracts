from tests.constants import (
    ETH_RESERVE,
    HAY_RESERVE,
    HAY_SOLD,
    MIN_ETH_BOUGHT,
    ETH_BOUGHT,
    MAX_HAY_SOLD,
    INITIAL_ETH,
    DEADLINE,
    ZERO_ADDR,
)

def test_swap_input(w3, HAY_token, HAY_exchange, swap_input, assert_fail):
    a0, a1, a2 = w3.eth.accounts[:3]
    ETH_PURCHASED = swap_input(HAY_SOLD, HAY_RESERVE, ETH_RESERVE)
    # Transfer HAY to BUYER
    HAY_token.transfer(a1, HAY_SOLD, transact={})
    HAY_token.approve(HAY_exchange.address, HAY_SOLD, transact={'from': a1})
    assert HAY_token.balanceOf(a1) == HAY_SOLD
    # tokens sold == 0
    assert_fail(lambda: HAY_exchange.tokenToEthSwapInput(0, MIN_ETH_BOUGHT, DEADLINE, transact={'from': a1}))
    # min eth == 0
    assert_fail(lambda: HAY_exchange.tokenToEthSwapInput(HAY_SOLD, 0, DEADLINE, transact={'from': a1}))
    # min eth > eth purchased
    assert_fail(lambda: HAY_exchange.tokenToEthSwapInput(HAY_SOLD, ETH_PURCHASED + 1, DEADLINE, transact={'from': a1}))
    # deadline < block.timestamp
    assert_fail(lambda: HAY_exchange.tokenToEthSwapInput(HAY_SOLD, MIN_ETH_BOUGHT, 1, transact={'from': a1}))
    # BUYER converts ETH to UNI
    HAY_exchange.tokenToEthSwapInput(HAY_SOLD, MIN_ETH_BOUGHT, DEADLINE, transact={'from': a1})
    # Updated balances of UNI exchange
    assert w3.eth.getBalance(HAY_exchange.address) == ETH_RESERVE - ETH_PURCHASED
    assert HAY_token.balanceOf(HAY_exchange.address) == HAY_RESERVE + HAY_SOLD
    # Updated balances of BUYER
    assert HAY_token.balanceOf(a1) == 0
    assert w3.eth.getBalance(a1) == INITIAL_ETH + ETH_PURCHASED

def test_transfer_input(w3, HAY_token, HAY_exchange, swap_input, assert_fail):
    a0, a1, a2 = w3.eth.accounts[:3]
    ETH_PURCHASED = swap_input(HAY_SOLD, HAY_RESERVE, ETH_RESERVE)
    # Transfer HAY to BUYER
    HAY_token.transfer(a1, HAY_SOLD, transact={})
    HAY_token.approve(HAY_exchange.address, HAY_SOLD, transact={'from': a1})
    assert HAY_token.balanceOf(a1) == HAY_SOLD
    # recipient == ZERO_ADDR
    assert_fail(lambda: HAY_exchange.tokenToEthTransferInput(HAY_SOLD, 1, DEADLINE, ZERO_ADDR, transact={'from': a1}))
    # recipient == exchange
    assert_fail(lambda: HAY_exchange.tokenToEthTransferInput(HAY_SOLD, 1, DEADLINE, HAY_exchange.address, transact={'from': a1}))
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

def test_swap_output(w3, HAY_token, HAY_exchange, swap_output, assert_fail):
    a0, a1, a2 = w3.eth.accounts[:3]
    HAY_COST = swap_output(ETH_BOUGHT, HAY_RESERVE, ETH_RESERVE)
    # Transfer HAY to BUYER
    HAY_token.transfer(a1, MAX_HAY_SOLD, transact={})
    HAY_token.approve(HAY_exchange.address, MAX_HAY_SOLD, transact={'from': a1})
    assert HAY_token.balanceOf(a1) == MAX_HAY_SOLD
    # tokens bought == 0
    assert_fail(lambda: HAY_exchange.tokenToEthSwapOutput(0, MAX_HAY_SOLD, DEADLINE, transact={'from': a1}))
    # max tokens < token cost
    assert_fail(lambda: HAY_exchange.tokenToEthSwapOutput(ETH_BOUGHT, HAY_COST - 1, DEADLINE, transact={'from': a1}))
    # deadline < block.timestamp
    assert_fail(lambda: HAY_exchange.tokenToEthSwapOutput(ETH_BOUGHT, MAX_HAY_SOLD, 1, transact={'from': a1}))
    # BUYER converts ETH to UNI
    HAY_exchange.tokenToEthSwapOutput(ETH_BOUGHT, MAX_HAY_SOLD, DEADLINE, transact={'from': a1})
    # Updated balances of UNI exchange
    assert w3.eth.getBalance(HAY_exchange.address) == ETH_RESERVE - ETH_BOUGHT
    assert HAY_token.balanceOf(HAY_exchange.address) == HAY_RESERVE + HAY_COST
    # Updated balances of BUYER
    assert HAY_token.balanceOf(a1) == MAX_HAY_SOLD - HAY_COST
    assert w3.eth.getBalance(a1) == INITIAL_ETH + ETH_BOUGHT

def test_transfer_output(w3, HAY_token, HAY_exchange, swap_output, assert_fail):
    a0, a1, a2 = w3.eth.accounts[:3]
    HAY_COST = swap_output(ETH_BOUGHT, HAY_RESERVE, ETH_RESERVE)
    # Transfer HAY to BUYER
    HAY_token.transfer(a1, MAX_HAY_SOLD, transact={})
    HAY_token.approve(HAY_exchange.address, MAX_HAY_SOLD, transact={'from': a1})
    assert HAY_token.balanceOf(a1) == MAX_HAY_SOLD
    # recipient == ZERO_ADDR
    assert_fail(lambda: HAY_exchange.tokenToEthTransferOutput(ETH_BOUGHT, MAX_HAY_SOLD, DEADLINE, ZERO_ADDR, transact={'from': a1}))
    # recipient == exchange
    assert_fail(lambda: HAY_exchange.tokenToEthTransferOutput(ETH_BOUGHT, MAX_HAY_SOLD, DEADLINE, HAY_exchange.address, transact={'from': a1}))
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
