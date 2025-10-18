# modules.wallets.py
from modules.wallet import Wallet

class Wallets:
    def __init__(self):
        self.wallets = {}
    def add_wallet(self, Wallet):
        self.wallets[Wallet.owner] = Wallet
    def get_wallet(self):
        return self.wallets