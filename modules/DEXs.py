# modules.DEXs.py
from modules.DEX import DEX

class DEXs:
    def __init__(self):
        self.DEXs = {}

    def add_dex(self, dex):
        self.DEXs[dex.name] = dex

    def get_dexs(self):
        return self.DEXs

    def get_dex(self, name):
        return self.DEXs.get(name)
