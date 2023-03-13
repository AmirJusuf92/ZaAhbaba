import pytest
import contracts123

@pytest.fixture
def blockchain():
    return Blockchain()

@pytest.fixture
def accounts():
    return [
        Account("Alice", 1000),
        Account("Bob", 1000),
        Account("Charlie", 1000),
    ]

@pytest.fixture
def weth():
    return ERC20("WETH")

@pytest.fixture
def usdc():
    return ERC20("USDC")

@pytest.fixture
def uniswap_pool(weth, usdc):
    return UniswapPool(weth, usdc)

def test_trade_back_and_forth(accounts, weth, usdc, uniswap_pool):
    # Alice buys WETH with USDC
    usdc.approve(accounts[0], 100)
    uniswap_pool.swap_input(usdc, weth, 100, 0, accounts[0])
    assert accounts[0].balance_of(weth) == 100

    # Bob buys USDC with WETH
    weth.approve(accounts[1], 100)
    uniswap_pool.swap_input(weth, usdc, 100, 0, accounts[1])
    assert accounts[1].balance_of(usdc) == 100

    # Charlie buys WETH with USDC
    usdc.approve(accounts[2], 100)
    uniswap_pool.swap_input(usdc, weth, 100, 0, accounts[2])
    assert accounts[2].balance_of(weth) == 100

def test_deposit_right_ratio(accounts, weth, usdc, uniswap_pool):
    # Alice and Bob deposit in the right ratio
    weth.approve(uniswap_pool, 100)
    usdc.approve(uniswap_pool, 200)
    uniswap_pool.add_liquidity([weth, usdc], [100, 200], accounts[0])
    assert accounts[0].balance_of(uniswap_pool) == 100

def test_deposit_wrong_ratio(accounts, weth, usdc, uniswap_pool):
    # Alice and Bob try to deposit in the wrong ratio
    weth.approve(uniswap_pool, 100)
    usdc.approve(uniswap_pool, 100)
    with pytest.raises(Exception):
        uniswap_pool.add_liquidity([weth, usdc], [100, 100], accounts[0])
    assert accounts[0].balance_of(uniswap_pool) == 0
