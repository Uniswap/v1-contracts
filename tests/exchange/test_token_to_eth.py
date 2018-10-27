def test_swap_input(w3, HAY_token, HAY_exchange):
    a0, a1, a2 = w3.eth.accounts[:3]
    deadline = w3.eth.getBlock(w3.eth.blockNumber).timestamp + 300
    HAY_token.transfer(a1, 2*10**18, transact={})
    HAY_token.approve(HAY_exchange.address, 10*10**18, transact={})
    HAY_token.approve(HAY_exchange.address, 2*10**18, transact={'from': a1})
    HAY_exchange.addLiquidity(0, 10*10**18, deadline, transact={'value': 5*10**18})
    # Starting balances of UNI exchange
    assert w3.eth.getBalance(HAY_exchange.address) == 5*10**18
    assert HAY_token.balanceOf(HAY_exchange.address) == 10*10**18
    # Starting balances of BUYER
    assert HAY_token.balanceOf(a1) == 2*10**18
    assert w3.eth.getBalance(a1) == 1*10**24
    # BUYER converts ETH to UNI
    HAY_exchange.tokenToEthSwapInput(2*10**18, 1, deadline, transact={'from': a1})
    # Updated balances of UNI exchange
    assert w3.eth.getBalance(HAY_exchange.address) == 4168751042187760547
    assert HAY_token.balanceOf(HAY_exchange.address) == 12*10**18
    # Updated balances of BUYER
    assert HAY_token.balanceOf(a1) == 0
    assert w3.eth.getBalance(a1) == 1*10**24 + 831248957812239453

def test_transfer_input(w3, HAY_token, HAY_exchange):
    a0, a1, a2 = w3.eth.accounts[:3]
    deadline = w3.eth.getBlock(w3.eth.blockNumber).timestamp + 300
    HAY_token.transfer(a1, 2*10**18, transact={})
    HAY_token.approve(HAY_exchange.address, 10*10**18, transact={})
    HAY_token.approve(HAY_exchange.address, 2*10**18, transact={'from': a1})
    HAY_exchange.addLiquidity(0, 10*10**18, deadline, transact={'value': 5*10**18})
    # Starting balances of UNI exchange
    assert w3.eth.getBalance(HAY_exchange.address) == 5*10**18
    assert HAY_token.balanceOf(HAY_exchange.address) == 10*10**18
    # Starting balances of BUYER
    assert HAY_token.balanceOf(a1) == 2*10**18
    assert w3.eth.getBalance(a1) == 1*10**24
    # Starting balances of RECIPIENT
    assert HAY_token.balanceOf(a2) == 0
    assert w3.eth.getBalance(a2) == 1*10**24
    # BUYER converts ETH to UNI
    HAY_exchange.tokenToEthTransferInput(2*10**18, 1, deadline, a2, transact={'from': a1})
    # Updated balances of UNI exchange
    assert w3.eth.getBalance(HAY_exchange.address) == 4168751042187760547
    assert HAY_token.balanceOf(HAY_exchange.address) == 12*10**18
    # Updated balances of BUYER
    assert HAY_token.balanceOf(a1) == 0
    assert w3.eth.getBalance(a1) == 1*10**24
    # Updated balances of RECIPIENT
    assert HAY_token.balanceOf(a2) == 0
    assert w3.eth.getBalance(a2) == 1*10**24 + 831248957812239453

def test_swap_output(w3, HAY_token, HAY_exchange):
    a0, a1, a2 = w3.eth.accounts[:3]
    deadline = w3.eth.getBlock(w3.eth.blockNumber).timestamp + 300
    HAY_token.transfer(a1, 3*10**18, transact={})
    HAY_token.approve(HAY_exchange.address, 10*10**18, transact={})
    HAY_token.approve(HAY_exchange.address, 3*10**18, transact={'from': a1})
    HAY_exchange.addLiquidity(0, 10*10**18, deadline, transact={'value': 5*10**18})
    # Starting balances of UNI exchange
    assert w3.eth.getBalance(HAY_exchange.address) == 5*10**18
    assert HAY_token.balanceOf(HAY_exchange.address) == 10*10**18
    # Starting balances of BUYER
    assert HAY_token.balanceOf(a1) == 3*10**18
    assert w3.eth.getBalance(a1) == 1*10**24
    # BUYER converts ETH to UNI
    HAY_exchange.tokenToEthSwapOutput(831248957812239453, 3*10**18, deadline, transact={'from': a1})
    # Updated balances of UNI exchange
    assert w3.eth.getBalance(HAY_exchange.address) == 4168751042187760547
    assert HAY_token.balanceOf(HAY_exchange.address) == 12*10**18
    # Updated balances of BUYER
    assert HAY_token.balanceOf(a1) == 1*10**18
    assert w3.eth.getBalance(a1) == 1*10**24 + 831248957812239453

def test_transfer_output(w3, HAY_token, HAY_exchange):
    a0, a1, a2 = w3.eth.accounts[:3]
    deadline = w3.eth.getBlock(w3.eth.blockNumber).timestamp + 300
    HAY_token.transfer(a1, 3*10**18, transact={})
    HAY_token.approve(HAY_exchange.address, 10*10**18, transact={})
    HAY_token.approve(HAY_exchange.address, 3*10**18, transact={'from': a1})
    HAY_exchange.addLiquidity(0, 10*10**18, deadline, transact={'value': 5*10**18})
    # Starting balances of UNI exchange
    assert w3.eth.getBalance(HAY_exchange.address) == 5*10**18
    assert HAY_token.balanceOf(HAY_exchange.address) == 10*10**18
    # Starting balances of BUYER
    assert HAY_token.balanceOf(a1) == 3*10**18
    assert w3.eth.getBalance(a1) == 1*10**24
    # Starting balances of RECIPIENT
    assert HAY_token.balanceOf(a2) == 0
    assert w3.eth.getBalance(a2) == 1*10**24
    # BUYER converts ETH to UNI
    HAY_exchange.tokenToEthTransferOutput(831248957812239453, 3*10**18, deadline, a2, transact={'from': a1})
    # Updated balances of UNI exchange
    assert w3.eth.getBalance(HAY_exchange.address) == 4168751042187760547
    assert HAY_token.balanceOf(HAY_exchange.address) == 12*10**18
    # Updated balances of BUYER
    assert HAY_token.balanceOf(a1) == 1*10**18
    assert w3.eth.getBalance(a1) == 1*10**24
    # Updated balances of RECIPIENT
    assert HAY_token.balanceOf(a2) == 0
    assert w3.eth.getBalance(a2) == 1*10**24 + 831248957812239453
