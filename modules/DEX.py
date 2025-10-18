# modules.DEX.py
# Import Necessary Packages
from decimal import Decimal


class DEX:
    def __init__(self, name: str):
        self.name = name
        self.pools = {}

    def pair_key(self, a: str, b: str):
        return frozenset({a, b})

    def register_pool(self, pool):
        key = self.pair_key(pool.tokenA, pool.tokenB)
        self.pools[key] = pool

    def get_pool(self, tokenA, tokenB):
        return self.pools.get(self.pair_key(tokenA, tokenB))

    def preview_swap(self, token_in, amount_in, token_out=None):
        amt = Decimal(str(amount_in))
        pool = None
        if token_out:
            pool = self.get_pool(token_in, token_out)
        else:
            for p in self.pools.values():
                if token_in in (p.tokenA, p.tokenB):
                    pool = p
                    break

        if pool is None:
            return None, None

        if token_in not in (pool.tokenA, pool.tokenB):
            return None, None

        out = pool.preview_swap(token_in, amt)
        return out, pool

    def exec_swap(self, pool, token_in: str, amount_in):
        amt = Decimal(str(amount_in))
        if pool is None:
            raise ValueError("exec_swap: pool is None")
        if token_in not in (pool.tokenA, pool.tokenB):
            raise ValueError(f"exec_swap: token_in {token_in} not in pool {pool.tokenA}/{pool.tokenB}")
        # Execution
        amount_out = pool.swap(token_in, amount_in)
        return +amount_out

    def show_dex(self):
        for p in self.pools:
            print(f"{p.tokenA}: {p.tokenB}")