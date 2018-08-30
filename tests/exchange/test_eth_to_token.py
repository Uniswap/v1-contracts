def test_swap_default(t, chain, omg_token, omg_exchange, assert_tx_failed):
    deadline = chain.head_state.timestamp + 300
    omg_token.approve(omg_exchange.address, 10*10**18)
    omg_exchange.addLiquidity(10*10**18, deadline, value=5*10**18)
    # Starting balances of UNI exchange
    assert chain.head_state.get_balance(omg_exchange.address) == 5*10**18
    assert omg_token.balanceOf(omg_exchange.address) == 10*10**18
    # Starting balances of BUYER
    assert omg_token.balanceOf(t.a1) == 0
    assert chain.head_state.get_balance(t.a1) == 1*10**24
    # BUYER converts ETH to UNI
    chain.tx(to=omg_exchange.address, startgas=63388, value=1*10**18, sender=t.k1)
    # Updated balances of UNI exchange
    assert chain.head_state.get_balance(omg_exchange.address) == 6*10**18
    assert omg_token.balanceOf(omg_exchange.address) == 8336807002917882451
    # Updated balances of BUYER
    assert omg_token.balanceOf(t.a1) == 1663192997082117549
    assert chain.head_state.get_balance(t.a1) == 1*10**24 - 1*10**18

def test_swap(t, chain, omg_token, omg_exchange, assert_tx_failed):
    deadline = chain.head_state.timestamp + 300
    omg_token.approve(omg_exchange.address, 10*10**18)
    omg_exchange.addLiquidity(10*10**18, deadline, value=5*10**18)
    # Starting balances of UNI exchange
    assert chain.head_state.get_balance(omg_exchange.address) == 5*10**18
    assert omg_token.balanceOf(omg_exchange.address) == 10*10**18
    # Starting balances of BUYER
    assert omg_token.balanceOf(t.a1) == 0
    assert chain.head_state.get_balance(t.a1) == 1*10**24
    # BUYER converts ETH to UNI
    # assert omg_exchange.ethToTokenSwap(1, deadline, value=1*10**18, startgas=62707, sender=t.k1) == 1663192997082117549 # Cost 1
    assert omg_exchange.ethToTokenSwap(1, deadline, value=1*10**18, startgas=63907, sender=t.k1) == 1663192997082117549 # Cost 2
    # Updated balances of UNI exchange
    assert chain.head_state.get_balance(omg_exchange.address) == 6*10**18
    assert omg_token.balanceOf(omg_exchange.address) == 8336807002917882451
    # Updated balances of BUYER
    assert omg_token.balanceOf(t.a1) == 1663192997082117549
    assert chain.head_state.get_balance(t.a1) == 1*10**24 - 1*10**18

def test_transfer(t, chain, omg_token, omg_exchange, assert_tx_failed):
    deadline = chain.head_state.timestamp + 300
    omg_token.approve(omg_exchange.address, 10*10**18)
    omg_exchange.addLiquidity(10*10**18, deadline, value=5*10**18)
    # Starting balances of UNI exchange
    assert chain.head_state.get_balance(omg_exchange.address) == 5*10**18
    assert omg_token.balanceOf(omg_exchange.address) == 10*10**18
    # Starting balances of BUYER
    assert omg_token.balanceOf(t.a1) == 0
    assert chain.head_state.get_balance(t.a1) == 1*10**24
    # Starting balances of RECIPIENT
    assert omg_token.balanceOf(t.a2) == 0
    assert chain.head_state.get_balance(t.a2) == 1*10**24
    # BUYER converts ETH to UNI
    omg_exchange.ethToTokenTransfer(1, deadline, t.a2, value=1*10**18, startgas=64750, sender=t.k1)
    # Updated balances of UNI exchange
    assert chain.head_state.get_balance(omg_exchange.address) == 6*10**18
    assert omg_token.balanceOf(omg_exchange.address) == 8336807002917882451
    # Updated balances of BUYER
    assert omg_token.balanceOf(t.a1) == 0
    assert chain.head_state.get_balance(t.a1) == 1*10**24 - 1*10**18
    # Updated balances of RECIPIENT
    assert omg_token.balanceOf(t.a2) == 1663192997082117549
    assert chain.head_state.get_balance(t.a2) == 1*10**24

def test_swap_exact(t, chain, omg_token, omg_exchange, assert_tx_failed):
    deadline = chain.head_state.timestamp + 300
    omg_token.approve(omg_exchange.address, 10*10**18)
    omg_exchange.addLiquidity(10*10**18, deadline, value=5*10**18)
    # Starting balances of UNI exchange
    assert chain.head_state.get_balance(omg_exchange.address) == 5*10**18
    assert omg_token.balanceOf(omg_exchange.address) == 10*10**18
    # Starting balances of BUYER
    assert omg_token.balanceOf(t.a1) == 0
    assert chain.head_state.get_balance(t.a1) == 1*10**24
    # BUYER converts ETH to UNI
    omg_exchange.ethToTokenSwapExact(1663192997082117549, deadline, value=2*10**18, startgas=74000, sender=t.k1)
    # Updated balances of UNI exchange
    assert chain.head_state.get_balance(omg_exchange.address) == 6*10**18
    assert omg_token.balanceOf(omg_exchange.address) == 8336807002917882451
    # Updated balances of BUYER
    assert omg_token.balanceOf(t.a1) == 1663192997082117549
    assert chain.head_state.get_balance(t.a1) == 1*10**24 - 1*10**18

def test_transfer_exact(t, chain, omg_token, omg_exchange, assert_tx_failed):
    deadline = chain.head_state.timestamp + 300
    omg_token.approve(omg_exchange.address, 10*10**18)
    omg_exchange.addLiquidity(10*10**18, deadline, value=5*10**18)
    # Starting balances of UNI exchange
    assert chain.head_state.get_balance(omg_exchange.address) == 5*10**18
    assert omg_token.balanceOf(omg_exchange.address) == 10*10**18
    # Starting balances of BUYER
    assert omg_token.balanceOf(t.a1) == 0
    assert chain.head_state.get_balance(t.a1) == 1*10**24
    # Starting balances of RECIPIENT
    assert omg_token.balanceOf(t.a2) == 0
    assert chain.head_state.get_balance(t.a2) == 1*10**24
    # BUYER converts ETH to UNI
    omg_exchange.ethToTokenTransferExact(1663192997082117549, deadline, t.a2, value=2*10**18, startgas=75000, sender=t.k1)
    # Updated balances of UNI exchange
    assert chain.head_state.get_balance(omg_exchange.address) == 6*10**18
    assert omg_token.balanceOf(omg_exchange.address) == 8336807002917882451
    # Updated balances of BUYER
    assert omg_token.balanceOf(t.a1) == 0
    assert chain.head_state.get_balance(t.a1) == 1*10**24 - 1*10**18
    # Updated balances of RECIPIENT
    assert omg_token.balanceOf(t.a2) == 1663192997082117549
    assert chain.head_state.get_balance(t.a2) == 1*10**24
