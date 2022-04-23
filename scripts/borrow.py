from scripts.script_helper import get_account
from brownie import network, config, interface
from scripts.get_weth import get_weth
from web3 import Web3

amount = Web3.toWei(0.1, "ether")


def main():
    account = get_account()
    erc20_address = config["networks"][network.show_active()]["weth_token"]
    dai_eth_price_address = config["networks"][network.show_active()][
        "dai_eth_price_feed"
    ]
    if network.show_active() in ["mainnet-fork"]:
        get_weth(amount)

    # Get aave lendingPool contract
    lending_pool = get_lending_pool()

    # Approve sending ERC20 tokens
    erc20_approve(amount, lending_pool.address, erc20_address, account)

    # Deposit to aave
    deposit(lending_pool, erc20_address, amount, account)

    # retrive account data from aave and get borrowable ETH amount.
    borrowable_eth, total_debt = get_borrowable_data(lending_pool, account)

    print("lets borrow some DAI!")

    dai_eth_price = get_asset_price(dai_eth_price_address)

    # Now lets calculate how much DAI we can borrow considering liquidation threshold
    #  borrowable_eth -> borrowable_dai * 95%

    amount_dai_to_borrow = (1 / dai_eth_price) * (borrowable_eth * 0.95)
    print(f"We are going to borrow {amount_dai_to_borrow} DAI")
    borrow_dai(
        lending_pool, Web3.toWei(amount_dai_to_borrow, "ether"), 1, account.address
    )
    get_borrowable_data()
    print("Repaying all....")
    repay_all(amount, lending_pool, account, dai_eth_price_address, 1)


def borrow_dai(_lending_pool, _amount, _interest_rate, _account):
    dai_address = config["networks"][network.show_active()]["dai_token_address"]
    tx = _lending_pool.borrow(
        dai_address, _amount, _interest_rate, _account.address, {"from": _account}
    )
    tx.wait(1)
    print("Operation borrow DAI successful!")


def repay_all(_amount, _lending_pool, _account, _dai_token_address, _interest):
    erc20_approve(
        Web3.toWei(_amount, "ether"),
        _lending_pool,
        _dai_token_address,
        {"from": _account},
    )

    repay_tx = _lending_pool.repay(
        _dai_token_address, _amount, _interest, {"from": _account}
    )
    repay_tx.wait(1)
    print("Repayed!")


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


def get_asset_price(price_feed_address):
    dai_eth_price_feed = interface.IAggregatorV3(price_feed_address)
    latest_price = dai_eth_price_feed.latestRoundData()[1]
    wei_price = Web3.fromWei(latest_price, "ether")
    print(f"The DAI -> ETH price is {wei_price}")
    return float(wei_price)


def get_borrowable_data(lending_pool, account):
    (
        total_colleteral_eth,
        total_debt_eth,
        available_borrow_eth,
        current_liquidation_threshold,
        loan_to_value,
        health_factor,
    ) = lending_pool.getUserAccountData(account.address)
    # convert WEI -> ETH
    available_borrow_eth = Web3.fromWei(available_borrow_eth, "ether")
    total_colleteral_eth = Web3.fromWei(total_colleteral_eth, "ether")
    total_debt_eth = Web3.fromWei(total_debt_eth, "ether")

    # Print values
    print(f"you have {total_colleteral_eth} worth of ETH deposited.")
    print(f"you have {total_debt_eth} worth of ETH borrowed.")
    print(f"you can borrow {available_borrow_eth} worth of ETH.")

    return (float(available_borrow_eth), float(total_debt_eth))
