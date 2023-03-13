class Manager:
    def __init__(self):
        self.accounts = []
        self.contracts = []
        self.pools = []

    def launch_bank(self):
        bank = Blockchain()
        self.contracts.append(bank)
        return bank

    def launch_account(self, bank):
        account = Account()
        bank.add_account(account)
        self.accounts.append(account)
        return account

    def launch_stablecoin_manager(self, bank):
        stablecoin_manager = StablecoinManager(bank)
        self.accounts.append(stablecoin_manager)
        return stablecoin_manager


#######################################


manager = Manager()

# launch the bank
bank = manager.launch_bank()

# launch some accounts
account1 = manager.launch_account(bank)
account2 = manager.launch_account(bank)

# launch a stablecoin manager
stablecoin_manager = manager.launch_stablecoin_manager(bank)
