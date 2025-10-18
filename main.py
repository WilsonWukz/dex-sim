import guidance
import json, os, tempfile
from modules.wallet import Wallet
from modules.DEX import DEX
from modules.LiquitityPool import LiquitityPool
from modules.DEXs import DEXs
from modules.wallets import Wallets
from decimal import Decimal
ADMIN_PASSWORD = 'WILSONWUROX'

def get_wallet_or_fail(wallets_manager: Wallets, owner_name:str) -> Wallet|None:
    wallet = wallets_manager.wallets.get(owner_name)
    if wallet is None:
        return None
    return wallet

def get_dex_or_fail(dexs_manager: DEXs, dex_name:str) -> DEX|None:
    dex = dexs_manager.DEXs.get(dex_name)
    if dex is None:
        return None
    return dex

# Try to convert decimal to string for JSON serialization
def _dec_to_str(obj):
    if isinstance(obj, Decimal):
        return str(obj)
    return obj

def _recursive_serialize(value):
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, dict):
        return {str(k): _recursive_serialize(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_recursive_serialize(v) for v in value]
    return value

def save_state_json(filename:str, dexs_manager, wallets_manager)-> bool:
    """Save state to json file"""
    state = {"DEXs":{}, "Wallets":{}}

    # Dexs and Pools
    for dex_name, dex in dexs_manager.DEXs.items():
        dex_obj = {"pools":[]}
        for pool in dex.pools.values():
            pool_obj = {
                "tokenA": pool.tokenA,
                "tokenB": pool.tokenB,
                "reserve_a": str(pool.reserve_a),
                "reserve_b": str(pool.reserve_b),
                "fee": str(pool.fee),
                "total_lp": str(pool.total_lp),
                "lp_balances":{owner: str(amount) for owner, amount in pool.lp_balances.items()}
            }
            dex_obj["pools"].append(pool_obj)
        state["DEXs"][dex_name] = dex_obj

    # Wallets
    for owner, wallet in wallets_manager.wallets.items():
        w_obj = {
            "owner": wallet.owner,
            "balances": {sym: str(amount) for sym, amount in wallet.balances.items()},
            "lp_tokens": {f"{k[0]}|{k[1]}": str(v) for k, v in wallet.lp_tokens.items()},
            "tr_history": _recursive_serialize(wallet.tr_history)
        }
        state["Wallets"][owner] = w_obj
    try:
        dirnam = os.path.dirname(filename) or "."
        fd, tmp = tempfile.mkstemp(dir=dirnam, prefix="._dexsim_tmp_", text=True)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
        os.replace(tmp, filename)  # atomic move
        print(f"Saved state to {filename}")
        return True
    except Exception as e:
        print("Error saving state:", e)
        return False

def load_state_json(filename: str, DEXsClass, WalletsClass) -> tuple:
    """
    Load state from filename and return (dex_manager, wallet_manager).
    """
    if not os.path.exists(filename):
        raise FileNotFoundError(filename)

    with open(filename, "r", encoding="utf-8") as f:
        state = json.load(f)

    # create new managers
    dex_manager = DEXsClass()
    wallet_manager = WalletsClass()

    # Reconstruct DEXs and pools
    for dex_name, dex_obj in state.get("DEXs", {}).items():
        dex_inst = DEX(dex_name)  # use your DEX class
        dex_manager.add_dex(dex_inst)
        for pool_obj in dex_obj.get("pools", []):
            tokenA = pool_obj["tokenA"]
            tokenB = pool_obj["tokenB"]
            reserve_a = Decimal(pool_obj["reserve_a"])
            reserve_b = Decimal(pool_obj["reserve_b"])
            fee = Decimal(pool_obj.get("fee", "0.003"))
            # construct pool
            pool = LiquitityPool(tokenA, tokenB, reserve_a, reserve_b, fee)
            # restore lp balances & total_lp
            pool.lp_balances = {owner: Decimal(amount) for owner, amount in pool_obj.get("lp_balances", {}).items()}
            pool.total_lp = Decimal(pool_obj.get("total_lp", str((reserve_a * reserve_b).sqrt())))
            dex_inst.register_pool(pool)

    # Reconstruct wallets
    for owner, w_obj in state.get("Wallets", {}).items():
        fallback_symbol = next(iter(w_obj["balances"].keys()), "USDT")
        fallback_amount = Decimal(w_obj["balances"].get(fallback_symbol, "0"))
        w = Wallet(owner, fallback_symbol, fallback_amount)
        w.balances = {sym: Decimal(amount) for sym, amount in w_obj.get("balances", {}).items()}
        w.lp_tokens = {}
        for k, v in w_obj.get("lp_tokens", {}).items():
            if "|" in k:
                a, b = k.split("|", 1)
                w.lp_tokens[(a, b)] = Decimal(v)
            else:
                w.lp_tokens[k] = Decimal(v)
        w.tr_history = w_obj.get("tr_history", [])
        wallet_manager.add_wallet(w)

    print(f"Loaded state from {filename}")
    return dex_manager, wallet_manager

if __name__ == "__main__":
    dex_manager = DEXs()
    wallet_manager = Wallets()
    guidance.show_guidance()

    # Example Initialization
    uniswap = DEX('Uniswap')
    dex_manager.add_dex(uniswap)
    alice = Wallet('Alice','ETH', 10)
    alice.deposit('USDT', 20000)
    wallet_manager.add_wallet(alice)

    ETH_USDT = LiquitityPool('ETH', 'USDT', 10, 20000)
    uniswap.register_pool(ETH_USDT)

    print("\n--- Preset Status ---")
    alice.show_balance()
    uniswap.get_pool("ETH", "USDT").show()
    print("--------------------\n")

    ex = False
    while not ex:
        try:
            print("############################################################")
            command = input("Enter your command (Type 'GUIDE' for help): ").strip().upper()
            if command == "GUIDE":
                guidance.show_guidance()

            #DEX Related
            elif command == "+DEX":
                dex_name = input("Enter DEX name: ")
                dex_obj = get_dex_or_fail(dex_manager, dex_name)
                if dex_obj is not None:
                    print(f"DEX {dex_name} is already registered!")
                    continue
                dex = DEX(dex_name)
                dex_manager.add_dex(dex)
                print(f"DEX {dex_name} added successfully!")
            elif command == "SHOW DEXS":
                dexs = dex_manager.get_dexs()
                if not dexs:
                    print("No DEXs registered.")
                for dex_name, dex in dexs.items():
                    print(f" - {dex_name}")

            #Wallet Related
            elif command == "+WALLET":
                owner_name = input("Enter your name: ")
                wlt = get_wallet_or_fail(wallet_manager, owner_name)
                if wlt is not None:
                    print(f"Wallet {owner_name} is already registered!")
                    continue
                symbol = input("Enter your wallet symbol: ")
                amount = input("Enter your symbol amount: ")
                wallet = Wallet(owner_name, symbol, amount)
                wallet_manager.add_wallet(wallet)
                print(f"  --Wallet for '{owner_name}' created successfully with {amount} {symbol}.")
            elif command == "SHOW WALLET":
                owner_name = input("Enter your name: ")
                wlt = get_wallet_or_fail(wallet_manager, owner_name)
                if not wlt:
                    print(f"No such a wallet {owner_name} exists!")
                    continue
                print("------------------")
                wlt.show_balance()

            elif command == "SHOW WALLETS":
                ipt = input("Are you the administrator? Please input the PASSWORD: ")
                if ipt != ADMIN_PASSWORD:
                    print("Wrong password. Request is terminated.")
                    continue
                wlts = wallet_manager.get_wallet()
                print("\n Registered Wallets:")
                if not wlts:
                    print("No Wallets registered.")
                    continue
                for name, wlt in wlts.items():
                    print(f" - {name}")
                    wlt.show_balance()
            elif command == "DEPOSIT":
                owner_name = input("Enter your name: ")
                wlt = get_wallet_or_fail(wallet_manager, owner_name)
                if not wlt:
                    print(f"No Wallet {owner_name} registered.")
                    continue
                symbol = input("Enter the symbol you want to deposit: ")
                amount = Decimal(input(f"How much you want to deposit the {symbol}? "))
                wlt.deposit(symbol, amount)
                print(f"  --Deposited {symbol} to {amount} {symbol}, and here is the updated wallet balance:")
                wlt.show_balance()
                wlt.tr_history.append({
                    "type": "DEPOSIT",
                    "symbol": symbol,
                    "amount": amount
                })

            #Pool Related
            elif command == "+POOL":
                dex_name = input("Enter the DEX name to register the pool in: ")
                dex = get_dex_or_fail(dex_manager, dex_name)
                if not dex:
                    print(f"No DEX {dex_name} registered. Please '+DEX' for {dex_name} first.")
                    continue
                tA = input("Enter the token A (e.g., BTC): ")
                tB = input("Enter the token B (e.g., USDT): ")
                nA = input(f"Enter initial reserve amount of {tA}: ")
                nB = input(f"Enter initial reserve amount of {tB}: ")
                pool = LiquitityPool(tA, tB, nA, nB)
                dex.register_pool(pool)
                print(f"  --Liquidity Pool {tA}/{tB} registered in {dex_name} successfully!")
            elif command == "SHOW POOLS":
                dex_name = input("Enter the DEX name you want to show its pool: ")
                dex = get_dex_or_fail(dex_manager, dex_name)
                if not dex: continue
                tA = input("Enter the token A (e.g., BTC): ")
                tB = input("Enter the token B (e.g., USDT): ")
                pool = dex.get_pool(tA, tB)
                if not pool:
                    print(f"Pool {tA}/{tB} not found in DEX {dex_name}.")
                    continue
                elif pool:
                    pool.show()

            # SWAP Trading Related
            elif command == "SWAP":
                owner_name = input("Wallet owner name: ")
                wallet = get_wallet_or_fail(wallet_manager, owner_name)
                if not wallet: continue
                dex_name = input("Enter DEX name to use: ")
                dex = get_dex_or_fail(dex_manager, dex_name)
                if not dex: continue
                token_in = input("Token to swap FROM: ")
                amount_in = Decimal(input(f"Enter amount of {token_in} to swap: "))
                token_out = input("Token to swap TO: ")
                pool = dex.get_pool(token_in, token_out) or dex.get_pool(token_out, token_in)
                if not pool:
                    print(f"Unable to find liquidity pool for {token_in}/{token_out}.")
                    continue
                # Balance check
                if wallet.balance_of(token_in) < amount_in:
                    print(f"Insufficient balance.{owner_name} only has {wallet.balance_of(token_in):.6f}{token_in}.")
                    continue
                amount_out, _ = dex.preview_swap(token_in, amount_in, pool.another_token(token_in))
                if amount_out is None:
                    print("Previous swap failed.")
                    continue
                if not wallet.withdraw(token_in, amount_in):
                    continue

                #DEX Execution
                amount_received = dex.exec_swap(pool, token_in, amount_in)
                wallet.deposit(pool.another_token(token_in), amount_received)
                print("  --Swap done.")
                print(f"   In: {amount_in:.6f} {token_in}")
                print(f"   Out: {amount_received:.6f} {pool.another_token(token_in)}")
                wallet.tr_history.append({
                    "type": "SWAP",
                    "From": token_in,
                    "Amount_in": amount_in,
                    "To": token_out,
                    "Amount_out": amount_received
                })
                pool.show()
                wallet.show_balance()

            # Liquidity Providing
            elif command == "LP":
                owner_name = input("What's your name: ")
                wallet = get_wallet_or_fail(wallet_manager, owner_name)
                if not wallet:
                    print(f"No Wallet {owner_name} registered.")
                    continue
                dex_name = input("Which DEX you want to use?: ")
                dex = get_dex_or_fail(dex_manager, dex_name)
                if not dex:
                    print(f"The DEX {dex_name} not found.")
                    continue
                tA = input(f"\nThe token A you want to provide to the pool of {dex_name}: ")
                tB = input(f"The token B you want to provide to the pool of {dex_name}: ")
                key = (tA, tB)
                pool = dex.get_pool(tA, tB)
                if not pool:
                    print(f"Unable to find liquidity pool for {tA}/{tB} in DEX {dex_name}.")
                    continue
                print(f"Available pool for {tA}/{tB} in DEX {dex_name} is founded:")
                pool.show()
                print(f"   And here is your balance in wallet {owner_name}:\n")
                wallet.show_balance()
                cont = True
                tpl = pool.total_lp
                while cont:
                    print(f"The total liquidity of the pool is {tpl:.6f}.")
                    lpt = Decimal(input(f"How much liquidity you want to provide to the pool of {dex_name}: (Please enter type of 'FLOAT')"))
                    ratio = lpt / tpl
                    amtA = ratio * pool.reserve_a
                    amtB = ratio * pool.reserve_b
                    print(f"To provide liquidity of {lpt}, you will need to pay {amtA:.6f} of {tA} and {amtB:.6f} of {tB}.")
                    confirm = input("\nDo you want to proceed? (Y/N): ")
                    if confirm == "N":
                        print(f"Process cancelled.")
                        ask = input("\nDo you want to back to the main menu? (Enter 'Y' to confirm)")
                        if ask == "Y":
                            cont = False
                        else:
                            continue
                    if not wallet.withdraw(tA, amtA):
                        continue
                    if not wallet.withdraw(tB, amtB):
                        continue
                    lpt = pool.add_lq(owner_name, amtA, amtB)
                    if lpt == 0 or lpt == Decimal('0'):
                        wallet.deposit(tA, amtA)
                        wallet.deposit(tB, amtB)
                        print("Liquidity provide failed. May be wrong ratio of the two tokens.")
                        continue
                    wallet.lp_tokens[key]=lpt
                    print(f"  --Thanks for your liquidity providing, here is the updated balance of {tA} and {tB} pool, and your balance in wallet {wallet}:")
                    pool.show()
                    wallet.show_balance()
                    wallet.tr_history.append({
                        "type": "LP",
                        "Tokens": key,
                        "Amount_A": amtA,
                        "Amount_B": amtB,
                        "Get_Liquidity": lpt
                    })
                    cont = False


            elif command == "RMLP":
                owner_name = input("What's your name: ")
                wallet = get_wallet_or_fail(wallet_manager, owner_name)
                if not wallet:
                    print(f"No Wallet {owner_name} registered.")
                    continue
                dex_name = input("Enter the DEX name you want to use:")
                dex = get_dex_or_fail(dex_manager, dex_name)
                if not dex:
                    print(f"The DEX {dex_name} not found.")
                    continue
                tA = input(f"The token A you want to take from the pool of {dex_name}: ")
                tB = input(f"The token B you want to take from the pool of {dex_name}: ")
                key = (tA, tB)
                pool = dex.get_pool(tA, tB)
                if not pool:
                    print(f"Unable to find such a liquidity pool for {tA}/{tB} in DEX {dex_name}.")
                    continue
                print(f"  --Available pool for {tA}/{tB} in {dex_name} is founded:")
                pool.show()
                lpt = pool.lp_balances[owner_name]
                cont = True
                while cont:
                    dlpt = Decimal(input(f"The liquidity token you want to take from the pool of {dex_name}: (Please enter in type of FLOAT)"))
                    if not dlpt:
                        print(f"Wrong input. Please enter again, in type of FLOAT.")
                        continue
                    if dlpt < lpt:
                        print(f"Not enough liquidity token of {dlpt} of you in the pool {tA}/{tB}.")
                        continue
                    returnA, returnB = pool.remove_lq(owner_name, dlpt)
                    wallet.deposit(tA, returnA)
                    wallet.deposit(tB, returnB)
                    print(f"Your liquidity token of {dlpt} in your wallet {wallet} is now removed.")
                    print(f"  --{returnA} of {tA} and {returnB} of {tB} have been refunded to your wallet {wallet}.")
                    print(f"  --Thanks for your liquidity providing experience, looking forward to your future participation")
                    wallet.tr_history.append({
                        "type": "RMLP",
                        "Tokens": key,
                        "Amount_A": returnA,
                        "Amount_B": returnB,
                        "Use_Liquidity": dlpt
                    })
                    cont = False

            elif command == "HISTORY":
                owner_name = input("What's your name: ")
                wallet = get_wallet_or_fail(wallet_manager, owner_name)
                if not wallet:
                    print(f"No Wallet {owner_name} registered.")
                    continue
                for record in wallet.tr_history:
                    print(record)


            elif command == "SAVE":
                fname = input("Enter filename to save (default: dexsim_state.json): ").strip()
                if not fname:
                    fname = "dexsim_state.json"
                save_state_json(fname, dex_manager, wallet_manager)

                # LOAD state (will replace current managers)
            elif command == "LOAD":
                fname = input("Enter filename to load (default: dexsim_state.json): ").strip()
                if not fname:
                    fname = "dexsim_state.json"
                try:
                    dex_manager, wallet_manager = load_state_json(fname, DEXs, Wallets)
                    print("State loaded. Current DEXs and wallets updated.")
                except FileNotFoundError:
                    print("File not found:", fname)
                except Exception as e:
                    print("Failed to load state:", e)

            # exit
            elif command == "EXIT":
                ex = True

            else:
                print(f"Unknown command {command}. Please view guidance.")

        except Exception as e:
            print(f"\nError: {e}")
            print("Please check your input.")





