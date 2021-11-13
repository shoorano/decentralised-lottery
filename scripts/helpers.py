from brownie import (
    MockV3Aggregator,
    VRFCoordinatorMock,
    LinkToken,
    interface,
    accounts,
    config,
    network,
    Contract
)

FORKED_LOCAL_ENVIRONMENTS = ["mainnet-fork-dev"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["hardhat", "development", "hardhat-local"]
HARDHAT_CHAIN_ID=31337
HARDHAT_HOST="http://127.0.0.1:8545/"
DECIMALS=8
UNIT="ether"
INITIAL_AMOUNT=4477.85*10**8
STATIC_RNG = 777
CONTRACT_TO_MOCK = {
    "eth_usd_price_feed": MockV3Aggregator,
    "vrf_coordinator": VRFCoordinatorMock,
    "link_token": LinkToken,
}

def get_account(index=None, id=None):
    """return account based on chain:
    - index identifies a different account from local / mainnet-fork accounts
    - id identifies accounts stored within brownie for testnet and mainnet usage
    """
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    if (
        network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS
        or network.show_active() in FORKED_LOCAL_ENVIRONMENTS
    ):
        return accounts[0]
    return accounts.add(config["wallets"]["from_key"])

def get_brownie_config_variable(variable):
    """returns brownie config variable based on network running, deploys mock if
    on local chain"""
    return config["networks"][network.show_active()][variable]
    

def get_contract(contract_name):
    """This function will grab the contract addresses from the brownie config
    if defined, otherwise, it will deploy a mock version of that contract, and
    return that mock contract.
    
        Args:
            contract_name (string)
        
        Returns:
            brownie.network.contract.ProjectContract: The most recently deployed
            version of this contract.
    """
    contract_type = CONTRACT_TO_MOCK[contract_name]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        if len(contract_type) <= 0:
            deploy_mocks()
        return contract_type[-1]
    contract_address = config["networks"][network.show_active()][contract_name]
    return Contract.from_abi(
        contract_type._name,
        contract_address,
        contract_type.abi
    )

def deploy_mocks(decimals=DECIMALS, initial_amount=INITIAL_AMOUNT):
    """deploys MockV3Aggregator contract"""
    print(f"Active network is {network.show_active()}")
    print("Deploying mocks")
    account = get_account()
    MockV3Aggregator.deploy(decimals, initial_amount, {"from": account})
    link_token = LinkToken.deploy({"from": account})
    VRFCoordinatorMock.deploy(link_token.address, {"from": account})
    print("Deployed mocks")

def fund_with_link(contract_address, account=None, link_token=None, amount=10000000000000000000): # 0.1 link
    """funds address with link token"""
    account = account if account else get_account()
    link_token = link_token if link_token else get_contract("link_token")
    # Can be used this way if contract does not give access to all methods
    # Also skips the step of grabbing abi and compiling as brownie automates this
    # link_token_contract = interface.LinkTokenInterface(link_token.address)
    tx = link_token.transfer(contract_address, amount, {"from": account})
    tx.wait(1)
    print("Funded contract with Link")

def to_wei(amount, unit):
    conversion_dictionary = {
        "ether": amount*10**18,
        "gwei": amount*10*9
    }
    return conversion_dictionary.get(unit)
