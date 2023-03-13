class Account:
    def __init__(self, address, private_key):
        self.address = address
        self.private_key = private_key
        self.nonce = 0
        self.balance = 0
        
    def increase_nonce(self):
        self.nonce += 1
        
    def transfer(self, recipient, amount):
        # check if sender has enough balance
        if self.balance < amount:
            raise Exception("Insufficient balance")
        
        # deduct amount from sender balance and increase nonce
        self.balance -= amount
        self.increase_nonce()
        
        # add amount to recipient balance and increase nonce
        recipient.balance += amount
        recipient.increase_nonce()

class ERC20:
    def __init__(self, name, symbol, total_supply, deployer_address):
        self.name = name
        self.symbol = symbol
        self.total_supply = total_supply
        self.deployer_address = deployer_address
        self.balances = {deployer_address: total_supply}
        
    def get_balance(self, address):
        if address in self.balances:
            return self.balances[address]
        return 0
        
    def mint(self, recipient, amount):
        # check if deployer can mint
        if recipient.address != self.deployer_address:
            raise Exception("Not authorized to mint")
            
        # increase recipient balance and total supply
        self.balances[recipient.address] = self.get_balance(recipient.address) + amount
        self.total_supply += amount
        
class WETH(ERC20):
    def __init__(self, name, symbol, total_supply, deployer_address):
        super().__init__(name, symbol, total_supply, deployer_address)
        
    def deposit(self, account, amount):
        # convert ETH to WETH
        account.transfer(self, amount)
        self.mint(account, amount)
        
    def withdraw(self, account, amount):
        # convert WETH to ETH
        if self.get_balance(account.address) < amount:
            raise Exception("Insufficient WETH balance")
            
        account.transfer(self, amount)
        self.balances[account.address] -= amount
        self.total_supply -= amount

class UniswapPool:
    def __init__(self, token_a, token_b, balance_a, balance_b):
        self.token_a = token_a
        self.token_b = token_b
        self.balance_a = balance_a
        self.balance_b = balance_b
        self.share_tokens = ERC20("Uniswap Pool Shares", "UPS", 0, None)
        self.share_balances = {}
        
    def get_price(self):
        return self.balance_b / self.balance_a
        
    def sell_token_a(self, account, amount):
        # check if pool has enough token A
        if self.balance_a < amount:
            raise Exception("Insufficient token A balance in pool")
            
        # calculate amount of token B to give to account
        price = self.get_price()
        amount_b = amount * price
        
        # transfer token A from account to pool and increase balances
        account.transfer(self.token_a, amount)
        self.balance_a += amount
        
        # transfer token B from pool to account and decrease balances
        self.token_b.transfer(account, amount_b)
        self.balance_b -= amount_b
        
        # transfer pool shares to account
        share_amount = self.share_tokens.get_balance(account.address)
        self.share_tokens.balances[account.address] = share_amount + amount
        
    def sell_token_b(self, account, amount):
        # check if pool has enough token
