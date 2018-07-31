def test_swap_all(t, chain, uni_token, swap_token, uni_exchange, swap_exchange, assert_tx_failed):
    deadline = chain.head_state.timestamp + 300
    uni_token.transfer(t.a1, 3*10**18)
    uni_token.approve(uni_exchange.address, 10*10**18)
    uni_token.approve(uni_exchange.address, 3*10**18, sender=t.k1)
    uni_exchange.addLiquidity(10*10**18, deadline, value=5*10**18)
    swap_token.approve(swap_exchange.address, 20*10**18)
    swap_exchange.addLiquidity(20*10**18, deadline, value=5*10**18)
    # Starting balances of UNI exchange
    assert chain.head_state.get_balance(uni_exchange.address) == 5*10**18
    assert uni_token.balanceOf(uni_exchange.address) == 10*10**18
    # Starting balances of SWAP exchange
    assert chain.head_state.get_balance(swap_exchange.address) == 5*10**18
    assert swap_token.balanceOf(swap_exchange.address) == 20*10**18
    # Starting balances of BUYER
    assert uni_token.balanceOf(t.a1) == 3*10**18
    assert swap_token.balanceOf(t.a1) == 0
    assert chain.head_state.get_balance(t.a1) == 1*10**24
    # BUYER converts ETH to UNI
    uni_exchange.tokenToTokenSwap(swap_token.address, 2*10**18, 1, deadline, startgas=110000, sender=t.k1)
    # Updated balances of UNI exchange
    assert chain.head_state.get_balance(uni_exchange.address) == 4168403501458941225
    assert uni_token.balanceOf(uni_exchange.address) == 12*10**18
    # Updated balances of SWAP exchange
    assert chain.head_state.get_balance(swap_exchange.address) == 5831596498541058775
    assert swap_token.balanceOf(swap_exchange.address) == 17154078339222077916
    # Updated balances of BUYER
    assert uni_token.balanceOf(t.a1) == 1*10**18
    assert swap_token.balanceOf(t.a1) == 2845921660777922084
    assert chain.head_state.get_balance(t.a1) == 1*10**24

def test_swap_exact(t, chain, uni_token, swap_token, uni_exchange, swap_exchange, assert_tx_failed):
    deadline = chain.head_state.timestamp + 300
    uni_token.transfer(t.a1, 3*10**18)
    uni_token.approve(uni_exchange.address, 10*10**18)
    uni_token.approve(uni_exchange.address, 3*10**18, sender=t.k1)
    uni_exchange.addLiquidity(10*10**18, deadline, value=5*10**18)
    swap_token.approve(swap_exchange.address, 20*10**18)
    swap_exchange.addLiquidity(20*10**18, deadline, value=5*10**18)
    # Starting balances of UNI exchange
    assert chain.head_state.get_balance(uni_exchange.address) == 5*10**18
    assert uni_token.balanceOf(uni_exchange.address) == 10*10**18
    # Starting balances of SWAP exchange
    assert chain.head_state.get_balance(swap_exchange.address) == 5*10**18
    assert swap_token.balanceOf(swap_exchange.address) == 20*10**18
    # Starting balances of BUYER
    assert uni_token.balanceOf(t.a1) == 3*10**18
    assert swap_token.balanceOf(t.a1) == 0
    assert chain.head_state.get_balance(t.a1) == 1*10**24
    # BUYER converts ETH to UNI
    uni_exchange.tokenToTokenSwapExact(swap_token.address, 3*10**18, 2845921660777922084, deadline, startgas=116650, sender=t.k1)
    # Updated balances of UNI exchange
    assert chain.head_state.get_balance(uni_exchange.address) == 4168403501458941225
    assert uni_token.balanceOf(uni_exchange.address) == 12*10**18 + 1
    # Updated balances of SWAP exchange
    assert chain.head_state.get_balance(swap_exchange.address) == 5831596498541058775
    assert swap_token.balanceOf(swap_exchange.address) == 17154078339222077916
    # Updated balances of BUYER
    assert uni_token.balanceOf(t.a1) == 1*10**18 - 1
    assert swap_token.balanceOf(t.a1) == 2845921660777922084
    assert chain.head_state.get_balance(t.a1) == 1*10**24

def test_transfer_all(t, chain, uni_token, swap_token, uni_exchange, swap_exchange, assert_tx_failed):
    deadline = chain.head_state.timestamp + 300
    uni_token.transfer(t.a1, 3*10**18)
    uni_token.approve(uni_exchange.address, 10*10**18)
    uni_token.approve(uni_exchange.address, 3*10**18, sender=t.k1)
    uni_exchange.addLiquidity(10*10**18, deadline, value=5*10**18)
    swap_token.approve(swap_exchange.address, 20*10**18)
    swap_exchange.addLiquidity(20*10**18, deadline, value=5*10**18)
    # Starting balances of UNI exchange
    assert chain.head_state.get_balance(uni_exchange.address) == 5*10**18
    assert uni_token.balanceOf(uni_exchange.address) == 10*10**18
    # Starting balances of SWAP exchange
    assert chain.head_state.get_balance(swap_exchange.address) == 5*10**18
    assert swap_token.balanceOf(swap_exchange.address) == 20*10**18
    # Starting balances of BUYER
    assert uni_token.balanceOf(t.a1) == 3*10**18
    assert swap_token.balanceOf(t.a1) == 0
    assert chain.head_state.get_balance(t.a1) == 1*10**24
    # Starting balances of RECIPIENT
    assert uni_token.balanceOf(t.a2) == 0
    assert swap_token.balanceOf(t.a2) == 0
    assert chain.head_state.get_balance(t.a2) == 1*10**24
    # BUYER converts ETH to UNI
    uni_exchange.tokenToTokenTransfer(swap_token.address, t.a2, 2*10**18, 1, deadline, startgas=116000, sender=t.k1)
    # Updated balances of UNI exchange
    assert chain.head_state.get_balance(uni_exchange.address) == 4168403501458941225
    assert uni_token.balanceOf(uni_exchange.address) == 12*10**18
    # Updated balances of SWAP exchange
    assert chain.head_state.get_balance(swap_exchange.address) == 5831596498541058775
    assert swap_token.balanceOf(swap_exchange.address) == 17154078339222077916
    # Updated balances of BUYER
    assert uni_token.balanceOf(t.a1) == 1*10**18
    assert swap_token.balanceOf(t.a1) == 0
    assert chain.head_state.get_balance(t.a1) == 1*10**24
    # Updated balances of RECIPIENT
    assert uni_token.balanceOf(t.a2) == 0
    assert swap_token.balanceOf(t.a2) == 2845921660777922084
    assert chain.head_state.get_balance(t.a2) == 1*10**24

def test_transfer_exact(t, chain, uni_token, swap_token, uni_exchange, swap_exchange, assert_tx_failed):
    deadline = chain.head_state.timestamp + 300
    uni_token.transfer(t.a1, 3*10**18)
    uni_token.approve(uni_exchange.address, 10*10**18)
    uni_token.approve(uni_exchange.address, 3*10**18, sender=t.k1)
    uni_exchange.addLiquidity(10*10**18, deadline, value=5*10**18)
    swap_token.approve(swap_exchange.address, 20*10**18)
    swap_exchange.addLiquidity(20*10**18, deadline, value=5*10**18)
    # Starting balances of UNI exchange
    assert chain.head_state.get_balance(uni_exchange.address) == 5*10**18
    assert uni_token.balanceOf(uni_exchange.address) == 10*10**18
    # Starting balances of SWAP exchange
    assert chain.head_state.get_balance(swap_exchange.address) == 5*10**18
    assert swap_token.balanceOf(swap_exchange.address) == 20*10**18
    # Starting balances of BUYER
    assert uni_token.balanceOf(t.a1) == 3*10**18
    assert swap_token.balanceOf(t.a1) == 0
    assert chain.head_state.get_balance(t.a1) == 1*10**24
    # Starting balances of RECIPIENT
    assert uni_token.balanceOf(t.a2) == 0
    assert swap_token.balanceOf(t.a2) == 0
    assert chain.head_state.get_balance(t.a2) == 1*10**24
    # BUYER converts ETH to UNI
    uni_exchange.tokenToTokenTransferExact(swap_token.address, t.a2, 3*10**18, 2845921660777922084, deadline, startgas=125000, sender=t.k1)
    # Updated balances of UNI exchange
    assert chain.head_state.get_balance(uni_exchange.address) == 4168403501458941225
    assert uni_token.balanceOf(uni_exchange.address) == 12*10**18 + 1
    # Updated balances of SWAP exchange
    assert chain.head_state.get_balance(swap_exchange.address) == 5831596498541058775
    assert swap_token.balanceOf(swap_exchange.address) == 17154078339222077916
    # Updated balances of BUYER
    assert uni_token.balanceOf(t.a1) == 1*10**18 - 1
    assert swap_token.balanceOf(t.a1) == 0
    assert chain.head_state.get_balance(t.a1) == 1*10**24
    # Updated balances of RECIPIENT
    assert uni_token.balanceOf(t.a2) ==  0
    assert swap_token.balanceOf(t.a2) == 2845921660777922084
    assert chain.head_state.get_balance(t.a2) == 1*10**24
