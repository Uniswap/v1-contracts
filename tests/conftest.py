import os
import pytest

from ethereum.tools import tester
from ethereum import utils as ethereum_utils
from vyper import (
    compile_lll,
    optimizer,
    compiler,
)

'''
run tests with:             python -m pytest -v
'''

OWN_DIR = os.path.dirname(os.path.realpath(__file__))
EXCHANGE_CODE = open(os.path.join(OWN_DIR, os.pardir, 'contracts/uniswap_exchange.vy')).read()
ERC20_CODE = open(os.path.join(OWN_DIR, os.pardir, 'contracts/ERC20.vy')).read()
FACTORY_CODE = open(os.path.join(OWN_DIR, os.pardir, 'contracts/uniswap_factory.vy')).read()


@pytest.fixture
def t():
    tester.s = tester.Chain()
    return tester


# @pytest.fixture(scope="module")
@pytest.fixture()
def chain():
    s = tester.Chain()
    s.head_state.gas_limit = 10**9
    return s


@pytest.fixture
def utils():
    return ethereum_utils


@pytest.fixture
def get_contract(chain):
    def get_contract(source_code, *args, **kwargs):
        return chain.contract(source_code, language="vyper", *args, **kwargs)
    return get_contract


@pytest.fixture
def assert_tx_failed(t):
    def assert_tx_failed(function_to_test, exception=tester.TransactionFailed):
        initial_state = t.s.snapshot()
        with pytest.raises(exception):
            function_to_test()
        # t.s.revert(initial_state)
    return assert_tx_failed


@pytest.fixture
def get_logs():
    def get_logs(receipt, contract, event_name=None):
        contract_log_ids = contract.translator.event_data.keys()  # All the log ids contract has
        # All logs originating from contract, and matching event_name (if specified)
        logs = [log for log in receipt.logs
                if log.topics[0] in contract_log_ids and
                log.address == contract.address and
                (not event_name or
                 contract.translator.event_data[log.topics[0]]['name'] == event_name)]
        assert len(logs) > 0, "No logs in last receipt"

        # Return all events decoded in the receipt
        return [contract.translator.decode_event(log.topics, log.data) for log in logs]
    return get_logs


@pytest.fixture
def get_last_log(get_logs):
    def get_last_log(tester, contract, event_name=None):
        receipt = tester.s.head_state.receipts[-1]  # Only the receipts for the last block
        # Get last log event with correct name and return the decoded event
        print(get_logs(receipt, contract, event_name=event_name))
        return get_logs(receipt, contract, event_name=event_name)[-1]
    return get_last_log

# @pytest.fixture
# def bytes_helper():
#     def bytes_helper(str, length):
#         return bytes(str, 'utf-8') + bytearray(length - len(str))
#     return bytes_helper

@pytest.fixture
def pad_bytes32():
    def pad_bytes32(instr):
        """ Pad a string \x00 bytes to return correct bytes32 representation. """
        bstr = instr.encode()
        return bstr + (32 - len(bstr)) * b'\x00'
    return pad_bytes32

@pytest.fixture
def exchange_abi(chain):
    chain.mine()
    return tester.languages['vyper'].mk_full_signature(EXCHANGE_CODE)


@pytest.fixture
def exchange_template(chain):
    chain.mine()
    return chain.contract(EXCHANGE_CODE, language='vyper')


@pytest.fixture
def omg_token(chain):
    chain.mine()
    return chain.contract(ERC20_CODE, language='vyper', args=["OMG Token", "OMG", 18, 100000*10**18])


@pytest.fixture
def dai_token(chain):
    chain.mine()
    return chain.contract(ERC20_CODE, language='vyper', args=["DAI Token", "DAI", 18, 100000*10**18])


@pytest.fixture
def exchange_factory(chain, exchange_template, assert_tx_failed):
    chain.mine()
    factory_contract = chain.contract(FACTORY_CODE, language='vyper')
    factory_contract.initializeFactory(exchange_template.address)
    return factory_contract


@pytest.fixture
def omg_exchange(t, chain, exchange_factory, exchange_abi, omg_token):
    chain.mine()
    omg_exchange_address = exchange_factory.createExchange(omg_token.address)
    return t.ABIContract(chain, exchange_abi, omg_exchange_address)


@pytest.fixture
def dai_exchange(t, chain, exchange_factory, exchange_abi, dai_token):
    chain.mine()
    dai_exchange_address = exchange_factory.createExchange(dai_token.address)
    return t.ABIContract(chain, exchange_abi, dai_exchange_address)
