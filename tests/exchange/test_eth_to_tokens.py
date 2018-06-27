def test_eth_to_tokens_default(t, chain, utils, uni_token, exchange_factory, uni_exchange, assert_tx_failed):
    timeout = chain.head_state.timestamp + 300
    uni_token.approve(uni_exchange.address, 10*10**18)
    uni_exchange.initialize(10*10**18, value=5*10**18)
    # Starting balances of UNI exchange
    assert chain.head_state.get_balance(uni_exchange.address) == 5*10**18
    assert uni_token.balanceOf(uni_exchange.address) == 10*10**18
    # Starting balances of BUYER
    assert uni_token.balanceOf(t.a1) == 0
    assert chain.head_state.get_balance(t.a1) == 1*10**24
    # BUYER converts ETH to UNI
    chain.tx(to=uni_exchange.address, startgas=63450, value=1*10**18, sender=t.k1)
    # Updated balances of UNI exchange
    assert chain.head_state.get_balance(uni_exchange.address) == 6*10**18
    assert uni_token.balanceOf(uni_exchange.address) == 8336112037345781927
    # Updated balances of BUYER
    assert uni_token.balanceOf(t.a1) == 1663887962654218073
    assert chain.head_state.get_balance(t.a1) == 1*10**24 - 1*10**18

def test_swap_eth_to_tokens_all(t, chain, utils, uni_token, exchange_factory, uni_exchange, assert_tx_failed):
    timeout = chain.head_state.timestamp + 300
    uni_token.approve(uni_exchange.address, 10*10**18)
    uni_exchange.initialize(10*10**18, value=5*10**18)
    # Starting balances of UNI exchange
    assert chain.head_state.get_balance(uni_exchange.address) == 5*10**18
    assert uni_token.balanceOf(uni_exchange.address) == 10*10**18
    # Starting balances of BUYER
    assert uni_token.balanceOf(t.a1) == 0
    assert chain.head_state.get_balance(t.a1) == 1*10**24
    # BUYER converts ETH to UNI
    # uni_exchange.swap_eth_to_tokens_all(1, timeout, value=1*10**18, startgas=63081, sender=t.k1)
    uni_exchange.swap_eth_to_tokens(1, timeout, False, value=1*10**18, startgas=63381, sender=t.k1)
    # Updated balances of UNI exchange
    assert chain.head_state.get_balance(uni_exchange.address) == 6*10**18
    assert uni_token.balanceOf(uni_exchange.address) == 8336112037345781927
    # Updated balances of BUYER
    assert uni_token.balanceOf(t.a1) == 1663887962654218073
    assert chain.head_state.get_balance(t.a1) == 1*10**24 - 1*10**18

def test_pay_eth_to_tokens_all(t, chain, utils, uni_token, exchange_factory, uni_exchange, assert_tx_failed):
    timeout = chain.head_state.timestamp + 300
    uni_token.approve(uni_exchange.address, 10*10**18)
    uni_exchange.initialize(10*10**18, value=5*10**18)
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
    uni_exchange.pay_eth_to_tokens(t.a2, 1, timeout, False, value=1*10**18, startgas=65750, sender=t.k1)
    # Updated balances of UNI exchange
    assert chain.head_state.get_balance(uni_exchange.address) == 6*10**18
    assert uni_token.balanceOf(uni_exchange.address) == 8336112037345781927
    # Updated balances of BUYER
    assert uni_token.balanceOf(t.a1) == 0
    assert chain.head_state.get_balance(t.a1) == 1*10**24 - 1*10**18
    # Updated balances of RECIPIENT
    assert uni_token.balanceOf(t.a2) == 1663887962654218073
    assert chain.head_state.get_balance(t.a2) == 1*10**24

def test_swap_eth_to_tokens_exact(t, chain, utils, uni_token, exchange_factory, uni_exchange, assert_tx_failed):
    timeout = chain.head_state.timestamp + 300
    uni_token.approve(uni_exchange.address, 10*10**18)
    uni_exchange.initialize(10*10**18, value=5*10**18)
    # Starting balances of UNI exchange
    assert chain.head_state.get_balance(uni_exchange.address) == 5*10**18
    assert uni_token.balanceOf(uni_exchange.address) == 10*10**18
    # Starting balances of BUYER
    assert uni_token.balanceOf(t.a1) == 0
    assert chain.head_state.get_balance(t.a1) == 1*10**24
    # BUYER converts ETH to UNI
    uni_exchange.swap_eth_to_tokens(1663887962654218073, timeout, True, value=2*10**18, startgas=74000, sender=t.k1)
    # Updated balances of UNI exchange
    assert chain.head_state.get_balance(uni_exchange.address) == 6*10**18
    assert uni_token.balanceOf(uni_exchange.address) == 8336112037345781927
    # Updated balances of BUYER
    assert uni_token.balanceOf(t.a1) == 1663887962654218073
    assert chain.head_state.get_balance(t.a1) == 1*10**24 - 1*10**18

def test_pay_eth_to_tokens_exact(t, chain, utils, uni_token, exchange_factory, uni_exchange, assert_tx_failed):
    timeout = chain.head_state.timestamp + 300
    uni_token.approve(uni_exchange.address, 10*10**18)
    uni_exchange.initialize(10*10**18, value=5*10**18)
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
    uni_exchange.pay_eth_to_tokens(t.a2, 1663887962654218073, timeout, True, value=2*10**18, startgas=75000, sender=t.k1)
    # Updated balances of UNI exchange
    assert chain.head_state.get_balance(uni_exchange.address) == 6*10**18
    assert uni_token.balanceOf(uni_exchange.address) == 8336112037345781927
    # Updated balances of BUYER
    assert uni_token.balanceOf(t.a1) == 0
    assert chain.head_state.get_balance(t.a1) == 1*10**24 - 1*10**18
    # Updated balances of RECIPIENT
    assert uni_token.balanceOf(t.a2) == 1663887962654218073
    assert chain.head_state.get_balance(t.a2) == 1*10**24
