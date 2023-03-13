import hashlib
import random
import string

class Account:
    def __init__(self, account_number, balance, address):
        self.account_number = account_number
        self.balance = balance
        self.address = address
        self.private_key = self.generate_private_key()
        self.nonce = 0
    
    def generate_private_key(self):
        # Generate a random 256-bit private key
        return hashlib.sha256(str(random.getrandbits(256)).encode('utf-8')).hexdigest()
    
    def deposit(self, amount):
        self.nonce += 1
        self.balance += amount
        print(f"Deposit of {amount} to account {self.account_number}, new balance: {self.balance}")
        
    def withdraw(self, amount):
        if amount > self.balance:
            print(f"Withdrawal of {amount} from account {self.account_number} failed: insufficient funds")
        else:
            self.nonce += 1
            self.balance -= amount
            print(f"Withdrawal of {amount} from account {self.account_number}, new balance: {self.balance}")
    
    def get_balance(self):
        return self.balance
    
    def get_address(self):
        return self.address
    
    def get_private_key(self):
        return self.private_key
    
    def get_nonce(self):
        return self.nonce


import hashlib

class ERC20:
    def __init__(self, name, symbol, total_supply, deployer_address):
        self.name = name
        self.symbol = symbol
        self.total_supply = total_supply
        self.deployer_address = deployer_address
        self.address = self.generate_address()
        self.balances = {}
        self.allowances = {}
    
    def generate_address(self):
        # Generate a unique address based on the deployer address and symbol
        return hashlib.sha256(f"{self.deployer_address}{self.symbol}".encode('utf-8')).hexdigest()
    
    def mint(self, account, amount):
        if account == self.deployer_address:
            self.total_supply += amount
            self.balances[account] = self.balances.get(account, 0) + amount
            print(f"Minted {amount} {self.symbol} for account {account}")
        else:
            print("Only the contract deployer can mint new tokens")
    
    def transfer(self, sender, recipient, amount):
        if self.balances.get(sender, 0) < amount:
            print(f"Transfer of {amount} {self.symbol} from {sender} to {recipient} failed: insufficient balance")
        else:
            self.balances[sender] -= amount
            self.balances[recipient] = self.balances.get(recipient, 0) + amount
            print(f"Transfer of {amount} {self.symbol} from {sender} to {recipient} successful")
    
    def approve(self, owner, spender, amount):
        if self.balances.get(owner, 0) < amount:
            print(f"Approval of {amount} {self.symbol} from {owner} to {spender} failed: insufficient balance")
        else:
            self.allowances[(owner, spender)] = amount
            print(f"Approval of {amount} {self.symbol} from {owner} to {spender} successful")
    
    def transfer_from(self, spender, sender, recipient, amount):
        if self.allowances.get((sender, spender), 0) < amount:
            print(f"Transfer of {amount} {self.symbol} from {sender} to {recipient} by {spender} failed: insufficient allowance")
        elif self.balances.get(sender, 0) < amount:
            print(f"Transfer of {amount} {self.symbol} from {sender} to {recipient} by {spender} failed: insufficient balance")
        else:
            self.allowances[(sender, spender)] -= amount
            self.balances[sender] -= amount
            self.balances[recipient] = self.balances.get(recipient, 0) + amount
            print(f"Transfer of {amount} {self.symbol} from {sender} to {recipient} by {spender} successful")
    
    def get_name(self):
        return self.name
    
    def get_symbol(self):
        self.symbol = ''.join(random.choice(string.ascii_letters+string.digits+string.punctuation) for i in range(3))
        return self.symbol
    
    def get_total_supply(self):
        return self.total_supply
    
    def get_address(self):
        return self.address
    
    def get_balance(self, account):
        return self.balances.get(account, 0)
    
    def get_allowance(self, owner, spender):
        return self.allowances.get((owner, spender), 0)







from typing import List
#from ERC20 import ERC20


class UniswapPool:
    def __init__(self, token_a: ERC20, token_b: ERC20, initial_balance_a: int, initial_balance_b: int):
        self.token_a = token_a
        self.token_b = token_b
        self.balance_a = initial_balance_a
        self.balance_b = initial_balance_b
        self.total_supply = 0
        self.shares = {}
        self.price_last = 0

    def deposit(self, amount_a: int, amount_b: int, sender_address: str):
        assert self.token_a.transfer_from(sender_address, self.address, amount_a)
        assert self.token_b.transfer_from(sender_address, self.address, amount_b)
        shares = 0
        if self.total_supply > 0:
            shares = min(
                (amount_a * self.total_supply) // self.balance_a,
                (amount_b * self.total_supply) // self.balance_b
            )
        else:
            shares = max(amount_a, amount_b)
        assert shares > 0
        self.shares[sender_address] = self.shares.get(sender_address, 0) + shares
        self.total_supply += shares
        self.balance_a += amount_a
        self.balance_b += amount_b

    def withdraw(self, amount_shares: int, sender_address: str):
        assert amount_shares > 0
        assert sender_address in self.shares
        shares = self.shares[sender_address]
        assert shares >= amount_shares
        amount_a = (amount_shares * self.balance_a) // self.total_supply
        amount_b = (amount_shares * self.balance_b) // self.total_supply
        assert self.token_a.transfer(sender_address, amount_a)
        assert self.token_b.transfer(sender_address, amount_b)
        self.shares[sender_address] = shares - amount_shares
        self.total_supply -= amount_shares
        self.balance_a -= amount_a
        self.balance_b -= amount_b

    def sell_token_a(self, amount: int, sender_address: str):
        assert amount > 0
        assert sender_address in self.shares
        assert self.balance_a > 0 and self.balance_b > 0
        shares = self.shares[sender_address]
        amount_out = 0
        if self.total_supply > 0:
            amount_out = (amount * self.balance_b) // ((amount + self.balance_a) * self.total_supply // self.balance_a)
        else:
            amount_out = self.balance_b
        assert amount_out > 0
        assert self.token_a.transfer_from(sender_address, self.address, amount)
        assert self.token_b.transfer(sender_address, amount_out)
        self.balance_a += amount
        self.balance_b -= amount_out
        self.price_last = self.balance_b * (10 ** self.token_a.decimals) // self.balance_a
        self.shares[sender_address] = shares * self.balance_a // self.total_supply

    def sell_token_b(self, amount: int, sender_address: str):
        assert amount > 0
        assert sender_address in self.shares
        assert self.balance_a > 0 and self.balance_b > 0
        shares = self.shares[sender_address]
        amount_out = 0
        if self.total_supply > 0:
            amount_out = (amount * self.balance_a) // ((amount + self.balance_b) * self.total_supply // self.balance_b)
        else:
            amount_out = self.balance_a
        assert amount_out > 0



class Blockchain:
    def __init__(self):
        self.accounts = []
        self.erc20_contracts = []
        self.pools = []
        self.eth_balance = {}  # dictionary to keep track of ETH balances of all accounts
    
    def create_account(self, address):
        account = Account(address)
        self.accounts.append(account)
        self.eth_balance[address] = 0  # initialize ETH balance of the new account to 0
        
    def mint_eth(self, address, amount):
        self.eth_balance[address] += amount
        
    def get_eth_balance(self, address):
        return self.eth_balance.get(address, 0)  # return 0 if the account doesn't exist
    
    def create_erc20(self, symbol, name, address):
        erc20 = ERC20(symbol, name, address)
        self.erc20_contracts.append(erc20)
        
    def get_erc20_contract(self, address):
        for erc20 in self.erc20_contracts:
            if erc20.address == address:
                return erc20
        return None  # return None if the contract doesn't exist
    
    def create_pool(self, token_a_address, token_b_address, pool_token_address):
        token_a_contract = self.get_erc20_contract(token_a_address)
        token_b_contract = self.get_erc20_contract(token_b_address)
        pool_token_contract = ERC20("POOL", f"{token_a_contract.symbol}-{token_b_contract.symbol} Pool Token", pool_token_address)
        pool = UniswapPool(token_a_contract, token_b_contract, pool_token_contract)
        self.pools.append(pool)
        self.erc20_contracts.append(pool_token_contract)
        
    def get_all_accounts(self):
        return self.accounts
    
    def get_account_by_address(self, address):
        for account in self.accounts:
            if account.address == address:
                return account
        return None  # return None if the account doesn't exist
    
    def get_all_contracts(self):
        return self.erc20_contracts
    
    def get_contract_by_address(self, address):
        for contract in self.erc20_contracts:
            if contract.address == address:
                return contract
        return None  # return None if the contract doesn't exist
    
    def get_all_pools(self):
        return self.pools

    

account = Account("1234", 100.0, "0x123456789abcdef")
print(f"Account balance: {account.get_balance()}")
account.deposit(50.0)
account.withdraw(25.0)
print(f"Account balance: {account.get_balance()}")
print(f"Account address: {account.get_address()}")
print(f"Account private key: {account.get_private_key()}")
print(f"Account nonce: {account.get_nonce()}")
#print(f"account symbol:{ERC20.get_symbol()}")
