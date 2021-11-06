from brownie import MockV3Aggregator, accounts, config, network

FORKED_LOCAL_ENVIRONMENTS = ["mainnet-fork-dev"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["hardhat", "development", "hardhat-local"]
HARDHAT_CHAIN_ID=31337
HARDHAT_HOST="http://127.0.0.1:8545/"
DECIMALS=8
UNIT="ether"
STARTING_PRICE=4477.85*10**8

def get_account():
    """return account based on chain"""
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS or network.show_active() in FORKED_LOCAL_ENVIRONMENTS:
        return accounts[0]
    accounts.add(config["wallets"]["from_key"])
    return accounts[0]

def get_eth_price_feed_address():
    """returns price feed address based on chain, deploys mock if
    on local chain"""
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS or network.show_active() in FORKED_LOCAL_ENVIRONMENTS:
        return config["networks"][network.show_active()]["eth_usd_price_feed_address"]
    else:
        return deploy_mock_v3_aggregator()

def deploy_mock_v3_aggregator():
    """deploys MockV3Aggregator contract"""
    print(f"Active network is {network.show_active()}")
    if len(MockV3Aggregator) > 0:
        return MockV3Aggregator[-1].address
    print("Deploying MockV3Aggregator")
    mock_v3_aggregator = MockV3Aggregator.deploy(DECIMALS, STARTING_PRICE, {"from": get_account()})
    print("Deployed MockV3Aggregator")
    return mock_v3_aggregator.address

def to_wei(amount, unit):
    conversion_dictionary = {
        "ether": amount*10**18,
        "gwei": amount*10*9
    }
    return conversion_dictionary.get(unit)
