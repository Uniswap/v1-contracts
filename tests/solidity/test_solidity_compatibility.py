import os
import pytest

OWN_DIR = os.path.dirname(os.path.realpath(__file__))
RELAYER_CODE = open(os.path.join(OWN_DIR, os.pardir, os.pardir, 'contracts/solidity_compatibility/relayer.sol')).read()

@pytest.fixture
def relayer(t, chain):
    chain.mine()
    return chain.contract(RELAYER_CODE, language='solidity')

def test_relayer_eth_to_token(t, chain, utils, uni_token, uni_exchange, relayer, assert_tx_failed):
    deadline = chain.head_state.timestamp + 300
    uni_token.approve(uni_exchange.address, 10*10**18)
    uni_exchange.addLiquidity(10*10**18, deadline, value=5*10**18)
    # Set up relayer
    relayer.initialize(uni_exchange.address, uni_token.address)
    assert relayer.exchangeAddress() == uni_exchange.address
    assert utils.remove_0x_head(relayer.tokenAddress()) == uni_token.address.hex()
    # Make trade
    relayer.ethToTokenTrade(deadline, value=1*10**18)
    assert uni_token.balanceOf(relayer.address) == 1663192997082117549

def test_relayer_token_to_eth(t, chain, utils, uni_token, uni_exchange, relayer, assert_tx_failed):
    deadline = chain.head_state.timestamp + 300
    uni_token.approve(uni_exchange.address, 10*10**18)
    uni_token.transfer(relayer.address, 10*10**18)
    uni_exchange.addLiquidity(10*10**18, deadline, value=5*10**18)
    assert uni_token.balanceOf(relayer.address) == 10*10**18
    # Set up relayer
    relayer.initialize(uni_exchange.address, uni_token.address)
    assert uni_token.allowance(relayer.address, uni_exchange.address) == 100000000*10**18
    assert relayer.exchangeAddress() == uni_exchange.address
    assert utils.remove_0x_head(relayer.tokenAddress()) == uni_token.address.hex()
    # Make trade
    relayer.tokenToEthTrade(2*10**18, deadline)
    assert chain.head_state.get_balance(relayer.address) == 831596498541058775
