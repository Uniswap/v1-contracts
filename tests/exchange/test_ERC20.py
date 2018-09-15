def test_ERC20(w3, omg_token, pad_bytes32):
    a0, a1 = w3.eth.accounts[:2]
    assert omg_token.name() == pad_bytes32('OMG Token')
    assert omg_token.symbol() == pad_bytes32('OMG')
    assert omg_token.decimals() == 18
    assert omg_token.totalSupply() == 100000*10**18
    assert omg_token.balanceOf(a0) == 100000*10**18
    omg_token.transfer(a1, 1*10**18, transact={})
    assert omg_token.balanceOf(a0) == 100000*10**18 - 1*10**18
    assert omg_token.balanceOf(a1) == 1*10**18
