def test_tokens_to_eth_swap(t, chain, utils, uni_token, uniswap_factory, uni_token_exchange, assert_tx_failed):
    uni_token.transfer(t.a1, 2*10**18)
    uni_token.approve(uni_token_exchange.address, 10*10**18)
    uni_token.approve(uni_token_exchange.address, 2*10**18, sender=t.k1)
    uni_token_exchange.initiate(10*10**18, value=5*10**18)
    # Starting balances of UNI exchange
    assert uni_token_exchange.eth_pool() == 5*10**18
    assert uni_token_exchange.token_pool() == 10*10**18
    assert uni_token_exchange.invariant() == 50000000000000000000000000000000000000
    # Starting balances of BUYER
    assert uni_token.balanceOf(t.a1) == 2*10**18
    assert chain.head_state.get_balance(t.a1) == 1*10**24
    # BUYER converts ETH to UNI
    uni_token_exchange.tokens_to_eth_swap(2*10**18, 1, sender=t.k1)
    # Updated balances of UNI exchange
    assert uni_token_exchange.eth_pool() == 4168056018672890963
    assert uni_token_exchange.token_pool() == 12*10**18
    assert uni_token_exchange.invariant() == 50016672224074691556000000000000000000
    # Updated balances of BUYER
    assert uni_token.balanceOf(t.a1) == 0
    assert chain.head_state.get_balance(t.a1) == 1*10**24 + 831943981327109037

def test_tokens_to_eth_payment(t, chain, utils, uni_token, uniswap_factory, uni_token_exchange, assert_tx_failed):
    uni_token.transfer(t.a1, 2*10**18)
    uni_token.approve(uni_token_exchange.address, 10*10**18)
    uni_token.approve(uni_token_exchange.address, 2*10**18, sender=t.k1)
    uni_token_exchange.initiate(10*10**18, value=5*10**18)
    # Starting balances of UNI exchange
    assert uni_token_exchange.eth_pool() == 5*10**18
    assert uni_token_exchange.token_pool() == 10*10**18
    assert uni_token_exchange.invariant() == 50000000000000000000000000000000000000
    # Starting balances of BUYER
    assert uni_token.balanceOf(t.a1) == 2*10**18
    assert chain.head_state.get_balance(t.a1) == 1*10**24 + 831943981327109037
    # Starting balances of RECIPIENT
    assert uni_token.balanceOf(t.a2) == 0
    assert chain.head_state.get_balance(t.a2) == 1*10**24
    # BUYER converts ETH to UNI
    uni_token_exchange.tokens_to_eth_payment(t.a2, 2*10**18, 1, sender=t.k1)
    # Updated balances of UNI exchange
    assert uni_token_exchange.eth_pool() == 4168056018672890963
    assert uni_token_exchange.token_pool() == 12*10**18
    assert uni_token_exchange.invariant() == 50016672224074691556000000000000000000
    # Updated balances of BUYER
    assert uni_token.balanceOf(t.a1) == 0
    assert chain.head_state.get_balance(t.a1) == 1*10**24 + 831943981327109037
    # Updated balances of RECIPIENT
    assert uni_token.balanceOf(t.a2) == 0
    assert chain.head_state.get_balance(t.a2) == 1*10**24 + 831943981327109037
