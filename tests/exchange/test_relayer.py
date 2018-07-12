import os
import pytest

OWN_DIR = os.path.dirname(os.path.realpath(__file__))
RELAYER_CODE = open(os.path.join(OWN_DIR, os.pardir, os.pardir, 'contracts/relayer.v.py')).read()

@pytest.fixture
def relayer(t, chain):
    chain.mine()
    return chain.contract(RELAYER_CODE, language='vyper')

def test_relayer_token_to_token(t, chain, utils, uni_token, swap_token, exchange_factory, uni_exchange, swap_exchange, relayer, assert_tx_failed):
    timeout = chain.head_state.timestamp + 300
    # Set up relayer
    relayer.initialize(exchange_factory.address)
    assert utils.remove_0x_head(relayer.factory()) == exchange_factory.address.hex()
    relayer.add_exchange(uni_token.address)
    relayer.add_exchange(swap_token.address)
    relayer.approve_exchange(uni_token.address, 1000*10**18)
    relayer.approve_exchange(swap_token.address, 1000*10**18)
    uni_token.approve(relayer.address, 3*10**18, sender=t.k1)
    # initialize exchanges
    uni_token.transfer(t.a1, 3*10**18)
    uni_token.approve(uni_exchange.address, 10*10**18)
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
    # BUYER converts UNI to SWAP
    relayer.tokenToTokenSwap(uni_token.address, swap_token.address, 2*10**18, 1, timeout, startgas=153000, sender=t.k1)
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

def test_relayer_exchange_to_exchange(t, chain, utils, uni_token, swap_token, exchange_factory, uni_exchange, swap_exchange, relayer, assert_tx_failed):
    timeout = chain.head_state.timestamp + 300
    # Set up relayer
    relayer.initialize(exchange_factory.address)
    assert utils.remove_0x_head(relayer.factory()) == exchange_factory.address.hex()
    relayer.add_exchange(uni_token.address)
    relayer.add_exchange(swap_token.address)
    relayer.approve_exchange(uni_token.address, 1000*10**18)
    relayer.approve_exchange(swap_token.address, 1000*10**18)
    uni_token.approve(relayer.address, 3*10**18, sender=t.k1)
    # initialize exchanges
    uni_token.transfer(t.a1, 3*10**18)
    uni_token.approve(uni_exchange.address, 10*10**18)
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
    # BUYER converts UNI to SWAP
    relayer.tokenToExchangeSwap(uni_token.address, swap_exchange.address, 2*10**18, 1, timeout, sender=t.k1)
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
