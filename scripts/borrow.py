from scripts.script_helper import get_account
from brownie import network, config, interface
from scripts.get_weth import get_weth
from web3 import Web3

amount = Web3.toWei(0.1, "ether")


def main():
    account = get_account
    erc20_address = config["networks"][network.show_active()]["weth_token"]
    if network.show_active in ["Mainbet-fork"]:
        get_weth(0.1)

    # Get aave lendingPool contract
    lending_pool = get_lending_pool

    # Approve sending ERC20 tokens
    erc20_approve(amount, lending_pool.address, erc20_address, account)

    # Deposit to aave
    deposit(lending_pool, erc20_address, amount, account)


def get_lending_pool():
    lending_pool_addresses_provider = interface.ILendingPoolAddressesProvider(
        config["networks"][network.show_active()]["lending_pool_addresses_provider"]
    )
    lending_pool_address = lending_pool_addresses_provider.getLendingPool()
    lending_pool = interface.ILendingPool(lending_pool_address)
    return lending_pool


def erc20_approve(amount, spender_address, erc20_address, account):
    print("Approving ERC20 Token......")
    erc20 = interface.IERC20(erc20_address)
    tx = erc20.approve(spender_address, amount, {"from": account})
    tx.wait(1)
    print("Approved ERC20 Token!")
    return tx


def deposit(_lending_pool, _erc20_address, _amount, _account):
    print(f"Depositing amount: {amount} to aave.....")
    tx = _lending_pool.deposit(
        _erc20_address, _amount, _account.address, 0, {"from": _account}
    )
    tx.wait(1)
    print(f"Amount: {amount} has been deposited successfully!")
