def test_swap_all(t, chain, utils, uni_token, swap_token, exchange_factory, uni_exchange, swap_exchange, assert_tx_failed):
    timeout = chain.head_state.timestamp + 300
    uni_token.transfer(t.a1, 3*10**18)
    uni_token.approve(uni_exchange.address, 10*10**18)
    uni_token.approve(uni_exchange.address, 3*10**18, sender=t.k1)
    uni_exchange.initialize(10*10**18, value=5*10**18)
    swap_token.approve(swap_exchange.address, 20*10**18)
    swap_exchange.initialize(20*10**18, value=5*10**18)
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
    uni_exchange.tokenToTokenSwap(swap_token.address, 2*10**18, 1, timeout, startgas=110000, sender=t.k1)
    # Updated balances of UNI exchange
    assert chain.head_state.get_balance(uni_exchange.address) == 4168056018672890963
    assert uni_token.balanceOf(uni_exchange.address) == 12*10**18
    # Updated balances of SWAP exchange
    assert chain.head_state.get_balance(swap_exchange.address) == 5831943981327109037
    assert swap_token.balanceOf(swap_exchange.address) == 17151834628633326487
    # Updated balances of BUYER
    assert uni_token.balanceOf(t.a1) == 1*10**18
    assert swap_token.balanceOf(t.a1) == 2848165371366673513
    assert chain.head_state.get_balance(t.a1) == 1*10**24

def test_swap_exact(t, chain, utils, uni_token, swap_token, exchange_factory, uni_exchange, swap_exchange, assert_tx_failed):
    timeout = chain.head_state.timestamp + 300
    uni_token.transfer(t.a1, 3*10**18)
    uni_token.approve(uni_exchange.address, 10*10**18)
    uni_token.approve(uni_exchange.address, 3*10**18, sender=t.k1)
    uni_exchange.initialize(10*10**18, value=5*10**18)
    swap_token.approve(swap_exchange.address, 20*10**18)
    swap_exchange.initialize(20*10**18, value=5*10**18)
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
    uni_exchange.tokenToTokenSwapExact(swap_token.address, 3*10**18, 2848165371366673513, timeout, startgas=111950, sender=t.k1)
    # uni_exchange.swap_tokens_to_tokens_exact(swap_token.address, 2848165371366673513, 3*10**18, timeout, startgas=116050, sender=t.k1)
    # Updated balances of UNI exchange
    assert chain.head_state.get_balance(uni_exchange.address) == 4168056018672890963
    assert uni_token.balanceOf(uni_exchange.address) == 12*10**18 + 1
    # Updated balances of SWAP exchange
    assert chain.head_state.get_balance(swap_exchange.address) == 5831943981327109037
    assert swap_token.balanceOf(swap_exchange.address) == 17151834628633326487
    # Updated balances of BUYER
    assert uni_token.balanceOf(t.a1) == 1*10**18 - 1
    assert swap_token.balanceOf(t.a1) == 2848165371366673513
    assert chain.head_state.get_balance(t.a1) == 1*10**24

def test_transfer_all(t, chain, utils, uni_token, swap_token, exchange_factory, uni_exchange, swap_exchange, assert_tx_failed):
    timeout = chain.head_state.timestamp + 300
    uni_token.transfer(t.a1, 3*10**18)
    uni_token.approve(uni_exchange.address, 10*10**18)
    uni_token.approve(uni_exchange.address, 3*10**18, sender=t.k1)
    uni_exchange.initialize(10*10**18, value=5*10**18)
    swap_token.approve(swap_exchange.address, 20*10**18)
    swap_exchange.initialize(20*10**18, value=5*10**18)
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
    uni_exchange.tokenToTokenTransfer(swap_token.address, t.a2, 2*10**18, 1, timeout, startgas=116000, sender=t.k1)
    # Updated balances of UNI exchange
    assert chain.head_state.get_balance(uni_exchange.address) == 4168056018672890963
    assert uni_token.balanceOf(uni_exchange.address) == 12*10**18
    # Updated balances of SWAP exchange
    assert chain.head_state.get_balance(swap_exchange.address) == 5831943981327109037
    assert swap_token.balanceOf(swap_exchange.address) == 17151834628633326487
    # Updated balances of BUYER
    assert uni_token.balanceOf(t.a1) == 1*10**18
    assert swap_token.balanceOf(t.a1) == 0
    assert chain.head_state.get_balance(t.a1) == 1*10**24
    # Updated balances of RECIPIENT
    assert uni_token.balanceOf(t.a2) == 0
    assert swap_token.balanceOf(t.a2) == 2848165371366673513
    assert chain.head_state.get_balance(t.a2) == 1*10**24

def test_transfer_exact(t, chain, utils, uni_token, swap_token, exchange_factory, uni_exchange, swap_exchange, assert_tx_failed):
    timeout = chain.head_state.timestamp + 300
    uni_token.transfer(t.a1, 3*10**18)
    uni_token.approve(uni_exchange.address, 10*10**18)
    uni_token.approve(uni_exchange.address, 3*10**18, sender=t.k1)
    uni_exchange.initialize(10*10**18, value=5*10**18)
    swap_token.approve(swap_exchange.address, 20*10**18)
    swap_exchange.initialize(20*10**18, value=5*10**18)
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
    uni_exchange.tokenToTokenTransferExact(swap_token.address, t.a2, 3*10**18, 2848165371366673513, timeout, startgas=125000, sender=t.k1)
    # Updated balances of UNI exchange
    assert chain.head_state.get_balance(uni_exchange.address) == 4168056018672890963
    assert uni_token.balanceOf(uni_exchange.address) == 12*10**18 + 1
    # Updated balances of SWAP exchange
    assert chain.head_state.get_balance(swap_exchange.address) == 5831943981327109037
    assert swap_token.balanceOf(swap_exchange.address) == 17151834628633326487
    # Updated balances of BUYER
    assert uni_token.balanceOf(t.a1) == 1*10**18 - 1
    assert swap_token.balanceOf(t.a1) == 0
    assert chain.head_state.get_balance(t.a1) == 1*10**24
    # Updated balances of RECIPIENT
    assert uni_token.balanceOf(t.a2) ==  0
    assert swap_token.balanceOf(t.a2) == 2848165371366673513
    assert chain.head_state.get_balance(t.a2) == 1*10**24
