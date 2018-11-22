import os
import pytest
from pytest import raises

from web3 import Web3
from web3.contract import ConciseContract
import eth_tester
from eth_tester import EthereumTester, PyEVMBackend
from eth_tester.exceptions import TransactionFailed
from vyper import compiler

from tests.constants import (
    ETH_RESERVE,
    HAY_RESERVE,
    DEN_RESERVE,
    DEADLINE,
)

'''
# run tests with:             python -m pytest -v
'''

setattr(eth_tester.backends.pyevm.main, 'GENESIS_GAS_LIMIT', 10**9)
setattr(eth_tester.backends.pyevm.main, 'GENESIS_DIFFICULTY', 1)

@pytest.fixture
def tester():
    return EthereumTester(backend=PyEVMBackend())

@pytest.fixture
def w3(tester):
    w3 = Web3(Web3.EthereumTesterProvider(tester))
    w3.eth.setGasPriceStrategy(lambda web3, params: 0)
    w3.eth.defaultAccount = w3.eth.accounts[0]
    return w3

@pytest.fixture
def pad_bytes32():
    def pad_bytes32(instr):
        """ Pad a string \x00 bytes to return correct bytes32 representation. """
        bstr = instr.encode()
        return bstr + (32 - len(bstr)) * b'\x00'
    return pad_bytes32

# @pytest.fixture
def create_contract(w3, path):
    wd = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(wd, os.pardir, path)) as f:
        source = f.read()
    bytecode = '0x' + compiler.compile(source).hex()
    abi = compiler.mk_full_signature(source)
    return w3.eth.contract(abi=abi, bytecode=bytecode)

@pytest.fixture
def exchange_template(w3):
    deploy = create_contract(w3, 'contracts/uniswap_exchange.vy')
    tx_hash = deploy.constructor().transact()
    tx_receipt = w3.eth.getTransactionReceipt(tx_hash)
    return ConciseContract(w3.eth.contract(
        address=tx_receipt.contractAddress,
        abi=deploy.abi
    ))

@pytest.fixture
def HAY_token(w3):
    deploy = create_contract(w3, 'contracts/test_contracts/ERC20.vy')
    tx_hash = deploy.constructor(b'HAY Token', b'HAY', 18, 100000*10**18).transact()
    tx_receipt = w3.eth.getTransactionReceipt(tx_hash)
    return ConciseContract(w3.eth.contract(
        address=tx_receipt.contractAddress,
        abi=deploy.abi
    ))

@pytest.fixture
def DEN_token(w3):
    deploy = create_contract(w3, 'contracts/test_contracts/ERC20.vy')
    tx_hash = deploy.constructor(b'DEN Token', b'DEN', 18, 100000*10**18).transact()
    tx_receipt = w3.eth.getTransactionReceipt(tx_hash)
    return ConciseContract(w3.eth.contract(
        address=tx_receipt.contractAddress,
        abi=deploy.abi
    ))

@pytest.fixture
def factory(w3, exchange_template):
    deploy = create_contract(w3, 'contracts/uniswap_factory.vy')
    tx_hash = deploy.constructor().transact()
    tx_receipt = w3.eth.getTransactionReceipt(tx_hash)
    contract = ConciseContract(w3.eth.contract(
        address=tx_receipt.contractAddress,
        abi=deploy.abi
    ))
    contract.initializeFactory(exchange_template.address, transact={})
    return contract

@pytest.fixture
def exchange_abi():
    wd = os.path.dirname(os.path.realpath(__file__))
    code = open(os.path.join(wd, os.pardir, 'contracts/uniswap_exchange.vy')).read()
    return compiler.mk_full_signature(code)

@pytest.fixture
def HAY_exchange(w3, exchange_abi, factory, HAY_token):
    factory.createExchange(HAY_token.address, transact={})
    exchange_address = factory.getExchange(HAY_token.address)
    exchange = ConciseContract(w3.eth.contract(
        address=exchange_address,
        abi=exchange_abi
    ))
    HAY_token.approve(exchange_address, HAY_RESERVE, transact={})
    exchange.addLiquidity(0, HAY_RESERVE, DEADLINE, transact={'value': ETH_RESERVE})
    return exchange

@pytest.fixture
def DEN_exchange(w3, exchange_abi, factory, DEN_token):
    factory.createExchange(DEN_token.address, transact={})
    exchange_address = factory.getExchange(DEN_token.address)
    exchange = ConciseContract(w3.eth.contract(
        address=exchange_address,
        abi=exchange_abi
    ))
    DEN_token.approve(exchange_address, DEN_RESERVE, transact={})
    exchange.addLiquidity(0, DEN_RESERVE, DEADLINE, transact={'value': ETH_RESERVE})
    return exchange


@pytest.fixture
def swap_input():
    def swap_input(input_amount, input_reserve, output_reserve):
        input_amount_with_fee = input_amount * 997
        numerator = input_amount_with_fee * output_reserve
        denominator = input_reserve * 1000 + input_amount_with_fee
        return numerator // denominator
    return swap_input

@pytest.fixture
def swap_output():
    def swap_output(output_amount, input_reserve, output_reserve):
        numerator = input_reserve * output_amount * 1000
        denominator = (output_reserve - output_amount) * 997
        return numerator // denominator + 1
    return swap_output

@pytest.fixture
def assert_fail():
    def assert_fail(func):
        with raises(Exception):
            func()
    return assert_fail
