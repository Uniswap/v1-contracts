def test_swap_tokens_to_tokens_all(t, chain, utils, uni_token, swap_token, uniswap_factory, uni_token_exchange, swap_token_exchange, assert_tx_failed):
    uni_token.transfer(t.a1, 3*10**18)
    uni_token.approve(uni_token_exchange.address, 10*10**18)
    uni_token.approve(uni_token_exchange.address, 3*10**18, sender=t.k1)
    uni_token_exchange.initialize(10*10**18, value=5*10**18)
    swap_token.approve(swap_token_exchange.address, 20*10**18)
    swap_token_exchange.initialize(20*10**18, value=5*10**18)
    timeout = chain.head_state.timestamp + 300
    # Starting balances of UNI exchange
    assert chain.head_state.get_balance(uni_token_exchange.address) == 5*10**18
    assert uni_token.balanceOf(uni_token_exchange.address) == 10*10**18
    # Starting balances of SWAP exchange
    assert chain.head_state.get_balance(swap_token_exchange.address) == 5*10**18
    assert swap_token.balanceOf(swap_token_exchange.address) == 20*10**18
    # Starting balances of BUYER
    assert uni_token.balanceOf(t.a1) == 3*10**18
    assert swap_token.balanceOf(t.a1) == 0
    assert chain.head_state.get_balance(t.a1) == 1*10**24
    # BUYER converts ETH to UNI
    uni_token_exchange.swap_tokens_to_tokens_all(swap_token.address, 2*10**18, 1, timeout, startgas=115000, sender=t.k1)
    # Updated balances of UNI exchange
    assert chain.head_state.get_balance(uni_token_exchange.address) == 4168056018672890963
    assert uni_token.balanceOf(uni_token_exchange.address) == 12*10**18
    # Updated balances of SWAP exchange
    assert chain.head_state.get_balance(swap_token_exchange.address) == 5831943981327109037
    assert swap_token.balanceOf(swap_token_exchange.address) == 17151834628633326487
    # Updated balances of BUYER
    assert uni_token.balanceOf(t.a1) == 1*10**18
    assert swap_token.balanceOf(t.a1) == 2848165371366673513
    assert chain.head_state.get_balance(t.a1) == 1*10**24

def test_pay_tokens_to_tokens_all(t, chain, utils, uni_token, swap_token, uniswap_factory, uni_token_exchange, swap_token_exchange, assert_tx_failed):
    uni_token.transfer(t.a2, 3*10**18)
    uni_token.approve(uni_token_exchange.address, 10*10**18)
    uni_token.approve(uni_token_exchange.address, 3*10**18, sender=t.k2)
    uni_token_exchange.initialize(10*10**18, value=5*10**18)
    swap_token.approve(swap_token_exchange.address, 20*10**18)
    swap_token_exchange.initialize(20*10**18, value=5*10**18)
    timeout = chain.head_state.timestamp + 300
    # Starting balances of UNI exchange
    assert chain.head_state.get_balance(uni_token_exchange.address) == 5*10**18
    assert uni_token.balanceOf(uni_token_exchange.address) == 10*10**18
    # Starting balances of SWAP exchange
    assert chain.head_state.get_balance(swap_token_exchange.address) == 5*10**18
    assert swap_token.balanceOf(swap_token_exchange.address) == 20*10**18
    # Starting balances of BUYER
    assert uni_token.balanceOf(t.a2) == 3*10**18
    assert swap_token.balanceOf(t.a2) == 0
    assert chain.head_state.get_balance(t.a2) == 1*10**24
    # Starting balances of RECIPIENT
    assert uni_token.balanceOf(t.a3) == 0
    assert swap_token.balanceOf(t.a3) == 0
    assert chain.head_state.get_balance(t.a3) == 1*10**24
    # BUYER converts ETH to UNI
    uni_token_exchange.pay_tokens_to_tokens_all(swap_token.address, t.a3, 2*10**18, 1, timeout, startgas=116000, sender=t.k2)
    # Updated balances of UNI exchange
    assert chain.head_state.get_balance(uni_token_exchange.address) == 4168056018672890963
    assert uni_token.balanceOf(uni_token_exchange.address) == 12*10**18
    # Updated balances of SWAP exchange
    assert chain.head_state.get_balance(swap_token_exchange.address) == 5831943981327109037
    assert swap_token.balanceOf(swap_token_exchange.address) == 17151834628633326487
    # Updated balances of BUYER
    assert uni_token.balanceOf(t.a2) == 1*10**18
    assert swap_token.balanceOf(t.a2) == 0
    assert chain.head_state.get_balance(t.a2) == 1*10**24
    # Updated balances of RECIPIENT
    assert uni_token.balanceOf(t.a3) == 0
    assert swap_token.balanceOf(t.a3) == 2848165371366673513
    assert chain.head_state.get_balance(t.a3) == 1*10**24

def test_swap_tokens_to_tokens_exact(t, chain, utils, uni_token, swap_token, uniswap_factory, uni_token_exchange, swap_token_exchange, assert_tx_failed):
    uni_token.transfer(t.a4, 3*10**18)
    uni_token.approve(uni_token_exchange.address, 10*10**18)
    uni_token.approve(uni_token_exchange.address, 3*10**18, sender=t.k4)
    uni_token_exchange.initialize(10*10**18, value=5*10**18)
    swap_token.approve(swap_token_exchange.address, 20*10**18)
    swap_token_exchange.initialize(20*10**18, value=5*10**18)
    timeout = chain.head_state.timestamp + 300
    # Starting balances of UNI exchange
    assert chain.head_state.get_balance(uni_token_exchange.address) == 5*10**18
    assert uni_token.balanceOf(uni_token_exchange.address) == 10*10**18
    # Starting balances of SWAP exchange
    assert chain.head_state.get_balance(swap_token_exchange.address) == 5*10**18
    assert swap_token.balanceOf(swap_token_exchange.address) == 20*10**18
    # Starting balances of BUYER
    assert uni_token.balanceOf(t.a4) == 3*10**18
    assert swap_token.balanceOf(t.a4) == 0
    assert chain.head_state.get_balance(t.a4) == 1*10**24
    # BUYER converts ETH to UNI
    uni_token_exchange.swap_tokens_to_tokens_exact(swap_token.address, 2848165371366673513, 3*10**18, timeout, startgas=116000, sender=t.k4)
    # Updated balances of UNI exchange
    assert chain.head_state.get_balance(uni_token_exchange.address) == 4168056018672890963
    assert uni_token.balanceOf(uni_token_exchange.address) == 12*10**18 + 1
    # Updated balances of SWAP exchange
    assert chain.head_state.get_balance(swap_token_exchange.address) == 5831943981327109037
    assert swap_token.balanceOf(swap_token_exchange.address) == 17151834628633326487
    # Updated balances of BUYER
    assert uni_token.balanceOf(t.a4) == 1*10**18 - 1
    assert swap_token.balanceOf(t.a4) == 2848165371366673513
    assert chain.head_state.get_balance(t.a4) == 1*10**24

def test_pay_tokens_to_tokens_exact(t, chain, utils, uni_token, swap_token, uniswap_factory, uni_token_exchange, swap_token_exchange, assert_tx_failed):
    uni_token.transfer(t.a5, 3*10**18)
    uni_token.approve(uni_token_exchange.address, 10*10**18)
    uni_token.approve(uni_token_exchange.address, 3*10**18, sender=t.k5)
    uni_token_exchange.initialize(10*10**18, value=5*10**18)
    swap_token.approve(swap_token_exchange.address, 20*10**18)
    swap_token_exchange.initialize(20*10**18, value=5*10**18)
    timeout = chain.head_state.timestamp + 300
    # Starting balances of UNI exchange
    assert chain.head_state.get_balance(uni_token_exchange.address) == 5*10**18
    assert uni_token.balanceOf(uni_token_exchange.address) == 10*10**18
    # Starting balances of SWAP exchange
    assert chain.head_state.get_balance(swap_token_exchange.address) == 5*10**18
    assert swap_token.balanceOf(swap_token_exchange.address) == 20*10**18
    # Starting balances of BUYER
    assert uni_token.balanceOf(t.a5) == 3*10**18
    assert swap_token.balanceOf(t.a5) == 0
    assert chain.head_state.get_balance(t.a5) == 1*10**24
    # Starting balances of RECIPIENT
    assert uni_token.balanceOf(t.a6) == 0
    assert swap_token.balanceOf(t.a6) == 0
    assert chain.head_state.get_balance(t.a6) == 1*10**24
    # BUYER converts ETH to UNI
    uni_token_exchange.pay_tokens_to_tokens_exact(swap_token.address, t.a6, 2848165371366673513, 3*10**18, timeout, startgas=118000, sender=t.k5)
    # Updated balances of UNI exchange
    assert chain.head_state.get_balance(uni_token_exchange.address) == 4168056018672890963
    assert uni_token.balanceOf(uni_token_exchange.address) == 12*10**18 + 1
    # Updated balances of SWAP exchange
    assert chain.head_state.get_balance(swap_token_exchange.address) == 5831943981327109037
    assert swap_token.balanceOf(swap_token_exchange.address) == 17151834628633326487
    # Updated balances of BUYER
    assert uni_token.balanceOf(t.a5) == 1*10**18 - 1
    assert swap_token.balanceOf(t.a5) == 0
    assert chain.head_state.get_balance(t.a5) == 1*10**24
    # Updated balances of RECIPIENT
    assert uni_token.balanceOf(t.a6) ==  0
    assert swap_token.balanceOf(t.a6) == 2848165371366673513
    assert chain.head_state.get_balance(t.a6) == 1*10**24
