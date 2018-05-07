def test_eth_to_tokens_swap(t, chain, check_gas, utils, uni_token, uniswap_factory, uni_token_exchange, assert_tx_failed):
    uni_token.approve(uni_token_exchange.address, 10*10**18)
    uni_token_exchange.initialize(10*10**18, value=5*10**18)
    timeout = chain.head_state.timestamp + 300
    # Starting balances of UNI exchange
    assert chain.head_state.get_balance(uni_token_exchange.address) == 5*10**18
    assert uni_token.balanceOf(uni_token_exchange.address) == 10*10**18
    # Starting balances of BUYER
    assert uni_token.balanceOf(t.a1) == 0
    assert chain.head_state.get_balance(t.a1) == 1*10**24
    # BUYER converts ETH to UNI
    uni_token_exchange.eth_to_tokens_swap(1, timeout, value=1*10**18, startgas=65000, sender=t.k1)
    # Updated balances of UNI exchange
    assert chain.head_state.get_balance(uni_token_exchange.address) == 6*10**18
    assert uni_token.balanceOf(uni_token_exchange.address) == 8336112037345781927
    # Updated balances of BUYER
    assert uni_token.balanceOf(t.a1) == 1663887962654218073
    assert chain.head_state.get_balance(t.a1) == 1*10**24 - 1*10**18

def test_eth_to_tokens_payment(t, chain, utils, uni_token, uniswap_factory, uni_token_exchange, assert_tx_failed):
    uni_token.approve(uni_token_exchange.address, 10*10**18)
    uni_token_exchange.initialize(10*10**18, value=5*10**18)
    timeout = chain.head_state.timestamp + 300
    # Starting balances of UNI exchange
    assert chain.head_state.get_balance(uni_token_exchange.address) == 5*10**18
    assert uni_token.balanceOf(uni_token_exchange.address) == 10*10**18
    # Starting balances of BUYER
    assert uni_token.balanceOf(t.a1) == 0
    assert chain.head_state.get_balance(t.a1) == 1*10**24 - 1*10**18
    # Starting balances of RECIPIENT
    assert uni_token.balanceOf(t.a2) == 0
    assert chain.head_state.get_balance(t.a2) == 1*10**24
    # BUYER converts ETH to UNI
    uni_token_exchange.eth_to_tokens_payment(t.a2, 1, timeout, value=1*10**18, startgas=66000, sender=t.k1)
    # Updated balances of UNI exchange
    assert chain.head_state.get_balance(uni_token_exchange.address) == 6*10**18
    assert uni_token.balanceOf(uni_token_exchange.address) == 8336112037345781927
    # Updated balances of BUYER
    assert uni_token.balanceOf(t.a1) == 0
    assert chain.head_state.get_balance(t.a1) == 1*10**24 - 2*10**18
    # Updated balances of RECIPIENT
    assert uni_token.balanceOf(t.a2) == 1663887962654218073
    assert chain.head_state.get_balance(t.a2) == 1*10**24
