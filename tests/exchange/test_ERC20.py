def test_ERC20(t, omg_token, pad_bytes32):
    assert omg_token.name() == pad_bytes32('OMG Token')
    assert omg_token.symbol() == pad_bytes32('OMG')
    assert omg_token.decimals() == 18
    assert omg_token.totalSupply() == 100000*10**18
    assert omg_token.balanceOf(t.a0) == 100000*10**18
    omg_token.transfer(t.a1, 1*10**18, startgas=51875)
    assert omg_token.balanceOf(t.a0) == 100000*10**18 - 1*10**18
    assert omg_token.balanceOf(t.a1) == 1*10**18
