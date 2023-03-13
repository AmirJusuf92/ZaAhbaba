import pytest
import contracts_extended123
def test_create_stablecoin_and_vaults():
    # Create bank and blockchain objects
    bank = Bank()
    blockchain = Blockchain()

    # Create WETH and USDC ERC20 tokens
    WETH = ERC20("WETH", "WETH")
    USDC = ERC20("USDC", "USDC")

    # Create stablecoin and vaults
    stablecoin = Stablecoin("STC", "STC", bank, blockchain)
    vault1 = Vault(bank, stablecoin, WETH, USDC)
    vault2 = Vault(bank, stablecoin, WETH, USDC)

    # Verify that stablecoin and vaults were created successfully
    assert stablecoin.symbol == "STC"
    assert stablecoin.name == "STC"
    assert len(stablecoin.vaults) == 2
    assert stablecoin.vaults[0] == vault1
    assert stablecoin.vaults[1] == vault2

    assert vault1.stablecoin == stablecoin
    assert vault1.collateral_token == WETH
    assert vault1.borrowed_token == USDC

    assert vault2.stablecoin == stablecoin
    assert vault2.collateral_token == WETH
    assert vault2.borrowed_token == USDC

    assert bank.get_balance(vault1) == 0
    assert bank.get_balance(vault2) == 0

    assert WETH.balanceOf(vault1) == 0
    assert WETH.balanceOf(vault2) == 0

    assert USDC.balanceOf(vault1) == 0
    assert USDC.balanceOf(vault2) == 0

def test_environment():
    bank = Bank()
    weth = ERC20('WETH')
    usdc = ERC20('USDC')
    chef = StablecoinChef(bank, weth, usdc)
    liquidator = Liquidator(bank, weth, usdc)
    return {'bank': bank, 'weth': weth, 'usdc': usdc, 'chef': chef, 'liquidator': liquidator}

# test regular users can mint stablecoins
def test_mint_stablecoin(test_environment):
    chef = test_environment['chef']
    chef.mint_stablecoin(1000)
    assert chef.stablecoin_balance == 1000

# test users can use stablecoins to buy Ethereum with leverage
def test_buy_ethereum(test_environment):
    chef = test_environment['chef']
    chef.mint_stablecoin(1000)
    chef.buy_ethereum(500, 2)
    assert chef.ethereum_balance == 1000
    assert chef.stablecoin_balance == 500

# test liquidation of bad vaults
def test_liquidation(test_environment):
    chef = test_environment['chef']
    liquidator = test_environment['liquidator']
    chef.mint_stablecoin(1000)
    chef.buy_ethereum(500, 2)
    chef.create_vault(500, 1000)
    # sell a lot of Ethereum to cause the price to drop
    chef.sell_ethereum(500)
    # check that the bad vault was liquidated
    assert chef.ethereum_balance == 500
    assert chef.stablecoin_balance == 1000
    assert chef.vaults == []
    assert liquidator.liquidated_vaults == [Vault(500, 1000)]

# test invalid operations
def test_invalid_operations(test_environment):
    chef = test_environment['chef']
    # deposit in wrong ratio
    with pytest.raises(ValueError):
        chef.create_vault(500, 800)
    # trade more than what is available
    with pytest.raises(ValueError):
        chef.buy_ethereum(500, 3)
    # test stablecoin functions
    chef.mint_stablecoin(1000)
    chef.burn_stablecoin(500)
    assert chef.stablecoin_balance == 500
    # test liquidation functions
    liquidator = test_environment['liquidator']
    liquidator.liquidate_vault(Vault(500, 1000))
    assert liquidator.liquidated_vaults == [Vault(500, 1000)]
