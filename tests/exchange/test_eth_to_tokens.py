def test_swap_eth_to_tokens_all(t, chain, check_gas, utils, uni_token, uniswap_factory, uni_token_exchange, assert_tx_failed):
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
    uni_token_exchange.swap_eth_to_tokens_all(1, timeout, value=1*10**18, startgas=63325, sender=t.k1)
    # Updated balances of UNI exchange
    assert chain.head_state.get_balance(uni_token_exchange.address) == 6*10**18
    assert uni_token.balanceOf(uni_token_exchange.address) == 8336112037345781927
    # Updated balances of BUYER
    assert uni_token.balanceOf(t.a1) == 1663887962654218073
    assert chain.head_state.get_balance(t.a1) == 1*10**24 - 1*10**18

def test_pay_eth_to_tokens_all(t, chain, utils, uni_token, uniswap_factory, uni_token_exchange, assert_tx_failed):
    uni_token.approve(uni_token_exchange.address, 10*10**18)
    uni_token_exchange.initialize(10*10**18, value=5*10**18)
    timeout = chain.head_state.timestamp + 300
    # Starting balances of UNI exchange
    assert chain.head_state.get_balance(uni_token_exchange.address) == 5*10**18
    assert uni_token.balanceOf(uni_token_exchange.address) == 10*10**18
    # Starting balances of BUYER
    assert uni_token.balanceOf(t.a2) == 0
    assert chain.head_state.get_balance(t.a2) == 1*10**24
    # Starting balances of RECIPIENT
    assert uni_token.balanceOf(t.a3) == 0
    assert chain.head_state.get_balance(t.a3) == 1*10**24
    # BUYER converts ETH to UNI
    uni_token_exchange.pay_eth_to_tokens_all(t.a3, 1, timeout, value=1*10**18, startgas=64750, sender=t.k2)
    # Updated balances of UNI exchange
    assert chain.head_state.get_balance(uni_token_exchange.address) == 6*10**18
    assert uni_token.balanceOf(uni_token_exchange.address) == 8336112037345781927
    # Updated balances of BUYER
    assert uni_token.balanceOf(t.a2) == 0
    assert chain.head_state.get_balance(t.a2) == 1*10**24 - 1*10**18
    # Updated balances of RECIPIENT
    assert uni_token.balanceOf(t.a3) == 1663887962654218073
    assert chain.head_state.get_balance(t.a3) == 1*10**24

def test_swap_eth_to_tokens_exact(t, chain, check_gas, utils, uni_token, uniswap_factory, uni_token_exchange, assert_tx_failed):
    uni_token.approve(uni_token_exchange.address, 10*10**18)
    uni_token_exchange.initialize(10*10**18, value=5*10**18)
    timeout = chain.head_state.timestamp + 300
    # Starting balances of UNI exchange
    assert chain.head_state.get_balance(uni_token_exchange.address) == 5*10**18
    assert uni_token.balanceOf(uni_token_exchange.address) == 10*10**18
    # Starting balances of BUYER
    assert uni_token.balanceOf(t.a4) == 0
    assert chain.head_state.get_balance(t.a4) == 1*10**24
    # BUYER converts ETH to UNI
    uni_token_exchange.swap_eth_to_tokens_exact(1663887962654218073, timeout, value=2*10**18, startgas=74000, sender=t.k4)
    # Updated balances of UNI exchange
    assert chain.head_state.get_balance(uni_token_exchange.address) == 6*10**18
    assert uni_token.balanceOf(uni_token_exchange.address) == 8336112037345781927
    # Updated balances of BUYER
    assert uni_token.balanceOf(t.a4) == 1663887962654218073
    assert chain.head_state.get_balance(t.a4) == 1*10**24 - 1*10**18

def test_pay_eth_to_tokens_exact(t, chain, utils, uni_token, uniswap_factory, uni_token_exchange, assert_tx_failed):
    uni_token.approve(uni_token_exchange.address, 10*10**18)
    uni_token_exchange.initialize(10*10**18, value=5*10**18)
    timeout = chain.head_state.timestamp + 300
    # Starting balances of UNI exchange
    assert chain.head_state.get_balance(uni_token_exchange.address) == 5*10**18
    assert uni_token.balanceOf(uni_token_exchange.address) == 10*10**18
    # Starting balances of BUYER
    assert uni_token.balanceOf(t.a5) == 0
    assert chain.head_state.get_balance(t.a5) == 1*10**24
    # Starting balances of RECIPIENT
    assert uni_token.balanceOf(t.a6) == 0
    assert chain.head_state.get_balance(t.a6) == 1*10**24
    # BUYER converts ETH to UNI
    uni_token_exchange.pay_eth_to_tokens_exact(t.a6, 1663887962654218073, timeout, value=2*10**18, startgas=75000, sender=t.k5)
    # Updated balances of UNI exchange
    assert chain.head_state.get_balance(uni_token_exchange.address) == 6*10**18
    assert uni_token.balanceOf(uni_token_exchange.address) == 8336112037345781927
    # Updated balances of BUYER
    assert uni_token.balanceOf(t.a5) == 0
    assert chain.head_state.get_balance(t.a5) == 1*10**24 - 1*10**18
    # Updated balances of RECIPIENT
    assert uni_token.balanceOf(t.a6) == 1663887962654218073
    assert chain.head_state.get_balance(t.a6) == 1*10**24

def test_eth_to_tokens_default(t, chain, check_gas, utils, uni_token, uniswap_factory, uni_token_exchange, assert_tx_failed):
    uni_token.approve(uni_token_exchange.address, 10*10**18)
    uni_token_exchange.initialize(10*10**18, value=5*10**18)
    timeout = chain.head_state.timestamp + 300
    # Starting balances of UNI exchange
    assert chain.head_state.get_balance(uni_token_exchange.address) == 5*10**18
    assert uni_token.balanceOf(uni_token_exchange.address) == 10*10**18
    # Starting balances of BUYER
    assert uni_token.balanceOf(t.a7) == 0
    assert chain.head_state.get_balance(t.a7) == 1*10**24
    # BUYER converts ETH to UNI
    chain.tx(to=uni_token_exchange.address, startgas=63325, value=1*10**18, sender=t.k7)
    # Updated balances of UNI exchange
    assert chain.head_state.get_balance(uni_token_exchange.address) == 6*10**18
    assert uni_token.balanceOf(uni_token_exchange.address) == 8336112037345781927
    # Updated balances of BUYER
    assert uni_token.balanceOf(t.a7) == 1663887962654218073
    assert chain.head_state.get_balance(t.a7) == 1*10**24 - 1*10**18
