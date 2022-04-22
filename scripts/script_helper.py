from brownie import accounts, network, config

LOCAL_BLOCKCHAIN_ENV = ["development", "ganache-local", "mainnet-fork"]


def get_account(index=None, id=None):
    """
    This function will return the account based on the given args or network status.
    """
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    if network.show_active() in LOCAL_BLOCKCHAIN_ENV:
        return accounts[0]

    return accounts.add(config["wallets"]["from_key"])
