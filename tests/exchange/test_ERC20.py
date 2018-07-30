def pad_bytes32(instr):
    """ Pad a string \x00 bytes to return correct bytes32 representation. """
    bstr = instr.encode()
    return bstr + (32 - len(bstr)) * b'\x00'


def test_ERC20(t, uni_token):
    assert uni_token.name() == pad_bytes32('UNI Token')
    assert uni_token.symbol() == pad_bytes32('UNI')
    assert uni_token.decimals() == 18
    assert uni_token.totalSupply() == 100000*10**18
    assert uni_token.balanceOf(t.a0) == 100000*10**18
    uni_token.transfer(t.a1, 1*10**18, startgas=51875)
    assert uni_token.balanceOf(t.a0) == 100000*10**18 - 1*10**18
    assert uni_token.balanceOf(t.a1) == 1*10**18
