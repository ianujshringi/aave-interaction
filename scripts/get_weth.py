from scripts.script_helper import get_account
from brownie import interface, config, network


def main():
    get_weth


def get_weth(eth):
    """
    This function mints WETH by depositing ETH.
    """
    # Get an account
    account = get_account()
    weth = interface.IWETH(config["networks"][network.show_active()]["weth_token"])
    tx = weth.deposit({"from": account, "value": eth * 10**18})
    tx.wait(1)
    print("Recieved {eth}} WETH")
