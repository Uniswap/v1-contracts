def test_swap_default(w3, HAY_token, HAY_exchange):
    a0, a1, a2 = w3.eth.accounts[:3]
    deadline = w3.eth.getBlock(w3.eth.blockNumber).timestamp + 300
    HAY_token.approve(HAY_exchange.address, 10*10**18, transact={})
    HAY_exchange.addLiquidity(0, 10*10**18, deadline, transact={'value': 5*10**18})
    # # Starting balances of UNI exchange
    assert w3.eth.getBalance(HAY_exchange.address) == 5*10**18
    assert HAY_token.balanceOf(HAY_exchange.address) == 10*10**18
    # Starting balances of BUYER
    assert HAY_token.balanceOf(a1) == 0
    assert w3.eth.getBalance(a1) == 1*10**24
    # BUYER converts ETH to UNI
    # w3.eth.sendTransaction({'to': HAY_exchange.address, 'gas': 67122, 'value': 1*10**18, 'from': a1})
    w3.eth.sendTransaction({'to': HAY_exchange.address, 'value': 1*10**18, 'from': a1})
    # Updated balances of UNI exchange
    assert w3.eth.getBalance(HAY_exchange.address) == 6*10**18
    assert HAY_token.balanceOf(HAY_exchange.address) == 8337502084375521094
    # Updated balances of BUYER
    assert HAY_token.balanceOf(a1) == 1662497915624478906
    assert w3.eth.getBalance(a1) == 1*10**24 - 1*10**18

def test_swap_input(w3, HAY_token, HAY_exchange):
    a0, a1, a2 = w3.eth.accounts[:3]
    deadline = w3.eth.getBlock(w3.eth.blockNumber).timestamp + 300
    HAY_token.approve(HAY_exchange.address, 10*10**18, transact={})
    HAY_exchange.addLiquidity(0, 10*10**18, deadline, transact={'value': 5*10**18})
    # Starting balances of UNI exchange
    assert w3.eth.getBalance(HAY_exchange.address) == 5*10**18
    assert HAY_token.balanceOf(HAY_exchange.address) == 10*10**18
    # Starting balances of BUYER
    assert HAY_token.balanceOf(a1) == 0
    assert w3.eth.getBalance(a1) == 1*10**24
    # BUYER converts ETH to UNI
    # HAY_exchange.ethToTokenSwap(1, deadline, transact={'gas': 66929, 'value': 1*10**18, 'from': a1})
    HAY_exchange.ethToTokenSwapInput(1, deadline, transact={'value': 1*10**18, 'from': a1})
    # Updated balances of UNI exchange
    assert w3.eth.getBalance(HAY_exchange.address) == 6*10**18
    assert HAY_token.balanceOf(HAY_exchange.address) == 8337502084375521094
#     # Updated balances of BUYER
    assert HAY_token.balanceOf(a1) == 1662497915624478906
    assert w3.eth.getBalance(a1) == 1*10**24 - 1*10**18
#
def test_transfer_input(w3, HAY_token, HAY_exchange):
    a0, a1, a2 = w3.eth.accounts[:3]
    deadline = w3.eth.getBlock(w3.eth.blockNumber).timestamp + 300
    HAY_token.approve(HAY_exchange.address, 10*10**18, transact={})
    HAY_exchange.addLiquidity(0, 10*10**18, deadline, transact={'value': 5*10**18})
    # Starting balances of UNI exchange
    assert w3.eth.getBalance(HAY_exchange.address) == 5*10**18
    assert HAY_token.balanceOf(HAY_exchange.address) == 10*10**18
    # Starting balances of BUYER
    assert HAY_token.balanceOf(a1) == 0
    assert w3.eth.getBalance(a1) == 1*10**24
    # Starting balances of RECIPIENT
    assert HAY_token.balanceOf(a2) == 0
    assert w3.eth.getBalance(a2) == 1*10**24
    # BUYER converts ETH to UNI
    # HAY_exchange.ethToTokenTransfer(1, deadline, a2, transact={'gas': 68397, 'value': 1*10**18, 'from': a1})
    HAY_exchange.ethToTokenTransferInput(1, deadline, a2, transact={'value': 1*10**18, 'from': a1})
    # Updated balances of UNI exchange
    assert w3.eth.getBalance(HAY_exchange.address) == 6*10**18
    assert HAY_token.balanceOf(HAY_exchange.address) == 8337502084375521094
    # Updated balances of BUYER
    assert HAY_token.balanceOf(a1) == 0
    assert w3.eth.getBalance(a1) == 1*10**24 - 1*10**18
    # Updated balances of RECIPIENT
    assert HAY_token.balanceOf(a2) == 1662497915624478906
    assert w3.eth.getBalance(a2) == 1*10**24

def test_swap_output(w3, HAY_token, HAY_exchange):
    a0, a1, a2 = w3.eth.accounts[:3]
    deadline = w3.eth.getBlock(w3.eth.blockNumber).timestamp + 300
    HAY_token.approve(HAY_exchange.address, 10*10**18, transact={})
    HAY_exchange.addLiquidity(0, 10*10**18, deadline, transact={'value': 5*10**18})
    # Starting balances of UNI exchange
    assert w3.eth.getBalance(HAY_exchange.address) == 5*10**18
    assert HAY_token.balanceOf(HAY_exchange.address) == 10*10**18
    # Starting balances of BUYER
    assert HAY_token.balanceOf(a1) == 0
    assert w3.eth.getBalance(a1) == 1*10**24
    # BUYER converts ETH to UNI
    HAY_exchange.ethToTokenSwapOutput(1662497915624478906, deadline, transact={'gas': 76394, 'value': 2*10**18, 'from': a1})
    # Updated balances of UNI exchange
    assert w3.eth.getBalance(HAY_exchange.address) == 6*10**18
    assert HAY_token.balanceOf(HAY_exchange.address) == 8337502084375521094
    # Updated balances of BUYER
    assert HAY_token.balanceOf(a1) == 1662497915624478906
    assert w3.eth.getBalance(a1) == 1*10**24 - 1*10**18

def test_transfer_output(w3, HAY_token, HAY_exchange):
    a0, a1, a2 = w3.eth.accounts[:3]
    deadline = w3.eth.getBlock(w3.eth.blockNumber).timestamp + 300
    HAY_token.approve(HAY_exchange.address, 10*10**18, transact={})
    HAY_exchange.addLiquidity(0, 10*10**18, deadline, transact={'value': 5*10**18})
    # Starting balances of UNI exchange
    assert w3.eth.getBalance(HAY_exchange.address) == 5*10**18
    assert HAY_token.balanceOf(HAY_exchange.address) == 10*10**18
    # Starting balances of BUYER
    assert HAY_token.balanceOf(a1) == 0
    assert w3.eth.getBalance(a1) == 1*10**24
    # Starting balances of RECIPIENT
    assert HAY_token.balanceOf(a2) == 0
    assert w3.eth.getBalance(a2) == 1*10**24
    # BUYER converts ETH to UNI
    HAY_exchange.ethToTokenTransferOutput(1662497915624478906, deadline, a2, transact={'gas': 77862, 'value': 2*10**18, 'from': a1})
    # Updated balances of UNI exchange
    assert w3.eth.getBalance(HAY_exchange.address) == 6*10**18
    assert HAY_token.balanceOf(HAY_exchange.address) == 8337502084375521094
    # Updated balances of BUYER
    assert HAY_token.balanceOf(a1) == 0
    assert w3.eth.getBalance(a1) == 1*10**24 - 1*10**18
    # Updated balances of RECIPIENT
    assert HAY_token.balanceOf(a2) == 1662497915624478906
    assert w3.eth.getBalance(a2) == 1*10**24
