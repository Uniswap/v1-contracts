def test_tokens_to_tokens_swap(t, chain, utils, uni_token, swap_token, uniswap_factory, uni_token_exchange, swap_token_exchange, assert_tx_failed):
    uni_token.transfer(t.a1, 2*10**18)
    uni_token.approve(uni_token_exchange.address, 10*10**18)
    uni_token.approve(uni_token_exchange.address, 2*10**18, sender=t.k1)
    uni_token_exchange.initialize(10*10**18, value=5*10**18)
    swap_token.approve(swap_token_exchange.address, 20*10**18)
    swap_token_exchange.initialize(20*10**18, value=5*10**18)
    timeout = chain.head_state.timestamp + 300
    # Starting balances of UNI exchange
    assert uni_token_exchange.eth_pool() == 5*10**18
    assert uni_token_exchange.token_pool() == 10*10**18
    # Starting balances of SWAP exchange
    assert swap_token_exchange.eth_pool() == 5*10**18
    assert swap_token_exchange.token_pool() == 20*10**18
    # Starting balances of BUYER
    assert uni_token.balanceOf(t.a1) == 2*10**18
    assert swap_token.balanceOf(t.a1) == 0
    assert chain.head_state.get_balance(t.a1) == 1*10**24
    # BUYER converts ETH to UNI
    uni_token_exchange.tokens_to_tokens_swap(swap_token.address, 2*10**18, 1, timeout, startgas=300000, sender=t.k1)
    # Updated balances of UNI exchange
    assert uni_token_exchange.eth_pool() == 4168056018672890963
    assert uni_token_exchange.token_pool() == 12*10**18
    # Updated balances of SWAP exchange
    assert swap_token_exchange.eth_pool() == 5831943981327109037
    assert swap_token_exchange.token_pool() == 17151834628633326487
    # Updated balances of BUYER
    assert uni_token.balanceOf(t.a1) == 0
    assert swap_token.balanceOf(t.a1) == 2848165371366673513
    assert chain.head_state.get_balance(t.a1) == 1*10**24

def test_tokens_to_tokens_payment(t, chain, utils, uni_token, swap_token, uniswap_factory, uni_token_exchange, swap_token_exchange, assert_tx_failed):
    uni_token.transfer(t.a1, 2*10**18)
    uni_token.approve(uni_token_exchange.address, 10*10**18)
    uni_token.approve(uni_token_exchange.address, 2*10**18, sender=t.k1)
    uni_token_exchange.initialize(10*10**18, value=5*10**18)
    swap_token.approve(swap_token_exchange.address, 20*10**18)
    swap_token_exchange.initialize(20*10**18, value=5*10**18)
    timeout = chain.head_state.timestamp + 300
    # Starting balances of UNI exchange
    assert uni_token_exchange.eth_pool() == 5*10**18
    assert uni_token_exchange.token_pool() == 10*10**18
    # Starting balances of SWAP exchange
    assert swap_token_exchange.eth_pool() == 5*10**18
    assert swap_token_exchange.token_pool() == 20*10**18
    # Starting balances of BUYER
    assert uni_token.balanceOf(t.a1) == 2*10**18
    assert swap_token.balanceOf(t.a1) == 0
    assert chain.head_state.get_balance(t.a1) == 1*10**24
    # Starting balances of RECIPIENT
    assert uni_token.balanceOf(t.a2) == 0
    assert swap_token.balanceOf(t.a2) == 0
    assert chain.head_state.get_balance(t.a2) == 1*10**24
    # BUYER converts ETH to UNI
    uni_token_exchange.tokens_to_tokens_payment(swap_token.address, t.a2, 2*10**18, 1, timeout, startgas=500000, sender=t.k1)
    # Updated balances of UNI exchange
    assert uni_token_exchange.eth_pool() == 4168056018672890963
    assert uni_token_exchange.token_pool() == 12*10**18
    # Updated balances of SWAP exchange
    assert swap_token_exchange.eth_pool() == 5831943981327109037
    assert swap_token_exchange.token_pool() == 17151834628633326487
    # Updated balances of BUYER
    assert uni_token.balanceOf(t.a1) == 0
    assert swap_token.balanceOf(t.a1) == 0
    assert chain.head_state.get_balance(t.a1) == 1*10**24
    # Updated balances of RECIPIENT
    assert uni_token.balanceOf(t.a2) == 0
    assert swap_token.balanceOf(t.a2) == 2848165371366673513
    assert chain.head_state.get_balance(t.a2) == 1*10**24
