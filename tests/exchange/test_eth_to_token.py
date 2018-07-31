def test_swap_default(t, chain, uni_token, uni_exchange, assert_tx_failed):
    deadline = chain.head_state.timestamp + 300
    uni_token.approve(uni_exchange.address, 10*10**18)
    uni_exchange.addLiquidity(10*10**18, deadline, value=5*10**18)
    # Starting balances of UNI exchange
    assert chain.head_state.get_balance(uni_exchange.address) == 5*10**18
    assert uni_token.balanceOf(uni_exchange.address) == 10*10**18
    # Starting balances of BUYER
    assert uni_token.balanceOf(t.a1) == 0
    assert chain.head_state.get_balance(t.a1) == 1*10**24
    # BUYER converts ETH to UNI
    chain.tx(to=uni_exchange.address, startgas=63388, value=1*10**18, sender=t.k1)
    # Updated balances of UNI exchange
    assert chain.head_state.get_balance(uni_exchange.address) == 6*10**18
    assert uni_token.balanceOf(uni_exchange.address) == 8336807002917882451
    # Updated balances of BUYER
    assert uni_token.balanceOf(t.a1) == 1663192997082117549
    assert chain.head_state.get_balance(t.a1) == 1*10**24 - 1*10**18

def test_swap_all(t, chain, uni_token, uni_exchange, assert_tx_failed):
    deadline = chain.head_state.timestamp + 300
    uni_token.approve(uni_exchange.address, 10*10**18)
    uni_exchange.addLiquidity(10*10**18, deadline, value=5*10**18)
    # Starting balances of UNI exchange
    assert chain.head_state.get_balance(uni_exchange.address) == 5*10**18
    assert uni_token.balanceOf(uni_exchange.address) == 10*10**18
    # Starting balances of BUYER
    assert uni_token.balanceOf(t.a1) == 0
    assert chain.head_state.get_balance(t.a1) == 1*10**24
    # BUYER converts ETH to UNI
    assert uni_exchange.ethToTokenSwap(1, deadline, value=1*10**18, startgas=62877, sender=t.k1) == 1663192997082117549
    # Updated balances of UNI exchange
    assert chain.head_state.get_balance(uni_exchange.address) == 6*10**18
    assert uni_token.balanceOf(uni_exchange.address) == 8336807002917882451
    # Updated balances of BUYER
    assert uni_token.balanceOf(t.a1) == 1663192997082117549
    assert chain.head_state.get_balance(t.a1) == 1*10**24 - 1*10**18
#
def test_swap_exact(t, chain, uni_token, uni_exchange, assert_tx_failed):
    deadline = chain.head_state.timestamp + 300
    uni_token.approve(uni_exchange.address, 10*10**18)
    uni_exchange.addLiquidity(10*10**18, deadline, value=5*10**18)
    # Starting balances of UNI exchange
    assert chain.head_state.get_balance(uni_exchange.address) == 5*10**18
    assert uni_token.balanceOf(uni_exchange.address) == 10*10**18
    # Starting balances of BUYER
    assert uni_token.balanceOf(t.a1) == 0
    assert chain.head_state.get_balance(t.a1) == 1*10**24
    # BUYER converts ETH to UNI
    uni_exchange.ethToTokenSwapExact(1663192997082117549, deadline, value=2*10**18, startgas=74000, sender=t.k1)
    # Updated balances of UNI exchange
    assert chain.head_state.get_balance(uni_exchange.address) == 6*10**18
    assert uni_token.balanceOf(uni_exchange.address) == 8336807002917882451
    # Updated balances of BUYER
    assert uni_token.balanceOf(t.a1) == 1663192997082117549
    assert chain.head_state.get_balance(t.a1) == 1*10**24 - 1*10**18

def test_transfer_all(t, chain, uni_token, uni_exchange, assert_tx_failed):
    deadline = chain.head_state.timestamp + 300
    uni_token.approve(uni_exchange.address, 10*10**18)
    uni_exchange.addLiquidity(10*10**18, deadline, value=5*10**18)
    # Starting balances of UNI exchange
    assert chain.head_state.get_balance(uni_exchange.address) == 5*10**18
    assert uni_token.balanceOf(uni_exchange.address) == 10*10**18
    # Starting balances of BUYER
    assert uni_token.balanceOf(t.a1) == 0
    assert chain.head_state.get_balance(t.a1) == 1*10**24
    # Starting balances of RECIPIENT
    assert uni_token.balanceOf(t.a2) == 0
    assert chain.head_state.get_balance(t.a2) == 1*10**24
    # BUYER converts ETH to UNI
    uni_exchange.ethToTokenTransfer(t.a2, 1, deadline, value=1*10**18, startgas=65750, sender=t.k1)
    # Updated balances of UNI exchange
    assert chain.head_state.get_balance(uni_exchange.address) == 6*10**18
    assert uni_token.balanceOf(uni_exchange.address) == 8336807002917882451
    # Updated balances of BUYER
    assert uni_token.balanceOf(t.a1) == 0
    assert chain.head_state.get_balance(t.a1) == 1*10**24 - 1*10**18
    # Updated balances of RECIPIENT
    assert uni_token.balanceOf(t.a2) == 1663192997082117549
    assert chain.head_state.get_balance(t.a2) == 1*10**24

def test_transfer_exact(t, chain, uni_token, uni_exchange, assert_tx_failed):
    deadline = chain.head_state.timestamp + 300
    uni_token.approve(uni_exchange.address, 10*10**18)
    uni_exchange.addLiquidity(10*10**18, deadline, value=5*10**18)
    # Starting balances of UNI exchange
    assert chain.head_state.get_balance(uni_exchange.address) == 5*10**18
    assert uni_token.balanceOf(uni_exchange.address) == 10*10**18
    # Starting balances of BUYER
    assert uni_token.balanceOf(t.a1) == 0
    assert chain.head_state.get_balance(t.a1) == 1*10**24
    # Starting balances of RECIPIENT
    assert uni_token.balanceOf(t.a2) == 0
    assert chain.head_state.get_balance(t.a2) == 1*10**24
    # BUYER converts ETH to UNI
    uni_exchange.ethToTokenTransferExact(t.a2, 1663192997082117549, deadline, value=2*10**18, startgas=75000, sender=t.k1)
    # Updated balances of UNI exchange
    assert chain.head_state.get_balance(uni_exchange.address) == 6*10**18
    assert uni_token.balanceOf(uni_exchange.address) == 8336807002917882451
    # Updated balances of BUYER
    assert uni_token.balanceOf(t.a1) == 0
    assert chain.head_state.get_balance(t.a1) == 1*10**24 - 1*10**18
    # Updated balances of RECIPIENT
    assert uni_token.balanceOf(t.a2) == 1663192997082117549
    assert chain.head_state.get_balance(t.a2) == 1*10**24
