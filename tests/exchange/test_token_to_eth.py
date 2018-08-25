def test_swap(t, chain, omg_token, omg_exchange, assert_tx_failed):
    deadline = chain.head_state.timestamp + 300
    omg_token.transfer(t.a1, 2*10**18)
    omg_token.approve(omg_exchange.address, 10*10**18)
    omg_token.approve(omg_exchange.address, 2*10**18, sender=t.k1)
    omg_exchange.addLiquidity(10*10**18, deadline, value=5*10**18)
    # Starting balances of UNI exchange
    assert chain.head_state.get_balance(omg_exchange.address) == 5*10**18
    assert omg_token.balanceOf(omg_exchange.address) == 10*10**18
    # Starting balances of BUYER
    assert omg_token.balanceOf(t.a1) == 2*10**18
    assert chain.head_state.get_balance(t.a1) == 1*10**24
    # BUYER converts ETH to UNI
    omg_exchange.tokenToEthSwap(2*10**18, 1, deadline, sender=t.k1)
    # Updated balances of UNI exchange
    assert chain.head_state.get_balance(omg_exchange.address) == 4168403501458941225
    assert omg_token.balanceOf(omg_exchange.address) == 12*10**18
    # Updated balances of BUYER
    assert omg_token.balanceOf(t.a1) == 0
    assert chain.head_state.get_balance(t.a1) == 1*10**24 + 831596498541058775

def test_transfer(t, chain, omg_token, omg_exchange, assert_tx_failed):
    deadline = chain.head_state.timestamp + 300
    omg_token.transfer(t.a1, 2*10**18)
    omg_token.approve(omg_exchange.address, 10*10**18)
    omg_token.approve(omg_exchange.address, 2*10**18, sender=t.k1)
    omg_exchange.addLiquidity(10*10**18, deadline, value=5*10**18)
    # Starting balances of UNI exchange
    assert chain.head_state.get_balance(omg_exchange.address) == 5*10**18
    assert omg_token.balanceOf(omg_exchange.address) == 10*10**18
    # Starting balances of BUYER
    assert omg_token.balanceOf(t.a1) == 2*10**18
    assert chain.head_state.get_balance(t.a1) == 1*10**24
    # Starting balances of RECIPIENT
    assert omg_token.balanceOf(t.a2) == 0
    assert chain.head_state.get_balance(t.a2) == 1*10**24
    # BUYER converts ETH to UNI
    omg_exchange.tokenToEthTransfer(2*10**18, 1, deadline, t.a2, sender=t.k1)
    # Updated balances of UNI exchange
    assert chain.head_state.get_balance(omg_exchange.address) == 4168403501458941225
    assert omg_token.balanceOf(omg_exchange.address) == 12*10**18
    # Updated balances of BUYER
    assert omg_token.balanceOf(t.a1) == 0
    assert chain.head_state.get_balance(t.a1) == 1*10**24
    # Updated balances of RECIPIENT
    assert omg_token.balanceOf(t.a2) == 0
    assert chain.head_state.get_balance(t.a2) == 1*10**24 + 831596498541058775

def test_swap_exact(t, chain, omg_token, omg_exchange, assert_tx_failed):
    deadline = chain.head_state.timestamp + 300
    omg_token.transfer(t.a1, 3*10**18)
    omg_token.approve(omg_exchange.address, 10*10**18)
    omg_token.approve(omg_exchange.address, 3*10**18, sender=t.k1)
    omg_exchange.addLiquidity(10*10**18, deadline, value=5*10**18)
    # Starting balances of UNI exchange
    assert chain.head_state.get_balance(omg_exchange.address) == 5*10**18
    assert omg_token.balanceOf(omg_exchange.address) == 10*10**18
    # Starting balances of BUYER
    assert omg_token.balanceOf(t.a1) == 3*10**18
    assert chain.head_state.get_balance(t.a1) == 1*10**24
    # BUYER converts ETH to UNI
    omg_exchange.tokenToEthSwapExact(831596498541058775, 3*10**18, deadline, sender=t.k1)
    # Updated balances of UNI exchange
    assert chain.head_state.get_balance(omg_exchange.address) == 4168403501458941225
    assert omg_token.balanceOf(omg_exchange.address) == 12*10**18 + 1         # Exchange gets 1 more token due to fee rounding
    # Updated balances of BUYER
    assert omg_token.balanceOf(t.a1) == 1*10**18 - 1
    assert chain.head_state.get_balance(t.a1) == 1*10**24 + 831596498541058775

def test_transfer_exact(t, chain, omg_token, omg_exchange, assert_tx_failed):
    deadline = chain.head_state.timestamp + 300
    omg_token.transfer(t.a1, 3*10**18)
    omg_token.approve(omg_exchange.address, 10*10**18)
    omg_token.approve(omg_exchange.address, 3*10**18, sender=t.k1)
    omg_exchange.addLiquidity(10*10**18, deadline, value=5*10**18)
    # Starting balances of UNI exchange
    assert chain.head_state.get_balance(omg_exchange.address) == 5*10**18
    assert omg_token.balanceOf(omg_exchange.address) == 10*10**18
    # Starting balances of BUYER
    assert omg_token.balanceOf(t.a1) == 3*10**18
    assert chain.head_state.get_balance(t.a1) == 1*10**24
    # Starting balances of RECIPIENT
    assert omg_token.balanceOf(t.a2) == 0
    assert chain.head_state.get_balance(t.a2) == 1*10**24
    # BUYER converts ETH to UNI
    omg_exchange.tokenToEthTransferExact(831596498541058775, 3*10**18, deadline, t.a2, sender=t.k1)
    # Updated balances of UNI exchange
    assert chain.head_state.get_balance(omg_exchange.address) == 4168403501458941225
    assert omg_token.balanceOf(omg_exchange.address) == 12*10**18 + 1
    # Updated balances of BUYER
    assert omg_token.balanceOf(t.a1) == 1*10**18 - 1
    assert chain.head_state.get_balance(t.a1) == 1*10**24
    # Updated balances of RECIPIENT
    assert omg_token.balanceOf(t.a2) == 0
    assert chain.head_state.get_balance(t.a2) == 1*10**24 + 831596498541058775
