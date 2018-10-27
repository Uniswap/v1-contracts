import os
import pytest

from web3 import Web3
from web3.contract import ConciseContract
import eth_tester
from eth_tester import EthereumTester, PyEVMBackend
from eth_tester.exceptions import TransactionFailed
from vyper import compiler

'''
run tests with:             python -m pytest -v

useful web3:                w3.eth.getTransactionReceipt(tx_hash)['status']
'''

OWN_DIR = os.path.dirname(os.path.realpath(__file__))
EXCHANGE_CODE = open(os.path.join(OWN_DIR, os.pardir, 'contracts/uniswap_exchange.vy')).read()
ERC20_CODE = open(os.path.join(OWN_DIR, os.pardir, 'contracts/ERC20.vy')).read()
FACTORY_CODE = open(os.path.join(OWN_DIR, os.pardir, 'contracts/uniswap_factory.vy')).read()

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
def exchange_abi():
    return compiler.mk_full_signature(EXCHANGE_CODE)

@pytest.fixture
def exchange_bytecode():
    return '0x' + compiler.compile(EXCHANGE_CODE).hex()

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
def omg_token(w3):
    deploy = create_contract(w3, 'contracts/ERC20.vy')
    tx_hash = deploy.constructor(b'OMG Token', b'OMG', 18, 100000*10**18).transact()
    tx_receipt = w3.eth.getTransactionReceipt(tx_hash)
    return ConciseContract(w3.eth.contract(
        address=tx_receipt.contractAddress,
        abi=deploy.abi
    ))

@pytest.fixture
def dai_token(w3):
    deploy = create_contract(w3, 'contracts/ERC20.vy')
    tx_hash = deploy.constructor(b'DAI Token', b'DAI', 18, 100000*10**18).transact()
    tx_receipt = w3.eth.getTransactionReceipt(tx_hash)
    return ConciseContract(w3.eth.contract(
        address=tx_receipt.contractAddress,
        abi=deploy.abi
    ))

@pytest.fixture
def exchange_factory(w3, exchange_template):
    deploy = create_contract(w3, 'contracts/uniswap_factory.vy')
    tx_hash = deploy.constructor().transact()
    tx_receipt = w3.eth.getTransactionReceipt(tx_hash)
    factory_contract = ConciseContract(w3.eth.contract(
        address=tx_receipt.contractAddress,
        abi=deploy.abi
    ))
    factory_contract.initializeFactory(exchange_template.address, transact={})
    return factory_contract

@pytest.fixture
def omg_exchange(w3, exchange_abi, exchange_factory, omg_token):
    exchange_factory.createExchange(omg_token.address, transact={})
    exchange_address = exchange_factory.getExchange(omg_token.address)
    return ConciseContract(w3.eth.contract(
        address=exchange_address,
        abi=exchange_abi
    ))

@pytest.fixture
def dai_exchange(w3, exchange_abi, exchange_factory, dai_token):
    exchange_factory.createExchange(dai_token.address, transact={})
    exchange_address = exchange_factory.getExchange(dai_token.address)
    return ConciseContract(w3.eth.contract(
        address=exchange_address,
        abi=exchange_abi
    ))
