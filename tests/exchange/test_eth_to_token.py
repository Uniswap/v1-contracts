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
    chain.tx(to=omg_exchange.address, startgas=67388, value=1*10**18, sender=t.k1)
    # Updated balances of UNI exchange
    assert chain.head_state.get_balance(omg_exchange.address) == 6*10**18
    assert omg_token.balanceOf(omg_exchange.address) == 8337502084375521096
    # Updated balances of BUYER
    assert omg_token.balanceOf(t.a1) == 1662497915624478904
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
    # assert omg_exchange.ethToTokenSwap(1, deadline, value=1*10**18, startgas=62707, sender=t.k1) == 1662497915624478904 # Cost 1
    omg_exchange.ethToTokenSwap(1, deadline, value=1*10**18, startgas=67907, sender=t.k1)
    # Updated balances of UNI exchange
    assert chain.head_state.get_balance(omg_exchange.address) == 6*10**18
    assert omg_token.balanceOf(omg_exchange.address) == 8337502084375521096
    # Updated balances of BUYER
    assert omg_token.balanceOf(t.a1) == 1662497915624478904
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
    omg_exchange.ethToTokenTransfer(1, deadline, t.a2, value=1*10**18, startgas=68750, sender=t.k1)
    # Updated balances of UNI exchange
    assert chain.head_state.get_balance(omg_exchange.address) == 6*10**18
    assert omg_token.balanceOf(omg_exchange.address) == 8337502084375521096
    # Updated balances of BUYER
    assert omg_token.balanceOf(t.a1) == 0
    assert chain.head_state.get_balance(t.a1) == 1*10**24 - 1*10**18
    # Updated balances of RECIPIENT
    assert omg_token.balanceOf(t.a2) == 1662497915624478904
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
    omg_exchange.ethToTokenSwapExact(1662497915624478904, deadline, value=2*10**18, startgas=77000, sender=t.k1)
    # Updated balances of UNI exchange
    assert chain.head_state.get_balance(omg_exchange.address) == 6*10**18 - 1
    assert omg_token.balanceOf(omg_exchange.address) == 8337502084375521096
    # Updated balances of BUYER
    assert omg_token.balanceOf(t.a1) == 1662497915624478904
    assert chain.head_state.get_balance(t.a1) == 1*10**24 - 1*10**18 + 1

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
    omg_exchange.ethToTokenTransferExact(1662497915624478904, deadline, t.a2, value=2*10**18, startgas=78000, sender=t.k1)
    # Updated balances of UNI exchange
    assert chain.head_state.get_balance(omg_exchange.address) == 6*10**18 - 1
    assert omg_token.balanceOf(omg_exchange.address) == 8337502084375521096
    # Updated balances of BUYER
    assert omg_token.balanceOf(t.a1) == 0
    assert chain.head_state.get_balance(t.a1) == 1*10**24 - 1*10**18 + 1
    # Updated balances of RECIPIENT
    assert omg_token.balanceOf(t.a2) == 1662497915624478904
    assert chain.head_state.get_balance(t.a2) == 1*10**24
