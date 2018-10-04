from web3.contract import (
    ConciseContract,
    ConciseMethod
)

class VyperMethod(ConciseMethod):
    ALLOWED_MODIFIERS = {'call', 'estimateGas', 'transact', 'buildTransaction'}

    def __call__(self, *args, **kwargs):
        return self.__prepared_function(*args, **kwargs)

    def __prepared_function(self, *args, **kwargs):
        if not kwargs:
            modifier, modifier_dict = 'call', {}
            fn_abi = [x for x in self._function.contract_abi if x['name'] == self._function.function_identifier].pop()
            modifier_dict.update({'gas': fn_abi.get('gas', 0) + 50000})  # To make tests faster just supply some high gas value.
        elif len(kwargs) == 1:
            modifier, modifier_dict = kwargs.popitem()
            if modifier not in self.ALLOWED_MODIFIERS:
                raise TypeError(
                    "The only allowed keyword arguments are: %s" % self.ALLOWED_MODIFIERS)
        else:
            raise TypeError("Use up to one keyword argument, one of: %s" % self.ALLOWED_MODIFIERS)

        return getattr(self._function(*args), modifier)(modifier_dict)


class VyperContract(ConciseContract):

    def __init__(self, classic_contract, method_class=VyperMethod):
        super().__init__(classic_contract, method_class)

def test_factory(w3, exchange_template, omg_token, exchange_factory, pad_bytes32, assert_tx_failed, exchange_bytecode, exchange_abi):
    a0, a1 = w3.eth.accounts[:2]
    # Factory initial state
    assert exchange_factory.exchangeTemplate() == exchange_template.address
    assert exchange_factory.getExchange(omg_token.address) == None
    # Create Exchange for UNI Token
    exchange_factory.createExchange(omg_token.address, transact={})
    omg_exchange_address = exchange_factory.getExchange(omg_token.address)
    assert omg_exchange_address != None
    omg_exchange = w3.eth.contract(omg_exchange_address, abi=exchange_abi, bytecode=exchange_bytecode, ContractFactoryClass=VyperContract)
    assert exchange_factory.getToken(omg_exchange.address) == omg_token.address
    assert exchange_factory.tokenCount() == 1
    assert exchange_factory.getTokenWithId(1) == omg_token.address
    # # Can't call initializeFactory on factory twice
    # assert_tx_failed(lambda: exchange_factory.initializeFactory(omg_token.address))
    # # Exchange already exists
    # assert_tx_failed(lambda: exchange_factory.createExchange(omg_token.address))
    # # Can't call setup on exchange
    # assert_tx_failed(lambda: omg_exchange.setup(exchange_factory.address))
    # # Exchange initial state
    assert omg_exchange.name() == pad_bytes32('Uniswap V1')
    assert omg_exchange.symbol() == pad_bytes32('UNI-V1')
    assert omg_exchange.decimals() == 18
    assert omg_exchange.totalSupply() == 0
    assert omg_exchange.tokenAddress() == omg_token.address
    assert omg_exchange.factoryAddress() == exchange_factory.address
    assert w3.eth.getBalance(omg_exchange.address) == 0
    assert omg_token.balanceOf(omg_exchange.address) == 0
