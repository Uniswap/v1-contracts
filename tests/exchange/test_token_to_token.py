def test_swap_input(w3, omg_token, dai_token, omg_exchange, dai_exchange, assert_tx_failed):
    a0, a1, a2 = w3.eth.accounts[:3]
    deadline = w3.eth.getBlock(w3.eth.blockNumber).timestamp + 300
    omg_token.transfer(a1, 3*10**18, transact={})
    omg_token.approve(omg_exchange.address, 10*10**18, transact={})
    omg_token.approve(omg_exchange.address, 3*10**18, transact={'from': a1})
    omg_exchange.addLiquidity(0, 10*10**18, deadline, transact={'value': 5*10**18})
    dai_token.approve(dai_exchange.address, 20*10**18, transact={})
    dai_exchange.addLiquidity(0, 20*10**18, deadline, transact={'value': 5*10**18})
    # Starting balances of UNI exchange
    assert w3.eth.getBalance(omg_exchange.address) == 5*10**18
    assert omg_token.balanceOf(omg_exchange.address) == 10*10**18
    # Starting balances of SWAP exchange
    assert w3.eth.getBalance(dai_exchange.address) == 5*10**18
    assert dai_token.balanceOf(dai_exchange.address) == 20*10**18
    # Starting balances of BUYER
    assert omg_token.balanceOf(a1) == 3*10**18
    assert dai_token.balanceOf(a1) == 0
    assert w3.eth.getBalance(a1) == 1*10**24
    # BUYER converts ETH to UNI
    # omg_exchange.tokenToTokenSwap(2*10**18, 1, 1, deadline, dai_token.address, transact={'gas': 118574, 'from': a1})
    omg_exchange.tokenToTokenSwapInput(2*10**18, 1, 1, deadline, dai_token.address, transact={'from': a1})
    # Updated balances of UNI exchange
    assert w3.eth.getBalance(omg_exchange.address) == 4168751042187760547
    assert omg_token.balanceOf(omg_exchange.address) == 12*10**18
    # Updated balances of SWAP exchange
    assert w3.eth.getBalance(dai_exchange.address) == 5831248957812239453
    assert dai_token.balanceOf(dai_exchange.address) == 17156321784165919398
    # Updated balances of BUYER
    assert omg_token.balanceOf(a1) == 1*10**18
    assert dai_token.balanceOf(a1) == 2843678215834080602
    assert w3.eth.getBalance(a1) == 1*10**24

def test_transfer_input(w3, omg_token, dai_token, omg_exchange, dai_exchange, assert_tx_failed):
    a0, a1, a2 = w3.eth.accounts[:3]
    deadline = w3.eth.getBlock(w3.eth.blockNumber).timestamp + 300
    omg_token.transfer(a1, 3*10**18, transact={})
    omg_token.approve(omg_exchange.address, 10*10**18, transact={})
    omg_token.approve(omg_exchange.address, 3*10**18, transact={'from': a1})
    omg_exchange.addLiquidity(0, 10*10**18, deadline, transact={'value': 5*10**18})
    dai_token.approve(dai_exchange.address, 20*10**18, transact={})
    dai_exchange.addLiquidity(0, 20*10**18, deadline, transact={'value': 5*10**18})
    # Starting balances of UNI exchange
    assert w3.eth.getBalance(omg_exchange.address) == 5*10**18
    assert omg_token.balanceOf(omg_exchange.address) == 10*10**18
    # Starting balances of SWAP exchange
    assert w3.eth.getBalance(dai_exchange.address) == 5*10**18
    assert dai_token.balanceOf(dai_exchange.address) == 20*10**18
    # Starting balances of BUYER
    assert omg_token.balanceOf(a1) == 3*10**18
    assert dai_token.balanceOf(a1) == 0
    assert w3.eth.getBalance(a1) == 1*10**24
    # Starting balances of RECIPIENT
    assert omg_token.balanceOf(a2) == 0
    assert dai_token.balanceOf(a2) == 0
    assert w3.eth.getBalance(a2) == 1*10**24
    # BUYER converts ETH to UNI
    omg_exchange.tokenToTokenTransferInput(2*10**18, 1, 1, deadline, a2, dai_token.address, transact={'from': a1})
    # Updated balances of UNI exchange
    assert w3.eth.getBalance(omg_exchange.address) == 4168751042187760547
    assert omg_token.balanceOf(omg_exchange.address) == 12*10**18
    # Updated balances of SWAP exchange
    assert w3.eth.getBalance(dai_exchange.address) == 5831248957812239453
    assert dai_token.balanceOf(dai_exchange.address) == 17156321784165919398
    # Updated balances of BUYER
    assert omg_token.balanceOf(a1) == 1*10**18
    assert dai_token.balanceOf(a1) == 0
    assert w3.eth.getBalance(a1) == 1*10**24
    # Updated balances of RECIPIENT
    assert omg_token.balanceOf(a2) == 0
    assert dai_token.balanceOf(a2) == 2843678215834080602
    assert w3.eth.getBalance(a2) == 1*10**24

def test_swap_output(w3, omg_token, dai_token, omg_exchange, dai_exchange, assert_tx_failed):
    a0, a1, a2 = w3.eth.accounts[:3]
    deadline = w3.eth.getBlock(w3.eth.blockNumber).timestamp + 300
    omg_token.transfer(a1, 3*10**18, transact={})
    omg_token.approve(omg_exchange.address, 10*10**18, transact={})
    omg_token.approve(omg_exchange.address, 3*10**18, transact={'from': a1})
    omg_exchange.addLiquidity(0, 10*10**18, deadline, transact={'value': 5*10**18})
    dai_token.approve(dai_exchange.address, 20*10**18, transact={})
    dai_exchange.addLiquidity(0, 20*10**18, deadline, transact={'value': 5*10**18})
    # Starting balances of UNI exchange
    assert w3.eth.getBalance(omg_exchange.address) == 5*10**18
    assert omg_token.balanceOf(omg_exchange.address) == 10*10**18
    # Starting balances of SWAP exchange
    assert w3.eth.getBalance(dai_exchange.address) == 5*10**18
    assert dai_token.balanceOf(dai_exchange.address) == 20*10**18
    # Starting balances of BUYER
    assert omg_token.balanceOf(a1) == 3*10**18
    assert dai_token.balanceOf(a1) == 0
    assert w3.eth.getBalance(a1) == 1*10**24
    # BUYER converts ETH to UNI
    omg_exchange.tokenToTokenSwapOutput(2843678215834080602, 3*10**18, 2*10**18, deadline, dai_token.address, transact={'from': a1})
    # Updated balances of UNI exchange
    assert w3.eth.getBalance(omg_exchange.address) == 4168751042187760547
    assert omg_token.balanceOf(omg_exchange.address) == 12*10**18
    # Updated balances of SWAP exchange
    assert w3.eth.getBalance(dai_exchange.address) == 5831248957812239453
    assert dai_token.balanceOf(dai_exchange.address) == 17156321784165919398
    # Updated balances of BUYER
    assert omg_token.balanceOf(a1) == 1*10**18
    assert dai_token.balanceOf(a1) == 2843678215834080602
    assert w3.eth.getBalance(a1) == 1*10**24

def test_transfer_output(w3, omg_token, dai_token, omg_exchange, dai_exchange, assert_tx_failed):
    a0, a1, a2 = w3.eth.accounts[:3]
    deadline = w3.eth.getBlock(w3.eth.blockNumber).timestamp + 300
    omg_token.transfer(a1, 3*10**18, transact={})
    omg_token.approve(omg_exchange.address, 10*10**18, transact={})
    omg_token.approve(omg_exchange.address, 3*10**18, transact={'from': a1})
    omg_exchange.addLiquidity(0, 10*10**18, deadline, transact={'value': 5*10**18})
    dai_token.approve(dai_exchange.address, 20*10**18, transact={})
    dai_exchange.addLiquidity(0, 20*10**18, deadline, transact={'value': 5*10**18})
    # Starting balances of UNI exchange
    assert w3.eth.getBalance(omg_exchange.address) == 5*10**18
    assert omg_token.balanceOf(omg_exchange.address) == 10*10**18
    # Starting balances of SWAP exchange
    assert w3.eth.getBalance(dai_exchange.address) == 5*10**18
    assert dai_token.balanceOf(dai_exchange.address) == 20*10**18
    # Starting balances of BUYER
    assert omg_token.balanceOf(a1) == 3*10**18
    assert dai_token.balanceOf(a1) == 0
    assert w3.eth.getBalance(a1) == 1*10**24
    # Starting balances of RECIPIENT
    assert omg_token.balanceOf(a2) == 0
    assert dai_token.balanceOf(a2) == 0
    assert w3.eth.getBalance(a2) == 1*10**24
    # BUYER converts ETH to UNI
    # omg_exchange.tokenToTokenTransferOutput(2843678215834080602, 3*10**18, 1, deadline, a2, dai_token.address, transact={'gas': 131749,'from': a1})
    omg_exchange.tokenToTokenTransferOutput(2843678215834080602, 3*10**18, 2*10**18, deadline, a2, dai_token.address, transact={'from': a1})
    # Updated balances of UNI exchange
    assert w3.eth.getBalance(omg_exchange.address) == 4168751042187760547
    assert omg_token.balanceOf(omg_exchange.address) == 12*10**18
    # Updated balances of SWAP exchange
    assert w3.eth.getBalance(dai_exchange.address) == 5831248957812239453
    assert dai_token.balanceOf(dai_exchange.address) == 17156321784165919398
    # Updated balances of BUYER
    assert omg_token.balanceOf(a1) == 1*10**18
    assert dai_token.balanceOf(a1) == 0
    assert w3.eth.getBalance(a1) == 1*10**24
    # Updated balances of RECIPIENT
    assert omg_token.balanceOf(a2) ==  0
    assert dai_token.balanceOf(a2) == 2843678215834080602
    assert w3.eth.getBalance(a2) == 1*10**24
