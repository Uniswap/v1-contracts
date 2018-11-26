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
    ZERO_ADDR,
)

def test_swap_input(w3, HAY_token, DEN_token, HAY_exchange, DEN_exchange, swap_input, assert_fail):
    a0, a1, a2 = w3.eth.accounts[:3]
    ETH_PURCHASED = swap_input(HAY_SOLD, HAY_RESERVE, ETH_RESERVE)
    DEN_PURCHASED = swap_input(ETH_PURCHASED, ETH_RESERVE, DEN_RESERVE)
    # Transfer HAY to BUYER
    HAY_token.transfer(a1, HAY_SOLD, transact={})
    HAY_token.approve(HAY_exchange.address, HAY_SOLD, transact={'from': a1})
    assert HAY_token.balanceOf(a1) == HAY_SOLD
    # tokens sold == 0
    assert_fail(lambda: HAY_exchange.tokenToTokenSwapInput(0, MIN_DEN_BOUGHT, MIN_ETH_BOUGHT, DEADLINE, DEN_token.address, transact={'from': a1}))
    # min tokens bought == 0
    assert_fail(lambda: HAY_exchange.tokenToTokenSwapInput(HAY_SOLD, 0, MIN_ETH_BOUGHT, DEADLINE, DEN_token.address, transact={'from': a1}))
    # min tokens bought > tokens bought
    assert_fail(lambda: HAY_exchange.tokenToTokenSwapInput(HAY_SOLD, DEN_PURCHASED + 1, MIN_ETH_BOUGHT, DEADLINE, DEN_token.address, transact={'from': a1}))
    # min eth bought == 0
    assert_fail(lambda: HAY_exchange.tokenToTokenSwapInput(HAY_SOLD, MIN_DEN_BOUGHT, 0, DEADLINE, DEN_token.address, transact={'from': a1}))
    # min eth bought > eth bought
    assert_fail(lambda: HAY_exchange.tokenToTokenSwapInput(HAY_SOLD, MIN_DEN_BOUGHT, ETH_PURCHASED + 1, DEADLINE, DEN_token.address, transact={'from': a1}))
    # deadline < block.timestamp
    assert_fail(lambda: HAY_exchange.tokenToTokenSwapInput(HAY_SOLD, MIN_DEN_BOUGHT, MIN_ETH_BOUGHT, 1, DEN_token.address, transact={'from': a1}))
    # output token == input token
    assert_fail(lambda: HAY_exchange.tokenToTokenSwapInput(HAY_SOLD, MIN_DEN_BOUGHT, MIN_ETH_BOUGHT, DEADLINE, HAY_token.address, transact={'from': a1}))
    # output token == input exchange
    assert_fail(lambda: HAY_exchange.tokenToTokenSwapInput(HAY_SOLD, MIN_DEN_BOUGHT, MIN_ETH_BOUGHT, DEADLINE, HAY_exchange.address, transact={'from': a1}))
    # output token == ZERO_ADDR
    assert_fail(lambda: HAY_exchange.tokenToTokenSwapInput(HAY_SOLD, MIN_DEN_BOUGHT, MIN_ETH_BOUGHT, DEADLINE, ZERO_ADDR, transact={'from': a1}))
    # BUYER converts ETH to UNI
    HAY_exchange.tokenToTokenSwapInput(HAY_SOLD, MIN_DEN_BOUGHT, MIN_ETH_BOUGHT, DEADLINE, DEN_token.address, transact={'from': a1})
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

def test_transfer_input(w3, HAY_token, DEN_token, HAY_exchange, DEN_exchange, swap_input, assert_fail):
    a0, a1, a2 = w3.eth.accounts[:3]
    ETH_PURCHASED = swap_input(HAY_SOLD, HAY_RESERVE, ETH_RESERVE)
    DEN_PURCHASED = swap_input(ETH_PURCHASED, ETH_RESERVE, DEN_RESERVE)
    # Transfer HAY to BUYER
    HAY_token.transfer(a1, HAY_SOLD, transact={})
    HAY_token.approve(HAY_exchange.address, HAY_SOLD, transact={'from': a1})
    assert HAY_token.balanceOf(a1) == HAY_SOLD
    # recipient == ZERO_ADDR
    assert_fail(lambda: HAY_exchange.tokenToTokenTransferInput(HAY_SOLD, MIN_DEN_BOUGHT, MIN_ETH_BOUGHT, DEADLINE, ZERO_ADDR, DEN_token.address, transact={'from': a1}))
    # recipient == output exchange
    assert_fail(lambda: HAY_exchange.tokenToTokenTransferInput(HAY_SOLD, MIN_DEN_BOUGHT, MIN_ETH_BOUGHT, DEADLINE, DEN_exchange.address, DEN_token.address, transact={'from': a1}))
    # BUYER converts ETH to UNI
    HAY_exchange.tokenToTokenTransferInput(HAY_SOLD, MIN_DEN_BOUGHT, MIN_ETH_BOUGHT, DEADLINE, a2, DEN_token.address, transact={'from': a1})
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

def test_swap_output(w3, HAY_token, DEN_token, HAY_exchange, DEN_exchange, swap_output, assert_fail):
    a0, a1, a2 = w3.eth.accounts[:3]
    ETH_COST = swap_output(DEN_BOUGHT, ETH_RESERVE, DEN_RESERVE)
    HAY_COST = swap_output(ETH_COST, HAY_RESERVE, ETH_RESERVE)
    # Transfer HAY to BUYER
    HAY_token.transfer(a1, MAX_HAY_SOLD, transact={})
    HAY_token.approve(HAY_exchange.address, MAX_HAY_SOLD, transact={'from': a1})
    assert HAY_token.balanceOf(a1) == MAX_HAY_SOLD
    # tokens bought == 0
    assert_fail(lambda: HAY_exchange.tokenToTokenSwapOutput(0, MAX_HAY_SOLD, MAX_ETH_SOLD, DEADLINE, DEN_token.address, transact={'from': a1}))
    # max tokens < token cost
    assert_fail(lambda: HAY_exchange.tokenToTokenSwapOutput(DEN_BOUGHT, HAY_COST - 1, MAX_ETH_SOLD, DEADLINE, DEN_token.address, transact={'from': a1}))
    # max eth < token cost
    assert_fail(lambda: HAY_exchange.tokenToTokenSwapOutput(DEN_BOUGHT, MAX_HAY_SOLD, ETH_COST - 1, DEADLINE, DEN_token.address, transact={'from': a1}))
    # deadline < block.timestamp
    assert_fail(lambda: HAY_exchange.tokenToTokenSwapOutput(DEN_BOUGHT, MAX_HAY_SOLD, MAX_ETH_SOLD, 1, DEN_token.address, transact={'from': a1}))
    # output token == input token
    assert_fail(lambda: HAY_exchange.tokenToTokenSwapOutput(DEN_BOUGHT, MAX_HAY_SOLD, MAX_ETH_SOLD, DEADLINE, HAY_token.address, transact={'from': a1}))
    # output token == input exchange
    assert_fail(lambda: HAY_exchange.tokenToTokenSwapOutput(DEN_BOUGHT, MAX_HAY_SOLD, MAX_ETH_SOLD, DEADLINE, HAY_exchange.address, transact={'from': a1}))
    # output token == ZERO_ADDR
    assert_fail(lambda: HAY_exchange.tokenToTokenSwapOutput(DEN_BOUGHT, MAX_HAY_SOLD, MAX_ETH_SOLD, DEADLINE, ZERO_ADDR, transact={'from': a1}))
    # BUYER converts ETH to UNI
    HAY_exchange.tokenToTokenSwapOutput(DEN_BOUGHT, MAX_HAY_SOLD, MAX_ETH_SOLD, DEADLINE, DEN_token.address, transact={'from': a1})
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

def test_transfer_output(w3, HAY_token, DEN_token, HAY_exchange, DEN_exchange, swap_output, assert_fail):
    a0, a1, a2 = w3.eth.accounts[:3]
    ETH_COST = swap_output(DEN_BOUGHT, ETH_RESERVE, DEN_RESERVE)
    HAY_COST = swap_output(ETH_COST, HAY_RESERVE, ETH_RESERVE)
    # Transfer HAY to BUYER
    HAY_token.transfer(a1, MAX_HAY_SOLD, transact={})
    HAY_token.approve(HAY_exchange.address, MAX_HAY_SOLD, transact={'from': a1})
    assert HAY_token.balanceOf(a1) == MAX_HAY_SOLD
    # recipient == ZERO_ADDR
    assert_fail(lambda: HAY_exchange.tokenToTokenTransferOutput(DEN_BOUGHT, MAX_HAY_SOLD, MAX_ETH_SOLD, DEADLINE, ZERO_ADDR, DEN_token.address, transact={'from': a1}))
    # recipient == output exchange
    assert_fail(lambda: HAY_exchange.tokenToTokenTransferOutput(DEN_BOUGHT, MAX_HAY_SOLD, MAX_ETH_SOLD, DEADLINE, DEN_exchange.address, DEN_token.address, transact={'from': a1}))
    # BUYER converts ETH to UNI
    HAY_exchange.tokenToTokenTransferOutput(DEN_BOUGHT, MAX_HAY_SOLD, MAX_ETH_SOLD, DEADLINE, a2, DEN_token.address, transact={'from': a1})
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
