def test_tokens_to_eth_swap(t, chain, utils, uni_token, uniswap_factory, uni_token_exchange, assert_tx_failed):
    uni_token.transfer(t.a1, 2*10**18)
    uni_token.approve(uni_token_exchange.address, 10*10**18)
    uni_token.approve(uni_token_exchange.address, 2*10**18, sender=t.k1)
    uni_token_exchange.initialize(10*10**18, value=5*10**18)
    timeout = chain.head_state.timestamp + 300
    # Starting balances of UNI exchange
    assert chain.head_state.get_balance(uni_token_exchange.address) == 5*10**18
    assert uni_token.balanceOf(uni_token_exchange.address) == 10*10**18
    # Starting balances of BUYER
    assert uni_token.balanceOf(t.a1) == 2*10**18
    assert chain.head_state.get_balance(t.a1) == 1*10**24
    # BUYER converts ETH to UNI
    uni_token_exchange.tokens_to_eth_swap(2*10**18, 1, timeout, sender=t.k1)
    # Updated balances of UNI exchange
    assert chain.head_state.get_balance(uni_token_exchange.address) == 4168056018672890963
    assert uni_token.balanceOf(uni_token_exchange.address) == 12*10**18
    # Updated balances of BUYER
    assert uni_token.balanceOf(t.a1) == 0
    assert chain.head_state.get_balance(t.a1) == 1*10**24 + 831943981327109037

def test_tokens_to_eth_payment(t, chain, utils, uni_token, uniswap_factory, uni_token_exchange, assert_tx_failed):
    uni_token.transfer(t.a2, 2*10**18)
    uni_token.approve(uni_token_exchange.address, 10*10**18)
    uni_token.approve(uni_token_exchange.address, 2*10**18, sender=t.k2)
    uni_token_exchange.initialize(10*10**18, value=5*10**18)
    timeout = chain.head_state.timestamp + 300
    # Starting balances of UNI exchange
    assert chain.head_state.get_balance(uni_token_exchange.address) == 5*10**18
    assert uni_token.balanceOf(uni_token_exchange.address) == 10*10**18
    # Starting balances of BUYER
    assert uni_token.balanceOf(t.a2) == 2*10**18
    assert chain.head_state.get_balance(t.a2) == 1*10**24
    # Starting balances of RECIPIENT
    assert uni_token.balanceOf(t.a3) == 0
    assert chain.head_state.get_balance(t.a3) == 1*10**24
    # BUYER converts ETH to UNI
    uni_token_exchange.tokens_to_eth_payment(t.a3, 2*10**18, 1, timeout, sender=t.k2)
    # Updated balances of UNI exchange
    assert chain.head_state.get_balance(uni_token_exchange.address) == 4168056018672890963
    assert uni_token.balanceOf(uni_token_exchange.address) == 12*10**18
    # Updated balances of BUYER
    assert uni_token.balanceOf(t.a2) == 0
    assert chain.head_state.get_balance(t.a2) == 1*10**24
    # Updated balances of RECIPIENT
    assert uni_token.balanceOf(t.a3) == 0
    assert chain.head_state.get_balance(t.a3) == 1*10**24 + 831943981327109037

def test_tokens_to_eth_exact_swap(t, chain, utils, uni_token, uniswap_factory, uni_token_exchange, assert_tx_failed):
    uni_token.transfer(t.a4, 3*10**18)
    uni_token.approve(uni_token_exchange.address, 10*10**18)
    uni_token.approve(uni_token_exchange.address, 3*10**18, sender=t.k4)
    uni_token_exchange.initialize(10*10**18, value=5*10**18)
    timeout = chain.head_state.timestamp + 300
    # Starting balances of UNI exchange
    assert chain.head_state.get_balance(uni_token_exchange.address) == 5*10**18
    assert uni_token.balanceOf(uni_token_exchange.address) == 10*10**18
    # Starting balances of BUYER
    assert uni_token.balanceOf(t.a4) == 3*10**18
    assert chain.head_state.get_balance(t.a4) == 1*10**24
    # BUYER converts ETH to UNI
    uni_token_exchange.tokens_to_eth_exact_swap(831943981327109037, 3*10**18, timeout, sender=t.k4)
    # Updated balances of UNI exchange
    assert chain.head_state.get_balance(uni_token_exchange.address) == 4168056018672890963
    assert uni_token.balanceOf(uni_token_exchange.address) == 12*10**18 + 1         # Exchange gets 1 more token due to fee rounding
    # Updated balances of BUYER
    assert uni_token.balanceOf(t.a4) == 1*10**18 - 1
    assert chain.head_state.get_balance(t.a4) == 1*10**24 + 831943981327109037

def test_tokens_to_eth_exact_payment(t, chain, utils, uni_token, uniswap_factory, uni_token_exchange, assert_tx_failed):
    uni_token.transfer(t.a5, 3*10**18)
    uni_token.approve(uni_token_exchange.address, 10*10**18)
    uni_token.approve(uni_token_exchange.address, 3*10**18, sender=t.k5)
    uni_token_exchange.initialize(10*10**18, value=5*10**18)
    timeout = chain.head_state.timestamp + 300
    # Starting balances of UNI exchange
    assert chain.head_state.get_balance(uni_token_exchange.address) == 5*10**18
    assert uni_token.balanceOf(uni_token_exchange.address) == 10*10**18
    # Starting balances of BUYER
    assert uni_token.balanceOf(t.a5) == 3*10**18
    assert chain.head_state.get_balance(t.a5) == 1*10**24
    # Starting balances of RECIPIENT
    assert uni_token.balanceOf(t.a6) == 0
    assert chain.head_state.get_balance(t.a6) == 1*10**24
    # BUYER converts ETH to UNI
    uni_token_exchange.tokens_to_eth_exact_payment(t.a6, 831943981327109037, 3*10**18, timeout, sender=t.k5)
    # Updated balances of UNI exchange
    assert chain.head_state.get_balance(uni_token_exchange.address) == 4168056018672890963
    assert uni_token.balanceOf(uni_token_exchange.address) == 12*10**18 + 1
    # Updated balances of BUYER
    assert uni_token.balanceOf(t.a5) == 1*10**18 - 1
    assert chain.head_state.get_balance(t.a5) == 1*10**24
    # Updated balances of RECIPIENT
    assert uni_token.balanceOf(t.a6) == 0
    assert chain.head_state.get_balance(t.a6) == 1*10**24 + 831943981327109037
