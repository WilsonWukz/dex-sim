# modules.LiquitityPool.py
# Import Necessary Packages
from decimal import Decimal


class LiquitityPool:
    def __init__(self, tokenA: str, tokenB: str, reserve_a, reserve_b, fee=3e-3):
        self.tokenA = tokenA
        self.tokenB = tokenB
        self.reserve_a = Decimal(str(reserve_a))
        self.reserve_b = Decimal(str(reserve_b))
        self.fee = Decimal(str(fee))
        self.total_lp = (self.reserve_a * self.reserve_b).sqrt() if (self.reserve_a and self.reserve_b) else Decimal(
            '0')
        self.lp_balances = {}

    def another_token(self, symbol):
        return self.tokenB if symbol == self.tokenA else self.tokenA

    def price_a_in_b(self):
        if self.reserve_a == Decimal('0'):
            return Decimal('0')
        return +(self.reserve_b / self.reserve_a)

    def preview_swap(self, symbol_in: str, amount_in) -> Decimal:
        """
        Only preview, make no change, return amount_out (Decimal).
        """
        dx = Decimal(str(amount_in))
        if dx <= 0:
            return Decimal('0')

        if symbol_in == self.tokenA:
            x = self.reserve_a
            y = self.reserve_b
        elif symbol_in == self.tokenB:
            x = self.reserve_b
            y = self.reserve_a
        else:
            raise ValueError(f"{symbol_in} is not in this pool!")

        dx_eff = dx * (Decimal('1') - self.fee)
        x_new = x + dx_eff
        y_new = (x * y) / x_new
        dy = y - y_new
        return +dy

    def swap(self, symbol_in: str, amount_in: Decimal) -> Decimal:
        """
        Automotive Market Maker
        Input: symbol of tokenA/b, amount in Decimal
        Output: amount_out(Decimal) to taker
        """
        dx = Decimal(str(amount_in))
        if dx <= 0:
            return Decimal('0')

        if symbol_in == self.tokenA:
            x = self.reserve_a
            y = self.reserve_b
            dx_eff = dx * (Decimal('1') - self.fee)
            x_new = x + dx_eff
            y_new = (x * y) / x_new
            dy = y - y_new
            self.reserve_a = x_new
            self.reserve_b = y_new
            return +dy

        elif symbol_in == self.tokenB:
            x = self.reserve_b
            y = self.reserve_a
            dx_eff = dx * (Decimal('1') - self.fee)
            x_new = x + dx_eff
            y_new = (x * y) / x_new
            dy = y - y_new
            self.reserve_b = x_new
            self.reserve_a = y_new
            return +dy

        else:
            raise ValueError(f"{symbol_in} is not in this pool!")

    def add_lq(self, owner: str, amount_a, amount_b) -> Decimal:
        """
        Adding liquidity in a specified proportion to the pool,
        and returns the LP token.
        """
        a = Decimal(str(amount_a))
        b = Decimal(str(amount_b))
        if a < 0 or b < 0:
            return Decimal('0')

        # Add first time:
        if self.reserve_a == 0 and self.reserve_b == 0:
            self.reserve_a += a
            self.reserve_b += b
            LPT = (self.reserve_a * self.reserve_b).sqrt()
            self.total_lp = LPT
            self.lp_balances[owner] = self.lp_balances.get(owner, Decimal('0')) + LPT
            return +LPT

        ratio_a = a / self.reserve_a
        ratio_b = b / self.reserve_b
        # Fail because the incorrect ratio
        if abs(ratio_a - ratio_b) > Decimal('1e-12'):
            return Decimal('0')

        LPT = ratio_a * self.total_lp
        self.reserve_a += a
        self.reserve_b += b
        self.lp_balances[owner] = self.lp_balances.get(owner, Decimal('0')) + LPT
        return +LPT

    def remove_lq(self, owner: str, lpt) -> tuple:
        """
        Users remove liquidity,
        then it will return the two tokens in a specified ratio.
        """
        amt = Decimal(str(lpt))
        if amt <= 0 or self.total_lp <= 0:
            return (Decimal('0'), Decimal('0'))
        owner_have = self.lp_balances.get(owner, Decimal('0'))
        if owner_have < amt:
            return (Decimal('0'), Decimal('0'))

        share = amt / self.total_lp
        out_a = share * self.reserve_a
        out_b = share * self.reserve_b

        self.reserve_a -= out_a
        self.reserve_b -= out_b
        self.total_lp -= amt
        self.lp_balances[owner] = owner_have - amt
        return (+out_a, +out_b)

    def show(self):
        print(f"Pool {self.tokenA}/{self.tokenB}:")
        print(f"  reserve {self.tokenA}: {self.reserve_a}")
        print(f"  reserve {self.tokenB}: {self.reserve_b}")
        print(f"  price (1 {self.tokenA} = {self.price_a_in_b():.6f} {self.tokenB})")
        print(f"  total LP: {self.total_lp}")
        tokens = list(self.lp_balances.keys())
        print("LP balances:")
        for k, v in self.lp_balances.items():
            print(f"{k}:{v:.6f}")