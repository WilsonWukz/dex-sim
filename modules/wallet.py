# modules.wallet.py
# Import Necessary Packages
from decimal import Decimal


class Wallet:
    def __init__(self, owner: str, symbol: str, amount):
        amt = Decimal(str(amount))
        self.owner = owner
        self.balances = {symbol: amt}
        self.lp_tokens = {}
        self.tr_history = []

    def balance_of(self, symbol: str) -> Decimal:
        return self.balances.get(symbol, Decimal('0'))

    def deposit(self, symbol: str, amount):
        amt = Decimal(str(amount))
        self.balances[symbol] = self.balances.get(symbol, Decimal('0')) + amt

    def withdraw(self, symbol: str, amount) -> bool:
        amt = Decimal(str(amount))
        if self.balances.get(symbol, Decimal('0')) < amt:
            print(f"Not enough {symbol} balances.")
            return False

        self.balances[symbol] -= amt
        return True

    def buy(self, symbol_pay: "USDT", symbol: str, amount, dex):
        amt = Decimal(str(amount))
        price = dex.get_price(symbol)
        cost = price * amt
        if self.balances.get(symbol_pay, Decimal('0')) < cost:
            print(f"Not enough balance of {symbol_pay} to buy {amt} of {symbol}.")
        else:
            self.balances[symbol_pay] -= cost
            self.deposit(symbol, amt)
            print(f"Buy {amt} of {symbol} successfully!")

    def sell(self, symbol: str, amount: float, dex):
        amt = Decimal(str(amount))
        price = dex.get_price(symbol)
        if self.withdraw:
            revenue = price * amt
            self.balances[symbol] += revenue
            print(f"Sold {amt} of {symbol} successfully!")

    def show_balance(self):
        print(f"The owner of this wallet is: {self.owner}")
        symbols = list(self.balances.keys())
        for s in symbols:
            print(f"{s}'s position is: {self.balances.get(s)}")