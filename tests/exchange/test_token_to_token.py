def test_swap(t, chain, omg_token, dai_token, omg_exchange, dai_exchange, assert_tx_failed):
    deadline = chain.head_state.timestamp + 300
    omg_token.transfer(t.a1, 3*10**18)
    omg_token.approve(omg_exchange.address, 10*10**18)
    omg_token.approve(omg_exchange.address, 3*10**18, sender=t.k1)
    omg_exchange.addLiquidity(10*10**18, deadline, value=5*10**18)
    dai_token.approve(dai_exchange.address, 20*10**18)
    dai_exchange.addLiquidity(20*10**18, deadline, value=5*10**18)
    # Starting balances of UNI exchange
    assert chain.head_state.get_balance(omg_exchange.address) == 5*10**18
    assert omg_token.balanceOf(omg_exchange.address) == 10*10**18
    # Starting balances of SWAP exchange
    assert chain.head_state.get_balance(dai_exchange.address) == 5*10**18
    assert dai_token.balanceOf(dai_exchange.address) == 20*10**18
    # Starting balances of BUYER
    assert omg_token.balanceOf(t.a1) == 3*10**18
    assert dai_token.balanceOf(t.a1) == 0
    assert chain.head_state.get_balance(t.a1) == 1*10**24
    # BUYER converts ETH to UNI
    omg_exchange.tokenToTokenSwap(2*10**18, 1, deadline, dai_token.address, startgas=118048, sender=t.k1)
    # omg_exchange.tokenToTokenSwap(dai_token.address, 2*10**18, 1, deadline, startgas=108048, sender=t.k1)
    # Updated balances of UNI exchange
    assert chain.head_state.get_balance(omg_exchange.address) == 4168751042187760548
    assert omg_token.balanceOf(omg_exchange.address) == 12*10**18
    # Updated balances of SWAP exchange
    assert chain.head_state.get_balance(dai_exchange.address) == 5831248957812239452
    assert dai_token.balanceOf(dai_exchange.address) == 17156321784165919403
    # Updated balances of BUYER
    assert omg_token.balanceOf(t.a1) == 1*10**18
    assert dai_token.balanceOf(t.a1) == 2843678215834080597
    assert chain.head_state.get_balance(t.a1) == 1*10**24

def test_transfer(t, chain, omg_token, dai_token, omg_exchange, dai_exchange, assert_tx_failed):
    deadline = chain.head_state.timestamp + 300
    omg_token.transfer(t.a1, 3*10**18)
    omg_token.approve(omg_exchange.address, 10*10**18)
    omg_token.approve(omg_exchange.address, 3*10**18, sender=t.k1)
    omg_exchange.addLiquidity(10*10**18, deadline, value=5*10**18)
    dai_token.approve(dai_exchange.address, 20*10**18)
    dai_exchange.addLiquidity(20*10**18, deadline, value=5*10**18)
    # Starting balances of UNI exchange
    assert chain.head_state.get_balance(omg_exchange.address) == 5*10**18
    assert omg_token.balanceOf(omg_exchange.address) == 10*10**18
    # Starting balances of SWAP exchange
    assert chain.head_state.get_balance(dai_exchange.address) == 5*10**18
    assert dai_token.balanceOf(dai_exchange.address) == 20*10**18
    # Starting balances of BUYER
    assert omg_token.balanceOf(t.a1) == 3*10**18
    assert dai_token.balanceOf(t.a1) == 0
    assert chain.head_state.get_balance(t.a1) == 1*10**24
    # Starting balances of RECIPIENT
    assert omg_token.balanceOf(t.a2) == 0
    assert dai_token.balanceOf(t.a2) == 0
    assert chain.head_state.get_balance(t.a2) == 1*10**24
    # BUYER converts ETH to UNI
    omg_exchange.tokenToTokenTransfer(2*10**18, 1, deadline, t.a2, dai_token.address, startgas=119550, sender=t.k1)
    # Updated balances of UNI exchange
    assert chain.head_state.get_balance(omg_exchange.address) == 4168751042187760548
    assert omg_token.balanceOf(omg_exchange.address) == 12*10**18
    # Updated balances of SWAP exchange
    assert chain.head_state.get_balance(dai_exchange.address) == 5831248957812239452
    assert dai_token.balanceOf(dai_exchange.address) == 17156321784165919403
    # Updated balances of BUYER
    assert omg_token.balanceOf(t.a1) == 1*10**18
    assert dai_token.balanceOf(t.a1) == 0
    assert chain.head_state.get_balance(t.a1) == 1*10**24
    # Updated balances of RECIPIENT
    assert omg_token.balanceOf(t.a2) == 0
    assert dai_token.balanceOf(t.a2) == 2843678215834080597
    assert chain.head_state.get_balance(t.a2) == 1*10**24

def test_swap_exact(t, chain, omg_token, dai_token, omg_exchange, dai_exchange, assert_tx_failed):
    deadline = chain.head_state.timestamp + 300
    omg_token.transfer(t.a1, 3*10**18)
    omg_token.approve(omg_exchange.address, 10*10**18)
    omg_token.approve(omg_exchange.address, 3*10**18, sender=t.k1)
    omg_exchange.addLiquidity(10*10**18, deadline, value=5*10**18)
    dai_token.approve(dai_exchange.address, 20*10**18)
    dai_exchange.addLiquidity(20*10**18, deadline, value=5*10**18)
    # Starting balances of UNI exchange
    assert chain.head_state.get_balance(omg_exchange.address) == 5*10**18
    assert omg_token.balanceOf(omg_exchange.address) == 10*10**18
    # Starting balances of SWAP exchange
    assert chain.head_state.get_balance(dai_exchange.address) == 5*10**18
    assert dai_token.balanceOf(dai_exchange.address) == 20*10**18
    # Starting balances of BUYER
    assert omg_token.balanceOf(t.a1) == 3*10**18
    assert dai_token.balanceOf(t.a1) == 0
    assert chain.head_state.get_balance(t.a1) == 1*10**24
    # BUYER converts ETH to UNI
    omg_exchange.tokenToTokenSwapExact(2843678215834080597, 3*10**18, deadline, dai_token.address, sender=t.k1)
    # Updated balances of UNI exchange
    assert chain.head_state.get_balance(omg_exchange.address) == 4168751042187760548
    assert omg_token.balanceOf(omg_exchange.address) == 12*10**18 - 3
    # Updated balances of SWAP exchange
    assert chain.head_state.get_balance(dai_exchange.address) == 5831248957812239452
    assert dai_token.balanceOf(dai_exchange.address) == 17156321784165919403
    # Updated balances of BUYER
    assert omg_token.balanceOf(t.a1) == 1*10**18 + 3
    assert dai_token.balanceOf(t.a1) == 2843678215834080597
    assert chain.head_state.get_balance(t.a1) == 1*10**24

def test_transfer_exact(t, chain, omg_token, dai_token, omg_exchange, dai_exchange, assert_tx_failed):
    deadline = chain.head_state.timestamp + 300
    omg_token.transfer(t.a1, 3*10**18)
    omg_token.approve(omg_exchange.address, 10*10**18)
    omg_token.approve(omg_exchange.address, 3*10**18, sender=t.k1)
    omg_exchange.addLiquidity(10*10**18, deadline, value=5*10**18)
    dai_token.approve(dai_exchange.address, 20*10**18)
    dai_exchange.addLiquidity(20*10**18, deadline, value=5*10**18)
    # Starting balances of UNI exchange
    assert chain.head_state.get_balance(omg_exchange.address) == 5*10**18
    assert omg_token.balanceOf(omg_exchange.address) == 10*10**18
    # Starting balances of SWAP exchange
    assert chain.head_state.get_balance(dai_exchange.address) == 5*10**18
    assert dai_token.balanceOf(dai_exchange.address) == 20*10**18
    # Starting balances of BUYER
    assert omg_token.balanceOf(t.a1) == 3*10**18
    assert dai_token.balanceOf(t.a1) == 0
    assert chain.head_state.get_balance(t.a1) == 1*10**24
    # Starting balances of RECIPIENT
    assert omg_token.balanceOf(t.a2) == 0
    assert dai_token.balanceOf(t.a2) == 0
    assert chain.head_state.get_balance(t.a2) == 1*10**24
    # BUYER converts ETH to UNI
    omg_exchange.tokenToTokenTransferExact(2843678215834080597, 3*10**18, deadline, t.a2, dai_token.address, startgas=150000, sender=t.k1)
    # Updated balances of UNI exchange
    assert chain.head_state.get_balance(omg_exchange.address) == 4168751042187760548
    assert omg_token.balanceOf(omg_exchange.address) == 12*10**18 - 3
    # Updated balances of SWAP exchange
    assert chain.head_state.get_balance(dai_exchange.address) == 5831248957812239452
    assert dai_token.balanceOf(dai_exchange.address) == 17156321784165919403
    # Updated balances of BUYER
    assert omg_token.balanceOf(t.a1) == 1*10**18 + 3
    assert dai_token.balanceOf(t.a1) == 0
    assert chain.head_state.get_balance(t.a1) == 1*10**24
    # Updated balances of RECIPIENT
    assert omg_token.balanceOf(t.a2) ==  0
    assert dai_token.balanceOf(t.a2) == 2843678215834080597
    assert chain.head_state.get_balance(t.a2) == 1*10**24
